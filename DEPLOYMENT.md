# Deployment Guide

## 📚 Overview

This guide covers multiple deployment options for the AI Security Risk Detection API.

---

## 🚀 Local Development

### Quick Start

```bash
# 1. Navigate to project
cd d:\MCA\Projects\ai-security-system

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Run the API
python api/app.py
```

**Access API at:** `http://127.0.0.1:5000`

---

## 🐳 Docker Deployment

### Prerequisites
- Docker installed and running
- Docker Compose (optional but recommended)

### Option 1: Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop the container
docker-compose down
```

**Access API at:** `http://localhost:5000`

### Option 2: Docker Manual Build

```bash
# Build image
docker build -t ai-security-api:1.0.0 .

# Run container
docker run -d \
  --name ai-security-api \
  -p 5000:5000 \
  -v $(pwd)/model:/app/model \
  ai-security-api:1.0.0

# View logs
docker logs -f ai-security-api

# Stop container
docker stop ai-security-api
docker rm ai-security-api
```

### Docker Configuration

**Dockerfile features:**
- Python 3.11 slim base image
- System dependencies installed
- Gunicorn for production
- Health checks enabled
- Port 5000 exposed

**docker-compose.yml features:**
- Auto-restart on failure
- Volume mapping for hot updates
- Health check configuration
- Network isolation
- Environment variable management

---

## 🌐 Production Deployment

### Option 1: AWS EC2

```bash
# 1. SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 2. Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose -y

# 3. Clone repository
git clone https://github.com/yourusername/ai-security-risk-system.git
cd ai-security-risk-system

# 4. Create .env file
cp .env.example .env
# Edit .env with production settings

# 5. Start with Docker Compose
sudo docker-compose up -d
```

### Option 2: Heroku

```bash
# 1. Install Heroku CLI
# Download from https://devcenter.heroku.com/articles/heroku-cli

# 2. Login to Heroku
heroku login

# 3. Create Heroku app
heroku create your-app-name

# 4. Set environment variables
heroku config:set FLASK_ENV=production

# 5. Deploy
git push heroku main
```

### Option 3: Google Cloud Platform

```bash
# 1. Install Google Cloud SDK
# Follow: https://cloud.google.com/sdk/docs/install

# 2. Authentication
gcloud auth login

# 3. Build and deploy
gcloud run deploy ai-security-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 4: Azure Container Instances

```bash
# 1. Install Azure CLI
# Follow: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# 2. Login
az login

# 3. Create resource group
az group create --name ai-security-rg --location eastus

# 4. Deploy container
az container create \
  --resource-group ai-security-rg \
  --name ai-security-api \
  --image yourusername/ai-security-api:1.0.0 \
  --ports 5000 \
  --environment-variables FLASK_ENV=production
```

---

## 🔐 Production Configuration

### Environment Variables

Create `.env` file:

```bash
# Flask Settings
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Model Settings
MODEL_PATH=/app/model/model.pkl

# API Settings
API_VERSION=1.0.0
API_NAME="AI Security Risk Detection API"

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/api.log
```

### Security Best Practices

✅ **Use HTTPS/TLS**
```bash
# Use Let's Encrypt with Certbot
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d your-domain.com
```

✅ **Enable CORS** (if needed)
```python
from flask_cors import CORS
CORS(app, resources={r"/predict": {"origins": ["https://your-domain.com"]}})
```

✅ **API Authentication** (Future enhancement)
```python
from functools import wraps
from flask import request

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
```

✅ **Rate Limiting** (Future enhancement)
```bash
pip install Flask-Limiter
```

---

## 📊 Monitoring & Logging

### Health Check Monitoring

```bash
# Continuous monitoring
watch -n 5 'curl -s http://localhost:5000/health | jq .'

# Prometheus metrics (add to app.py)
pip install prometheus-flask-exporter
```

### Application Logs

```bash
# View logs with Docker Compose
docker-compose logs -f api

# View logs with Docker
docker logs -f ai-security-api

# View logs with Gunicorn
tail -f /var/log/api.log
```

### Error Tracking (Optional)

```python
# Add Sentry for error tracking
pip install sentry-sdk
import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The `.github/workflows/tests.yml` file automates:
- ✅ Code linting
- ✅ API endpoint testing
- ✅ Input validation testing
- ✅ Automatic deployment triggers

### Manual Deployment Steps

```bash
# 1. Make changes
git add .
git commit -m "Your changes"

# 2. Push to repository
git push origin main

# 3. GitHub Actions automatically:
#    - Runs tests
#    - Validates code
#    - Deploys to production (if configured)
```

---

## 📈 Scaling

### Horizontal Scaling (Multiple Instances)

```yaml
# docker-compose.yml with scaling
version: '3.8'
services:
  api:
    build: .
    ports:
      - "5000-5003:5000"
    environment:
      FLASK_ENV: production
    restart: unless-stopped
    deploy:
      replicas: 4
```

### Load Balancing

```bash
# Using Nginx as reverse proxy
upstream api_backend {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
    server localhost:5003;
}

server {
    listen 80;
    location / {
        proxy_pass http://api_backend;
    }
}
```

---

## 🧪 Testing Before Production

### Load Testing

```bash
# Install Apache Bench
# Windows: Download from Apache website
# Linux: sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:5000/health

# Using wrk (more advanced)
wrk -t4 -c100 -d30s http://localhost:5000/health
```

### Integration Testing

```python
# tests/test_integration.py
import requests

def test_prediction_api():
    response = requests.post(
        'http://localhost:5000/predict',
        json={
            "failed_login_attempts": 3,
            "login_time_deviation": 0.5,
            "ip_change": 1,
            "device_change": 0,
            "transaction_amount_deviation": 0.8
        }
    )
    assert response.status_code == 200
    assert 'risk_label' in response.json()
```

---

## ❌ Troubleshooting

### Docker Issues

```bash
# Container won't start
docker-compose logs api

# Port already in use
netstat -ano | findstr :5000
taskkill /PID [PID] /F

# Clear Docker cache
docker system prune -a
```

### Model Loading Issues

```bash
# Verify model exists
ls -la model/model.pkl

# Check permissions
chmod 644 model/model.pkl

# Verify model integrity
python -c "import joblib; model = joblib.load('model/model.pkl')"
```

### Memory Issues

```bash
# Monitor memory usage
docker stats ai-security-api

# Limit memory in docker-compose.yml
services:
  api:
    mem_limit: 512m
    memswap_limit: 1g
```

---

## 📋 Deployment Checklist

- [ ] Code passes all tests
- [ ] Requirements.txt is updated
- [ ] .env file created with production settings
- [ ] Model file (model.pkl) is available
- [ ] Docker image builds successfully
- [ ] Health endpoint responds with 200
- [ ] Prediction endpoint tested with sample data
- [ ] Error handling tested
- [ ] Logs are properly configured
- [ ] HTTPS/TLS is configured
- [ ] Backups are configured
- [ ] Monitoring is enabled
- [ ] Documentation is updated
- [ ] Team members are notified

---

## 📞 Support

For deployment issues:
1. Check error logs
2. Verify all environment variables
3. Test connectivity to model file
4. Review Docker health checks
5. Check port availability
6. Verify firewall rules

---

**Last Updated:** February 15, 2026  
**Version:** 1.0.0
