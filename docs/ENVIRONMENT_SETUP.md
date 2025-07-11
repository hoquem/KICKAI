# Environment Variables Setup Guide

This guide explains how to set up environment variables for KICKAI securely, keeping sensitive data out of source control.

## 🔒 Security First

**IMPORTANT**: Never commit `.env` files or any files containing secrets to version control. This includes:
- `TELEGRAM_BOT_TOKEN`
- `GOOGLE_API_KEY`
- `OPENAI_API_KEY`
- Firebase credentials
- Session strings

## 📋 Required Environment Variables

### Core Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | ✅ | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `TELEGRAM_BOT_USERNAME` | Bot username (without @) | ✅ | `my_bot` |
| `TELEGRAM_MAIN_CHAT_ID` | Main chat ID | ✅ | `-1001234567890` |
| `TELEGRAM_LEADERSHIP_CHAT_ID` | Leadership chat ID | ✅ | `-1001234567891` |
| `FIRESTORE_PROJECT_ID` | Firebase project ID | ✅ | `my-project-123` |
| `FIREBASE_CREDENTIALS_FILE` | Path to Firebase credentials | ✅ | `./credentials/firebase_credentials.json` |

### AI Provider Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `AI_PROVIDER` | AI provider to use | ✅ | `google_gemini` |
| `GOOGLE_API_KEY` | Google API key (for Gemini) | ✅ | `AIzaSy...` |
| `OPENAI_API_KEY` | OpenAI API key (if using OpenAI) | ⚠️ | `sk-...` |
| `AI_MODEL_NAME` | AI model name | ✅ | `gemini-pro` |

### Optional Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `ENVIRONMENT` | Environment name | ❌ | `development` |
| `DEBUG` | Debug mode | ❌ | `true` |
| `LOG_LEVEL` | Logging level | ❌ | `INFO` |
| `DEFAULT_TEAM_ID` | Default team ID | ❌ | `KAI` |
| `PAYMENT_ENABLED` | Enable payment system | ❌ | `false` |

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

Run the setup wizard:

```bash
python setup_local_environment.py
```

This will guide you through the setup process and generate the commands to set your environment variables.

### Option 2: Manual Setup

1. Copy the template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values:
   ```bash
   nano .env
   ```

3. Set environment variables from the file:
   ```bash
   export $(cat .env | xargs)
   ```

## 🔧 Setting Environment Variables

### macOS/Linux

#### Temporary (Current Session Only)
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export GOOGLE_API_KEY="your_google_api_key_here"
export FIRESTORE_PROJECT_ID="your_project_id"
# ... add other variables
```

#### Permanent (Add to Shell Profile)
Add to `~/.bashrc`, `~/.zshrc`, or `~/.profile`:

```bash
# KICKAI Environment Variables
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export GOOGLE_API_KEY="your_google_api_key_here"
export FIRESTORE_PROJECT_ID="your_project_id"
export TELEGRAM_BOT_USERNAME="your_bot_username"
export TELEGRAM_MAIN_CHAT_ID="-1001234567890"
export TELEGRAM_LEADERSHIP_CHAT_ID="-1001234567891"
export FIREBASE_CREDENTIALS_FILE="./credentials/firebase_credentials.json"
export AI_PROVIDER="google_gemini"
export AI_MODEL_NAME="gemini-pro"
export ENVIRONMENT="development"
export DEBUG="true"
export LOG_LEVEL="INFO"
export DEFAULT_TEAM_ID="KAI"
export PAYMENT_ENABLED="false"
```

Then reload your shell:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Windows

#### Command Prompt (Temporary)
```cmd
set TELEGRAM_BOT_TOKEN=your_bot_token_here
set GOOGLE_API_KEY=your_google_api_key_here
set FIRESTORE_PROJECT_ID=your_project_id
```

#### PowerShell (Temporary)
```powershell
$env:TELEGRAM_BOT_TOKEN="your_bot_token_here"
$env:GOOGLE_API_KEY="your_google_api_key_here"
$env:FIRESTORE_PROJECT_ID="your_project_id"
```

#### System Environment Variables (Permanent)
1. Open System Properties → Advanced → Environment Variables
2. Add each variable under "User variables" or "System variables"
3. Restart your terminal/IDE

## 🧪 Testing Environment Setup

For E2E testing, you'll need additional variables:

```bash
# Test-specific variables
export TEST_MODE="true"
export ADMIN_SESSION_STRING="your_session_string_here"
export PLAYER_SESSION_STRING="your_session_string_here"
export TEST_TIMEOUT="30"
export TEST_MAX_RETRIES="3"
export TEST_PARALLEL="false"
export TEST_LOG_LEVEL="INFO"
export TEST_TEAM_ID="test-team-123"
export TEST_USER_ID="test_user_123"
export TEST_CHAT_ID="test_chat_456"
```

Generate session strings using:
```bash
python setup_telegram_credentials.py
```

## 🔍 Verifying Your Setup

Run the validation script:
```bash
python validate_setup.py
```

This will check that all required environment variables are set correctly.

## 🚨 Troubleshooting

### Common Issues

1. **"Environment variable not found"**
   - Make sure you've set the variable in your current shell session
   - Restart your terminal after adding to shell profile
   - Check for typos in variable names

2. **"Invalid bot token"**
   - Ensure the token format is correct: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - Verify the token is active in @BotFather

3. **"Firebase credentials not found"**
   - Check that `FIREBASE_CREDENTIALS_FILE` points to a valid JSON file
   - Ensure the credentials file has the correct permissions

4. **"Google API key invalid"**
   - Verify your API key is active in Google Cloud Console
   - Check that the API key has the necessary permissions

### Debug Mode

Enable debug logging to see what's happening:
```bash
export DEBUG="true"
export LOG_LEVEL="DEBUG"
```

## 🔄 Environment-Specific Configuration

### Development
```bash
export ENVIRONMENT="development"
export DEBUG="true"
export LOG_LEVEL="DEBUG"
```

### Production
```bash
export ENVIRONMENT="production"
export DEBUG="false"
export LOG_LEVEL="WARNING"
```

### Testing
```bash
export ENVIRONMENT="testing"
export TEST_MODE="true"
export LOG_LEVEL="INFO"
```

## 📚 Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Firebase Console](https://console.firebase.google.com/)
- [Environment Variables Best Practices](https://12factor.net/config)

## 🛡️ Security Best Practices

1. **Never commit secrets to version control**
2. **Use different keys for different environments**
3. **Rotate API keys regularly**
4. **Use environment-specific credentials**
5. **Limit API key permissions to minimum required**
6. **Monitor API usage for unusual activity**
7. **Use secure credential storage in production**

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run `python validate_setup.py` for diagnostics
3. Check the logs with `DEBUG=true`
4. Review the [README.md](README.md) for additional information 