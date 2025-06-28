# 🚀 Railway Deployment Guide for KICKAI

This guide will help you deploy the KICKAI Telegram Bot to Railway for production testing with real users.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your KICKAI code should be in a GitHub repository
3. **Environment Variables**: All required environment variables configured

## 🔧 Environment Variables Setup

Set these environment variables in Railway:

### Required Variables:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
GOOGLE_API_KEY=your_google_ai_api_key
```

### Optional Variables:
```
RAILWAY_ENVIRONMENT=production
PORT=8080
```

**Note**: The bot token is retrieved from the database, so `TELEGRAM_BOT_TOKEN` is not needed in environment variables.

## 🚀 Deployment Steps

### Step 1: Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your KICKAI repository

### Step 2: Configure Environment Variables

1. In your Railway project, go to "Variables" tab
2. Add all required environment variables from the list above
3. Save the variables

### Step 3: Deploy

1. Railway will automatically detect the Python project
2. The deployment will use the `railway.json` configuration
3. The bot will start with: `python run_telegram_bot.py`

### Step 4: Monitor Deployment

1. Check the "Deployments" tab for build status
2. Monitor logs in the "Logs" tab
3. Verify health check at: `https://your-app.railway.app/health`

## 🔍 Testing with Real Users

### Pre-Deployment Checklist:

1. ✅ **Database Setup**: Ensure all tables are created in Supabase
2. ✅ **Bot Configuration**: Verify bot is active in `team_bots` table
3. ✅ **Team Members**: Add test users to `team_members` table
4. ✅ **Chat Groups**: Ensure Telegram groups are configured

### Test Users Setup:

1. **Add Team Members to Database**:
   ```sql
   INSERT INTO team_members (team_id, telegram_user_id, username, role, is_active)
   VALUES 
   ('0854829d-445c-4138-9fd3-4db562ea46ee', 123456789, 'testuser1', 'player', true),
   ('0854829d-445c-4138-9fd3-4db562ea46ee', 987654321, 'testuser2', 'captain', true);
   ```

2. **Test Commands**:
   - `/help` - Should show available commands
   - `/status` - Should show team status
   - `/tasks` - Should list current tasks

### Monitoring Commands:

1. **Check Bot Status**:
   ```bash
   curl https://your-app.railway.app/health
   ```

2. **View Logs**:
   - Railway Dashboard → Logs tab
   - Monitor for errors and successful message processing

## 🛠️ Troubleshooting

### Common Issues:

1. **409 Conflict Errors**:
   - Run webhook cleanup: `python cleanup_webhook.py`
   - Check for multiple bot instances

2. **Database Connection Issues**:
   - Verify `SUPABASE_URL` and `SUPABASE_KEY`
   - Check Supabase project status

3. **Bot Not Responding**:
   - Check Railway logs for errors
   - Verify bot token in database
   - Test bot connection locally first

### Debug Commands:

```bash
# Check bot status
python check_bot_status.py

# Clean webhook
python cleanup_webhook.py

# Test database connection
python test_database_setup.py
```

## 📊 Monitoring & Analytics

### Railway Metrics:
- CPU/Memory usage
- Request logs
- Error rates
- Response times

### Bot Analytics:
- Command usage logs in `command_logs` table
- User interaction patterns
- Error tracking

## 🔄 Continuous Deployment

Railway will automatically redeploy when you push to your main branch. To disable:

1. Go to Railway project settings
2. Disable "Auto Deploy"

## 🚨 Production Considerations

1. **Scaling**: Railway can auto-scale based on traffic
2. **Backups**: Ensure Supabase has regular backups
3. **Monitoring**: Set up alerts for bot downtime
4. **Security**: Review environment variable security

## 📞 Support

If you encounter issues:

1. Check Railway logs first
2. Verify environment variables
3. Test locally to isolate issues
4. Check Supabase dashboard for database issues

## 🎯 Next Steps

After successful deployment:

1. **Add Real Users**: Invite team members to Telegram groups
2. **Test Commands**: Verify all bot commands work
3. **Monitor Usage**: Track user engagement
4. **Scale Up**: Add more teams as needed

---

**Happy Deploying! 🚀** 