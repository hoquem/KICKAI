# KICKAI Deployment & Environment Management Plan

## 🎯 Overview

This document outlines the complete deployment strategy for KICKAI across three environments:
- **Development** (Local)
- **Testing** (Railway)
- **Production** (Railway)

## 🏗️ Environment Architecture

### Environment Matrix

| Environment | Hosting | Database | Bot | Chats | Purpose | Branch |
|-------------|---------|----------|-----|-------|---------|---------|
| **Development** | Local | Mock/Mock Firestore | Mock | Mock | Feature Development | `development` |
| **Testing** | Railway | Test Firestore | Test Bot | Test Chats | Integration Testing | `main` |
| **Production** | Railway | Production Firestore | Production Bot | Production Chats | Live Users | `main` |

### Environment-Specific Configurations

#### Development Environment
- **Database**: Mock DataStore (with optional local Firestore for integration testing)
- **Bot**: Mock Telegram client
- **Chats**: Mock chat interactions
- **AI**: Local Ollama or Google Gemini
- **Purpose**: Rapid development and unit testing

#### Testing Environment
- **Database**: Dedicated Test Firestore
- **Bot**: Real Telegram bot (test instance)
- **Chats**: Real test chats (KickAI Testing + Leadership)
- **AI**: Google Gemini
- **Purpose**: Integration testing with real users

#### Production Environment
- **Database**: Production Firestore
- **Bot**: Production Telegram bot
- **Chats**: Production team chats
- **AI**: Google Gemini
- **Purpose**: Live user service

## 🚀 Deployment Pipeline

### Branch Strategy

```
development (feature development)
    ↓ (feature complete)
feature/fix branches
    ↓ (code review + tests pass)
main (deployment branch)
    ↓ (automated deployment)
Testing Environment (Railway)
    ↓ (testing validation)
Production Environment (Railway)
```

### Deployment Flow

1. **Development**: Local development on `development` branch
2. **Feature Branches**: Create `feature/` or `fix/` branches for specific work
3. **Code Review**: Merge to `development` after review
4. **Testing**: Merge `development` to `main` for testing deployment
5. **Validation**: Test with real users in testing environment
6. **Production**: Deploy to production after testing validation

## 🔧 Development Environment Setup

### Local Development Configuration

#### Option 1: Mock Everything (Recommended for most development)
```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
USE_MOCK_DATASTORE=true
USE_MOCK_TELEGRAM=true
USE_MOCK_AI=true
AI_PROVIDER=mock
```

#### Option 2: Real Services (For integration testing)
```bash
# .env.development.integration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
USE_MOCK_DATASTORE=false
USE_MOCK_TELEGRAM=false
USE_MOCK_AI=false
AI_PROVIDER=google_gemini
FIRESTORE_PROJECT_ID=your-dev-firestore-id
TELEGRAM_BOT_TOKEN=your-dev-bot-token
```

### Development Database Strategy

**Recommendation**: Use Mock DataStore for most development, with optional local Firestore for integration testing.

**Benefits**:
- Fast development cycles
- No external dependencies
- Consistent test data
- No risk of affecting real data

**When to use real Firestore**:
- Testing Firestore-specific features
- Integration testing with real data
- Performance testing

### Development Bot Strategy

**Recommendation**: Use Mock Telegram client for most development.

**Benefits**:
- No need for real bot tokens
- Faster development cycles
- No risk of sending messages to real chats
- Consistent test scenarios

## 🧪 Testing Environment Setup

### Railway Configuration

#### Environment Variables for Testing
```bash
# Railway Testing Environment Variables
ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=INFO
FIRESTORE_PROJECT_ID=kickai-testing-firestore
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"kickai-testing-firestore","private_key_id":"your_private_key_id","private_key":"-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n","client_email":"firebase-adminsdk-xxxxx@kickai-testing-firestore.iam.gserviceaccount.com","client_id":"your_client_id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40kickai-testing-firestore.iam.gserviceaccount.com"}
TELEGRAM_BOT_TOKEN=your_testing_bot_token
TELEGRAM_BOT_USERNAME=KickAI_Testing_Bot
TELEGRAM_MAIN_CHAT_ID=-1001234567890  # KickAI Testing chat
TELEGRAM_LEADERSHIP_CHAT_ID=-1001234567891  # KickAI Testing - Leadership
AI_PROVIDER=google_gemini
AI_MODEL_NAME=gemini-pro
GOOGLE_API_KEY=your_google_api_key
DEFAULT_TEAM_ID=KAI
PAYMENT_ENABLED=false
```

#### Railway Service Configuration
```yaml
# railway.json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python run_telegram_bot.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Testing Environment Initialization

#### Step 1: Clean Test Firestore
```bash
# Run cleanup script
python scripts-oneoff/cleanup/clean_firestore_collections.py --environment=testing
```

#### Step 2: Initialize Test Team
```bash
# Bootstrap the KickAI Testing team
python scripts/bootstrap_team.py --environment=testing --team-name="KickAI Testing"
```

#### Step 3: Verify Setup
```bash
# Run health checks
python scripts/run_health_checks.py --environment=testing

# Run E2E tests
python run_e2e_tests.py --suite=smoke --environment=testing
```

### Testing Environment Validation

#### Automated Validation
```bash
# Run comprehensive validation
python scripts/validate_feature_deployment.py --feature=all --environment=testing
```

#### Manual Validation Checklist
- [ ] Bot responds to `/start` in main chat
- [ ] Bot responds to `/help` in main chat
- [ ] Player registration works (`/register`)
- [ ] Leadership commands work in leadership chat
- [ ] Database operations work correctly
- [ ] AI responses are appropriate
- [ ] Error handling works as expected

## 🏭 Production Environment Setup

### Railway Configuration

#### Environment Variables for Production
```bash
# Railway Production Environment Variables
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
FIRESTORE_PROJECT_ID=kickai-production-firestore
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"kickai-production-firestore","private_key_id":"your_private_key_id","private_key":"-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n","client_email":"firebase-adminsdk-xxxxx@kickai-production-firestore.iam.gserviceaccount.com","client_id":"your_client_id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40kickai-production-firestore.iam.gserviceaccount.com"}
TELEGRAM_BOT_TOKEN=your_production_bot_token
TELEGRAM_BOT_USERNAME=KickAI_Bot
TELEGRAM_MAIN_CHAT_ID=-1001234567892  # Production main chat
TELEGRAM_LEADERSHIP_CHAT_ID=-1001234567893  # Production leadership chat
AI_PROVIDER=google_gemini
AI_MODEL_NAME=gemini-pro
GOOGLE_API_KEY=your_google_api_key
DEFAULT_TEAM_ID=KAI
PAYMENT_ENABLED=true
```

### Production Deployment Process

#### Pre-Deployment Checklist
- [ ] All tests pass in testing environment
- [ ] Code review completed
- [ ] Security review completed
- [ ] Performance testing completed
- [ ] Backup of production data (if applicable)

#### Deployment Steps
1. **Merge to main**: Ensure all changes are in main branch
2. **Deploy to testing**: Verify in testing environment
3. **User acceptance testing**: Get feedback from test users
4. **Deploy to production**: Deploy to production environment
5. **Post-deployment validation**: Verify production deployment

## 🔄 Deployment Automation

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m pytest tests/ --cov=src
        env:
          PYTHONPATH: src

  deploy-testing:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway Testing
        uses: railway/deploy@v1
        with:
          service: kickai-testing
          token: ${{ secrets.RAILWAY_TOKEN }}

  deploy-production:
    needs: [test, deploy-testing]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway Production
        uses: railway/deploy@v1
        with:
          service: kickai-production
          token: ${{ secrets.RAILWAY_TOKEN }}
```

## 📊 Monitoring and Health Checks

### Health Check Endpoints

```python
# Health check endpoints for Railway
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('ENVIRONMENT'),
        'version': '1.0.0'
    }

@app.route('/health/detailed')
def detailed_health_check():
    # Comprehensive health check including database, AI, etc.
    pass
```

### Monitoring Metrics

- **Application Metrics**: Response time, error rates, memory usage
- **Business Metrics**: User registrations, command usage, AI response quality
- **Infrastructure Metrics**: CPU, memory, disk usage, network

## 🔒 Security Considerations

### Environment Isolation

- **Separate Firestore projects** for each environment
- **Different bot tokens** for each environment
- **Environment-specific API keys**
- **Separate Railway projects** for testing and production

### Secret Management

- **Railway Secrets**: Use Railway's built-in secret management
- **Environment Variables**: Never commit secrets to version control
- **Rotation**: Regular rotation of API keys and tokens

### Access Control

- **Development**: Local access only
- **Testing**: Limited team access
- **Production**: Restricted access with audit logging

## 📋 Implementation Checklist

### Phase 1: Development Environment
- [ ] Set up local development with mocks
- [ ] Configure development environment variables
- [ ] Test local development workflow
- [ ] Document development setup process

### Phase 2: Testing Environment
- [ ] Set up Railway testing project
- [ ] Configure test Firestore
- [ ] Set up test bot and chats
- [ ] Deploy initial version to testing
- [ ] Validate testing environment
- [ ] Onboard test users

### Phase 3: Production Environment
- [ ] Set up Railway production project
- [ ] Configure production Firestore
- [ ] Set up production bot and chats
- [ ] Deploy to production
- [ ] Validate production environment
- [ ] Go live with real users

### Phase 4: Automation
- [ ] Set up GitHub Actions workflows
- [ ] Configure automated testing
- [ ] Set up monitoring and alerting
- [ ] Document deployment procedures

## 🚨 Rollback Procedures

### Emergency Rollback Process

1. **Immediate Action**: Stop the deployment
2. **Assessment**: Identify the issue
3. **Rollback**: Deploy previous working version
4. **Investigation**: Root cause analysis
5. **Fix**: Develop and test the fix
6. **Re-deploy**: Deploy the fix

### Rollback Triggers

- High error rates (>5%)
- Service unavailability
- Data corruption
- Security incidents
- Performance degradation

## 📞 Support and Maintenance

### Support Contacts

- **Development Issues**: Development team
- **Testing Issues**: QA team
- **Production Issues**: DevOps team
- **User Issues**: Support team

### Maintenance Schedule

- **Daily**: Health check monitoring
- **Weekly**: Performance review
- **Monthly**: Security review
- **Quarterly**: Architecture review

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [GitHub Actions Documentation](https://docs.github.com/en/actions) 