# KICKAI Branching Strategy & Deployment Workflow

## Overview

This document outlines the branching strategy and deployment workflow for the KICKAI project, ensuring safe and controlled deployments across multiple environments.

## Branch Structure

```
feature/* → development → main → (Railway deploys to testing/staging/production)
```

### Branches

- **`feature/*`**: Feature branches for individual development work
- **`development`**: Integration branch for team collaboration
- **`main`**: Production-ready code (triggers deployments)

## Deployment Environments

### 1. Testing Environment
- **Railway Project**: `kickai-testing`
- **Auto-deploy**: ✅ Yes (on push to main)
- **Purpose**: Automated testing and validation
- **URL**: `https://test-kickai.railway.app`

### 2. Staging Environment
- **Railway Project**: `kickai-staging`
- **Auto-deploy**: ❌ No (manual promotion)
- **Purpose**: Pre-production testing and validation
- **URL**: `https://staging-kickai.railway.app`

### 3. Production Environment
- **Railway Project**: `kickai-production`
- **Auto-deploy**: ❌ No (manual promotion)
- **Purpose**: Live production environment
- **URL**: `https://production-kickai.railway.app`

## Workflow

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Develop and Commit**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Push and Create PR**
   ```bash
   git push -u origin feature/new-feature
   # Create PR to development branch
   ```

4. **Merge to Development**
   ```bash
   # After PR review, merge to development
   git checkout development
   git pull origin development
   ```

5. **Merge to Main**
   ```bash
   # Create PR from development to main
   # After review and testing, merge to main
   ```

### Deployment Workflow

1. **Automatic Testing Deployment**
   - Push to `main` triggers automatic deployment to testing
   - GitHub Actions runs tests and deploys to Railway testing environment

2. **Manual Staging Deployment**
   ```bash
   # Via GitHub Actions UI or CLI
   gh workflow run deploy.yml -f environment=staging
   ```

3. **Manual Production Deployment**
   ```bash
   # Via GitHub Actions UI or CLI
   gh workflow run deploy.yml -f environment=production
   ```

## GitHub Branch Protection Rules

### Main Branch
- ✅ Require pull request reviews (minimum 1)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Restrict pushes to main
- ✅ Require linear history

### Development Branch
- ✅ Require pull request reviews (minimum 1)
- ✅ Allow force pushes (for cleanup)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date

## Environment Configuration

### Environment Detection
The application automatically detects the environment based on:
1. `ENVIRONMENT` environment variable
2. `RAILWAY_ENVIRONMENT` environment variable
3. Railway service name
4. Fallback to development

### Configuration Files
- `config/bot_config.testing.json` - Testing environment config
- `config/bot_config.staging.json` - Staging environment config
- `config/bot_config.production.json` - Production environment config

## Railway Setup

### Projects Created
- `kickai-testing` - Testing environment
- `kickai-staging` - Staging environment
- `kickai-production` - Production environment

### Environment Variables
Each environment has specific variables:
- `ENVIRONMENT`: testing/staging/production
- `RAILWAY_ENVIRONMENT`: testing/staging/production
- `FIREBASE_CREDENTIALS_JSON`: Environment-specific Firebase credentials
- `TELEGRAM_BOT_TOKEN`: Environment-specific bot token

## Deployment Scripts

### Local Deployment
```bash
# Deploy to testing
./scripts/deploy-testing.sh

# Deploy to staging
./scripts/deploy-staging.sh

# Deploy to production
./scripts/deploy-production.sh
```

### Railway CLI Commands
```bash
# Link to specific project
railway link --project kickai-testing

# Set environment variables
railway variables set ENVIRONMENT=testing

# Deploy
railway up --environment testing
```

## Rollback Strategy

### Quick Rollback
```bash
# Revert to previous commit
git revert HEAD
git push origin main
```

### Railway Rollback
```bash
# Rollback to previous deployment
railway rollback
```

## Monitoring and Alerts

### Health Checks
- Testing: `https://test-kickai.railway.app/health`
- Staging: `https://staging-kickai.railway.app/health`
- Production: `https://production-kickai.railway.app/health`

### Logs
```bash
# View logs for specific environment
railway logs --environment testing
railway logs --environment staging
railway logs --environment production
```

## Best Practices

1. **Never push directly to main** - Always use PRs
2. **Test in development** - Ensure features work before merging
3. **Use descriptive commit messages** - Follow conventional commits
4. **Monitor deployments** - Check logs and health endpoints
5. **Document changes** - Update documentation with new features
6. **Backup before major changes** - Create backup branches for safety

## Troubleshooting

### Common Issues

1. **Deployment Fails**
   - Check Railway logs: `railway logs`
   - Verify environment variables: `railway variables`
   - Check GitHub Actions workflow

2. **Environment Detection Issues**
   - Verify `ENVIRONMENT` variable is set
   - Check Railway service name
   - Review configuration files

3. **Branch Protection Issues**
   - Ensure PR has required reviews
   - Check status checks are passing
   - Verify branch is up to date

### Support
- Railway Documentation: https://docs.railway.app/
- GitHub Actions Documentation: https://docs.github.com/en/actions
- KICKAI Team: Contact team lead for issues 