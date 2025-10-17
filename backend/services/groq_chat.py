from groq import Groq
import os
from dotenv import load_dotenv
from datetime import datetime
import subprocess
from shutil import which
import re
import time
import random

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set. Add it to your environment or .env file.")

client = Groq(api_key=api_key)

def retry_with_backoff(func, max_retries=3, base_delay=1, max_delay=60):
    """Retry a function with exponential backoff and jitter."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_msg = str(e)
            print(f"Attempt {attempt + 1} failed: {error_msg}")
            
            # Check if it's a rate limit or overload error
            if any(keyword in error_msg.lower() for keyword in ['rate limit', '429', 'quota', 'overloaded', 'too many requests']):
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    # Exponential backoff with jitter
                    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                    print(f"API rate limited, retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    continue
            
            # If it's not a retryable error or last attempt, re-raise
            if attempt == max_retries - 1:
                # Provide user-friendly error messages
                if 'rate limit' in error_msg.lower() or '429' in error_msg:
                    raise RuntimeError("🚫 Groq API rate limit exceeded. Please try again in a few minutes, or use Gemini instead.")
                elif 'quota' in error_msg.lower():
                    raise RuntimeError("🚫 API quota exceeded. Please check your Groq API limits or try Gemini instead.")
                elif 'invalid' in error_msg.lower() and 'key' in error_msg.lower():
                    raise RuntimeError("🚫 Invalid Groq API key. Please check your GROQ_API_KEY in the .env file.")
                else:
                    raise RuntimeError(f"🚫 Groq API error: {error_msg}")
            raise

def read_template(template_path: str) -> str:
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at: {template_path}")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def clean_template_from_images(template_tex: str) -> str:
    """Remove image-related content from template to avoid missing file issues."""
    # Remove includegraphics commands
    template_tex = re.sub(r'\\includegraphics\[.*?\]\{.*?\}', '', template_tex, flags=re.DOTALL)
    
    # Remove figure environments completely
    template_tex = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', template_tex, flags=re.DOTALL)
    
    # Remove references to figures in text
    template_tex = re.sub(r'Figure~?\\ref\{[^}]+\}', 'the analysis', template_tex)
    template_tex = re.sub(r'figure~?\\ref\{[^}]+\}', 'the analysis', template_tex)
    
    # Clean up any leftover figure references
    template_tex = re.sub(r'\\ref\{fig:[^}]+\}', 'the analysis', template_tex)
    
    # Fix header height issue by adding proper header height setting
    if '\\pagestyle{fancy}' in template_tex and '\\setlength{\\headheight}' not in template_tex:
        template_tex = template_tex.replace(
            '\\pagestyle{fancy}',
            '\\pagestyle{fancy}\n\\setlength{\\headheight}{14.5pt}'
        )
    
    # Fix cite/natbib conflict by removing cite package when natbib is present
    if '\\usepackage{natbib}' in template_tex:
        template_tex = re.sub(r'\\usepackage\{cite\}\n?', '', template_tex)
        # Ensure natbib uses numerical style to match the bibliography format
        template_tex = template_tex.replace(
            '\\usepackage{natbib}',
            '\\usepackage[numbers]{natbib}'
        )
    
    # Also fix the bibliographystyle to be compatible with natbib numbers
    if '\\bibliographystyle{unsrtnat}' in template_tex:
        template_tex = template_tex.replace(
            '\\bibliographystyle{unsrtnat}',
            '\\bibliographystyle{unsrtnat}'  # This is already correct for numerical
        )
    
    return template_tex


def build_system_instruction(template_tex: str) -> str:
    # Clean template from images first
    clean_template = clean_template_from_images(template_tex)
    
    return (
        "You are a professional research writing assistant that outputs LaTeX only. "
        "Follow the provided LaTeX template exactly. Replace bracketed placeholders with concrete, topic-relevant content. "
        "Output must be a single valid LaTeX document starting with \\documentclass and ending with \\end{document}. "
        "Do NOT include any explanations, markdown, code fences, or commentary. "
        "Do NOT include any images, figures, or \\includegraphics commands. "
        "Do NOT invent citations; use neutral placeholders in the bibliography consistent with the template if needed. "
        "In bibliography entries, always escape & characters as \\& (backslash-ampersand). "
        "Use numerical citation style with natbib: \\citep{key} for parenthetical and \\citet{key} for textual citations. "
        "Bibliography entries should follow the numerical format: Author, A. (Year). Title. Journal, Volume(Issue), Pages. "
        "Focus on text content, tables, and mathematical equations only. "
        "Ensure the document compiles with standard LaTeX engines and follows proper LaTeX syntax.\n\n"
        "TEMPLATE BEGIN\n" + clean_template + "\nTEMPLATE END"
    )


def fix_bibliography_formatting(tex_content: str) -> str:
    """Fix common bibliography formatting issues."""
    # Fix unescaped & characters in bibliography entries
    # This regex finds & characters that are not already escaped and are within bibliography entries
    def replace_ampersand(match):
        content = match.group(0)
        # Replace & with \& but don't double-escape
        content = re.sub(r'(?<!\\)&', r'\\&', content)
        return content
    
    # Apply the fix within bibliography entries
    tex_content = re.sub(r'\\bibitem\{[^}]+\}.*?(?=\\bibitem|\n\n|\\end\{thebibliography\})', 
                        replace_ampersand, tex_content, flags=re.DOTALL)
    
    # Ensure citations use proper natbib numerical format
    # Convert any author-year style citations to numerical
    tex_content = re.sub(r'\\cite\{([^}]+)\}', r'\\citep{\1}', tex_content)
    
    # Fix common bibliography formatting issues for numerical style
    # Ensure bibitem entries don't have author-year format remnants
    def fix_bibitem_format(match):
        entry = match.group(0)
        # Remove any author-year formatting artifacts
        entry = re.sub(r'\([0-9]{4}[a-z]?\)', '', entry)  # Remove (2020a) style years
        return entry
    
    tex_content = re.sub(r'\\bibitem\{[^}]+\}[^\n]*\n(?:[^\n\\][^\n]*\n)*', 
                        fix_bibitem_format, tex_content, flags=re.MULTILINE)
    
    return tex_content


def remove_images_from_latex(tex_content: str) -> str:
    """Remove all image-related content from LaTeX."""
    # Remove includegraphics commands
    tex_content = re.sub(r'\\includegraphics\[.*?\]\{.*?\}', '', tex_content, flags=re.DOTALL)
    
    # Remove figure environments completely
    tex_content = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', tex_content, flags=re.DOTALL)
    
    # Remove references to figures in text and replace with generic text
    tex_content = re.sub(r'Figure~?\\ref\{[^}]+\}', 'the analysis', tex_content)
    tex_content = re.sub(r'figure~?\\ref\{[^}]+\}', 'the analysis', tex_content)
    tex_content = re.sub(r'\\ref\{fig:[^}]+\}', 'the analysis', tex_content)
    
    # Remove figure labels
    tex_content = re.sub(r'\\label\{fig:[^}]+\}', '', tex_content)
    
    # Clean up any leftover graphicx draft mode references
    tex_content = re.sub(r'placeholder_.*?\.pdf', '', tex_content)
    
    # Clean up multiple newlines
    tex_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', tex_content)
    
    return tex_content


def sanitize_latex_output(text: str) -> str:
    """Clean and sanitize the LaTeX output from the model."""
    # Remove common code-fence wrappers if present
    if text.strip().startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    
    # Remove any remaining image-related content that the model might have generated
    text = remove_images_from_latex(text)
    
    # Fix bibliography formatting issues
    text = fix_bibliography_formatting(text)
    
    return text.strip()


def write_output(tex_content: str, out_dir: str = "output") -> str:
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"research_paper_{timestamp}.tex")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)
    return out_path


def compile_latex_with_system(tex_path: str, export_dir: str = "export") -> str:
    """Compile LaTeX using system installation (faster than Docker)."""
    os.makedirs(export_dir, exist_ok=True)
    
    # Get absolute paths
    tex_abs = os.path.abspath(tex_path)
    export_abs = os.path.abspath(export_dir)
    
    jobname = os.path.splitext(os.path.basename(tex_path))[0]
    
    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={export_abs}",
        f"-jobname={jobname}",
        tex_abs
    ]
    
    try:
        # Run first time
        result1 = subprocess.run(cmd, capture_output=True, text=True, cwd=export_abs)
        if result1.returncode != 0:
            print("First LaTeX run had issues, attempting to continue...")
            print("First run errors:", result1.stderr)
            
            # For natbib errors, we can try to continue in non-interactive mode
            cmd_continue = [
                "pdflatex",
                "-interaction=nonstopmode",
                f"-output-directory={export_abs}",
                f"-jobname={jobname}",
                tex_abs
            ]
            
            # Try without halt-on-error for bibliography issues
            result1 = subprocess.run(cmd_continue, capture_output=True, text=True, cwd=export_abs, input="\n")
        
        # Run second time for cross-references
        result2 = subprocess.run(cmd_continue if 'cmd_continue' in locals() else cmd, 
                               capture_output=True, text=True, cwd=export_abs, input="\n")
        
        # Check if PDF was actually created (sometimes LaTeX succeeds with warnings)
        pdf_path = os.path.join(export_abs, f"{jobname}.pdf")
        if os.path.exists(pdf_path):
            return pdf_path
        else:
            print("LaTeX output:")
            print(result2.stdout)
            if result2.stderr:
                print("LaTeX errors:")
                print(result2.stderr)
            raise subprocess.CalledProcessError(result2.returncode or 1, cmd)
            
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"LaTeX compilation failed. Check the .tex content and logs.") from e
    
    return pdf_path


def compile_latex_with_docker(tex_path: str, export_dir: str = "export") -> str:
    """Compile LaTeX using Docker (fallback option)."""
    if which("docker") is None:
        raise RuntimeError("Docker is required to compile LaTeX. Please install Docker and ensure it's on PATH.")

    os.makedirs(export_dir, exist_ok=True)

    project_root = os.getcwd()
    host_workdir = project_root
    tex_abs = os.path.abspath(tex_path)

    # Container paths mirror host via single bind mount at /workdir
    container_workdir = "/workdir"
    container_tex = os.path.join(container_workdir, os.path.relpath(tex_abs, host_workdir))
    container_export_dir = os.path.join(container_workdir, export_dir)

    jobname = os.path.splitext(os.path.basename(tex_path))[0]

    base_cmd = [
        "docker", "run", "--rm",
        "-v", f"{host_workdir}:{container_workdir}",
        "-w", container_workdir,
        "texlive/texlive:latest",
        "pdflatex", "-interaction=nonstopmode", "-halt-on-error",
        f"-output-directory={container_export_dir}",
        "-jobname", jobname,
        container_tex,
    ]

    try:
        subprocess.run(base_cmd, check=True)
        subprocess.run(base_cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("LaTeX compilation failed. Check the .tex content and LaTeX logs in the export directory.") from e

    pdf_name = jobname + ".pdf"
    pdf_host_path = os.path.join(export_dir, pdf_name)
    if not os.path.exists(pdf_host_path):
        raise RuntimeError(f"Expected PDF not found at {pdf_host_path}")
    return pdf_host_path


def main() -> None:
    try:
        topic = input("Enter the research paper topic: ").strip()
    except EOFError:
        raise RuntimeError("No topic provided via stdin.")

    if not topic:
        raise RuntimeError("Topic cannot be empty.")

    template_path = os.path.join("paper", "research-pap.tex")
    template_tex = read_template(template_path)

    system_instruction = build_system_instruction(template_tex)

    user_prompt = (
        "Generate a complete research paper in LaTeX strictly following the template. "
        f"Topic: {topic}. "
        "Ensure all placeholders are replaced with detailed, coherent content relevant to this topic. "
        "Do NOT include any figures, images, or \\includegraphics commands. "
        "Focus on comprehensive text content, tables, and mathematical equations only."
    )

    print("Generating research paper...")
    
    def make_api_call():
        return client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",  # Using Llama 3.3 70B for best quality
            temperature=0.7,  # Some creativity but still focused
            max_tokens=8000,  # Sufficient for a research paper
        )
    
    try:
        chat_completion = retry_with_backoff(make_api_call)
        
        tex = sanitize_latex_output(chat_completion.choices[0].message.content or "")
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate content with Groq: {e}")

    if not tex.startswith("\\documentclass") or not tex.strip().endswith("\\end{document}"):
        raise RuntimeError("Model output is not a complete LaTeX document.")

    out_tex_path = write_output(tex)
    print(f"LaTeX written to: {out_tex_path}")

    # Try system LaTeX first, fallback to Docker
    try:
        if which("pdflatex"):
            print("Compiling with system LaTeX...")
            pdf_path = compile_latex_with_system(out_tex_path, export_dir="export")
        else:
            print("System LaTeX not found, using Docker...")
            pdf_path = compile_latex_with_docker(out_tex_path, export_dir="export")
            
        print(f"PDF successfully generated: {pdf_path}")
        
    except Exception as e:
        print(f"Compilation failed: {e}")
        print("You can try to compile manually with:")
        print(f"pdflatex -output-directory=export {out_tex_path}")


if __name__ == "__main__":
    main()