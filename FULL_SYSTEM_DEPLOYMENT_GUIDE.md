# 🚀 Full KICKAI System Deployment Guide

This guide will help you deploy the complete KICKAI system including CrewAI agents to Railway for production testing with real users.

## 🎯 What's Included

The full KICKAI system includes:

### 🤖 **AI Agents (CrewAI)**
- **Team Manager Agent**: Strategic planning and team coordination
- **Player Coordinator Agent**: Player management and availability tracking
- **Match Analyst Agent**: Performance analysis and tactical insights
- **Communication Specialist Agent**: Team communications and announcements

### 🛠️ **Tools & Integrations**
- **Supabase Database**: Player, fixture, and team data management
- **Telegram Bot**: Dual-channel messaging (team + leadership groups)
- **Google AI**: Natural language processing and AI capabilities
- **Search Tools**: Web search and information gathering
- **Payment Integration**: Collectiv payment system support

### 📊 **Monitoring & Health**
- **Health Check Server**: Railway monitoring endpoint
- **Command Logging**: Audit trail for all bot interactions
- **Error Tracking**: Comprehensive error logging and recovery

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
OLLAMA_BASE_URL=http://localhost:11434
```

## 🚀 Deployment Steps

### Step 1: Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your KICKAI repository: `hoquem/KICKAI`

### Step 2: Configure Environment Variables

1. In your Railway project, go to "Variables" tab
2. Add all required environment variables from the list above
3. Save the variables

### Step 3: Deploy Full System

1. Railway will automatically detect the Python project
2. The deployment will use the `railway.json` configuration
3. The full system will start with: `python railway_main.py`

### Step 4: Monitor Deployment

1. Check the "Deployments" tab for build status
2. Monitor logs in the "Logs" tab
3. Verify health check at: `https://your-app.railway.app/health`

## 🧠 CrewAI Agent System

### Agent Capabilities:

#### **Team Manager Agent**
- Strategic team planning
- Fixture coordination
- Team performance analysis
- Leadership communication

#### **Player Coordinator Agent**
- Player availability tracking
- Squad selection assistance
- Player communication
- Payment reminders

#### **Match Analyst Agent**
- Performance analysis
- Tactical insights
- Match preparation
- Post-match reviews

#### **Communication Specialist Agent**
- Team announcements
- Poll creation
- Message coordination
- Information distribution

### Agent Tools Available:
- **Player Management**: Add, update, list players
- **Fixture Management**: Schedule, update, track matches
- **Telegram Messaging**: Send messages, polls, announcements
- **Search Tools**: Web search for information
- **Database Tools**: Direct database operations

## 🔍 Testing with Real Users

### Pre-Deployment Checklist:

1. ✅ **Database Setup**: All tables created in Supabase
2. ✅ **Bot Configuration**: Bot active in `team_bots` table
3. ✅ **Team Members**: Test users added to `team_members` table
4. ✅ **Chat Groups**: Telegram groups configured
5. ✅ **AI Models**: Google AI API configured

### Test Commands for AI Agents:

#### **Player Management**:
```
"Add a new player named John Smith with phone 123456789"
"List all active players in the team"
"Update player John Smith's phone number to 987654321"
```

#### **Fixture Management**:
```
"Schedule a match against Rivals FC on Sunday at 2pm"
"List all upcoming fixtures"
"Update the match venue to Central Park"
```

#### **Team Communication**:
```
"Send a message to the team about the next match"
"Create a poll asking about availability for Sunday's match"
"Announce the squad for the upcoming fixture"
```

#### **Analysis & Insights**:
```
"Analyze our last match performance"
"Suggest improvements based on recent games"
"Provide tactical advice for the next match"
```

### Monitoring Commands:

1. **Check System Health**:
   ```bash
   curl https://your-app.railway.app/health
   ```

2. **View Agent Logs**:
   - Railway Dashboard → Logs tab
   - Look for CrewAI agent activity

3. **Check Command Logs**:
   - Supabase Dashboard → `command_logs` table
   - Monitor agent interactions

## 🛠️ Troubleshooting

### Common Issues:

1. **CrewAI Import Errors**:
   - Check `requirements.txt` has all dependencies
   - Verify CrewAI version compatibility

2. **AI Model Issues**:
   - Verify Google AI API key is valid
   - Check API quota and limits

3. **Database Connection Issues**:
   - Verify `SUPABASE_URL` and `SUPABASE_KEY`
   - Check Supabase project status

4. **Agent Tool Errors**:
   - Check tool permissions in Supabase
   - Verify team isolation is working

### Debug Commands:

```bash
# Test CrewAI setup
python test_crewai_ollama_correct.py

# Test database connection
python test_database_setup.py

# Test bot status
python check_bot_status.py

# Test multi-team isolation
python test_multi_team.py
```

## 📊 Monitoring & Analytics

### Railway Metrics:
- CPU/Memory usage
- Request logs
- Error rates
- Response times

### AI Agent Analytics:
- Agent interaction logs in `command_logs` table
- Tool usage patterns
- Response quality metrics
- Error tracking

### Bot Analytics:
- Command usage patterns
- User engagement metrics
- Response times
- Error rates

## 🔄 Continuous Deployment

Railway will automatically redeploy when you push to your main branch. The full system includes:

1. **Health Monitoring**: Automatic health checks
2. **Error Recovery**: Automatic restart on failures
3. **Logging**: Comprehensive logging for debugging
4. **Scaling**: Automatic scaling based on traffic

## 🚨 Production Considerations

1. **AI Model Costs**: Monitor Google AI API usage
2. **Database Performance**: Monitor Supabase query performance
3. **Agent Memory**: Monitor CrewAI memory usage
4. **Security**: Review environment variable security
5. **Backups**: Ensure Supabase has regular backups

## 📞 Support

If you encounter issues:

1. Check Railway logs first
2. Verify environment variables
3. Test locally to isolate issues
4. Check Supabase dashboard for database issues
5. Review CrewAI agent logs

## 🎯 Next Steps

After successful deployment:

1. **Add Real Users**: Invite team members to Telegram groups
2. **Test AI Commands**: Verify all agent commands work
3. **Monitor Performance**: Track agent response times and quality
4. **Scale Up**: Add more teams and expand functionality
5. **Optimize**: Fine-tune agent prompts and tools

## 🔧 Advanced Configuration

### Customizing Agents:
- Edit `src/agents.py` to modify agent roles and goals
- Update system prompts for better responses
- Add new tools to agent capabilities

### Adding New Teams:
- Use the multi-team manager for automatic team isolation
- Each team gets its own agents and tools
- Complete isolation between teams

### Performance Optimization:
- Monitor agent response times
- Optimize tool usage patterns
- Fine-tune LLM parameters

---

**Happy Deploying! 🚀**

The full KICKAI system with CrewAI agents is now ready for production testing with real users! 