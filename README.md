# 🎓 Research Paper Generator & AI Detection System

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive system that generates academic research papers using AI models (Gemini and Groq/Llama) and provides AI content detection capabilities. The system outputs professionally formatted LaTeX documents that can be compiled to PDF.

## ✨ Features

### 🤖 AI-Powered Research Paper Generation
- **Multiple AI Providers**: Support for Google Gemini and Groq (Llama models)
- **LaTeX Output**: Generate properly formatted academic papers in LaTeX
- **PDF Compilation**: Automatic compilation to PDF using system LaTeX or Docker
- **Template-Based**: Uses professional academic paper templates

### 🔍 AI Content Detection
- **Research Paper Analysis**: Detect AI-generated content in research papers
- **Multiple Input Formats**: Support for LaTeX, PDF, and raw text
- **Confidence Scoring**: Provides detection confidence scores (0-100)
- **Detailed Reasoning**: Explains the detection rationale

### 🖥️ Multiple Interfaces
- **Web API**: RESTful API with FastAPI for programmatic access
- **Interactive GUI**: Streamlit-based web interface for easy use
- **Command Line**: Direct CLI usage for batch processing

### 📊 Advanced Features
- **Run Management**: Track and manage generation runs
- **File Downloads**: Download LaTeX source and compiled PDFs
- **Error Handling**: Robust error handling with detailed feedback
- **Template Cleaning**: Automatic removal of problematic LaTeX elements

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- LaTeX distribution (TexLive recommended) OR Docker
- API keys for your chosen AI provider

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bharat3214/research-paper-generator-and-detector.git
   cd research-paper-generator-and-detector
   ```

2. **Install dependencies**
   ```bash
   pip install uv  # If you don't have uv installed
   uv sync
   ```

3. **Set up environment variables**
   
   ### Environment Variables
   ```bash
   # Required for Gemini
   GOOGLE_API_KEY=your_gemini_api_key

   # Required for Groq
   GROQ_API_KEY=your_groq_api_key

   ```

4. **Install LaTeX (Optional - Docker fallback available)**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install texlive-full
   
   # macOS
   brew install --cask mactex
   
   # Windows: Download from https://www.tug.org/texlive/
   ```

## 📖 Usage

### Web Interface (Recommended)
```bash
streamlit run streamlit_app.py
```
Open http://localhost:8501 in your browser

### API Server
```bash
# Using uv
uv run serve

# Or directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```
API documentation available at http://localhost:8000/docs

### Command Line

**Generate with Gemini:**
```bash
python main.py
# Enter your research topic when prompted
```

**Generate with Groq:**
```bash
python groq_chat.py
# Enter your research topic when prompted
```

## 📁 Project Structure

```
research-paper-generator-and-detector/
├── 📄 README.md                 # This file
├── 📄 CONTRIBUTING.md           # Contribution guidelines
├── ⚙️ pyproject.toml            # Project dependencies and configuration
├── 🔐 .env                      # Environment variables (create from .env.example)
├── 🚫 .gitignore               # Git ignore rules
│
├── 🐍 main.py                  # Gemini-based paper generation (CLI)
├── 🐍 groq_chat.py            # Groq/Llama-based paper generation (CLI)
├── 🌐 streamlit_app.py        # Streamlit web interface
├── 🔗 api.py                   # FastAPI REST API
│
├── 📂 paper/                   # LaTeX templates
│   └── research-pap.tex       # Main research paper template
│
├── 📂 static/                  # Static web files
│   ├── index.html             # API interface
│   └── upload.html            # Upload interface
│
├── 📂 output/                  # Generated LaTeX files
├── 📂 export/                  # Compiled PDF files
└── 📂 runs/                    # Run management directory
```


### LaTeX Requirements
The system requires specific LaTeX packages:
- `natbib` - Citation management
- `geometry` - Page layout
- `fancyhdr` - Headers and footers
- `amsmath, amsfonts, amssymb` - Mathematical symbols
- `graphicx` - Graphics support
- `booktabs` - Professional tables


## 🛠️ Development

### Setting Up Development Environment
```bash
# Clone repository
git clone https://github.com/bharat3214/research-paper-generator-and-detector.git
cd research-paper-generator-and-detector

### Running in Development Mode
```bash
# API with auto-reload
uvicorn api:app --reload --port 8000

# Streamlit with auto-reload
streamlit run streamlit_app.py --server.runOnSave true
```

## 🤝 Contributing

We welcome contributors!

### Quick Contribution Steps
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

**Built with ❤️ for the academic and research community**

*Generate professional research papers with AI, detect AI-generated content, and contribute to academic excellence.*
