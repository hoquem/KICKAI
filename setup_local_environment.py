#!/usr/bin/env python3
"""
KICKAI Local Environment Setup

This script helps set up the local environment for running KICKAI.
It will guide you through setting up the required environment variables.
"""

import os
import json
import sys
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("""
🎯 KICKAI Local Environment Setup
================================

This script will help you set up your local environment for running KICKAI.
You'll need to provide several configuration values.

Let's get started!
""")

def get_input(prompt, default=None, required=True):
    """Get user input with validation."""
    while True:
        if default:
            value = input(f"{prompt} (default: {default}): ").strip()
            if not value:
                value = default
        else:
            value = input(f"{prompt}: ").strip()
        
        if required and not value:
            print("❌ This field is required. Please provide a value.")
            continue
        
        return value

def setup_telegram():
    """Set up Telegram bot configuration."""
    print("\n🤖 TELEGRAM BOT SETUP")
    print("=" * 30)
    
    print("""
To get your Telegram bot token:
1. Message @BotFather on Telegram
2. Send /newbot
3. Follow the instructions to create a bot
4. Copy the token provided
""")
    
    bot_token = get_input("Enter your Telegram bot token")
    
    print("""
To get your chat IDs:
1. Add your bot to your group
2. Send a message in the group
3. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
4. Look for 'chat' -> 'id' in the response
""")
    
    main_chat_id = get_input("Enter your main chat ID")
    leadership_chat_id = get_input("Enter your leadership chat ID (can be same as main)")
    
    return {
        "TELEGRAM_BOT_TOKEN": bot_token,
        "MAIN_CHAT_ID": main_chat_id,
        "LEADERSHIP_CHAT_ID": leadership_chat_id
    }

def setup_firebase():
    """Set up Firebase configuration."""
    print("\n🔥 FIREBASE SETUP")
    print("=" * 20)
    
    print("""
To set up Firebase:
1. Go to https://console.firebase.google.com/
2. Create a new project or select existing
3. Go to Project Settings > Service Accounts
4. Click "Generate new private key"
5. Download the JSON file
""")
    
    project_id = get_input("Enter your Firebase project ID")
    
    print("""
For the service account JSON:
1. Open the downloaded JSON file
2. Copy the entire content
3. Paste it below (it should be a single line)
""")
    
    credentials_json = get_input("Enter your Firebase service account JSON")
    
    # Validate JSON
    try:
        json.loads(credentials_json)
    except json.JSONDecodeError:
        print("❌ Invalid JSON format. Please check your service account JSON.")
        return setup_firebase()
    
    return {
        "FIREBASE_CREDENTIALS_JSON": credentials_json,
        "FIREBASE_PROJECT_ID": project_id
    }

def setup_ai():
    """Set up AI provider configuration."""
    print("\n🤖 AI PROVIDER SETUP")
    print("=" * 25)
    
    print("""
Choose your AI provider:
1. Google Gemini (recommended for production)
2. OpenAI (requires API key)
3. Ollama (for local development)
""")
    
    provider = get_input("Enter AI provider (google_gemini/openai/ollama)", "google_gemini")
    
    if provider == "google_gemini":
        print("""
To get Google API key:
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key
""")
        api_key = get_input("Enter your Google API key")
        model = "gemini-pro"
    elif provider == "openai":
        print("""
To get OpenAI API key:
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key
""")
        api_key = get_input("Enter your OpenAI API key")
        model = "gpt-3.5-turbo"
    elif provider == "ollama":
        print("""
For Ollama (local development):
1. Install Ollama from https://ollama.ai
2. Run: ollama pull llama3.1:8b-instruct-q4_0
3. Use 'ollama_local' as API key
""")
        api_key = "ollama_local"
        model = "llama3.1:8b-instruct-q4_0"
    else:
        print("❌ Invalid provider. Using Google Gemini.")
        provider = "google_gemini"
        api_key = get_input("Enter your Google API key")
        model = "gemini-pro"
    
    return {
        "GOOGLE_API_KEY": api_key,
        "AI_PROVIDER": provider,
        "AI_MODEL_NAME": model
    }

def setup_optional():
    """Set up optional configuration."""
    print("\n⚙️ OPTIONAL CONFIGURATION")
    print("=" * 30)
    
    environment = get_input("Enter environment (development/production)", "development", required=False)
    payment_enabled = get_input("Enable payment system? (true/false)", "false", required=False)
    
    config = {
        "ENVIRONMENT": environment,
        "PAYMENT_ENABLED": payment_enabled
    }
    
    if payment_enabled.lower() == "true":
        print("""
Payment system setup:
You'll need a Collectiv API key for payment processing.
For now, we'll set it up as disabled.
""")
        config["PAYMENT_ENABLED"] = "false"
    
    return config

def create_env_file(config):
    """Create .env file with configuration."""
    env_content = """# KICKAI Environment Variables
# Generated by setup_local_environment.py

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={bot_token}
MAIN_CHAT_ID={main_chat_id}
LEADERSHIP_CHAT_ID={leadership_chat_id}

# Firebase Configuration
FIREBASE_CREDENTIALS_JSON={firebase_credentials}
FIREBASE_PROJECT_ID={firebase_project_id}

# AI Provider Configuration
GOOGLE_API_KEY={ai_api_key}
AI_PROVIDER={ai_provider}
AI_MODEL_NAME={ai_model}

# Environment
ENVIRONMENT={environment}

# Optional Configuration
PAYMENT_ENABLED={payment_enabled}

# Default Team ID
DEFAULT_TEAM_ID=0854829d-445c-4138-9fd3-4db562ea46ee

# Development Settings
DEBUG=true
VERBOSE_LOGGING=true
""".format(**config)
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")

def main():
    """Main setup function."""
    print_banner()
    
    try:
        # Collect configuration
        telegram_config = setup_telegram()
        firebase_config = setup_firebase()
        ai_config = setup_ai()
        optional_config = setup_optional()
        
        # Combine all configuration
        config = {
            **telegram_config,
            **firebase_config,
            **ai_config,
            **optional_config
        }
        
        # Create .env file
        create_env_file(config)
        
        print("""
🎉 SETUP COMPLETE!

Your KICKAI environment is now configured. Next steps:

1. Install dependencies:
   pip install -r requirements.txt

2. Run the bot:
   python run_telegram_bot.py

3. Test the bot:
   Send /start to your bot on Telegram

📁 Files created:
   - .env (environment variables)

📖 For more information, see README.md
""")
        
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 