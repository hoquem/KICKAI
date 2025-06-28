# ✅ KICKAI Deployment Checklist

## 🏠 Local Development Setup

### **Prerequisites**
- [ ] Python 3.8+ installed
- [ ] Ollama installed and running
- [ ] `.env` file configured
- [ ] Supabase project created

### **Environment Variables (.env)**
```bash
# Development mode
RAILWAY_ENVIRONMENT=development

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Telegram (optional for local testing)
TELEGRAM_BOT_TOKEN=your_bot_token
```

### **Setup Steps**
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Start Ollama: `ollama serve`
- [ ] Pull model: `ollama pull llama3.1:8b-instruct-q4_0`
- [ ] Test configuration: `python test_hybrid_config.py`
- [ ] Run bot: `python run_telegram_bot.py`

### **Testing**
- [ ] Test database connection: `python test_database_setup.py`
- [ ] Test CrewAI: `python test_crewai_ollama_correct.py`
- [ ] Test bot functionality: `python check_bot_status.py`
- [ ] Test AI commands in Telegram

## 🚀 Railway Production Setup

### **Prerequisites**
- [ ] Railway account created
- [ ] GitHub repository connected
- [ ] Google AI API key obtained
- [ ] Supabase project ready

### **Environment Variables (Railway)**
```bash
# Production mode
RAILWAY_ENVIRONMENT=production

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# AI Provider
GOOGLE_API_KEY=your_google_ai_api_key

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
```

### **Deployment Steps**
- [ ] Push code to GitHub: `git push origin main`
- [ ] Railway auto-deploys from main branch
- [ ] Check deployment logs in Railway dashboard
- [ ] Verify environment variables are set
- [ ] Test production deployment

### **Post-Deployment**
- [ ] Test bot functionality
- [ ] Monitor Railway logs
- [ ] Check Google AI usage
- [ ] Verify Supabase connections
- [ ] Test with real users

## 🔧 Configuration Testing

### **Local Development**
```bash
python test_hybrid_config.py
# Should show: AI Provider: ollama, Environment: development
```

### **Production Mode**
```bash
RAILWAY_ENVIRONMENT=production python test_hybrid_config.py
# Should show: AI Provider: google, Environment: production
```

## 📊 Monitoring Checklist

### **Local Development**
- [ ] Ollama is running: `ollama ps`
- [ ] Model is available: `ollama list`
- [ ] Bot responds to commands
- [ ] Database operations work
- [ ] No errors in logs

### **Railway Production**
- [ ] Deployment successful
- [ ] No 500 errors in logs
- [ ] Google AI API key valid
- [ ] Supabase connections working
- [ ] Telegram bot responding
- [ ] Memory usage reasonable
- [ ] Response times acceptable

## 🚨 Troubleshooting

### **Local Issues**
- [ ] Ollama not running: `ollama serve`
- [ ] Model missing: `ollama pull llama3.1:8b-instruct-q4_0`
- [ ] Environment variables: Check `.env` file
- [ ] Dependencies: `pip install -r requirements.txt`

### **Railway Issues**
- [ ] Environment variables: Check Railway dashboard
- [ ] Dependencies: Check `requirements.txt`
- [ ] Logs: Check Railway deployment logs
- [ ] API keys: Verify Google AI key is valid
- [ ] Database: Check Supabase connection

## 🎯 Success Criteria

### **Local Development**
- ✅ Bot responds to commands
- ✅ AI generates relevant responses
- ✅ Database operations work
- ✅ No errors in console
- ✅ Fast response times (< 3 seconds)

### **Railway Production**
- ✅ Deployment successful
- ✅ Bot responds to commands
- ✅ AI generates relevant responses
- ✅ Database operations work
- ✅ No 500 errors
- ✅ Response times < 1 second
- ✅ Handles multiple users

## 💰 Cost Monitoring

### **Development**
- [ ] Ollama: Free (local)
- [ ] Supabase: Free tier
- [ ] Total: $0/month

### **Production**
- [ ] Google AI: Monitor usage
- [ ] Railway: ~$5/month
- [ ] Supabase: Free tier
- [ ] Set up cost alerts
- [ ] Monitor monthly spending

## 🔄 Switching Environments

### **Local → Production**
1. Set `RAILWAY_ENVIRONMENT=production`
2. Add `GOOGLE_API_KEY`
3. Deploy to Railway
4. Test production deployment

### **Production → Local**
1. Set `RAILWAY_ENVIRONMENT=development`
2. Remove `GOOGLE_API_KEY`
3. Start Ollama locally
4. Test local deployment

---

## 🎉 Ready for Deployment!

Once you've completed this checklist:

1. **Local Development**: You can develop and test freely
2. **Railway Production**: Your app is ready for real users
3. **Monitoring**: You can track performance and costs
4. **Scaling**: Your app can handle growth automatically

The hybrid approach gives you the best of both worlds! 🚀
