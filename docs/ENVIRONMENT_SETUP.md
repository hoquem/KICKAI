# Environment Setup Guide

## 🎯 Overview

This guide explains how to set up environment variables for KICKAI across different environments:
- **Development** (Local with mocks)
- **Testing** (Railway with real services)
- **Production** (Railway with real services)

## 🔒 Security First

**IMPORTANT**: Never commit `.env` files or any files containing secrets to version control. This includes:
- `TELEGRAM_BOT_TOKEN`
- `GOOGLE_API_KEY`
- `OPENAI_API_KEY`
- Firebase credentials
- Session strings

## 🏗️ Environment-Specific Setup

### Development Environment

For local development, use mock services by default:

```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Mock Services (Recommended for development)
USE_MOCK_DATASTORE=true
USE_MOCK_TELEGRAM=true
USE_MOCK_AI=true
USE_MOCK_PAYMENT=true

# AI Configuration
AI_PROVIDER=mock  # or 'ollama' for local AI
AI_MODEL_NAME=mock-model

# Application Configuration
DEFAULT_TEAM_ID=KAI
PAYMENT_ENABLED=false

# Development-specific
PYTHONPATH=src
TESTING=true
```

**Benefits of Mock Services:**
- Fast development cycles
- No external dependencies
- Consistent test data
- No API costs
- No risk of affecting real data

### Testing Environment (Railway)

For integration testing with real services:

```bash
# Railway Testing Environment Variables
ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=INFO

# Real Services
FIRESTORE_PROJECT_ID=kickai-testing-firestore
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"kickai-testing-firestore","private_key_id":"your_private_key_id","private_key":"-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n","client_email":"firebase-adminsdk-xxxxx@kickai-testing-firestore.iam.gserviceaccount.com","client_id":"your_client_id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40kickai-testing-firestore.iam.gserviceaccount.com"}
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

### Production Environment (Railway)

For live user service:

```bash
# Railway Production Environment Variables
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Real Services
FIRESTORE_PROJECT_ID=kickai-production-firestore
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"kickai-production-firestore","private_key_id":"your_private_key_id","private_key":"-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n","client_email":"firebase-adminsdk-xxxxx@kickai-production-firestore.iam.gserviceaccount.com","client_id":"your_client_id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40kickai-production-firestore.iam.gserviceaccount.com"}
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

## 🚀 Quick Setup

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/KICKAI.git
cd KICKAI

# Create virtual environment
python -m venv venv
source venv311/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-local.txt

# Set up development environment
cp .env.development.example .env.development
# Edit .env.development with your preferences

# Load environment
export $(cat .env.development | xargs)

# Run tests
python -m pytest tests/unit/ -v
```

### Testing Environment Setup

```bash
# Set up Railway project
railway login
railway init kickai-testing

# Configure environment variables in Railway dashboard
# (Use the testing environment variables above)

# Deploy to Railway
railway up

# Initialize test environment
python scripts/bootstrap_team.py --environment=testing
```

### Production Environment Setup

```bash
# Set up Railway project
railway init kickai-production

# Configure environment variables in Railway dashboard
# (Use the production environment variables above)

# Deploy to Railway
railway up

# Initialize production environment
python scripts/bootstrap_team.py --environment=production
```

## 🔧 Environment Variable Reference

### Core Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `ENVIRONMENT` | Environment name | ✅ | `development`, `testing`, `production` |
| `DEBUG` | Debug mode | ❌ | `true`, `false` |
| `LOG_LEVEL` | Logging level | ❌ | `DEBUG`, `INFO`, `WARNING` |
| `PYTHONPATH` | Python path | ❌ | `src` |

### Mock Services Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `USE_MOCK_DATASTORE` | Use mock database | ❌ | `true`, `false` |
| `USE_MOCK_TELEGRAM` | Use mock Telegram | ❌ | `true`, `false` |
| `USE_MOCK_AI` | Use mock AI | ❌ | `true`, `false` |
| `USE_MOCK_PAYMENT` | Use mock payments | ❌ | `true`, `false` |

### Firebase Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `FIRESTORE_PROJECT_ID` | Firebase project ID | ⚠️ | `my-project-123` |
| `FIREBASE_CREDENTIALS_JSON` | Firebase credentials JSON | ⚠️ | `{"type":"service_account",...}` |

### Telegram Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | ⚠️ | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `TELEGRAM_BOT_USERNAME` | Bot username (without @) | ⚠️ | `my_bot` |
| `TELEGRAM_MAIN_CHAT_ID` | Main chat ID | ⚠️ | `-1001234567890` |
| `TELEGRAM_LEADERSHIP_CHAT_ID` | Leadership chat ID | ⚠️ | `-1001234567891` |

### AI Provider Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `AI_PROVIDER` | AI provider to use | ✅ | `mock`, `ollama`, `google_gemini` |
| `AI_MODEL_NAME` | AI model name | ✅ | `mock-model`, `llama2`, `gemini-pro` |
| `GOOGLE_API_KEY` | Google API key (for Gemini) | ⚠️ | `AIzaSy...` |

### Application Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DEFAULT_TEAM_ID` | Default team ID | ❌ | `KAI` |
| `PAYMENT_ENABLED` | Enable payment system | ❌ | `true`, `false` |

## 🔍 Verifying Your Setup

### Development Environment

```bash
# Validate development setup
python scripts/validate_feature_deployment.py --feature=player_registration

# Run health checks
python scripts/run_health_checks.py

# Run tests
python -m pytest tests/unit/ -v
```

### Testing Environment

```bash
# Validate testing setup
python scripts/validate_feature_deployment.py --feature=all --environment=testing

# Run E2E tests
python run_e2e_tests.py --suite=smoke --environment=testing
```

### Production Environment

```bash
# Validate production setup
python scripts/validate_feature_deployment.py --feature=all --environment=production

# Run smoke tests
python run_e2e_tests.py --suite=smoke --environment=production
```

## 🚨 Troubleshooting

### Common Issues

1. **"Environment variable not found"**
   - Make sure you've set the variable in your current shell session
   - Restart your terminal after adding to shell profile
   - Check for typos in variable names

2. **"Invalid bot token"**
   - Ensure the token format is correct: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - Verify the token is active in @BotFather

3. **"Firebase credentials not found"**
   - Check that `FIREBASE_CREDENTIALS_FILE` points to a valid JSON file
   - Ensure the credentials file has the correct permissions

4. **"Google API key invalid"**
   - Verify your API key is active in Google Cloud Console
   - Check that the API key has the necessary permissions

5. **"Mock service not working"**
   - Ensure `USE_MOCK_*` variables are set to `true`
   - Check that mock services are properly imported

### Debug Mode

Enable debug logging to see what's happening:

```bash
export DEBUG="true"
export LOG_LEVEL="DEBUG"
```

## 🔄 Environment Switching

### Switch Between Environments

```bash
# Development
export $(cat .env.development | xargs)

# Testing (if running locally)
export $(cat .env.testing | xargs)

# Production (if running locally)
export $(cat .env.production | xargs)
```

### Environment-Specific Commands

```bash
# Development commands
make dev
make test-dev
make lint-dev

# Testing commands
make test-testing
make deploy-testing

# Production commands
make test-production
make deploy-production
```