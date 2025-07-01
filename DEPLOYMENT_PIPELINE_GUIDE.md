# 🚀 KICKAI Deployment Pipeline Guide

## Overview

This guide covers the complete deployment pipeline for KICKAI, implementing DevOps best practices with robust dependency management, comprehensive testing, and high-success deployment strategies.

## 🏗️ Architecture Overview

### Deployment Strategy
- **Single Railway Project, Multiple Services**: Cost-effective approach with environment isolation
- **Three Environments**: Testing, Staging, Production
- **Automated CI/CD**: GitHub Actions with comprehensive validation
- **Rollback Capabilities**: Automatic rollback on deployment failures

### Service Structure
```
kickai-project/
├── kickai-testing     # Development & testing
├── kickai-staging     # Pre-production validation
└── kickai-production  # Live production
```

## 📋 Prerequisites

### Required Tools
```bash
# Install Railway CLI
npm install -g @railway/cli

# Install additional tools
brew install jq  # macOS
# or
apt-get install jq  # Ubuntu/Debian
```

### Required Accounts
- [Railway](https://railway.app) - Deployment platform
- [GitHub](https://github.com) - Source control & CI/CD
- [Firebase](https://firebase.google.com) - Database
- [Google AI](https://ai.google.dev) - AI services
- [Telegram](https://core.telegram.org/bots) - Bot platform

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd KICKAI

# Login to Railway
railway login

# Run automated setup
./scripts/setup-single-project.sh
```

### 2. Environment Configuration
```bash
# Set up environment variables for each service
railway service use kickai-testing
railway variables set TELEGRAM_BOT_TOKEN="your_testing_token"
railway variables set FIREBASE_CREDENTIALS="your_testing_creds"
railway variables set GOOGLE_AI_API_KEY="your_testing_key"

# Repeat for staging and production
```

### 3. First Deployment
```bash
# Deploy to testing
./scripts/deploy.sh deploy kickai-testing

# Verify deployment
./scripts/health_check.py --sync
```

## 🔧 Detailed Setup

### Environment-Specific Configuration

#### Testing Environment
- **Purpose**: Rapid iteration and development
- **Resources**: Minimal (0.25 CPU, 256MB RAM)
- **Deployment**: Automatic on push to `testing` branch
- **Health Checks**: Basic validation

#### Staging Environment
- **Purpose**: Pre-production validation
- **Resources**: Medium (0.5 CPU, 512MB RAM)
- **Deployment**: Manual or on push to `staging` branch
- **Health Checks**: Comprehensive validation

#### Production Environment
- **Purpose**: Live production service
- **Resources**: Full (1.0 CPU, 1GB RAM)
- **Deployment**: Manual approval required
- **Health Checks**: Full validation with alerts

### Railway Configuration Files

#### `railway.json` (Main Configuration)
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt",
    "watchPatterns": ["src/**/*", "requirements*.txt"]
  },
  "deploy": {
    "startCommand": "python src/main.py",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### Environment-Specific Configs
- `railway-testing.json` - Optimized for rapid iteration
- `railway-staging.json` - Balanced performance and safety
- `railway-production.json` - Production-grade configuration

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Production Deployment (`deploy-production.yml`)
- **Triggers**: Push to `main`, `staging`, `testing` branches
- **Features**:
  - Dependency caching and validation
  - Comprehensive testing (unit, integration, system)
  - Code quality checks (linting, security, performance)
  - Build validation and optimization
  - Environment-specific deployment
  - Health checks and rollback mechanisms
  - Post-deployment monitoring

#### 2. Staging Deployment (`deploy-staging.yml`)
- **Triggers**: Push to `staging` branch
- **Features**:
  - Quick dependency validation
  - Staging-specific tests
  - Quality checks
  - Deployment with health verification

#### 3. Testing Deployment (`deploy-testing.yml`)
- **Triggers**: Push to `testing` branch
- **Features**:
  - Fast dependency check
  - Critical tests only
  - Quick deployment
  - Basic health check

#### 4. Continuous Integration (`ci.yml`)
- **Triggers**: All pull requests
- **Features**:
  - Lint and format checks
  - Unit and integration tests
  - Security and dependency validation
  - Build validation
  - Performance checks
  - Documentation validation

#### 5. Dependency Updates (`dependency-update.yml`)
- **Triggers**: Weekly schedule, manual dispatch
- **Features**:
  - Automated dependency checking
  - Security vulnerability scanning
  - Update recommendations
  - Pull request creation for updates

### Pipeline Stages

#### 1. Dependencies Stage
```yaml
dependencies:
  - Cache key generation based on requirements files
  - Dependency installation with version pinning
  - Compatibility validation
  - Critical dependency verification
```

#### 2. Testing Stage
```yaml
test:
  - Unit tests with coverage
  - Integration tests
  - System tests
  - Parallel execution for speed
```

#### 3. Quality Stage
```yaml
quality:
  - Code formatting (Black, isort)
  - Linting (flake8)
  - Type checking (mypy)
  - Security scanning (bandit, safety)
```

#### 4. Build Stage
```yaml
build:
  - Application structure validation
  - Configuration file validation
  - Startup validation
  - Railway configuration validation
```

#### 5. Deploy Stage
```yaml
deploy:
  - Environment-specific deployment
  - Health check verification
  - Rollback on failure
  - Post-deployment monitoring
```

## 🛠️ Deployment Scripts

### Core Scripts

#### `scripts/setup-single-project.sh`
```bash
# Set up all environments in a single Railway project
./scripts/setup-single-project.sh

# Set up specific environment
./scripts/setup-single-project.sh -s kickai-testing

# Deploy only (skip setup)
./scripts/setup-single-project.sh -d
```

#### `scripts/deploy.sh`
```bash
# Deploy all services
./scripts/deploy.sh deploy

# Deploy specific service
./scripts/deploy.sh deploy kickai-production

# Check status
./scripts/deploy.sh status

# Health check
./scripts/deploy.sh health kickai-staging

# Rollback (requires backup file)
./scripts/deploy.sh rollback kickai-production backup_file.json
```

#### `scripts/health_check.py`
```bash
# Comprehensive health check
python scripts/health_check.py

# Simple health check
python scripts/health_check.py --sync

# Save report
python scripts/health_check.py --output health_report.json
```

#### `scripts/monitoring_dashboard.py`
```bash
# Real-time monitoring
python scripts/monitoring_dashboard.py

# Simple monitoring
python scripts/monitoring_dashboard.py --simple

# Custom interval
python scripts/monitoring_dashboard.py --interval 60
```

#### `scripts/preview_deployment.py`
```bash
# Preview production deployment
python scripts/preview_deployment.py -e production

# Preview staging deployment
python scripts/preview_deployment.py -e staging

# Save preview to file
python scripts/preview_deployment.py -e production -o preview.json
```

## 🔒 Security & Best Practices

### Environment Variables
```bash
# Required variables for each environment
TELEGRAM_BOT_TOKEN_<ENV>     # Telegram bot token
FIREBASE_CREDENTIALS_<ENV>   # Firebase service account JSON
GOOGLE_AI_API_KEY_<ENV>      # Google AI API key

# Common variables
ENVIRONMENT                  # Environment name
LOG_LEVEL                   # Logging level
PYTHONPATH                  # Python path
PYTHONUNBUFFERED           # Python output buffering
```

### Security Validations
- **Hardcoded Secrets Detection**: Scans for exposed credentials
- **Dependency Vulnerability Scanning**: Checks for known vulnerabilities
- **Configuration Validation**: Ensures secure configurations
- **Access Control**: Environment-specific permissions

### Dependency Management
```bash
# Pin all dependencies
pip freeze > requirements.txt

# Update dependencies safely
python scripts/preview_deployment.py --dependency-update

# Security audit
safety check
pip-audit
```

## 📊 Monitoring & Observability

### Health Checks
- **Endpoint**: `/health`
- **Response**: JSON with service status
- **Checks**: Database connectivity, AI service availability, bot status

### Metrics Collection
- **Response Times**: Track API performance
- **Error Rates**: Monitor service reliability
- **Resource Usage**: CPU, memory, disk utilization
- **Uptime**: Service availability tracking

### Alerting
- **Critical Alerts**: Production service down
- **Performance Alerts**: High response times
- **Error Alerts**: Elevated error rates
- **Resource Alerts**: High resource usage

## 🔄 Rollback Strategy

### Automatic Rollback
```yaml
# Triggered on:
- Health check failures
- Deployment timeouts
- Build failures
- Critical errors
```

### Manual Rollback
```bash
# Get deployment history
railway service status

# Rollback to previous deployment
railway service rollback <deployment_id>

# Verify rollback
./scripts/health_check.py --sync
```

### Rollback Validation
1. **Health Check**: Verify service is responding
2. **Functionality Test**: Test core features
3. **Performance Check**: Ensure acceptable performance
4. **Log Analysis**: Check for errors

## 🧪 Testing Strategy

### Test Types
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **System Tests**: End-to-end functionality testing
- **Performance Tests**: Load and stress testing

### Test Execution
```bash
# Run all tests
pytest

# Run specific test types
pytest tests/test_agents/     # Unit tests
pytest tests/test_integration/ # Integration tests
pytest tests/test_telegram/   # System tests

# Run with coverage
pytest --cov=src --cov-report=html
```

### Test Automation
- **Pre-deployment**: All tests must pass
- **Post-deployment**: Smoke tests verify deployment
- **Continuous**: Regular test execution

## 📈 Performance Optimization

### Build Optimization
- **Dependency Caching**: Reduces build times
- **Layer Optimization**: Efficient Docker layers
- **Parallel Processing**: Concurrent operations
- **Resource Limits**: Controlled resource usage

### Runtime Optimization
- **Connection Pooling**: Database connection management
- **Caching**: Response caching strategies
- **Async Processing**: Non-blocking operations
- **Resource Monitoring**: Real-time resource tracking

## 🚨 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check build logs
railway service logs

# Validate dependencies
pip check

# Check Python syntax
python -m py_compile src/main.py
```

#### Deployment Failures
```bash
# Check deployment status
railway service status

# View deployment logs
railway service logs --tail 100

# Health check
./scripts/health_check.py --sync
```

#### Runtime Issues
```bash
# Monitor real-time
python scripts/monitoring_dashboard.py

# Check specific service
./scripts/deploy.sh health kickai-production

# View logs
railway service logs --follow
```

### Debug Commands
```bash
# Validate configuration
python scripts/preview_deployment.py -e production

# Check environment variables
railway variables list

# Test connectivity
curl -f https://your-service.railway.app/health

# Monitor resources
railway service status --json | jq '.'
```

## 📚 Additional Resources

### Documentation
- [Railway Documentation](https://docs.railway.app)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Deployment Best Practices](https://docs.python-guide.org/deployment/)

### Monitoring Tools
- [Railway Dashboard](https://railway.app/dashboard)
- [GitHub Actions](https://github.com/features/actions)
- [Custom Monitoring Dashboard](./scripts/monitoring_dashboard.py)

### Support
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: Project README files

## 🎯 Success Metrics

### Deployment Success Rate
- **Target**: >95% successful deployments
- **Measurement**: Automated tracking in CI/CD
- **Improvement**: Rollback analysis and fixes

### Performance Metrics
- **Response Time**: <2 seconds average
- **Uptime**: >99.9% availability
- **Error Rate**: <1% error rate

### Development Velocity
- **Deployment Frequency**: Multiple times per day
- **Lead Time**: <1 hour from commit to production
- **Recovery Time**: <5 minutes for rollback

---

## 🚀 Quick Reference

### Essential Commands
```bash
# Deploy to testing
./scripts/deploy.sh deploy kickai-testing

# Deploy to staging
./scripts/deploy.sh deploy kickai-staging

# Deploy to production
./scripts/deploy.sh deploy kickai-production

# Check health
./scripts/health_check.py --sync

# Monitor services
python scripts/monitoring_dashboard.py

# Preview deployment
python scripts/preview_deployment.py -e production
```

### Emergency Procedures
```bash
# Immediate rollback
railway service rollback <previous_deployment_id>

# Health check
./scripts/health_check.py --sync

# Monitor logs
railway service logs --follow
```

This deployment pipeline ensures high reliability, fast deployments, and easy rollbacks while maintaining security and performance standards. 