# KICKAI - AI-Powered Football Team Management

A Telegram bot for football team management with Firebase backend and AI-powered natural language processing.

## 🚀 Quick Deploy to Railway

### 1. Environment Variables

Set these in your Railway project:

**Firebase Service Account:**
```
FIREBASE_PROJECT_ID=kickai-954c2
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@kickai-954c2.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=123456789012345678901
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40kickai-954c2.iam.gserviceaccount.com
```

**AI Provider (Optional):**
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

# Run locally
python run_telegram_bot.py
```

## 📁 Project Structure

- `run_telegram_bot.py` - Main bot runner
- `src/simple_agentic_handler.py` - AI-powered message processing
- `src/tools/firebase_tools.py` - Firebase database operations
- `src/tools/telegram_tools.py` - Telegram messaging tools

## 🔧 Features

- **Natural Language Processing** - Understand commands like "Create a match against Arsenal"
- **Player Management** - Add, list, and manage team players
- **Fixture Management** - Schedule and track matches
- **Role-Based Access** - Different commands for admins vs members
- **Firebase Backend** - Scalable, real-time database

## 📝 Commands

**For All Users:**
- "List all players"
- "Show upcoming matches"
- "Help" - Show available commands

**For Admins:**
- "Add player John with phone 123456789"
- "Create a match against Arsenal on July 1st at 2pm"
- "Update team name to BP Hatters United" 