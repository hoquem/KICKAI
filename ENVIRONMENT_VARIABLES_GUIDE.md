# Environment Variables Guide

This guide explains the correct environment variable names and their usage in the KICKAI system.

## 🔑 **Critical Variable Name Mismatch**

**IMPORTANT**: There was a mismatch between what the code expects and what our setup scripts were setting.

### **AI API Key Variables**
- ✅ **`GOOGLE_API_KEY`** - This is what the code actually uses
- ❌ **`GOOGLE_AI_API_KEY`** - This was being set but not used by the system

### **Code References**
The following files expect `GOOGLE_API_KEY`:
- `src/core/config.py` (line 204)
- `src/agents/handlers.py` (line 137)
- `src/agents/crew_agents.py` (line 184)

## 🏗️ **Environment Variable Architecture**

### **Testing/Staging Environment**
Uses environment variables for all configuration:

```bash
# AI Configuration
GOOGLE_API_KEY=your_google_api_key_here
AI_PROVIDER=google_gemini
AI_MODEL_NAME=gemini-pro

# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS={"type":"service_account",...}

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_LEADERSHIP_BOT_TOKEN=your_leadership_bot_token_here

# Environment
ENVIRONMENT=testing
RAILWAY_ENVIRONMENT=testing
```

### **Production Environment**
Uses environment variables for infrastructure, Firestore for dynamic configuration:

```bash
# AI Configuration (Required)
GOOGLE_API_KEY=your_google_api_key_here
AI_PROVIDER=google_gemini
AI_MODEL_NAME=gemini-pro

# Firebase Configuration (Required for Firestore access)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS={"type":"service_account",...}

# Environment
ENVIRONMENT=production
RAILWAY_ENVIRONMENT=production

# Bot tokens are stored in Firestore, not environment variables
```

## 🔧 **How the System Determines AI Provider**

The system uses this logic to determine which AI provider to use:

1. **Environment Variable**: `AI_PROVIDER` (defaults to "google_gemini")
2. **API Key Loading**: Based on provider:
   - `google_gemini` → Uses `GOOGLE_API_KEY`
   - `openai` → Uses `OPENAI_API_KEY`
   - `ollama` → Uses `AI_API_KEY` (fallback)

### **Code Flow**
```python
# In src/core/config.py
provider_str = os.getenv("AI_PROVIDER", "google_gemini").lower()
provider = AIProvider(provider_str)

# Load API key based on provider
if provider == AIProvider.GOOGLE_GEMINI:
    api_key = os.getenv("GOOGLE_API_KEY", "")
elif provider == AIProvider.OPENAI:
    api_key = os.getenv("OPENAI_API_KEY", "")
else:
    api_key = os.getenv("AI_API_KEY", "")
```

## 🧹 **Cleanup Required**

### **Redundant Variables to Remove**
The following variables are redundant and should be cleaned up:

**Testing Environment:**
- `GOOGLE_AI_API_KEY` (redundant with `GOOGLE_API_KEY`)
- `GOOGLE_AI_API_KEY_TESTING` (redundant)
- `TELEGRAM_BOT_TOKEN_TESTING` (redundant with `TELEGRAM_BOT_TOKEN`)

**Staging Environment:**
- `GOOGLE_AI_API_KEY` (redundant with `GOOGLE_API_KEY`)
- `GOOGLE_AI_API_KEY_STAGING` (redundant)
- `TELEGRAM_BOT_TOKEN_STAGING` (redundant with `TELEGRAM_BOT_TOKEN`)

### **Cleanup Commands**
```bash
# Remove redundant variables from testing
railway variables --unset GOOGLE_AI_API_KEY --service kickai-testing
railway variables --unset GOOGLE_AI_API_KEY_TESTING --service kickai-testing
railway variables --unset TELEGRAM_BOT_TOKEN_TESTING --service kickai-testing

# Remove redundant variables from staging
railway variables --unset GOOGLE_AI_API_KEY --service kickai-staging
railway variables --unset GOOGLE_AI_API_KEY_STAGING --service kickai-staging
railway variables --unset TELEGRAM_BOT_TOKEN_STAGING --service kickai-staging
```

## 📝 **Updated Setup Scripts**

All setup scripts should be updated to use the correct variable names:

### **Correct Variable Names**
```bash
# AI Configuration
railway variables --set "GOOGLE_API_KEY=your_key" --service kickai-testing
railway variables --set "AI_PROVIDER=google_gemini" --service kickai-testing
railway variables --set "AI_MODEL_NAME=gemini-pro" --service kickai-testing

# Firebase Configuration
railway variables --set "FIREBASE_PROJECT_ID=your_project" --service kickai-testing
railway variables --set "FIREBASE_CREDENTIALS=your_json" --service kickai-testing

# Telegram Configuration
railway variables --set "TELEGRAM_BOT_TOKEN=your_token" --service kickai-testing
railway variables --set "TELEGRAM_LEADERSHIP_BOT_TOKEN=your_token" --service kickai-testing
```

## 🎯 **Summary**

1. **Use `GOOGLE_API_KEY`** for Google Gemini API access
2. **Remove redundant `GOOGLE_AI_API_KEY`** variables
3. **Production uses Firestore** for bot tokens, not environment variables
4. **Testing/Staging uses environment variables** for all configuration
5. **Update all documentation** to reflect correct variable names

This ensures the system can properly access the Google Gemini API and function correctly across all environments. 