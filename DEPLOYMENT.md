# AI Security Risk Prediction System - Deployment Guide

## 🚀 Quick Start

### Option 1: Local Development with SQLite (Recommended for testing)

```bash
# Clone and setup
git clone <your-repo-url>
cd ai-security-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the application
python api/app.py
```

The application will automatically use SQLite as a fallback if MongoDB is not configured.

### Option 2: Local Development with Docker

```bash
# Deploy locally with Docker
chmod +x deploy.sh
./deploy.sh local
```

### Option 3: Deploy to Railway

```bash
# Deploy to Railway
chmod +x deploy.sh
./deploy.sh railway
```

### Option 4: Deploy to Heroku

```bash
# Deploy to Heroku
chmod +x deploy.sh
./deploy.sh heroku
```

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Git

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.production`:

```bash
cp .env.production .env
```

Edit `.env` with your configuration:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# MongoDB (Optional - will fallback to SQLite)
MONGODB_URI=mongodb+srv://your_username:your_password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=ai_security

# Security
SECRET_KEY=your-secret-key-here
```

### Database Options

1. **MongoDB Atlas (Recommended for production)**
   - Create a free MongoDB Atlas account
   - Get your connection string
   - Update `MONGODB_URI` in `.env`

2. **SQLite (Automatic fallback)**
   - No configuration needed
   - Automatically used when MongoDB is unavailable
   - Database file: `instance/ai_security.db`

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t ai-security-api .

# Run the container
docker run -p 5000:5000 -e FLASK_ENV=production ai-security-api
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### Railway

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Deploy: `./deploy.sh railway`
4. Or use the Railway web interface to connect your GitHub repo

### Heroku

1. Install Heroku CLI
2. Login: `heroku login`
3. Deploy: `./deploy.sh heroku`

### Other Platforms

The application is containerized and can be deployed to any platform that supports Docker:
- AWS ECS/EKS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

## 🔍 Health Checks

### Application Endpoints

- **Health Check**: `GET /health`
- **System Status**: `GET /status` (shows database backend info)
- **API Documentation**: `GET /` or `GET /docs`

### Database Status

Check which database backend is being used:

```bash
curl http://localhost:5000/status
```

Response example:
```json
{
  "status": "healthy",
  "database": {
    "backend": "sqlite",
    "available": true,
    "mongodb_available": false,
    "sqlite_available": true
  },
  "api_version": "1.0.0"
}
```

## 🛠️ Troubleshooting

### MongoDB Authentication Issues

If you see "bad auth : authentication failed":

1. Verify your MongoDB Atlas credentials
2. Check if your IP is whitelisted in MongoDB Atlas
3. Ensure the password is URL-encoded (replace `@` with `%40`)
4. The application will automatically fallback to SQLite

### Port Issues

- Ensure port 5000 is available
- For production, use the `PORT` environment variable
- Docker containers expose port 5000 by default

### Model Loading Issues

If the model fails to load:

```bash
# Train the model
python model/train_model.py

# Verify model file exists
ls -la model/model.pkl
```

## 📊 Monitoring

### Logs

- Application logs: `api.log`
- Docker logs: `docker-compose logs api`

### Metrics

The application tracks:
- Total API requests per user
- Database connection status
- Error rates

## 🔒 Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **API Keys**: Each user gets a unique API key after signup
3. **Password Security**: Passwords are hashed using bcrypt
4. **Database**: Use MongoDB Atlas or secure your SQLite database
5. **HTTPS**: Use HTTPS in production (most cloud platforms provide this)

## 🚀 Production Best Practices

1. **Use MongoDB Atlas** for production databases
2. **Enable HTTPS** through your hosting provider
3. **Monitor logs** for errors and performance issues
4. **Set up alerts** for database connection failures
5. **Regular backups** of your database
6. **Update dependencies** regularly

## 📞 Support

If you encounter issues:

1. Check the logs: `tail -f api.log`
2. Verify database status: `curl http://localhost:5000/status`
3. Test with SQLite fallback (disable MongoDB temporarily)
4. Check the GitHub Issues page for common problems

## 🔄 CI/CD

The application includes GitHub Actions for automated testing:

```yaml
# .github/workflows/tests.yml
# Runs tests on every push and pull request
```

## 📝 API Usage

### Authentication

Include your API key in the header:
```
x-api-key: your-api-key-here
```

### Endpoints

- **Predict Risk**: `POST /predict`
- **User Dashboard**: `GET /dashboard-data`
- **Signup**: `POST /signup`
- **Login**: `POST /login`

See the API documentation at `/docs` for detailed usage instructions.
