# Railway Deployment Guide for KICKAI

## 🚀 Quick Start

This guide provides step-by-step instructions for deploying KICKAI to Railway for both testing and production environments.

## 📋 Prerequisites

### Required Accounts
- [Railway Account](https://railway.app/)
- [Firebase Console Access](https://console.firebase.google.com/)
- [Telegram Bot Token](https://t.me/BotFather)
- [Google Cloud Console](https://console.cloud.google.com/) (for Gemini API)

### Required Tools
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Firebase CLI](https://firebase.google.com/docs/cli)
- [Git](https://git-scm.com/)

## 🏗️ Project Structure

### Railway Projects
```
KICKAI-Railway/
├── kickai-testing/          # Testing environment
│   ├── kickai-bot-testing   # Bot service
│   └── kickai-db-testing    # Database service (if needed)
└── kickai-production/       # Production environment
    ├── kickai-bot-prod      # Bot service
    └── kickai-db-prod       # Database service (if needed)
```

## 🔧 Step 1: Railway Project Setup

### Create Railway Projects

#### Testing Project
```bash
# Create testing project
railway login
railway init kickai-testing
cd kickai-testing

# Create bot service
railway service create kickai-bot-testing
```

#### Production Project
```bash
# Create production project
railway init kickai-production
cd kickai-production

# Create bot service
railway service create kickai-bot-prod
```

## 🔧 Step 2: Environment Configuration

### Testing Environment Variables

Set these variables in Railway dashboard for `kickai-bot-testing`:

```bash
# Core Configuration
ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=INFO

# Firebase Configuration
FIRESTORE_PROJECT_ID=kickai-testing-firestore
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"kickai-testing-firestore","private_key_id":"your_private_key_id","private_key":"-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n","client_email":"firebase-adminsdk-xxxxx@kickai-testing-firestore.iam.gserviceaccount.com","client_id":"your_client_id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40kickai-testing-firestore.iam.gserviceaccount.com"}

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_testing_bot_token
TELEGRAM_BOT_USERNAME=KickAI_Testing_Bot
TELEGRAM_MAIN_CHAT_ID=-1001234567890
TELEGRAM_LEADERSHIP_CHAT_ID=-1001234567891

# AI Configuration
AI_PROVIDER=google_gemini
AI_MODEL_NAME=gemini-pro
GOOGLE_API_KEY=your_google_api_key

# Application Configuration
DEFAULT_TEAM_ID=KAI
PAYMENT_ENABLED=false
```

### Production Environment Variables

Set these variables in Railway dashboard for `kickai-bot-prod`:

```bash
# Core Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Firebase Configuration
FIRESTORE_PROJECT_ID=kickai-production-firestore
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"kickai-production-firestore","private_key_id":"your_private_key_id","private_key":"-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n","client_email":"firebase-adminsdk-xxxxx@kickai-production-firestore.iam.gserviceaccount.com","client_id":"your_client_id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40kickai-production-firestore.iam.gserviceaccount.com"}

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_production_bot_token
TELEGRAM_BOT_USERNAME=KickAI_Bot
TELEGRAM_MAIN_CHAT_ID=-1001234567892
TELEGRAM_LEADERSHIP_CHAT_ID=-1001234567893

# AI Configuration
AI_PROVIDER=google_gemini
AI_MODEL_NAME=gemini-pro
GOOGLE_API_KEY=your_google_api_key

# Application Configuration
DEFAULT_TEAM_ID=KAI
PAYMENT_ENABLED=true
```

## 🔧 Step 3: Firebase Credentials Setup

### Create Service Account Keys

#### Testing Firestore
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your testing project
3. Go to Project Settings → Service Accounts
4. Click "Generate new private key"
5. Save as `firebase_credentials_testing.json`

#### Production Firestore
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your production project
3. Go to Project Settings → Service Accounts
4. Click "Generate new private key"
5. Save as `firebase_credentials_production.json`

### Set Firebase Credentials as Environment Variables

#### For Testing Environment
```bash
# Extract the JSON content from your credentials file
FIREBASE_CREDENTIALS_JSON=$(cat firebase_credentials_testing.json)

# Set in Railway dashboard or via CLI
railway variables set FIREBASE_CREDENTIALS_JSON="$FIREBASE_CREDENTIALS_JSON"
```

#### For Production Environment
```bash
# Extract the JSON content from your credentials file
FIREBASE_CREDENTIALS_JSON=$(cat firebase_credentials_production.json)

# Set in Railway dashboard or via CLI
railway variables set FIREBASE_CREDENTIALS_JSON="$FIREBASE_CREDENTIALS_JSON"
```

### Important Notes
- **Security**: Never commit credential files to version control
- **Environment Variables**: Use Railway's environment variable system for all secrets
- **JSON Format**: The entire JSON content should be set as a single environment variable
- **Validation**: Ensure the JSON is properly escaped and valid

## 🔧 Step 4: Railway Configuration Files

### Create railway.json

Create `railway.json` in your project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python run_bot_railway.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Create nixpacks.toml (Optional)

For more control over the build process:

```toml
[phases.setup]
nixPkgs = ["python311", "pip"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["python -m pytest tests/ --cov=src"]

[start]
cmd = "python run_bot_railway.py"
```

## 🔧 Step 5: Health Check Implementation

### Add Health Check Endpoints

Update your `run_bot_railway.py` to include health check endpoints:

```python
from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('ENVIRONMENT', 'unknown'),
        'version': '1.0.0'
    })

@app.route('/health/detailed')
def detailed_health_check():
    # Add comprehensive health checks
    checks = {
        'database': check_database_connection(),
        'telegram': check_telegram_connection(),
        'ai': check_ai_connection()
    }
    
    overall_status = 'healthy' if all(checks.values()) else 'unhealthy'
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'checks': checks
    })

def check_database_connection():
    try:
        # Add your database health check logic
        return True
    except Exception:
        return False

def check_telegram_connection():
    try:
        # Add your Telegram health check logic
        return True
    except Exception:
        return False

def check_ai_connection():
    try:
        # Add your AI health check logic
        return True
    except Exception:
        return False

if __name__ == '__main__':
    # Start Flask app for health checks
    from threading import Thread
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))).start()
    
    # Start your Telegram bot
    # Your existing bot startup code here
```

## 🔧 Step 6: Deployment Process

### Initial Deployment

#### Testing Environment
```bash
# Navigate to testing project
cd kickai-testing

# Deploy to Railway
railway up

# Check deployment status
railway status

# View logs
railway logs
```

#### Production Environment
```bash
# Navigate to production project
cd kickai-production

# Deploy to Railway
railway up

# Check deployment status
railway status

# View logs
railway logs
```

### Continuous Deployment

#### Using Railway CLI
```bash
# Deploy from local changes
railway up

# Deploy from specific branch
railway up --branch main
```

#### Using GitHub Integration
1. Connect your GitHub repository to Railway
2. Enable automatic deployments
3. Railway will deploy on every push to main branch

## 🔧 Step 7: Environment Initialization

### Clean and Initialize Firestore

#### Testing Environment
```bash
# Clean test Firestore
python scripts-oneoff/cleanup/clean_firestore_collections.py --environment=testing

# Initialize test team
python scripts/bootstrap_team.py --environment=testing --team-name="KickAI Testing"
```

#### Production Environment
```bash
# Clean production Firestore (if needed)
python scripts-oneoff/cleanup/clean_firestore_collections.py --environment=production

# Initialize production team
python scripts/bootstrap_team.py --environment=production --team-name="Your Team Name"
```

## 🔧 Step 8: Validation and Testing

### Automated Validation

#### Testing Environment
```bash
# Run health checks
python scripts/run_health_checks.py --environment=testing

# Run E2E tests
python run_e2e_tests.py --suite=smoke --environment=testing

# Validate feature deployment
python scripts/validate_feature_deployment.py --feature=all --environment=testing
```

#### Production Environment
```bash
# Run health checks
python scripts/run_health_checks.py --environment=production

# Run smoke tests
python run_e2e_tests.py --suite=smoke --environment=production
```

### Manual Validation

#### Testing Environment Checklist
- [ ] Bot responds to `/help` in test chat
- [ ] Player registration works (`/register`)
- [ ] Leadership commands work in leadership chat
- [ ] Database operations work correctly
- [ ] AI responses are appropriate
- [ ] Error handling works as expected

#### Production Environment Checklist
- [ ] All testing environment checks pass
- [ ] Bot responds in production chats
- [ ] Payment system works (if enabled)
- [ ] Performance is acceptable
- [ ] Monitoring is working
- [ ] Logs are being generated

## 🔧 Step 9: Monitoring and Maintenance

### Railway Monitoring

#### View Logs
```bash
# View real-time logs
railway logs --follow

# View logs for specific service
railway logs --service kickai-bot-testing
```

#### Monitor Resources
```bash
# View resource usage
railway status

# View service metrics
railway service show kickai-bot-testing
```

### Custom Monitoring

#### Health Check Monitoring
```bash
# Check health endpoint
curl https://your-app.railway.app/health

# Check detailed health
curl https://your-app.railway.app/health/detailed
```

#### Application Monitoring
- Set up alerts for health check failures
- Monitor error rates and response times
- Track user engagement metrics

## 🔧 Step 10: Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check build logs
railway logs --build

# Verify requirements.txt
pip install -r requirements.txt

# Check Python version compatibility
python --version
```

#### Runtime Errors
```bash
# Check application logs
railway logs

# Verify environment variables
railway variables

# Test locally with same environment
export $(railway variables | xargs)
python run_bot_railway.py
```

#### Database Connection Issues
```bash
# Verify Firebase credentials
python -c "import json; print(json.load(open('credentials/firebase_credentials_testing.json')))"

# Test database connection
python scripts/test_database_connection.py --environment=testing
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set debug mode
railway variables set DEBUG=true
railway variables set LOG_LEVEL=DEBUG

# Redeploy
railway up
```

## 🔧 Step 11: Scaling and Performance

### Railway Scaling

#### Automatic Scaling
Railway automatically scales based on:
- CPU usage
- Memory usage
- Request volume

#### Manual Scaling
```bash
# Scale service
railway scale kickai-bot-testing --min=1 --max=3

# Check scaling status
railway service show kickai-bot-testing
```

### Performance Optimization

#### Resource Optimization
- Monitor memory usage
- Optimize Python dependencies
- Use connection pooling for database
- Implement caching strategies

#### Cost Optimization
- Use appropriate instance sizes
- Monitor usage patterns
- Implement auto-scaling policies
- Review and optimize dependencies

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI Reference](https://docs.railway.app/develop/cli)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)
- [Railway Health Checks](https://docs.railway.app/deploy/healthchecks)
- [Railway Monitoring](https://docs.railway.app/deploy/monitoring)

## 🆘 Support

### Railway Support
- [Railway Discord](https://discord.gg/railway)
- [Railway Status Page](https://status.railway.app/)
- [Railway Documentation](https://docs.railway.app/)

### KICKAI Support
- Check logs: `railway logs`
- Run health checks: `python scripts/run_health_checks.py`
- Validate deployment: `python scripts/validate_feature_deployment.py` 