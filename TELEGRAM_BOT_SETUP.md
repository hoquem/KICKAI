# KICKAI Telegram Bot Setup Guide

## 🤖 **Multi-Environment Bot Strategy**

This guide covers setting up separate Telegram bots for testing, staging, and production environments in the single project multi-service deployment.

## 📋 **Bot Configuration Overview**

| Environment | Bot Name | Purpose | Users | Data |
|-------------|----------|---------|-------|------|
| **Testing** | Test KICKAI Bot | Development testing | Developers | Mock/Test data |
| **Staging** | Staging KICKAI Bot | Pre-production testing | Test users | Sanitized production data |
| **Production** | KICKAI Bot | Live service | Real users | Live production data |

## 🚀 **Bot Creation Process**

### **Step 1: Create Bots via @BotFather**

#### **Testing Environment Bots**
```bash
# 1. Message @BotFather on Telegram
# 2. Send: /newbot
# 3. Bot name: Test KICKAI Bot
# 4. Bot username: kickai_test_bot
# 5. Save the token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# 6. Create leadership bot
# 7. Send: /newbot  
# 8. Bot name: Test KICKAI Leadership Bot
# 9. Bot username: kickai_test_leadership_bot
# 10. Save the token: 0987654321:ZYXwvuTSRqpONMlkjIHGfedCBA
```

#### **Staging Environment Bots**
```bash
# 1. Message @BotFather on Telegram
# 2. Send: /newbot
# 3. Bot name: Staging KICKAI Bot
# 4. Bot username: kickai_staging_bot
# 5. Save the token: 1122334455:DDDeeeFFFgggHHHiiiJJJkkkLLL

# 6. Create leadership bot
# 7. Send: /newbot
# 8. Bot name: Staging KICKAI Leadership Bot
# 9. Bot username: kickai_staging_leadership_bot
# 10. Save the token: 5544332211:LLLkkkJJJiiiHHHgggFFFeeeDDD
```

#### **Production Environment Bots**
```bash
# 1. Message @BotFather on Telegram
# 2. Send: /newbot
# 3. Bot name: KICKAI Bot
# 4. Bot username: kickai_bot
# 5. Save the token: your-production-bot-token

# 6. Create leadership bot
# 7. Send: /newbot
# 8. Bot name: KICKAI Leadership Bot
# 9. Bot username: kickai_leadership_bot
# 10. Save the token: your-production-leadership-bot-token
```

### **Step 2: Configure Bot Settings**

#### **Testing Bots Configuration**
```bash
# Set bot commands for testing
/setcommands kickai_test_bot
help - Show available commands
test - Run test commands
status - Check bot status
mock_data - Generate mock data

# Set bot commands for testing leadership
/setcommands kickai_test_leadership_bot
help - Show leadership commands
addplayer - Add test player
removesplayer - Remove test player
listplayers - List test players
test_match - Create test match
```

#### **Staging Bots Configuration**
```bash
# Set bot commands for staging
/setcommands kickai_staging_bot
help - Show available commands
status - Check bot status
players - List players
matches - Show matches
profile - View profile

# Set bot commands for staging leadership
/setcommands kickai_staging_leadership_bot
help - Show leadership commands
addplayer - Add player
removeplayer - Remove player
listplayers - List players
creatematch - Create match
updateteam - Update team info
```

#### **Production Bots Configuration**
```bash
# Set bot commands for production
/setcommands kickai_bot
help - Show available commands
status - Check bot status
players - List players
matches - Show matches
profile - View profile
register - Register as player

# Set bot commands for production leadership
/setcommands kickai_leadership_bot
help - Show leadership commands
addplayer - Add player
removeplayer - Remove player
listplayers - List players
creatematch - Create match
updateteam - Update team info
generateinvite - Generate player invite
```

## 🔧 **Environment Variable Configuration**

### **Testing Environment Variables**
```bash
# Set in Railway service: kickai-testing
railway variables set TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz --service kickai-testing
railway variables set TELEGRAM_LEADERSHIP_BOT_TOKEN=0987654321:ZYXwvuTSRqpONMlkjIHGfedCBA --service kickai-testing
railway variables set TELEGRAM_BOT_USERNAME=kickai_test_bot --service kickai-testing
railway variables set TELEGRAM_LEADERSHIP_BOT_USERNAME=kickai_test_leadership_bot --service kickai-testing
```

### **Staging Environment Variables**
```bash
# Set in Railway service: kickai-staging
railway variables set TELEGRAM_BOT_TOKEN=1122334455:DDDeeeFFFgggHHHiiiJJJkkkLLL --service kickai-staging
railway variables set TELEGRAM_LEADERSHIP_BOT_TOKEN=5544332211:LLLkkkJJJiiiHHHgggFFFeeeDDD --service kickai-staging
railway variables set TELEGRAM_BOT_USERNAME=kickai_staging_bot --service kickai-staging
railway variables set TELEGRAM_LEADERSHIP_BOT_USERNAME=kickai_staging_leadership_bot --service kickai-staging
```

### **Production Environment Variables**
```bash
# Set in Railway service: kickai-production
railway variables set TELEGRAM_BOT_TOKEN=your-production-bot-token --service kickai-production
railway variables set TELEGRAM_LEADERSHIP_BOT_TOKEN=your-production-leadership-bot-token --service kickai-production
railway variables set TELEGRAM_BOT_USERNAME=kickai_bot --service kickai-production
railway variables set TELEGRAM_LEADERSHIP_BOT_USERNAME=kickai_leadership_bot --service kickai-production
```

## 🧪 **Testing Bot Features**

### **Testing Environment Bot Commands**
```python
# Testing-specific commands
@bot.command('test')
async def test_command(update, context):
    """Run test commands in testing environment."""
    await update.message.reply_text("🧪 Testing environment active!")

@bot.command('mock_data')
async def mock_data_command(update, context):
    """Generate mock data for testing."""
    # Generate test players, matches, etc.
    await update.message.reply_text("📊 Mock data generated!")

@bot.command('test_match')
async def test_match_command(update, context):
    """Create a test match."""
    # Create test match with mock data
    await update.message.reply_text("⚽ Test match created!")
```

### **Staging Environment Bot Features**
```python
# Staging-specific features
@bot.command('staging_info')
async def staging_info_command(update, context):
    """Show staging environment information."""
    await update.message.reply_text("🔄 Staging environment - testing with real data")

@bot.command('sync_production')
async def sync_production_command(update, context):
    """Sync sanitized data from production."""
    # Sync sanitized production data
    await update.message.reply_text("🔄 Synced sanitized production data")
```

## 🔒 **Security Considerations**

### **Bot Token Security**
- ✅ Store tokens in Railway environment variables
- ✅ Never commit tokens to Git
- ✅ Use different tokens for each environment
- ✅ Rotate tokens regularly
- ✅ Monitor bot usage and activity

### **Access Control**
```python
# Environment-based access control
def check_environment_access(update, context):
    """Check if user has access to current environment."""
    environment = os.getenv('ENVIRONMENT', 'unknown')
    user_id = update.effective_user.id
    
    if environment == 'testing':
        # Only allow developers in testing
        return user_id in TESTING_DEVELOPERS
    elif environment == 'staging':
        # Allow test users in staging
        return user_id in STAGING_TEST_USERS
    else:  # production
        # Allow all users in production
        return True
```

## 📊 **Bot Monitoring**

### **Health Check Integration**
```python
@app.route('/health')
def health_check():
    """Enhanced health check with bot status."""
    try:
        # Check bot connectivity
        bot_status = check_telegram_bot_connection()
        leadership_bot_status = check_leadership_bot_connection()
        
        return jsonify({
            'status': 'healthy',
            'environment': os.getenv('ENVIRONMENT', 'unknown'),
            'bots': {
                'main_bot': bot_status,
                'leadership_bot': leadership_bot_status
            },
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500
```

### **Bot Usage Analytics**
```python
# Track bot usage per environment
def track_bot_usage(update, context):
    """Track bot usage for analytics."""
    environment = os.getenv('ENVIRONMENT', 'unknown')
    user_id = update.effective_user.id
    command = update.message.text
    
    # Log usage to analytics service
    log_usage(environment, user_id, command)
```

## 🚀 **Deployment Checklist**

### **Pre-Deployment**
- [ ] Create all bots via @BotFather
- [ ] Configure bot commands for each environment
- [ ] Set up bot tokens in Railway environment variables
- [ ] Test bot connectivity in each environment
- [ ] Configure webhooks (if using webhooks)

### **Post-Deployment**
- [ ] Verify bot responses in each environment
- [ ] Test bot commands and features
- [ ] Monitor bot health checks
- [ ] Set up bot usage analytics
- [ ] Configure bot monitoring and alerting

### **Ongoing Maintenance**
- [ ] Monitor bot performance and usage
- [ ] Update bot commands as needed
- [ ] Rotate bot tokens regularly
- [ ] Review and update access controls
- [ ] Monitor for security issues

## 🎯 **Best Practices**

### **Bot Management**
1. **Separate Bots**: Use different bots for each environment
2. **Clear Naming**: Use descriptive bot names and usernames
3. **Command Organization**: Organize commands by environment needs
4. **Security**: Implement proper access controls
5. **Monitoring**: Track bot usage and performance

### **Environment Isolation**
1. **Data Separation**: Keep environment data completely separate
2. **User Access**: Control user access per environment
3. **Feature Testing**: Test new features in testing/staging first
4. **Rollback Plan**: Have rollback procedures for each environment

---

**Last Updated**: December 19, 2024  
**Version**: 1.0.0  
**Status**: 📋 **IMPLEMENTATION READY** 