# Environment Variables Guide

This guide explains the correct environment variable names and their usage in the KICKAI system.

## 🧠 **Advanced Memory System Configuration**

The advanced memory system can be configured using the following environment variables:

```bash
# Enable/Disable Advanced Memory System
ENABLE_ADVANCED_MEMORY=true  # Default: true

# Memory Retention Settings
MEMORY_RETENTION_DAYS=30     # Default: 30 days
MAX_CONVERSATION_HISTORY=50  # Default: 50 conversations
MAX_EPISODIC_MEMORY=1000     # Default: 1000 items

# Agentic Memory Features
AGENTIC_MEMORY_ENABLED=true  # Default: true
AGENTIC_PERFORMANCE_MONITORING=true  # Default: true
AGENTIC_ANALYTICS_ENABLED=true       # Default: true
```

### **Memory System Features**
- **Short-term Memory**: Stores recent conversations and context
- **Long-term Memory**: Stores user preferences and team patterns  
- **Episodic Memory**: Stores task execution history
- **Semantic Memory**: Stores learned patterns and rules
- **Pattern Learning**: Automatically learns from user interactions
- **User Preference Learning**: Adapts responses based on user preferences

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

## 💳 **Payment Configuration**

The payment system uses Collectiv for payment processing and can be configured using the following environment variables:

### **Collectiv Integration**
```bash
# Collectiv API Configuration
COLLECTIV_API_KEY=your_collectiv_api_key_here
COLLECTIV_BASE_URL=https://api.collectiv.com
COLLECTIV_WEBHOOK_SECRET=your_webhook_secret_here

# Payment Settings
DEFAULT_CURRENCY=GBP
PAYMENT_TIMEOUT=30
PAYMENT_RETRY_ATTEMPTS=3
```

### **Payment System Features**
- **Match Fee Payments**: Automated payment requests for match fees
- **Membership Fee Payments**: Recurring membership fee collection
- **Fine Payments**: Fine collection with due dates
- **Payment Status Tracking**: Real-time payment status updates
- **Payment History**: Complete payment history and analytics
- **Flexible Integration**: Easy to switch payment providers

### **Payment Commands**
The system provides the following payment commands:
- `/create_match_fee` - Create match fee payment
- `/create_membership_fee` - Create membership fee payment
- `/create_fine` - Create fine payment
- `/payment_status` - Check payment status
- `/pending_payments` - List pending payments
- `/payment_history` - View payment history
- `/payment_stats` - View payment statistics
- `/payment_help` - Get payment help

### **Environment-Specific Configuration**
- **Development**: Uses mock payment service for testing
- **Testing**: Uses mock payment service with simulated payments
- **Production**: Uses real Collectiv integration 