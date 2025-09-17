import streamlit as st
import os
import tempfile
import zipfile
from datetime import datetime
import subprocess
from pathlib import Path
import shutil

# Import your existing modules
try:
    import main as gemini_generator
except ImportError:
    st.error("main.py not found. Please ensure gemini logic is in main.py")
    gemini_generator = None

try:
    import groq_chat as groq_generator
except ImportError:
    st.error("groq_chat.py not found. Please ensure groq logic is in groq_chat.py")
    groq_generator = None

def setup_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Research Paper Generator",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎓 Research Paper Generator")
    st.markdown("Generate academic research papers using AI with LaTeX formatting")

def check_dependencies():
    """Check if required dependencies are available"""
    issues = []
    
    # Check template file
    template_path = os.path.join("paper", "research-pap.tex")
    if not os.path.exists(template_path):
        issues.append("❌ Template not found at paper/research-pap.tex")
    else:
        issues.append("✅ LaTeX template found")
    
    # Check LaTeX
    if not shutil.which("pdflatex"):
        issues.append("⚠️ pdflatex not found - PDF compilation will use Docker (if available)")
    else:
        issues.append("✅ pdflatex found")
    
    # Check Docker (fallback)
    if not shutil.which("pdflatex") and not shutil.which("docker"):
        issues.append("❌ Neither pdflatex nor Docker found - PDF compilation will fail")
    elif not shutil.which("pdflatex") and shutil.which("docker"):
        issues.append("✅ Docker found (will be used for PDF compilation)")
    
    # Check API modules
    if not gemini_generator:
        issues.append("❌ Gemini module (main.py) not available")
    else:
        issues.append("✅ Gemini module available")
    
    if not groq_generator:
        issues.append("❌ Groq module (groq_chat.py) not available")
    else:
        issues.append("✅ Groq module available")
    
    return issues

def setup_template_in_temp_dir(temp_dir):
    """Return absolute path to project template to avoid CWD/copy issues."""
    project_root = Path(__file__).resolve().parent
    original_template = project_root / "paper" / "research-pap.tex"
    if not original_template.exists():
        raise FileNotFoundError(f"Template not found at: {original_template}")
    return str(original_template)

def generate_with_gemini(topic, temp_dir):
    """Generate research paper using Gemini"""
    if not gemini_generator:
        raise RuntimeError("Gemini module not available")
    
    # Change to temp directory for file operations
    original_cwd = os.getcwd()
    try:
        os.chdir(temp_dir)
        
        # Create output and export directories
        os.makedirs("output", exist_ok=True)
        os.makedirs("export", exist_ok=True)
        
        # Setup template
        template_path = setup_template_in_temp_dir(temp_dir)
        
        # Read template
        template_tex = gemini_generator.read_template(template_path)
        system_instruction = gemini_generator.build_system_instruction(template_tex)
        
        user_prompt = (
            "Generate a complete research paper in LaTeX strictly following the template. "
            f"Topic: {topic}. "
            "Ensure all placeholders are replaced with detailed, coherent content relevant to this topic. "
            "Do NOT include any figures, images, or \\includegraphics commands. "
            "Focus on comprehensive text content, tables, and mathematical equations only."
        )
        
        # Generate content
        response = gemini_generator.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            config=gemini_generator.types.GenerateContentConfig(system_instruction=system_instruction),
            contents=user_prompt,
        )
        
        tex = gemini_generator.sanitize_latex_output(response.text or "")
        
        if not tex.startswith("\\documentclass") or not tex.strip().endswith("\\end{document}"):
            raise RuntimeError("Model output is not a complete LaTeX document.")
        
        # Save LaTeX file
        tex_path = gemini_generator.write_output(tex)
        
        # Compile to PDF
        try:
            if shutil.which("pdflatex"):
                pdf_path = gemini_generator.compile_latex_with_system(tex_path, export_dir="export")
            else:
                pdf_path = gemini_generator.compile_latex_with_docker(tex_path, export_dir="export")
        except Exception as e:
            st.warning(f"PDF compilation failed: {e}")
            pdf_path = None
        
        return tex_path, pdf_path
        
    finally:
        os.chdir(original_cwd)

def generate_with_groq(topic, temp_dir):
    """Generate research paper using Groq"""
    if not groq_generator:
        raise RuntimeError("Groq module not available")
    
    # Change to temp directory for file operations
    original_cwd = os.getcwd()
    try:
        os.chdir(temp_dir)
        
        # Create output and export directories
        os.makedirs("output", exist_ok=True)
        os.makedirs("export", exist_ok=True)
        
        # Setup template
        template_path = setup_template_in_temp_dir(temp_dir)
        
        # Read template
        template_tex = groq_generator.read_template(template_path)
        system_instruction = groq_generator.build_system_instruction(template_tex)
        
        user_prompt = (
            "Generate a complete research paper in LaTeX strictly following the template. "
            f"Topic: {topic}. "
            "Ensure all placeholders are replaced with detailed, coherent content relevant to this topic. "
            "Do NOT include any figures, images, or \\includegraphics commands. "
            "Focus on comprehensive text content, tables, and mathematical equations only."
        )
        
        # Generate content
        chat_completion = groq_generator.client.chat.completions.create(
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
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=8000,
        )
        
        tex = groq_generator.sanitize_latex_output(chat_completion.choices[0].message.content or "")
        
        if not tex.startswith("\\documentclass") or not tex.strip().endswith("\\end{document}"):
            raise RuntimeError("Model output is not a complete LaTeX document.")
        
        # Save LaTeX file
        tex_path = groq_generator.write_output(tex)
        
        # Compile to PDF
        try:
            if shutil.which("pdflatex"):
                pdf_path = groq_generator.compile_latex_with_system(tex_path, export_dir="export")
            else:
                pdf_path = groq_generator.compile_latex_with_docker(tex_path, export_dir="export")
        except Exception as e:
            st.warning(f"PDF compilation failed: {e}")
            pdf_path = None
        
        return tex_path, pdf_path
        
    finally:
        os.chdir(original_cwd)

def create_download_files(tex_path, pdf_path, temp_dir):
    """Create downloadable files"""
    downloads = {}
    
    if tex_path and os.path.exists(tex_path):
        with open(tex_path, 'rb') as f:
            downloads['latex'] = {
                'data': f.read(),
                'filename': os.path.basename(tex_path),
                'mime': 'text/plain'
            }
    
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            downloads['pdf'] = {
                'data': f.read(),
                'filename': os.path.basename(pdf_path),
                'mime': 'application/pdf'
            }
    
    # Create zip file with both
    if downloads:
        zip_path = os.path.join(temp_dir, "research_paper_bundle.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            if 'latex' in downloads:
                zipf.writestr(downloads['latex']['filename'], downloads['latex']['data'])
            if 'pdf' in downloads:
                zipf.writestr(downloads['pdf']['filename'], downloads['pdf']['data'])
        
        with open(zip_path, 'rb') as f:
            downloads['zip'] = {
                'data': f.read(),
                'filename': 'research_paper_bundle.zip',
                'mime': 'application/zip'
            }
    
    return downloads

def main():
    setup_page()
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Check dependencies
    issues = check_dependencies()
    if issues:
        with st.sidebar.expander("⚠️ System Status", expanded=True):
            for issue in issues:
                st.write(issue)
    
    # API Provider selection
    api_provider = st.sidebar.selectbox(
        "🤖 Choose AI Provider",
        ["Gemini (Google)", "Groq (Llama)"],
        help="Select which AI provider to use for content generation"
    )
    
    # API Key status
    if api_provider == "Gemini (Google)":
        api_key_env = "GOOGLE_API_KEY"
        module_available = gemini_generator is not None
    else:
        api_key_env = "GROQ_API_KEY"
        module_available = groq_generator is not None
    
    api_key_set = bool(os.getenv(api_key_env))
    
    if not api_key_set:
        st.sidebar.error(f"❌ {api_key_env} not set in environment")
    else:
        st.sidebar.success(f"✅ {api_key_env} configured")
    
    if not module_available:
        st.sidebar.error(f"❌ {api_provider} module not available")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Research Paper Configuration")
        
        # Topic input
        topic = st.text_input(
            "Research Topic",
            placeholder="Enter your research paper topic (e.g., 'Generative AI', 'Climate Change', etc.)",
            help="Describe the main subject of your research paper"
        )
        
        # Template info
        st.subheader("📄 LaTeX Template")
        template_path = os.path.join("paper", "research-pap.tex")
        if os.path.exists(template_path):
            st.success("✅ Using template: paper/research-pap.tex")
            with st.expander("Preview Template Content"):
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                    st.code(template_content[:1000] + "..." if len(template_content) > 1000 else template_content, 
                           language='latex')
                except Exception as e:
                    st.error(f"Error reading template: {e}")
        else:
            st.error("❌ Template not found at paper/research-pap.tex")
    
    with col2:
        st.header("🚀 Generation")
        
        # Generation button
        can_generate = (
            topic and 
            os.path.exists(template_path) and
            api_key_set and 
            module_available
        )
        
        if st.button(
            "🎯 Generate Research Paper", 
            disabled=not can_generate,
            help="Generate research paper using selected AI provider"
        ):
            if not can_generate:
                if not topic:
                    st.error("Please enter a research topic")
                elif not os.path.exists(template_path):
                    st.error("Template file not found")
                elif not api_key_set:
                    st.error("API key not configured")
                elif not module_available:
                    st.error("AI module not available")
            else:
                # Create temporary directory for processing
                with tempfile.TemporaryDirectory() as temp_dir:
                    try:
                        with st.spinner(f"Generating research paper using {api_provider}..."):
                            
                            # Generate paper
                            if api_provider == "Gemini (Google)":
                                tex_path, pdf_path = generate_with_gemini(topic, temp_dir)
                            else:
                                tex_path, pdf_path = generate_with_groq(topic, temp_dir)
                            
                            # Create downloadable files
                            downloads = create_download_files(tex_path, pdf_path, temp_dir)
                            
                            # Store in session state for download
                            st.session_state['downloads'] = downloads
                            st.session_state['generation_complete'] = True
                            
                        st.success("✅ Research paper generated successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Generation failed: {str(e)}")
    
    # Download section
    if st.session_state.get('generation_complete', False) and 'downloads' in st.session_state:
        st.header("📥 Download Generated Files")
        
        downloads = st.session_state['downloads']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'latex' in downloads:
                st.download_button(
                    label="📄 Download LaTeX (.tex)",
                    data=downloads['latex']['data'],
                    file_name=downloads['latex']['filename'],
                    mime=downloads['latex']['mime'],
                    help="Download the generated LaTeX source file"
                )
        
        with col2:
            if 'pdf' in downloads:
                st.download_button(
                    label="📑 Download PDF",
                    data=downloads['pdf']['data'],
                    file_name=downloads['pdf']['filename'],
                    mime=downloads['pdf']['mime'],
                    help="Download the compiled PDF file"
                )
        
        with col3:
            if 'zip' in downloads:
                st.download_button(
                    label="🗜️ Download All (ZIP)",
                    data=downloads['zip']['data'],
                    file_name=downloads['zip']['filename'],
                    mime=downloads['zip']['mime'],
                    help="Download both LaTeX and PDF in a ZIP bundle"
                )
        
        # Preview section
        with st.expander("👀 Preview Generated Content"):
            if 'latex' in downloads:
                st.subheader("LaTeX Source")
                latex_content = downloads['latex']['data'].decode('utf-8')
                st.code(latex_content, language='latex')
    
    # Instructions
    with st.expander("📖 Instructions"):
        st.markdown("""
        ### How to Use:
        
        1. **Choose AI Provider**: Select between Gemini or Groq in the sidebar
        2. **Check System Status**: Ensure all dependencies are satisfied (shown in sidebar)
        3. **Set API Key**: Make sure your API key is set in environment variables
           - For Gemini: `GOOGLE_API_KEY`
           - For Groq: `GROQ_API_KEY`
        4. **Enter Topic**: Provide a clear, specific research paper topic
        5. **Generate**: Click the generate button to create your research paper
        6. **Download**: Use the download buttons to get your LaTeX and PDF files
        
        ### Template:
        The app uses a fixed LaTeX template located at `paper/research-pap.tex`. This template includes:
        - Standard academic paper structure
        - Bibliography support with natbib
        - Professional formatting
        - All necessary LaTeX packages
        
        ### Requirements:
        - **Python packages**: `streamlit`, `google-genai` or `groq`, `python-dotenv`
        - **LaTeX**: pdflatex installation OR Docker for PDF compilation
        - **API Keys**: Valid keys for your chosen AI provider
        - **Template**: `paper/research-pap.tex` file in your project directory
        
        ### Expected File Structure:
        ```
        your_project/
        ├── streamlit_app.py (this GUI)
        ├── main.py (Gemini logic)
        ├── groq_chat.py (Groq logic)
        ├── paper/
        │   └── research-pap.tex (LaTeX template)
        └── .env (API keys)
        ```
        
        ### Features:
        - **Smart AI Selection**: Choose the best model for your needs
        - **Automatic Processing**: Template setup and compilation handled automatically
        - **Error Recovery**: Graceful handling of compilation issues
        - **Multiple Downloads**: Get LaTeX source, PDF, or bundled ZIP
        - **Live Preview**: View generated content before downloading
        """)

if __name__ == "__main__":
    # Initialize session state
    if 'generation_complete' not in st.session_state:
        st.session_state['generation_complete'] = False
    
    main()