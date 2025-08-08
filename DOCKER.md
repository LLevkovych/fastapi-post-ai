# Docker Setup Guide

## Overview

FastPostAI is fully containerized using Docker and Docker Compose, providing a complete development and production environment.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd FastPostAI
```

### 2. Environment Configuration

Copy the sample environment file:
```bash
cp env.sample .env
```

Edit `.env` with your configuration:
```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./test.db

# JWT
SECRET_KEY=your-super-secret-key-here

# AI Services
GOOGLE_AI_API_KEY=your-google-ai-api-key
OPENAI_API_KEY=your-openai-api-key

# Features
MODERATION_ENABLED=true
DEFAULT_AUTO_REPLY_DELAY=60
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Access the Application

- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Redis**: localhost:6379

## Services

### API Service
- **Image**: Built from local Dockerfile
- **Port**: 8001 (host) → 8000 (container)
- **Health Check**: `/health` endpoint
- **Dependencies**: Redis

### Redis Service
- **Image**: redis:7-alpine
- **Port**: 6379
- **Volume**: redis_data
- **Purpose**: Message broker for Celery

### Celery Worker
- **Image**: Built from local Dockerfile
- **Purpose**: Background task processing
- **Dependencies**: Redis, API

### Celery Beat
- **Image**: Built from local Dockerfile
- **Purpose**: Task scheduling
- **Dependencies**: Redis, API

## Dockerfile Details

```dockerfile
FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Security: non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Startup script
RUN echo '#!/bin/bash\npython init_db.py\nexec uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh \
    && chmod +x /app/start.sh

EXPOSE 8000
CMD ["/app/start.sh"]
```

## Docker Compose Configuration

### Volumes
- `redis_data`: Persistent Redis data
- `./data:/app/data`: Application data directory

### Networks
- Default bridge network for inter-service communication

### Environment Variables
All services share the same environment configuration for consistency.

## Development Workflow

### 1. Building Images
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build api
```

### 2. Running Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d api

# View logs
docker-compose logs -f api
```

### 3. Development with Hot Reload
For development, you can mount the source code:
```yaml
volumes:
  - .:/app
```

### 4. Database Migrations
```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"
```

### 5. Testing
```bash
# Run tests
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=app
```

## Production Deployment

### 1. Environment Variables
Set production environment variables:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SECRET_KEY=production-secret-key
GOOGLE_AI_API_KEY=production-api-key
```

### 2. Security
- Use secrets management for sensitive data
- Enable HTTPS with reverse proxy
- Configure proper firewall rules

### 3. Scaling
```bash
# Scale API service
docker-compose up -d --scale api=3

# Scale Celery workers
docker-compose up -d --scale celery-worker=2
```

### 4. Monitoring
- Add health checks for all services
- Configure logging aggregation
- Set up monitoring and alerting

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using port 8001
netstat -tulpn | grep 8001

# Use different port
docker-compose up -d -p 8002:8000
```

#### 2. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run as root (not recommended for production)
docker-compose up -d --user root
```

#### 3. Memory Issues
```bash
# Check resource usage
docker stats

# Increase memory limits in docker-compose.yml
```

#### 4. Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d

# Check database logs
docker-compose logs api | grep -i database
```

### Logs and Debugging

#### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs api

# Follow logs
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api
```

#### Debug Container
```bash
# Enter container
docker-compose exec api bash

# Check processes
docker-compose exec api ps aux

# Check environment
docker-compose exec api env
```

## Performance Optimization

### 1. Multi-stage Builds
Use multi-stage builds to reduce image size:
```dockerfile
FROM python:3.11-slim as builder
# Build dependencies

FROM python:3.11-slim
# Copy only necessary files
```

### 2. Caching
- Use `.dockerignore` to exclude unnecessary files
- Layer dependencies properly for better caching
- Use build cache in CI/CD

### 3. Resource Limits
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

## Backup and Recovery

### Database Backup
```bash
# SQLite backup
docker-compose exec api sqlite3 test.db ".backup backup.db"

# PostgreSQL backup
docker-compose exec postgres pg_dump -U user db > backup.sql
```

### Volume Backup
```bash
# Backup Redis data
docker run --rm -v fastpostai_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
```

## Security Best Practices

1. **Use non-root users** (already implemented)
2. **Scan images for vulnerabilities**
3. **Keep base images updated**
4. **Use secrets management**
5. **Enable security scanning in CI/CD**
6. **Regular security updates**

## Monitoring and Logging

### Health Checks
All services include health checks:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Logging
- Structured logging with JSON format
- Log rotation and retention policies
- Centralized logging with ELK stack or similar 