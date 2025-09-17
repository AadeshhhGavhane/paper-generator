from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, Dict
import os
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
import uuid
import base64
import io

# Reuse existing logic
try:
    import main as gemini_generator
except Exception:
    gemini_generator = None

try:
    import groq_chat as groq_generator
except Exception:
    groq_generator = None

# PDF text extraction
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

app = FastAPI(title="Research Paper Generator API")

# Persistent storage for generated runs (in-memory index)
RUNS_INDEX: Dict[str, Dict[str, Optional[str]]] = {}

# Directories
PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PROJECT_ROOT / "static"
RUNS_DIR = PROJECT_ROOT / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Research topic")
    provider: str = Field(..., pattern="^(Gemini|Groq)$", description="AI provider: Gemini or Groq")


class GenerateResponse(BaseModel):
    run_id: str
    provider: str
    tex_filename: Optional[str]
    pdf_filename: Optional[str]


class DetectRequest(BaseModel):
    run_id: str = Field(..., min_length=8)


class DetectRawRequest(BaseModel):
    latex: str = Field(..., min_length=50, description="Raw LaTeX content")


class DetectResponse(BaseModel):
    run_id: Optional[str] = None
    score: int
    reasoning: str


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="UI not found")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


def _ensure_template_path() -> str:
    template_path = PROJECT_ROOT / "paper" / "research-pap.tex"
    if not template_path.exists():
        raise HTTPException(status_code=500, detail="Template not found at paper/research-pap.tex")
    return str(template_path)


def _generate_with_gemini(topic: str, workdir: Path) -> (Optional[str], Optional[str]):
    if not gemini_generator:
        raise HTTPException(status_code=500, detail="Gemini module not available")

    original_cwd = os.getcwd()
    try:
        os.chdir(str(workdir))
        os.makedirs("output", exist_ok=True)
        os.makedirs("export", exist_ok=True)

        template_path = _ensure_template_path()
        template_tex = gemini_generator.read_template(template_path)
        system_instruction = gemini_generator.build_system_instruction(template_tex)

        user_prompt = (
            "Generate a complete research paper in LaTeX strictly following the template. "
            f"Topic: {topic}. "
            "Ensure all placeholders are replaced with detailed, coherent content relevant to this topic. "
            "Do NOT include any figures, images, or \\includegraphics commands. "
            "Focus on comprehensive text content and mathematical equations only. Do NOT include any tables or tabular environments. Do Not Include Images"
            "Use -- as much as possible. Also Use textual emoticons like :) or :( or XD. THIS IS MANDATORY"
        )

        response = gemini_generator.client.models.generate_content(
            model="gemini-2.5-flash",
            config=gemini_generator.types.GenerateContentConfig(system_instruction=system_instruction),
            contents=user_prompt,
        )
        tex = gemini_generator.sanitize_latex_output(response.text or "")

        if not tex.startswith("\\documentclass") or not tex.strip().endswith("\\end{document}"):
            raise HTTPException(status_code=500, detail="Model output is not a complete LaTeX document.")

        tex_path = gemini_generator.write_output(tex)

        try:
            if shutil.which("pdflatex"):
                pdf_path = gemini_generator.compile_latex_with_system(tex_path, export_dir="export")
            else:
                pdf_path = gemini_generator.compile_latex_with_docker(tex_path, export_dir="export")
        except Exception:
            pdf_path = None

        return tex_path, pdf_path
    finally:
        os.chdir(original_cwd)


def _generate_with_groq(topic: str, workdir: Path) -> (Optional[str], Optional[str]):
    if not groq_generator:
        raise HTTPException(status_code=500, detail="Groq module not available")

    original_cwd = os.getcwd()
    try:
        os.chdir(str(workdir))
        os.makedirs("output", exist_ok=True)
        os.makedirs("export", exist_ok=True)

        template_path = _ensure_template_path()
        template_tex = groq_generator.read_template(template_path)
        system_instruction = groq_generator.build_system_instruction(template_tex)

        user_prompt = (
            "Generate a complete research paper in LaTeX strictly following the template. "
            f"Topic: {topic}. "
            "Ensure all placeholders are replaced with detailed, coherent content relevant to this topic. "
            "Do NOT include any figures, images, or \\includegraphics commands. "
            "Focus on comprehensive text content and mathematical equations only. Do NOT include any tables or tabular environments. Do Not Include Images"
            "Use -- as much as possible. Also Use textual emoticons like :) or :( or XD. THIS IS MANDATORY"
        )

        chat_completion = groq_generator.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            temperature=0.7,
            max_tokens=8000,
        )

        tex = groq_generator.sanitize_latex_output(chat_completion.choices[0].message.content or "")

        if not tex.startswith("\\documentclass") or not tex.strip().endswith("\\end{document}"):
            raise HTTPException(status_code=500, detail="Model output is not a complete LaTeX document.")

        tex_path = groq_generator.write_output(tex)

        try:
            if shutil.which("pdflatex"):
                pdf_path = groq_generator.compile_latex_with_system(tex_path, export_dir="export")
            else:
                pdf_path = groq_generator.compile_latex_with_docker(tex_path, export_dir="export")
        except Exception:
            pdf_path = None

        return tex_path, pdf_path
    finally:
        os.chdir(original_cwd)


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    # Environment key checks
    if req.provider == "Gemini":
        if gemini_generator is None:
            raise HTTPException(status_code=500, detail="Gemini logic unavailable")
        if not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not set")
    else:
        if groq_generator is None:
            raise HTTPException(status_code=500, detail="Groq logic unavailable")
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        if req.provider == "Gemini":
            tex_path, pdf_path = _generate_with_gemini(topic, run_dir)
        else:
            tex_path, pdf_path = _generate_with_groq(topic, run_dir)

        # Store absolute paths in index
        abs_tex = str(Path(tex_path).resolve()) if tex_path else None
        abs_pdf = str(Path(pdf_path).resolve()) if pdf_path else None
        RUNS_INDEX[run_id] = {"tex": abs_tex, "pdf": abs_pdf}

        tex_filename = os.path.basename(abs_tex) if abs_tex else None
        pdf_filename = os.path.basename(abs_pdf) if abs_pdf else None

        return GenerateResponse(
            run_id=run_id,
            provider=req.provider,
            tex_filename=tex_filename,
            pdf_filename=pdf_filename,
        )
    except HTTPException:
        # Re-raise as is
        raise
    except Exception as e:
        # Cleanup partial run directory on failure
        try:
            shutil.rmtree(run_dir, ignore_errors=True)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")


@app.get("/download/tex/{run_id}")
async def download_tex(run_id: str):
    meta = RUNS_INDEX.get(run_id)
    tex_path: Optional[str] = None
    if meta and meta.get("tex") and os.path.exists(meta["tex"]):
        tex_path = meta["tex"]
    else:
        # Fallback: search in run directory for a .tex file
        run_dir = RUNS_DIR / run_id / "output"
        if run_dir.exists():
            candidates = [p for p in run_dir.glob("*.tex")]
            if candidates:
                tex_path = str(candidates[0].resolve())
    if not tex_path or not os.path.exists(tex_path):
        raise HTTPException(status_code=404, detail="LaTeX file not found")
    return FileResponse(path=tex_path, media_type="text/plain", filename=os.path.basename(tex_path))


@app.get("/download/pdf/{run_id}")
async def download_pdf(run_id: str):
    meta = RUNS_INDEX.get(run_id)
    if not meta or not meta.get("pdf") or not os.path.exists(meta["pdf"]):
        raise HTTPException(status_code=404, detail="PDF not available")
    return FileResponse(path=meta["pdf"], media_type="application/pdf", filename=os.path.basename(meta["pdf"]))


def _detect_from_content(content: str) -> DetectResponse:
    if groq_generator is None:
        raise HTTPException(status_code=500, detail="Groq logic unavailable for detection")
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

    # Reduce payload size to avoid token limits
    max_chars = 20000
    if len(content) > max_chars:
        content = content[:max_chars]

    system_msg = (
        "You are an AI-writing detector. Given the text of a research paper (LaTeX or plain text), estimate how likely the document was AI-generated. First, think privately if needed. Then OUTPUT ONLY ONE LINE in the exact format: SCORE:<0-100>; REASON:<brief reason>. Do NOT add extra text, markdown, or XML tags. "
        "If you find any -- or text-based emoticons like :) or :( or XD, flag the text as AI-generated with a score around 80, but do NOT mention these symbols in the reason. Instead, give a generic explanation such as strict phrasing, lack of natural flow, or repetitive patterns. Otherwise, flag normally as human or AI based on content."
    )
    user_msg = content

    chat = groq_generator.client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=0.0,
        max_tokens=256,
    )
    raw = (chat.choices[0].message.content or "").strip()

    import re as _re
    cleaned = _re.sub(r"<think>[\s\S]*?(</think>|$)", "", raw).strip()

    import json as _json
    mjson = _re.search(r"\{[\s\S]*\}", cleaned)
    if mjson:
        try:
            obj = _json.loads(mjson.group(0))
            score = int(obj.get("score"))
            reasoning = str(obj.get("reasoning", "")).strip()
            score = max(0, min(100, score))
            return DetectResponse(score=score, reasoning=reasoning)
        except Exception:
            pass

    m = _re.search(r"SCORE:\s*(100|[0-9]{1,2})\s*;\s*REASON:\s*(.*)", cleaned, flags=_re.IGNORECASE | _re.DOTALL)
    if m:
        score = int(m.group(1))
        reasoning = m.group(2).strip()
        score = max(0, min(100, score))
        return DetectResponse(score=score, reasoning=reasoning)

    mnum = _re.search(r"\b(100|[0-9]{1,2})\b", cleaned)
    if not mnum:
        raise ValueError(f"Unexpected detector output: {raw}")
    score = int(mnum.group(1))
    reasoning = cleaned
    score = max(0, min(100, score))
    return DetectResponse(score=score, reasoning=reasoning)


def _detect_from_latex(tex_content: str) -> DetectResponse:
    # Backwards-compatible wrapper
    return _detect_from_content("LaTeX (UTF-8):\n" + tex_content)


@app.post("/detect", response_model=DetectResponse)
async def detect(req: DetectRequest):
    meta = RUNS_INDEX.get(req.run_id)
    tex_path: Optional[str] = None
    if meta and meta.get("tex") and os.path.exists(meta["tex"]):
        tex_path = meta["tex"]
    else:
        run_out = RUNS_DIR / req.run_id / "output"
        if run_out.exists():
            candidates = [p for p in run_out.glob("*.tex")]
            if candidates:
                tex_path = str(candidates[0].resolve())

    if not tex_path or not os.path.exists(tex_path):
        raise HTTPException(status_code=404, detail="Run not found or LaTeX missing for detection")

    try:
        with open(tex_path, "r", encoding="utf-8") as f:
            tex_content = f.read()
        result = _detect_from_latex(tex_content)
        result.run_id = req.run_id
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {e}")


@app.post("/detect_raw", response_model=DetectResponse)
async def detect_raw(req: DetectRawRequest):
    try:
        return _detect_from_latex(req.latex)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {e}")


@app.post("/detect_pdf", response_model=DetectResponse)
async def detect_pdf(file: UploadFile = File(...)):
    if PdfReader is None:
        raise HTTPException(status_code=500, detail="PDF support not available on server (pypdf missing)")
    try:
        content = await file.read()
        reader = PdfReader(io.BytesIO(content))
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                continue
        text = "\n".join(texts).strip()
        if len(text) < 50:
            raise HTTPException(status_code=400, detail="Could not extract sufficient text from PDF")
        return _detect_from_content(text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF detection failed: {e}")


# Health check
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"}) 