#!/usr/bin/env python3
"""
Environment Setup Validation

This script validates that all required environment variables and credentials
are properly configured for the E2E testing framework.
"""

import os
import sys
from typing import List, Dict, Any


def check_environment_variables() -> Dict[str, bool]:
    """Check if all required environment variables are set."""
    print("🔍 Checking Environment Variables")
    print("=" * 40)
    
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Bot token from @BotFather',
        'TELEGRAM_API_ID': 'API ID from https://my.telegram.org',
        'TELEGRAM_API_HASH': 'API Hash from https://my.telegram.org',
        'TELEGRAM_SESSION_STRING': 'Session string from Telethon',
        'FIRESTORE_PROJECT_ID': 'Firestore project ID'
    }
    
    optional_vars = {
        'FIRESTORE_CREDENTIALS_PATH': 'Path to service account key file (optional)',
        'TEST_TIMEOUT': 'Test timeout in seconds (default: 30)',
        'TEST_MAX_RETRIES': 'Maximum retry attempts (default: 3)',
        'TEST_PARALLEL': 'Run tests in parallel (default: false)',
        'TEST_LOG_LEVEL': 'Logging level (default: INFO)'
    }
    
    results = {}
    
    # Check required variables
    print("\n📋 Required Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'TOKEN' in var or 'HASH' in var or 'SESSION' in var:
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
            results[var] = True
        else:
            print(f"❌ {var}: Not set - {description}")
            results[var] = False
    
    # Check optional variables
    print("\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set (using default) - {description}")
        results[var] = True  # Optional vars don't fail validation
    
    return results


def validate_telegram_credentials() -> bool:
    """Validate Telegram credentials format."""
    print("\n🤖 Validating Telegram Credentials")
    print("=" * 35)
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    session_string = os.getenv('TELEGRAM_SESSION_STRING')
    
    # Validate bot token
    if bot_token:
        if ':' in bot_token and len(bot_token) > 20:
            print("✅ Bot token format is valid")
        else:
            print("❌ Bot token format is invalid (should contain ':' and be longer)")
            return False
    else:
        print("❌ Bot token not set")
        return False
    
    # Validate API ID
    if api_id:
        if api_id.isdigit():
            print("✅ API ID format is valid")
        else:
            print("❌ API ID should be numeric")
            return False
    else:
        print("❌ API ID not set")
        return False
    
    # Validate API Hash
    if api_hash:
        if len(api_hash) == 32 and api_hash.isalnum():
            print("✅ API Hash format is valid")
        else:
            print("❌ API Hash should be 32 characters alphanumeric")
            return False
    else:
        print("❌ API Hash not set")
        return False
    
    # Validate session string
    if session_string:
        if len(session_string) > 50:
            print("✅ Session string format is valid")
        else:
            print("❌ Session string seems too short")
            return False
    else:
        print("❌ Session string not set")
        return False
    
    return True


def validate_firestore_config() -> bool:
    """Validate Firestore configuration."""
    print("\n🔥 Validating Firestore Configuration")
    print("=" * 35)
    
    project_id = os.getenv('FIRESTORE_PROJECT_ID')
    credentials_path = os.getenv('FIRESTORE_CREDENTIALS_PATH')
    
    # Validate project ID
    if project_id:
        if len(project_id) > 0 and ' ' not in project_id:
            print("✅ Project ID format is valid")
        else:
            print("❌ Project ID should not contain spaces")
            return False
    else:
        print("❌ Project ID not set")
        return False
    
    # Validate credentials path (if provided)
    if credentials_path:
        if os.path.exists(credentials_path):
            print("✅ Service account key file exists")
        else:
            print("❌ Service account key file not found")
            return False
    else:
        print("⚠️  No service account key file specified (using ADC)")
    
    return True


async def test_telegram_connection() -> bool:
    """Test Telegram connection."""
    print("\n🔗 Testing Telegram Connection")
    print("=" * 30)
    
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        session_string = os.getenv('TELEGRAM_SESSION_STRING')
        
        if not all([bot_token, api_id, api_hash, session_string]):
            print("❌ Missing Telegram credentials")
            return False
        
        # Create client
        client = TelegramClient(StringSession(session_string), int(api_id), api_hash)
        
        # Test connection
        await client.start()
        
        # Get bot info
        bot = await client.get_me()
        print(f"✅ Connected to Telegram as: {bot.username}")
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Telegram connection failed: {e}")
        return False


def test_firestore_connection() -> bool:
    """Test Firestore connection."""
    print("\n🔗 Testing Firestore Connection")
    print("=" * 30)
    
    try:
        from google.cloud import firestore
        from google.oauth2 import service_account
        
        project_id = os.getenv('FIRESTORE_PROJECT_ID')
        credentials_path = os.getenv('FIRESTORE_CREDENTIALS_PATH')
        
        if not project_id:
            print("❌ Project ID not set")
            return False
        
        # Initialize Firestore client
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            db = firestore.Client(project=project_id, credentials=credentials)
            print("✅ Using service account authentication")
        else:
            db = firestore.Client(project=project_id)
            print("✅ Using Application Default Credentials")
        
        # Test connection
        test_doc = db.collection('test').document('connection_test')
        test_doc.get()
        
        print(f"✅ Connected to Firestore project: {project_id}")
        return True
        
    except Exception as e:
        print(f"❌ Firestore connection failed: {e}")
        return False


def check_dependencies() -> bool:
    """Check if all required dependencies are installed."""
    print("\n📦 Checking Dependencies")
    print("=" * 25)
    
    required_packages = [
        'telethon',
        'google-cloud-firestore',
        'pytest',
        'pytest-asyncio',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main validation function."""
    print("🎯 KICKAI E2E Testing - Environment Validation")
    print("=" * 60)
    print()
    
    # Load .env file if it exists
    if os.path.exists('.env'):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ .env file loaded")
        except ImportError:
            print("⚠️  python-dotenv not installed, .env file not loaded")
    else:
        print("⚠️  .env file not found")
    
    # Run all validations
    results = {
        'env_vars': check_environment_variables(),
        'telegram_creds': validate_telegram_credentials(),
        'firestore_config': validate_firestore_config(),
        'dependencies': check_dependencies(),
        'firestore_connection': test_firestore_connection()
    }
    
    # Test Telegram connection asynchronously
    import asyncio
    results['telegram_connection'] = asyncio.run(test_telegram_connection())
    
    # Summary
    print("\n📊 Validation Summary")
    print("=" * 25)
    
    required_vars = results['env_vars']
    required_vars_set = all(required_vars.get(var, False) for var in [
        'TELEGRAM_BOT_TOKEN', 'TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 
        'TELEGRAM_SESSION_STRING', 'FIRESTORE_PROJECT_ID'
    ])
    
    print(f"Environment Variables: {'✅' if required_vars_set else '❌'}")
    print(f"Telegram Credentials: {'✅' if results['telegram_creds'] else '❌'}")
    print(f"Firestore Config: {'✅' if results['firestore_config'] else '❌'}")
    print(f"Dependencies: {'✅' if results['dependencies'] else '❌'}")
    print(f"Telegram Connection: {'✅' if results['telegram_connection'] else '❌'}")
    print(f"Firestore Connection: {'✅' if results['firestore_connection'] else '❌'}")
    
    # Overall result
    all_passed = all([
        required_vars_set,
        results['telegram_creds'],
        results['firestore_config'],
        results['dependencies'],
        results['telegram_connection'],
        results['firestore_connection']
    ])
    
    print(f"\n🎯 Overall Status: {'✅ READY' if all_passed else '❌ NOT READY'}")
    
    if all_passed:
        print("\n🎉 Environment is ready for E2E testing!")
        print("Next steps:")
        print("1. Run: python run_e2e_tests.py --suite smoke")
        print("2. Run: python example_e2e_test.py")
    else:
        print("\n🔧 Setup required:")
        print("1. Run: python setup_telegram_credentials.py")
        print("2. Run: python setup_firestore.py")
        print("3. Check: SETUP_GUIDE.md")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 