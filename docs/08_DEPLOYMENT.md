# 08_DEPLOYMENT.md

## Deployment Guide

### Deployment Overview

This document covers deployment strategies for the AI Meeting Intelligence Platform across different environments.

### Deployment Environments

| Environment | Purpose | Database | Scale |
|-------------|---------|----------|-------|
| Development | Local development | SQLite | Single machine |
| Staging | Pre-production testing | SQLite/PostgreSQL | Single machine |
| Production | Live application | PostgreSQL | Scalable |

---

## Local Development Deployment

### Prerequisites

- Python 3.12+
- pip or uv package manager
- Git

### Installation Steps

```bash
# Clone repository
git clone https://github.com/Kingnike1/transcripiton-python.git
cd transcripiton-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Initialize database
python main.py --init-db

# Run tests
pytest

# Start application
python main.py
```

### Access Application

```
Web UI: http://localhost:8000
API Docs: http://localhost:8000/docs
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create storage directory
RUN mkdir -p storage

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
      - DEBUG=false
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./storage:/app/storage
      - ./app.db:/app/app.db
    restart: unless-stopped

  # Optional: PostgreSQL for production
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=amip
      - POSTGRES_USER=amip
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Build and Run

```bash
# Build image
docker build -t amip:latest .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -v $(pwd)/storage:/app/storage \
  amip:latest

# Or use Docker Compose
docker-compose up -d
```

---

## Cloud Deployment

### Heroku Deployment

#### Procfile

```
web: gunicorn main:app
```

#### requirements.txt additions

```
gunicorn==21.2.0
```

#### Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create amip-app

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set DATABASE_URL=postgresql://...

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### AWS Deployment

#### Using Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.12 amip

# Create environment
eb create amip-env

# Deploy
eb deploy

# Open application
eb open
```

#### .ebextensions/python.config

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: main:app
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.medium
```

### Azure Deployment

#### Using App Service

```bash
# Login to Azure
az login

# Create resource group
az group create --name amip-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name amip-plan \
  --resource-group amip-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group amip-rg \
  --plan amip-plan \
  --name amip-app \
  --runtime "python|3.12"

# Deploy from GitHub
az webapp deployment source config-zip \
  --resource-group amip-rg \
  --name amip-app \
  --src app.zip
```

---

## Environment Configuration

### .env.example

```bash
# Application
DEBUG=false
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///./app.db
# For PostgreSQL: postgresql://user:password@localhost/amip

# AI Services
OPENAI_API_KEY=sk-...
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Transcription
WHISPER_MODEL=base
WHISPER_LANGUAGE=auto

# Speaker Identification
PYANNOTE_MODEL=pyannote/speaker-diarization-3.1
PYANNOTE_DEVICE=cpu

# Storage
STORAGE_PATH=./storage
MAX_UPLOAD_SIZE=500000000  # 500MB

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

---

## Database Migrations

### Initial Setup

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### Running Migrations

```bash
# In production
alembic upgrade head

# Check current version
alembic current

# Downgrade if needed
alembic downgrade -1
```

---

## Monitoring & Logging

### Application Logging

```python
# app/core/logging.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

### Health Check Endpoint

```python
# app/api/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }
```

### Performance Monitoring

```python
# Add to main.py
from time import time

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## Security Considerations

### HTTPS/SSL

```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Run with SSL
python main.py --ssl-keyfile key.pem --ssl-certfile cert.pem
```

### Environment Variables

- Never commit `.env` file
- Use `.env.example` as template
- Rotate secrets regularly
- Use secure secret management (AWS Secrets Manager, Azure Key Vault)

### Database Security

- Use strong passwords
- Enable SSL for database connections
- Restrict database access
- Regular backups
- Encryption at rest

### API Security

- Implement rate limiting
- Add CORS configuration
- Validate all inputs
- Sanitize outputs
- Use HTTPS in production

---

## Backup & Recovery

### Database Backup

```bash
# SQLite backup
cp app.db app.db.backup

# PostgreSQL backup
pg_dump -U amip amip > backup.sql

# Restore
psql -U amip amip < backup.sql
```

### File Storage Backup

```bash
# Backup storage directory
tar -czf storage_backup.tar.gz storage/

# Restore
tar -xzf storage_backup.tar.gz
```

### Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -U amip amip > $BACKUP_DIR/db_$DATE.sql

# Storage backup
tar -czf $BACKUP_DIR/storage_$DATE.tar.gz storage/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

---

## Scaling Considerations

### Horizontal Scaling

For multiple instances:

1. Use PostgreSQL instead of SQLite
2. Implement load balancing (nginx, HAProxy)
3. Use shared storage (S3, Azure Blob)
4. Implement session management
5. Use message queue for background tasks (Celery, RQ)

### Vertical Scaling

For single instance growth:

1. Increase server resources (CPU, RAM)
2. Optimize database queries
3. Implement caching (Redis)
4. Use connection pooling
5. Monitor resource usage

---

## Troubleshooting

### Common Issues

#### Application won't start

```bash
# Check logs
tail -f logs/app.log

# Verify Python version
python --version

# Check dependencies
pip list

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### Database connection error

```bash
# Check database URL
echo $DATABASE_URL

# Test connection
python -c "from app.database.session import engine; engine.connect()"

# Check database file permissions
ls -la app.db
```

#### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python main.py --port 8001
```

---

## Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Backups configured
- [ ] Monitoring enabled
- [ ] SSL/HTTPS configured
- [ ] Security audit completed
- [ ] Performance tested
- [ ] Rollback plan prepared

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
