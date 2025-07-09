#!/usr/bin/env python3
"""
KICKAI Local Environment Setup

This script helps you set up your local environment for KICKAI.
Instead of creating .env files, it will guide you to set system environment variables.
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def print_banner():
    """Print setup banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    KICKAI SETUP WIZARD                       ║
║                                                              ║
║  This script will help you configure your environment       ║
║  variables for KICKAI.                                       ║
║                                                              ║
║  ⚠️  IMPORTANT: We'll set system environment variables      ║
║     instead of creating .env files for better security.     ║
╚══════════════════════════════════════════════════════════════╝
""")


def get_input(prompt, default=None, required=True):
    """Get user input with validation."""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if required and not user_input:
            print("❌ This field is required. Please enter a value.")
            continue
        
        return user_input


def setup_telegram():
    """Set up Telegram configuration."""
    print("\n🤖 TELEGRAM SETUP")
    print("=" * 20)
    
    print("""
To get your bot token:
1. Go to @BotFather on Telegram
2. Send /newbot or use existing bot
3. Copy the bot token (format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
""")
    
    bot_token = get_input("Enter your bot token")
    
    if ':' not in bot_token:
        print("❌ Invalid bot token format. Should contain ':'")
        return setup_telegram()
    
    print("""
To get chat IDs:
1. Add your bot to the chat
2. Send a message in the chat
3. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
4. Look for 'chat' -> 'id' in the response
""")
    
    main_chat_id = get_input("Enter your main chat ID (can be same as leadership)")
    leadership_chat_id = get_input("Enter your leadership chat ID (can be same as main)")
    
    return {
        "TELEGRAM_BOT_TOKEN": bot_token,
        "TELEGRAM_MAIN_CHAT_ID": main_chat_id,
        "TELEGRAM_LEADERSHIP_CHAT_ID": leadership_chat_id
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
    
    # Create credentials directory and file
    credentials_dir = Path("credentials")
    credentials_dir.mkdir(exist_ok=True)
    
    credentials_file = credentials_dir / "firebase_credentials.json"
    with open(credentials_file, 'w') as f:
        f.write(credentials_json)
    
    print(f"✅ Firebase credentials saved to {credentials_file}")
    
    return {
        "FIRESTORE_PROJECT_ID": project_id,
        "FIREBASE_CREDENTIALS_FILE": str(credentials_file)
    }


def setup_ai():
    """Set up AI provider configuration."""
    print("\n🤖 AI PROVIDER SETUP")
    print("=" * 25)
    
    print("""
Choose your AI provider:
1. Google Gemini (recommended for production)
2. OpenAI (requires API key)
""")
    
    provider = get_input("Enter AI provider (google_gemini/openai)", "google_gemini")
    
    if provider == "google_gemini":
        print("""
To get Google API key:
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key
""")
        api_key = get_input("Enter your Google API key")
        model = "gemini-pro"
        config = {
            "GOOGLE_API_KEY": api_key,
            "AI_PROVIDER": provider,
            "AI_MODEL_NAME": model
        }
    elif provider == "openai":
        print("""
To get OpenAI API key:
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key
""")
        api_key = get_input("Enter your OpenAI API key")
        model = "gpt-3.5-turbo"
        config = {
            "OPENAI_API_KEY": api_key,
            "AI_PROVIDER": provider,
            "AI_MODEL_NAME": model
        }
    else:
        print("❌ Invalid provider. Using Google Gemini.")
        provider = "google_gemini"
        api_key = get_input("Enter your Google API key")
        model = "gemini-pro"
        config = {
            "GOOGLE_API_KEY": api_key,
            "AI_PROVIDER": provider,
            "AI_MODEL_NAME": model
        }
    
    return config


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


def generate_env_commands(config):
    """Generate commands to set environment variables."""
    print("\n🔧 ENVIRONMENT VARIABLE SETUP")
    print("=" * 40)
    
    print("""
To set up your environment variables, run the following commands:

For macOS/Linux (add to ~/.bashrc, ~/.zshrc, or ~/.profile):
""")
    
    for key, value in config.items():
        if key in ["GOOGLE_API_KEY", "TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY"]:
            # Mask sensitive values
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"export {key}='{value}'  # {masked_value}")
        else:
            print(f"export {key}='{value}'")
    
    print("""

For Windows (add to system environment variables or run in cmd):
""")
    
    for key, value in config.items():
        if key in ["GOOGLE_API_KEY", "TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY"]:
            # Mask sensitive values
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"set {key}={value}  # {masked_value}")
        else:
            print(f"set {key}={value}")
    
    print("""

For immediate use in current session:
""")
    
    for key, value in config.items():
        if key in ["GOOGLE_API_KEY", "TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY"]:
            # Mask sensitive values
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"export {key}='{value}'  # {masked_value}")
        else:
            print(f"export {key}='{value}'")


def create_env_template(config):
    """Create a .env template file for reference."""
    template_content = """# KICKAI Environment Variables
# Generated by setup_local_environment.py
# Copy this to .env and fill in your actual values

"""
    
    for key, value in config.items():
        if key in ["GOOGLE_API_KEY", "TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY"]:
            template_content += f"{key}=your_{key.lower()}_here\n"
        else:
            template_content += f"{key}={value}\n"
    
    with open(".env.template", "w") as f:
        f.write(template_content)
    
    print("✅ .env.template file created for reference")


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
        
        # Generate environment variable commands
        generate_env_commands(config)
        
        # Create template file
        create_env_template(config)
        
        print("""
🎉 SETUP COMPLETE!

Your KICKAI environment configuration is ready. Next steps:

1. Set the environment variables using the commands above
2. Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)
3. Install dependencies: pip install -r requirements.txt
4. Run the bot: python run_telegram_bot.py
5. Test the bot: Send /start to your bot on Telegram

📁 Files created:
   - .env.template (reference template)
   - credentials/firebase_credentials.json

⚠️  SECURITY NOTES:
   - Never commit .env files to version control
   - Keep your API keys secure
   - Use different keys for development and production

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