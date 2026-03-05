#!/bin/bash

# AI Security System Deployment Script
# This script helps deploy the application to various platforms

set -e

echo "🚀 AI Security System Deployment Script"
echo "======================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to deploy locally with Docker
deploy_local() {
    echo "🏠 Deploying locally with Docker..."
    
    # Build and start containers
    docker-compose down
    docker-compose build
    docker-compose up -d
    
    echo "✅ Local deployment complete!"
    echo "🌐 Application is running at: http://localhost:5000"
    echo "📊 Check status at: http://localhost:5000/status"
}

# Function to deploy to Railway
deploy_railway() {
    echo "🚂 Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI is not installed. Please install it first:"
        echo "   npm install -g @railway/cli"
        exit 1
    fi
    
    # Ensure Railway environment is set
    echo "🔧 Setting up Railway environment..."
    
    # Create instance directory for SQLite
    mkdir -p instance
    
    # Set environment variables for Railway
    export RAILWAY_ENVIRONMENT=production
    
    # Login to Railway (if not already logged in)
    railway login
    
    # Deploy with latest changes
    echo "📦 Deploying latest code with database fixes..."
    railway up
    
    # Wait for deployment and check status
    echo "⏳ Waiting for deployment to complete..."
    sleep 10
    
    # Get the deployment URL
    DEPLOY_URL=$(railway domains --json | jq -r '.[0].domain' 2>/dev/null || echo "ai-security-risk-system-production.up.railway.app")
    
    echo "✅ Railway deployment complete!"
    echo "🌐 Application URL: https://$DEPLOY_URL"
    echo "📊 Status URL: https://$DEPLOY_URL/status"
    echo "🔍 Testing database connectivity..."
    
    # Test the deployment
    sleep 5
    if curl -s "https://$DEPLOY_URL/status" > /dev/null; then
        echo "✅ Deployment is responding correctly"
    else
        echo "⚠️  Deployment may need more time to start up"
    fi
}

# Function to deploy to Heroku
deploy_heroku() {
    echo "🟣 Deploying to Heroku..."
    
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI is not installed. Please install it first:"
        echo "   https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Login to Heroku (if not already logged in)
    heroku login
    
    # Create app if it doesn't exist
    APP_NAME="ai-security-system-$(date +%s)"
    heroku create $APP_NAME
    
    # Set environment variables
    heroku config:set FLASK_ENV=production --app $APP_NAME
    heroku config:set FLASK_HOST=0.0.0.0 --app $APP_NAME
    
    # Deploy
    heroku container:login
    heroku container:push web --app $APP_NAME
    heroku container:release web --app $APP_NAME
    
    echo "✅ Heroku deployment complete!"
    echo "🌐 Application is running at: https://$APP_NAME.herokuapp.com"
}

# Function to prepare for deployment
prepare_deployment() {
    echo "🔧 Preparing for deployment..."
    
    # Create instance directory if it doesn't exist
    mkdir -p instance
    
    # Set proper permissions
    chmod 755 instance
    
    # Check if model exists, if not train it
    if [ ! -f "model/model.pkl" ]; then
        echo "🤖 Model not found, training..."
        python model/train_model.py
    fi
    
    # Create a production .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "📝 Creating .env file from template..."
        cp .env.production .env
        echo "⚠️  Please edit .env file with your actual configuration values"
    fi
    
    echo "✅ Deployment preparation complete!"
}

# Main deployment logic
case "${1:-local}" in
    "local")
        prepare_deployment
        deploy_local
        ;;
    "railway")
        prepare_deployment
        deploy_railway
        ;;
    "heroku")
        prepare_deployment
        deploy_heroku
        ;;
    "prepare")
        prepare_deployment
        ;;
    *)
        echo "Usage: $0 [local|railway|heroku|prepare]"
        echo ""
        echo "Options:"
        echo "  local    - Deploy locally with Docker (default)"
        echo "  railway  - Deploy to Railway"
        echo "  heroku   - Deploy to Heroku"
        echo "  prepare  - Prepare files for deployment"
        exit 1
        ;;
esac
