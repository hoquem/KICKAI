#!/usr/bin/env python3
"""
Script to list all bot configurations in Firestore.
"""

import asyncio
import os
import sys
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment variables
load_env_file()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import firebase_admin
from firebase_admin import credentials, firestore
from loguru import logger


async def list_bot_configs():
    """List all bot configurations in Firestore."""
    try:
        # Initialize Firebase
        try:
            firebase_admin.get_app()
            logger.info("✅ Using existing Firebase app")
        except ValueError:
            logger.info("🔄 Initializing new Firebase app...")
            
            # Get credentials from environment
            firebase_creds_file = os.getenv('FIREBASE_CREDENTIALS_FILE')
            if firebase_creds_file:
                cred = credentials.Certificate(firebase_creds_file)
                firebase_admin.initialize_app(cred)
                logger.info(f"✅ Firebase initialized with credentials from file: {firebase_creds_file}")
            else:
                raise RuntimeError("No Firebase credentials found.")
        
        db = firestore.client()
        
        # Get all bot configurations
        bot_configs = db.collection('kickai_bot_configurations').stream()
        
        configs = []
        for config in bot_configs:
            config_data = config.to_dict()
            config_data['id'] = config.id
            configs.append(config_data)
        
        if configs:
            print("\n" + "="*60)
            print("BOT CONFIGURATIONS FOUND:")
            print("="*60)
            
            for i, config in enumerate(configs, 1):
                print(f"\n{i}. Document ID: {config.get('id', 'N/A')}")
                print(f"   Team ID: {config.get('team_id', 'N/A')}")
                print(f"   Bot Token: {config.get('bot_token', 'N/A')[:20]}..." if config.get('bot_token') else "   Bot Token: Not found")
                print(f"   Main Chat ID: {config.get('main_chat_id', 'N/A')}")
                print(f"   Leadership Chat ID: {config.get('leadership_chat_id', 'N/A')}")
                print(f"   Created At: {config.get('created_at', 'N/A')}")
                print(f"   Updated At: {config.get('updated_at', 'N/A')}")
                print("-" * 40)
            
            print(f"\nTotal bot configurations: {len(configs)}")
            print("="*60)
            
            return configs
        else:
            print("\n" + "="*50)
            print("NO BOT CONFIGURATIONS FOUND!")
            print("="*50)
            return []
        
    except Exception as e:
        logger.error(f"❌ Error listing bot configs: {e}")
        return []


async def main():
    """Main function."""
    try:
        logger.info("🔍 Listing all bot configurations from Firestore...")
        configs = await list_bot_configs()
        
        if configs:
            print("✅ Successfully retrieved bot configurations")
            return configs
        else:
            print("⚠️ No bot configurations found")
            return []
            
    except Exception as e:
        logger.error(f"❌ Failed to list bot configurations: {e}")
        return []


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, format="{time} | {level} | {message}", level="INFO")
    
    # Run the script
    result = asyncio.run(main())
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1) 