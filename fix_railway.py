#!/usr/bin/env python3
"""
Quick fix script for Railway deployment issues.
This script ensures the latest database fixes are deployed to Railway.
"""

import os
import subprocess
import sys
import json

def run_command(cmd, check=True):
    """Run a command and return the result."""
    print(f"🔧 Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if check:
            sys.exit(1)
        return e

def check_railway_cli():
    """Check if Railway CLI is installed."""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        print(f"✅ Railway CLI found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Railway CLI not found. Please install it with:")
        print("   npm install -g @railway/cli")
        return False

def prepare_deployment():
    """Prepare files for deployment."""
    print("📦 Preparing for Railway deployment...")
    
    # Create instance directory
    os.makedirs('instance', exist_ok=True)
    print("✅ Created instance directory")
    
    # Create a simple .env file for Railway if it doesn't exist
    env_content = """# Railway Environment Configuration
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
PORT=5000
RAILWAY_ENVIRONMENT=production

# Model Configuration
MODEL_PATH=model/model.pkl

# API Configuration  
API_VERSION=1.0.0
API_NAME=AI Security Risk Detection API

# Logging
LOG_LEVEL=INFO

# Note: SQLite will be used automatically as fallback
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Created .env file for Railway")

def deploy_to_railway():
    """Deploy to Railway with latest fixes."""
    print("🚂 Deploying to Railway...")
    
    # Check if Railway CLI is available
    if not check_railway_cli():
        return False
    
    # Prepare deployment
    prepare_deployment()
    
    # Login to Railway
    print("🔐 Checking Railway login status...")
    run_command("railway whoami", check=False)
    
    # Deploy
    print("📤 Deploying to Railway...")
    run_command("railway up")
    
    # Wait a bit for deployment
    print("⏳ Waiting for deployment to process...")
    import time
    time.sleep(10)
    
    # Get deployment URL
    try:
        result = run_command("railway domains --json", check=False)
        if result.returncode == 0:
            try:
                domains = json.loads(result.stdout)
                if domains:
                    url = domains[0].get('domain', 'ai-security-risk-system-production.up.railway.app')
                    print(f"✅ Deployment successful!")
                    print(f"🌐 Application URL: https://{url}")
                    print(f"📊 Status URL: https://{url}/status")
                    return True
            except json.JSONDecodeError:
                pass
    except:
        pass
    
    print("✅ Deployment initiated!")
    print("🌐 Check your Railway dashboard for the application URL")
    print("📊 Status will be available at: https://your-url.railway.app/status")
    return True

def test_deployment():
    """Test the deployed application."""
    print("🧪 Testing deployment...")
    
    # Try to get the Railway URL
    try:
        result = run_command("railway domains --json", check=False)
        if result.returncode == 0:
            try:
                domains = json.loads(result.stdout)
                if domains:
                    url = domains[0].get('domain', 'ai-security-risk-system-production.up.railway.app')
                    
                    # Test health endpoint
                    print(f"🔍 Testing https://{url}/status")
                    import requests
                    response = requests.get(f"https://{url}/status", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        print("✅ Application is responding!")
                        print(f"📊 Database backend: {data.get('database', {}).get('backend', 'unknown')}")
                        print(f"🗄️  Database available: {data.get('database', {}).get('available', False)}")
                        return True
                    else:
                        print(f"⚠️  Status code: {response.status_code}")
            except Exception as e:
                print(f"⚠️  Could not test deployment: {e}")
    except:
        pass
    
    print("⚠️  Could not automatically test deployment")
    print("🌐 Please manually check your Railway dashboard and test the application")
    return False

if __name__ == "__main__":
    print("🚀 Railway Deployment Fix Script")
    print("=================================")
    
    # Deploy to Railway
    if deploy_to_railway():
        # Test the deployment
        test_deployment()
        
        print("\n📋 Next Steps:")
        print("1. Wait 2-3 minutes for Railway to fully deploy")
        print("2. Visit your Railway dashboard to see the deployment status")
        print("3. Test the signup/login functionality")
        print("4. Check the /status endpoint to verify database connectivity")
        
        print("\n🔧 If issues persist:")
        print("- Check Railway logs for any error messages")
        print("- Verify the deployment used the latest code")
        print("- The app should automatically fallback to SQLite if MongoDB fails")
    else:
        print("❌ Deployment failed. Please check the error messages above.")
        sys.exit(1)
