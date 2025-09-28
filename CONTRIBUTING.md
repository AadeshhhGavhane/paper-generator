# 🤝 Contributing to Research Paper Generator & AI Detection System

Thank you for your interest in contributing to this project! We welcome contributions from developers, researchers, and academic enthusiasts. This document provides guidelines for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## 🤗 Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- **Be respectful** and inclusive of all contributors
- **Be patient** with newcomers and those learning
- **Be constructive** in your feedback and criticism
- **Focus on the work**, not personal attributes
- **Respect different viewpoints** and experiences

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.12+** installed
- **Git** for version control
- **LaTeX distribution** (TexLive recommended) OR Docker
- **Basic knowledge** of Python, FastAPI, and Streamlit
- **Understanding** of LaTeX for document generation features

### 🔑 API Keys Setup

You'll need API keys for testing:

1. **Google Gemini API**: [Get API Key](https://aistudio.google.com/app/apikey)
2. **Groq API**: [Get API Key](https://console.groq.com/keys)

## 💻 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/research-paper-generator-and-detector.git
cd research-paper-generator-and-detector

# Add upstream remote
git remote add upstream https://github.com/bharat3214/research-paper-generator-and-detector.git
```

### 2. Environment Setup

```bash
# Install uv (if not already installed)
pip install uv

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
uv sync --dev
```

### 3. Environment Variables

```bash
# Create .env file
cp .env.example .env

# Edit .env with your API keys
echo "GOOGLE_API_KEY=your_gemini_key_here" >> .env
echo "GROQ_API_KEY=your_groq_key_here" >> .env
```

### 4. Install LaTeX (Optional)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install texlive-full

# macOS (using Homebrew)
brew install --cask mactex

# Verify installation
pdflatex --version
```

### 5. Verify Installation

```bash
# Test the API server
uvicorn api:app --reload --port 8000

# Test Streamlit interface
streamlit run streamlit_app.py

# Test CLI generation
python main.py
```

## 🛠️ How to Contribute

### Areas for Contribution

1. **🐛 Bug Fixes**: Fix existing issues
2. **✨ New Features**: Add functionality
3. **📚 Documentation**: Improve docs and examples
4. **🧪 Testing**: Add or improve tests
5. **⚡ Performance**: Optimize code performance
6. **🎨 UI/UX**: Enhance user interfaces
7. **🔧 DevOps**: Improve CI/CD and deployment

### Types of Contributions Welcome

- **Code improvements** and bug fixes
- **New AI model integrations** (e.g., Claude, OpenAI)
- **Additional LaTeX templates** for different paper types
- **Enhanced detection algorithms** for AI-generated content
- **UI/UX improvements** for web interfaces
- **Documentation** and tutorial enhancements
- **Test coverage** improvements
- **Performance optimizations**

## 🔄 Development Workflow

### 1. Choose or Create an Issue

- Browse [existing issues](https://github.com/bharat3214/research-paper-generator-and-detector/issues)
- For new features, create an issue first to discuss
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create a new branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes

Follow the coding standards below and make your changes:

```bash
# Make your changes
# Run tests frequently
python -m pytest

# Run code formatting
black .
isort .
flake8 .
```

### 4. Test Your Changes

```bash
# Run the full test suite
python -m pytest tests/

# Test specific functionality
python -m pytest tests/test_generation.py

# Test API endpoints
python -m pytest tests/test_api.py

# Manual testing
python main.py  # Test CLI
streamlit run streamlit_app.py  # Test web interface
```

### 5. Commit and Push

```bash
# Add files
git add .

# Commit with descriptive message
git commit -m "feat: add new AI model integration for research paper generation"

# Push to your fork
git push origin feature/your-feature-name
```

## 📏 Coding Standards

### Python Code Style

We follow **PEP 8** with some modifications:

```python
# Use Black for formatting
black --line-length 100 .

# Use isort for imports
isort .

# Use flake8 for linting
flake8 --max-line-length=100 --extend-ignore=E203,W503
```

### Code Organization

```python
# File structure for new modules
"""
Module description.

This module handles [functionality description].
"""

import os  # Standard library imports
import sys
from datetime import datetime

import requests  # Third-party imports
from fastapi import FastAPI

from .utils import helper_function  # Local imports


class YourClass:
    """Class documentation."""
    
    def __init__(self, param: str):
        """Initialize with clear parameter documentation."""
        self.param = param
    
    def your_method(self, input_data: dict) -> dict:
        """
        Method with clear documentation.
        
        Args:
            input_data: Description of input parameter
            
        Returns:
            Description of return value
            
        Raises:
            ValueError: When input is invalid
        """
        if not input_data:
            raise ValueError("Input data cannot be empty")
        
        # Implementation
        return {"result": "processed"}
```

### Documentation Standards

- **Docstrings** for all modules, classes, and functions
- **Type hints** for function parameters and returns
- **Inline comments** for complex logic
- **README updates** for new features

### LaTeX Template Guidelines

```latex
% Template Structure
\documentclass[11pt]{article}

% Required packages with comments
\usepackage[utf8]{inputenc}  % UTF-8 encoding
\usepackage{natbib}          % Bibliography management
\usepackage{geometry}        % Page layout

% Clear section structure
\title{[TITLE_PLACEHOLDER]}
\author{[AUTHOR_PLACEHOLDER]}
\date{[DATE_PLACEHOLDER]}

\begin{document}
% Well-commented sections
% Use placeholder format: [PLACEHOLDER_NAME]
\end{document}
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_generation.py       # Generation testing
├── test_detection.py        # Detection testing
├── test_api.py             # API endpoint testing
├── test_latex.py           # LaTeX processing tests
└── integration/            # Integration tests
    ├── __init__.py
    └── test_end_to_end.py
```

### Writing Tests

```python
import pytest
from unittest.mock import patch, MagicMock

def test_paper_generation_success():
    """Test successful paper generation."""
    # Given
    topic = "Machine Learning in Healthcare"
    
    # When
    with patch('main.gemini_generator.client') as mock_client:
        mock_client.models.generate_content.return_value.text = "\\documentclass{article}...\\end{document}"
        result = generate_paper(topic)
    
    # Then
    assert result.startswith("\\documentclass")
    assert topic.lower() in result.lower()

def test_invalid_topic_handling():
    """Test handling of invalid topics."""
    with pytest.raises(ValueError, match="Topic cannot be empty"):
        generate_paper("")
```

### Test Coverage

Aim for **80%+ test coverage**:

```bash
# Run tests with coverage
python -m pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 📖 Documentation

### Documentation Types

1. **Code Documentation**: Docstrings and comments
2. **User Documentation**: README and usage examples
3. **API Documentation**: FastAPI auto-generated docs
4. **Developer Documentation**: This file and technical guides

### Documentation Updates

When adding features:

1. **Update README.md** with new functionality
2. **Add docstrings** to new functions/classes
3. **Create examples** demonstrating usage
4. **Update API documentation** if adding endpoints

## 🐛 Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.12.0]
- Package version: [e.g. 0.1.0]

**Additional context**
Any other context about the problem.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions you've considered.

**Additional context**
Any other context or screenshots about the feature request.
```

## 🔀 Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
2. **Update documentation** as needed
3. **Follow coding standards**
4. **Rebase on latest main** branch
5. **Write descriptive commit messages**

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added to hard-to-understand areas
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. **Automated checks** must pass
2. **At least one approval** from maintainers
3. **All conversations resolved**
4. **Up-to-date** with main branch

## 🚀 Release Process

### Version Management

We use **Semantic Versioning** (SemVer):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md**
3. **Create release PR**
4. **Tag release** after merging
5. **Publish to PyPI** (maintainers only)

## 🎯 Specific Contribution Areas

### 🤖 Adding New AI Models

```python
# Create new module: your_model_chat.py
from your_ai_provider import YourClient

def generate_paper(topic: str) -> str:
    """Generate paper using your AI model."""
    # Implementation
    pass

# Update api.py to include your model
def _generate_with_your_model(topic: str, workdir: Path) -> tuple:
    # Implementation
    pass
```

### 📝 Adding LaTeX Templates

1. Create template in `paper/` directory
2. Follow existing template structure
3. Use `[PLACEHOLDER]` format for variables
4. Test compilation with sample content
5. Update documentation

### 🧪 Improving Detection

```python
def enhanced_detection_algorithm(content: str) -> DetectionResult:
    """
    Improved AI detection algorithm.
    
    Consider factors like:
    - Writing style patterns
    - Vocabulary diversity
    - Sentence structure variation
    - Domain-specific knowledge
    """
    # Your implementation
    pass
```

## 📞 Getting Help

- **Documentation**: Check README and this guide first
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: [Join our Discord community](https://discord.gg/your-server)
- **Email**: Contact maintainers at your-email@domain.com

## 🏆 Recognition

Contributors are recognized in:

- **README.md** contributors section
- **Release notes** for significant contributions
- **Special mentions** in project announcements

## 📊 Project Statistics

- **Languages**: Python (90%), HTML/CSS (5%), LaTeX (5%)
- **Test Coverage**: Target 80%+
- **Code Quality**: Maintained with automated tools
- **Documentation**: Comprehensive and up-to-date

---

## 💡 Tips for New Contributors

1. **Start small**: Begin with documentation or bug fixes
2. **Ask questions**: Don't hesitate to ask for clarification
3. **Follow examples**: Look at existing code for patterns
4. **Test thoroughly**: Always test your changes
5. **Be patient**: Code review takes time

## 🌟 Advanced Contributions

### Performance Optimization

- **Async/await** patterns for I/O operations
- **Caching** for template processing
- **Background tasks** for PDF compilation
- **Database** optimization for run management

### Security Enhancements

- **Input validation** improvements
- **API rate limiting**
- **Secure file handling**
- **Environment variable** security

### Infrastructure

- **Docker** containerization improvements
- **CI/CD** pipeline enhancements
- **Monitoring** and logging
- **Deployment** automation

---

**Thank you for contributing to the Research Paper Generator & AI Detection System! 🎉**

Your contributions help advance academic research and AI technology. Every contribution, no matter how small, makes a difference!