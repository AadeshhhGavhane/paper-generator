# Docker Setup Guide

This document provides detailed instructions for running the Paper Generator application using Docker.

## Prerequisites

1. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop/
   - Ensure Docker daemon is running before executing commands

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # - GOOGLE_API_KEY (for Gemini AI)
   # - GROQ_API_KEY (for Groq AI)
   ```

## Quick Start

```bash
# Start all services in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Services

### Backend Service
- **Container**: `paper-generator-backend`
- **Port**: 8000
- **Technology**: FastAPI with Python 3.12
- **Features**: 
  - AI paper generation (Gemini & Groq)
  - LaTeX compilation with system or Docker fallback
  - Health checks and auto-restart

### Frontend Service  
- **Container**: `paper-generator-frontend`
- **Ports**: 80 (main), 3000 (alternative)
- **Technology**: Nginx serving static files
- **Features**:
  - Reverse proxy to backend API
  - Static file serving with caching
  - Health checks and auto-restart

## Development Mode

For development with live reload:

```bash
# Start with development overrides
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

# This enables:
# - Live reload for backend code changes
# - Live reload for frontend file changes
# - Direct backend access on port 8000
```

## Docker Commands Reference

### Building and Running
```bash
# Build images without cache
docker-compose build --no-cache

# Start services (detached)
docker-compose up -d

# Start specific service
docker-compose up backend
docker-compose up frontend

# Force recreate containers
docker-compose up --force-recreate
```

### Monitoring and Debugging
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f

# Check service status
docker-compose ps

# View resource usage
docker stats
```

### Maintenance
```bash
# Stop services
docker-compose stop

# Remove containers (preserves volumes)
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove unused images
docker image prune

# Complete cleanup
docker system prune -a
```

### Accessing Containers
```bash
# Execute commands in running backend container
docker-compose exec backend bash
docker-compose exec backend python --version

# Execute commands in running frontend container
docker-compose exec frontend sh
docker-compose exec frontend nginx -t
```

## Volume Management

### Persistent Data
- `./runs` - Generated papers and outputs (mounted to both containers)
- `./paper` - LaTeX templates (mounted to backend)
- `backend_cache` - Python package cache (Docker volume)

### Development Mounts
When using development mode, source code is mounted for live reload:
- `./backend` → `/app` (backend container)
- `./frontend` → `/usr/share/nginx/html` (frontend container)

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost | Main application |
| Frontend (Alt) | http://localhost:3000 | Alternative port |
| Backend API | http://localhost:8000 | Direct API access |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Health Check | http://localhost/health | Service health |

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :80
   lsof -i :8000
   
   # Stop conflicting services or change ports in docker-compose.yml
   ```

2. **Docker Daemon Not Running**
   ```bash
   # Start Docker Desktop application
   # Or start Docker daemon on Linux:
   sudo systemctl start docker
   ```

3. **Build Failures**
   ```bash
   # Clean build without cache
   docker-compose build --no-cache
   
   # Remove old images
   docker image prune -f
   ```

4. **Permission Issues**
   ```bash
   # Fix file permissions
   chmod -R 755 frontend/
   chmod -R 755 backend/
   ```

5. **Environment Variables Not Loading**
   ```bash
   # Ensure .env file exists and has correct format
   cat .env
   
   # Rebuild containers after .env changes
   docker-compose up --build
   ```

### Health Checks

Both services include health checks:
- **Backend**: `curl -f http://localhost:8000/health`
- **Frontend**: `wget --spider http://localhost/health`

Check health status:
```bash
docker-compose ps
# Look for "healthy" status
```

### Logs Analysis

```bash
# Backend startup issues
docker-compose logs backend | grep -i error

# Frontend/Nginx issues  
docker-compose logs frontend | grep -i error

# API connection issues
docker-compose logs backend | grep -i "failed to import"
```

## Production Deployment

For production deployment:

1. **Security**: Remove development ports and mounts
2. **Environment**: Set `ENVIRONMENT=production` in .env
3. **Secrets**: Use Docker secrets or external secret management
4. **Monitoring**: Add monitoring and alerting
5. **Backup**: Implement backup strategy for volumes
6. **Load Balancing**: Consider adding load balancer for scaling

Example production docker-compose:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - ENVIRONMENT=production
    # Remove development ports and mounts
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    # Remove development ports and mounts
```

## Architecture Overview

```
[Frontend Container]     [Backend Container]
    Nginx                    FastAPI
    Port 80/3000            Port 8000
         |                      |
         |-- API Proxy ---------|
         |                      |
    Static Files          AI Processing
    HTML/CSS/JS           LaTeX Compilation
         |                      |
    [Shared Volumes: ./runs, ./paper]
```

The containerized architecture provides:
- **Isolation**: Services run in separate containers
- **Scalability**: Easy to scale individual services  
- **Persistence**: Data persisted through volumes
- **Development**: Live reload capabilities
- **Production**: Health checks and restart policies