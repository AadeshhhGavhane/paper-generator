# Research Paper Generator & AI Detection System

A modular web application that generates academic research papers using AI models (Gemini/Groq) and provides AI-generated content detection capabilities.

## 🚀 Features

- **AI Paper Generation**: Generate complete LaTeX research papers using Google Gemini or Groq LLaMA models
- **Multiple AI Providers**: Support for both Gemini 2.5 Flash and Groq LLaMA-4 Maverick models  
- **PDF Compilation**: Automatic LaTeX to PDF conversion with system or Docker fallback
- **AI Content Detection**: Detect AI-generated content from LaTeX, raw text, or PDF files
- **Modular Architecture**: Clean separation of frontend/backend with organized service layers
- **RESTful API**: Well-documented FastAPI backend with automatic OpenAPI documentation

## 📁 Project Structure

```
research-paper-generator-and-detector/
├── backend/                     # FastAPI Backend
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Backend dependencies
│   ├── .env                    # Environment variables
│   ├── routes/
│   │   └── api.py             # API endpoints
│   ├── services/
│   │   ├── gemini_chat.py     # Google Gemini service
│   │   └── groq_chat.py       # Groq AI service
│   ├── models/                # Pydantic models
│   └── utils/
│       └── latex_utils.py     # LaTeX processing utilities
├── frontend/                        # Web Interface
│   ├── index.html                   # Main paper generation interface
│   ├── upload.html                  # AI detection and file upload interface
│   ├── css/                         # Stylesheets
│   │   ├── styles.css               # Main page styling
│   │   └── upload.css               # Upload page styling
│   └── js/                          # JavaScript Logic
│       ├── main.js                  # Paper generation and detection logic
│       └── upload.js                # File upload and content detection logic
├── paper/
│   └── research-pap.tex       # LaTeX template
├── runs/                      # Generated papers storage
├── .gitignore
├── README.md
├── CONTRIBUTING.md
└── uv.lock                    # Dependency lock file
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.12+
- Git
- LaTeX distribution (TexLive) or Docker for PDF compilation

### 1. Clone Repository
```bash
git clone <your-repository-url>
cd research-paper-generator-and-detector
```

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Get API Keys
- **Google Gemini**: Get API key from [Google AI Studio](https://aistudio.google.com/)
- **Groq**: Get API key from [Groq Console](https://console.groq.com/)

## 🚀 Running the Application

### Start Backend Server
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## 🐳 Docker Support

The project includes full Docker containerization with separate containers for frontend and backend services.

### Prerequisites
- Docker and Docker Compose installed
- Environment file configured (see [Environment Setup](#environment-setup))

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/Kartika2005/paper-generator.git
cd paper-generator

# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Access backend logs
docker-compose logs backend

# Access frontend logs
docker-compose logs frontend
```

### Development with Docker

For development with live reload:

```bash
# Start with development overrides
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

### Service Access
- **Frontend**: http://localhost (port 80) or http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Docker Architecture
- **Frontend Container**: Nginx serving static files + reverse proxy
- **Backend Container**: FastAPI application with LaTeX support
- **Volumes**: Persistent storage for generated papers and cache
- **Network**: Internal Docker network for service communication

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Quick Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the project structure
4. Test your changes thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


**Made with ❤️ for academic research and AI detection**