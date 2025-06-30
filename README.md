# KICKAI - AI-Powered Football Team Management

**Status:** ✅ **PRODUCTION READY** - v1.5.0  
**Deployment:** 🚀 **Live on Railway**  
**AI Provider:** 🤖 **Google Gemini (Production)**

A Telegram bot for football team management with Firebase backend and AI-powered natural language processing.

## 🎉 **Production Status**

KICKAI is now **fully operational** in production with **Phase 1 features enabled**:
- ✅ **Stable Railway deployment**
- ✅ **Google AI (Gemini) integration**
- ✅ **Firebase Firestore database**
- ✅ **8-agent CrewAI system**
- ✅ **Natural language processing**
- ✅ **Health monitoring**
- ✅ **Intelligent Routing System** - LLM-powered agent selection
- ✅ **Dynamic Task Decomposition** - Smart task breakdown
- ✅ **Advanced Memory System** - Persistent conversation history
- ✅ **Performance Monitoring** - Real-time analytics

## 🚀 Quick Deploy to Railway

### 1. Environment Variables

Set these in your Railway project:

**Firebase Service Account:**
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com
```

**AI Provider:**
```
GOOGLE_API_KEY=your_google_api_key_here
```

**Environment:**
```
ENVIRONMENT=production
```

### 2. Deploy

1. Connect Railway to this GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main

### 3. Test

Send "help" to your Telegram bot to verify it's working.

## 🏗️ Local Development

```bash
# Install local dependencies (includes CrewAI and Ollama)
pip install -r requirements-local.txt

# Test imports
python test_railway_imports.py

# Run locally
python run_telegram_bot.py
```

## 📁 Project Structure

- `run_telegram_bot.py` - Main bot runner
- `railway_main.py` - Railway deployment entry point
- `src/simple_agentic_handler.py` - AI-powered message processing
- `src/tools/firebase_tools.py` - Firebase database operations
- `src/tools/telegram_tools.py` - Telegram messaging tools
- `src/telegram_command_handler.py` - Command parsing and routing

## 🔧 Features

- **Natural Language Processing** - Understand commands like "Create a match against Arsenal"
- **Player Management** - Add, list, and manage team players
- **Fixture Management** - Schedule and track matches with human-readable IDs
- **Role-Based Access** - Different commands for admins vs members
- **Firebase Backend** - Scalable, real-time database
- **AI-Powered Analysis** - 8-agent CrewAI system for intelligent responses
- **Health Monitoring** - Railway health checks and logging

## 📝 Commands

**For All Users:**
- "List all players"
- "Show upcoming matches"
- "Help" - Show available commands
- "Status" - Check bot status

**For Admins:**
- "Add player John with phone 123456789"
- "Create a match against Arsenal on July 1st at 2pm"
- "Update team name to BP Hatters United"

## 🎯 **Recent Achievements**

- ✅ **Resolved langchain_google_genai import issues**
- ✅ **Fixed threading and signal handling**
- ✅ **Established stable Railway deployment**
- ✅ **Implemented comprehensive health monitoring**
- ✅ **Achieved production-ready status**

## 🚀 **Ready for Next Features**

The system is now stable and ready for implementing:
- Enhanced match management
- Player analytics
- Advanced AI features
- Communication tools

See `PRODUCTION_STATUS.md` for detailed status information. 