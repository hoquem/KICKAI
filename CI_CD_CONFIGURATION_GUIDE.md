# CI/CD Configuration Guide for KICKAI

## Overview
This guide covers the complete CI/CD setup for the KICKAI Telegram bot using GitHub Actions and Railway deployment.

## Branch Strategy
- **main**: Production-ready code
- **development**: Integration and testing branch
- **feature/***: Feature development branches

## Environments
- **testing**: Automated testing and validation
- **staging**: Pre-production testing
- **production**: Live production environment

## GitHub Actions Workflows

### 1. Testing Deployment Pipeline (`.github/workflows/deploy-testing.yml`)
**Triggers:**
- Push to `testing` or `development` branches
- Pull requests to `testing`, `development`, or `main`
- Manual workflow dispatch

**Jobs:**
1. **Dependencies**: Quick dependency validation
2. **Test**: Fast critical tests
3. **Deploy**: Deploy to Railway testing environment

### 2. Main Deployment Pipeline (`.github/workflows/deploy.yml`)
**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Jobs:**
- **deploy-testing**: Deploy to testing environment
- **deploy-staging**: Deploy to staging environment (manual)
- **deploy-production**: Deploy to production environment (manual)

### 3. CI Pipeline (`.github/workflows/ci.yml`)
**Triggers:**
- All pushes and pull requests

**Jobs:**
- Code quality checks
- Unit tests
- Integration tests
- Security scans

## Required GitHub Secrets

### Railway Configuration
```bash
RAILWAY_TOKEN=your_railway_token_here
```

### Environment-Specific Variables
Each environment (testing, staging, production) should have:
- `TELEGRAM_BOT_TOKEN_<ENV>`
- `FIREBASE_CREDENTIALS_<ENV>`
- `OPENAI_API_KEY_<ENV>`

## Setting Up GitHub Secrets

### 1. Get Railway Token
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and get token
railway login
railway whoami --json
```

### 2. Add Secrets to GitHub
1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add the following secrets:
   - `RAILWAY_TOKEN`: Your Railway authentication token
   - `TELEGRAM_BOT_TOKEN_TESTING`: Testing bot token
   - `TELEGRAM_BOT_TOKEN_STAGING`: Staging bot token
   - `TELEGRAM_BOT_TOKEN_PRODUCTION`: Production bot token
   - `FIREBASE_CREDENTIALS_TESTING`: Testing Firebase credentials (JSON)
   - `FIREBASE_CREDENTIALS_STAGING`: Staging Firebase credentials (JSON)
   - `FIREBASE_CREDENTIALS_PRODUCTION`: Production Firebase credentials (JSON)
   - `OPENAI_API_KEY_TESTING`: Testing OpenAI API key
   - `OPENAI_API_KEY_STAGING`: Staging OpenAI API key
   - `OPENAI_API_KEY_PRODUCTION`: Production OpenAI API key

## Railway Projects Setup

### Testing Environment
```bash
# Create testing project
railway project create kickai-testing

# Link to local project
railway link --project kickai-testing

# Set environment variables
railway variables set TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN_TESTING
railway variables set FIREBASE_CREDENTIALS="$FIREBASE_CREDENTIALS_TESTING"
railway variables set OPENAI_API_KEY=$OPENAI_API_KEY_TESTING
railway variables set ENVIRONMENT=testing
```

### Staging Environment
```bash
# Create staging project
railway project create kickai-staging

# Link to local project
railway link --project kickai-staging

# Set environment variables
railway variables set TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN_STAGING
railway variables set FIREBASE_CREDENTIALS="$FIREBASE_CREDENTIALS_STAGING"
railway variables set OPENAI_API_KEY=$OPENAI_API_KEY_STAGING
railway variables set ENVIRONMENT=staging
```

### Production Environment
```bash
# Create production project
railway project create kickai-production

# Link to local project
railway link --project kickai-production

# Set environment variables
railway variables set TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN_PRODUCTION
railway variables set FIREBASE_CREDENTIALS="$FIREBASE_CREDENTIALS_PRODUCTION"
railway variables set OPENAI_API_KEY=$OPENAI_API_KEY_PRODUCTION
railway variables set ENVIRONMENT=production
```

## Deployment Process

### Automated Testing Deployment
1. Push to `development` branch
2. GitHub Actions automatically:
   - Runs dependency checks
   - Executes quick tests
   - Deploys to Railway testing environment
   - Performs health checks

### Manual Staging Deployment
1. Go to GitHub Actions
2. Select "Deploy to Railway" workflow
3. Choose "staging" environment
4. Click "Run workflow"

### Manual Production Deployment
1. Go to GitHub Actions
2. Select "Deploy to Railway" workflow
3. Choose "production" environment
4. Click "Run workflow"

## Health Checks

### Testing Environment
- **Health Endpoint**: `https://kickai-testing-production.up.railway.app/health`
- **Status Endpoint**: `https://kickai-testing-production.up.railway.app/status`
- **Root Endpoint**: `https://kickai-testing-production.up.railway.app/`

### Staging Environment
- **Health Endpoint**: `https://kickai-staging-production.up.railway.app/health`
- **Status Endpoint**: `https://kickai-staging-production.up.railway.app/status`

### Production Environment
- **Health Endpoint**: `https://kickai-production-production.up.railway.app/health`
- **Status Endpoint**: `https://kickai-production-production.up.railway.app/status`

## Monitoring and Alerts

### Railway Dashboard
- Monitor service status
- View logs in real-time
- Check resource usage
- Set up alerts for downtime

### GitHub Actions
- Monitor workflow runs
- View test results
- Check deployment status
- Set up notifications for failures

## Troubleshooting

### Common Issues

1. **Railway Token Expired**
   ```bash
   railway login
   # Get new token and update GitHub secret
   ```

2. **Environment Variables Missing**
   - Check Railway project variables
   - Verify GitHub secrets are set correctly
   - Ensure environment-specific variables are configured

3. **Deployment Failures**
   - Check Railway logs
   - Verify Procfile configuration
   - Ensure all dependencies are in requirements.txt

4. **Health Check Failures**
   - Verify service is running on Railway
   - Check application logs
   - Ensure FastAPI endpoints are responding

### Debug Commands
```bash
# Check Railway service status
railway service status

# View Railway logs
railway logs

# Check environment variables
railway variables

# Test health endpoint
curl https://kickai-testing-production.up.railway.app/health
```

## Best Practices

1. **Always test in testing environment first**
2. **Use feature branches for development**
3. **Merge to development for integration testing**
4. **Only deploy to production after staging validation**
5. **Monitor deployments and set up alerts**
6. **Keep secrets secure and rotate regularly**
7. **Document all environment-specific configurations**

## Security Considerations

1. **Never commit secrets to repository**
2. **Use environment-specific tokens**
3. **Rotate API keys regularly**
4. **Monitor access logs**
5. **Use least privilege principle for Railway tokens**
6. **Enable 2FA on GitHub and Railway accounts**

## Next Steps

1. Set up GitHub secrets for all environments
2. Configure Railway projects for staging and production
3. Test the complete CI/CD pipeline
4. Set up monitoring and alerting
5. Document team deployment procedures
6. Create rollback procedures
7. Set up automated testing for all environments 