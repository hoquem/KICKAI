# KICKAI Deployment Guide

## 🚀 Quick Start

This guide will help you deploy KICKAI to Railway with comprehensive monitoring.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Account**: For repository hosting
3. **Supabase Project**: Already set up with team_bots table
4. **Telegram Bot**: Already configured and stored in Supabase

## 🛠️ Step 1: Prepare Your Environment

### 1.1 Install Railway CLI
```bash
npm install -g @railway/cli
```

### 1.2 Login to Railway
```bash
railway login
```

### 1.3 Verify Your Setup
```bash
# Check if all files are present
ls -la Procfile railway.json src/main.py src/monitoring.py
```

## 🚀 Step 2: Deploy to Railway

### 2.1 Initialize Railway Project
```bash
# Navigate to your KICKAI directory
cd /path/to/KICKAI

# Initialize Railway project
railway init
```

### 2.2 Set Environment Variables
```bash
# Set required environment variables
railway variables set SUPABASE_URL="your_supabase_url"
railway variables set SUPABASE_KEY="your_supabase_key"
railway variables set ENVIRONMENT="testing"
railway variables set LOG_LEVEL="INFO"
railway variables set MONITORING_ENABLED="true"

# Note: TELEGRAM_BOT_TOKEN is fetched from Supabase database per team
# No need to set it as environment variable
```

### 2.3 Deploy
```bash
# Deploy to Railway
railway up
```

### 2.4 Get Your Deployment URL
```bash
railway status
```

## 📊 Step 3: Verify Deployment

### 3.1 Check Health Endpoint
```bash
# Replace with your actual URL
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "bot_status": "running",
  "system_metrics": {...},
  "app_metrics": {...},
  "environment": "testing"
}
```

### 3.2 Check Metrics Endpoint
```bash
curl https://your-app.railway.app/metrics
```

### 3.3 Check Bot Status
```bash
curl https://your-app.railway.app/bot/status
```

## 🔧 Step 4: Configure Monitoring

### 4.1 Set Up Logs
```bash
# View real-time logs
railway logs

# View logs for specific service
railway logs --service web
railway logs --service bot
railway logs --service monitor
```

### 4.2 Monitor System Resources
Railway provides built-in monitoring:
- Go to your Railway dashboard
- Click on your project
- View the "Metrics" tab

### 4.3 Set Up Alerts (Optional)
```bash
# Railway doesn't have built-in alerts, but you can:
# 1. Use the health check script
# 2. Set up external monitoring (UptimeRobot, etc.)
# 3. Use Railway's webhook notifications
```

## 🧪 Step 5: Test Your Deployment

### 5.1 Test Bot Functionality
1. Send a message to your Telegram bot
2. Check if it responds correctly
3. Verify commands work in both groups

### 5.2 Test Monitoring
```bash
# Run health check script
python scripts/health_check.py --urls https://your-app.railway.app

# Run continuous monitoring
python scripts/health_check.py --urls https://your-app.railway.app --continuous --interval 300
```

### 5.3 Test Bot Restart
```bash
# Test bot restart endpoint
curl -X POST https://your-app.railway.app/bot/restart
```

## 🔄 Step 6: Set Up CI/CD (Optional)

### 6.1 Configure GitHub Secrets
In your GitHub repository settings, add these secrets:
- `RAILWAY_TOKEN`: Your Railway API token
- `SUPABASE_URL`: Your Supabase URL
- `SUPABASE_KEY`: Your Supabase key

### 6.2 Push to Main Branch
```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

The GitHub Actions workflow will automatically deploy to Railway.

## 📈 Step 7: Monitor Performance

### 7.1 Key Metrics to Watch
- **System Health**: CPU, Memory, Disk usage
- **Bot Performance**: Response times, success rates
- **AI Quality**: Response relevance, user satisfaction
- **Uptime**: Service availability

### 7.2 Monitoring Dashboard
Access your monitoring data at:
- Health: `https://your-app.railway.app/health`
- Metrics: `https://your-app.railway.app/metrics`
- Bot Status: `https://your-app.railway.app/bot/status`

## 🚨 Troubleshooting

### Common Issues

#### 1. Bot Not Responding
```bash
# Check bot status
curl https://your-app.railway.app/bot/status

# Check logs
railway logs --service bot

# Restart bot
curl -X POST https://your-app.railway.app/bot/restart
```

#### 2. High Resource Usage
```bash
# Check system metrics
curl https://your-app.railway.app/metrics

# Scale up if needed
railway scale --service web --count 2
```

#### 3. Environment Variables Not Set
```bash
# List all variables
railway variables

# Set missing variables
railway variables set VARIABLE_NAME="value"
```

#### 4. Deployment Fails
```bash
# Check build logs
railway logs --service web

# Verify Procfile
cat Procfile

# Check requirements.txt
cat requirements.txt
```

### Debug Commands
```bash
# SSH into Railway container (if available)
railway shell

# View detailed logs
railway logs --follow

# Check service status
railway status --json
```

## 🔒 Security Considerations

### 1. Environment Variables
- Never commit sensitive data to Git
- Use Railway's environment variable management
- Rotate tokens regularly

### 2. Access Control
- Limit who has access to Railway dashboard
- Use different tokens for different environments
- Monitor access logs

### 3. Data Protection
- Ensure Supabase is properly configured
- Use HTTPS for all communications
- Implement proper error handling

## 📊 Performance Optimization

### 1. Resource Management
- Monitor memory usage
- Optimize Python imports
- Use connection pooling

### 2. Response Times
- Cache frequently used data
- Optimize database queries
- Use async operations where possible

### 3. Scaling
- Start with single instance
- Scale up based on usage
- Monitor costs

## 🔄 Production Deployment

### 1. Create Production Environment
```bash
# Create new Railway project for production
railway init --name kickai-production

# Set production environment variables
railway variables set ENVIRONMENT="production"
railway variables set LOG_LEVEL="WARNING"
```

### 2. Set Up Custom Domain (Optional)
```bash
# Add custom domain
railway domain

# Configure DNS
# Point your domain to Railway's provided CNAME
```

### 3. Set Up Monitoring
- Configure external monitoring (UptimeRobot, Pingdom)
- Set up alerting for downtime
- Monitor response times and error rates

## 📝 Maintenance

### Regular Tasks
1. **Weekly**: Review logs and metrics
2. **Monthly**: Update dependencies
3. **Quarterly**: Review security settings
4. **As needed**: Scale resources

### Backup Strategy
- Supabase handles database backups
- Code is backed up in GitHub
- Environment variables are in Railway

## 🎯 Success Metrics

### Technical Metrics
- Uptime > 99.9%
- Response time < 2 seconds
- Error rate < 1%
- Bot response success > 95%

### Business Metrics
- User engagement
- Command usage patterns
- AI response quality scores
- User satisfaction

## 📞 Support

### Railway Support
- Documentation: [docs.railway.app](https://docs.railway.app)
- Discord: [discord.gg/railway](https://discord.gg/railway)
- Email: support@railway.app

### KICKAI Support
- GitHub Issues: [github.com/your-repo/issues](https://github.com/your-repo/issues)
- Documentation: Check project README
- Community: Telegram group

## 🎉 Congratulations!

Your KICKAI deployment is now live with comprehensive monitoring! 

**Next Steps:**
1. Test all bot functionality
2. Set up monitoring alerts
3. Configure production environment
4. Train your team on monitoring
5. Plan for scaling

Remember to monitor your deployment regularly and adjust resources as needed. 