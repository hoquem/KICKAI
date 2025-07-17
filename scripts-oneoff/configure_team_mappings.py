#!/usr/bin/env python3
"""
Script to configure team mappings in the kickai_bot_mappings Firestore collection.

This script sets up the necessary team mappings for the KICKAI bot to function properly.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Chat IDs from environment
MAIN_CHAT_ID = os.getenv('TELEGRAM_MAIN_CHAT_ID')
LEADERSHIP_CHAT_ID = os.getenv('TELEGRAM_LEADERSHIP_CHAT_ID')
TEAM_ID = os.getenv('TEAM_ID', 'KAI')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME', 'kickai_bot')

def configure_team_mappings():
    """Configure team mappings in Firestore."""
    
    if not all([MAIN_CHAT_ID, LEADERSHIP_CHAT_ID, TEAM_ID, BOT_TOKEN]):
        logger.error("❌ Missing required environment variables:")
        logger.error(f"   TELEGRAM_MAIN_CHAT_ID: {MAIN_CHAT_ID}")
        logger.error(f"   TELEGRAM_LEADERSHIP_CHAT_ID: {LEADERSHIP_CHAT_ID}")
        logger.error(f"   TEAM_ID: {TEAM_ID}")
        logger.error(f"   TELEGRAM_BOT_TOKEN: {'Set' if BOT_TOKEN else 'Missing'}")
        return False
    
    try:
        # Initialize Firebase with existing credentials
        if not firebase_admin._apps:
            firebase_creds_file = os.getenv('FIREBASE_CREDENTIALS_FILE')
            if firebase_creds_file and os.path.exists(firebase_creds_file):
                logger.info(f"🔄 Using Firebase credentials from: {firebase_creds_file}")
                cred = credentials.Certificate(firebase_creds_file)
                firebase_admin.initialize_app(cred)
            else:
                logger.error("❌ Firebase credentials file not found")
                return False
        
        # Initialize Firestore client
        db = firestore.client()
        collection_ref = db.collection('kickai_bot_mappings')
        
        logger.info(f"🔧 Configuring team mappings for team: {TEAM_ID}")
        logger.info(f"   Main Chat ID: {MAIN_CHAT_ID}")
        logger.info(f"   Leadership Chat ID: {LEADERSHIP_CHAT_ID}")
        logger.info(f"   Bot Token: {BOT_TOKEN[:10]}...")
        logger.info(f"   Bot Username: {BOT_USERNAME}")
        
        # Configure main chat mapping
        main_chat_doc = {
            'chat_id': MAIN_CHAT_ID,
            'team_id': TEAM_ID,
            'chat_type': 'main',
            'bot_token': BOT_TOKEN,
            'bot_username': BOT_USERNAME,
            'is_admin': True,  # Bot should be admin in main chat
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        # Configure leadership chat mapping
        leadership_chat_doc = {
            'chat_id': LEADERSHIP_CHAT_ID,
            'team_id': TEAM_ID,
            'chat_type': 'leadership',
            'bot_token': BOT_TOKEN,
            'bot_username': BOT_USERNAME,
            'is_admin': True,  # Bot should be admin in leadership chat
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        # Write documents to Firestore
        logger.info("\n📝 Writing team mappings to Firestore...")
        
        # Use chat_id as document ID for easy lookup
        collection_ref.document(MAIN_CHAT_ID).set(main_chat_doc)
        logger.info(f"   ✅ Main chat mapping configured")
        
        collection_ref.document(LEADERSHIP_CHAT_ID).set(leadership_chat_doc)
        logger.info(f"   ✅ Leadership chat mapping configured")
        
        # Verify the mappings
        logger.info("\n🔍 Verifying team mappings...")
        
        main_doc = collection_ref.document(MAIN_CHAT_ID).get()
        leadership_doc = collection_ref.document(LEADERSHIP_CHAT_ID).get()
        
        if main_doc.exists and leadership_doc.exists:
            logger.info("   ✅ Team mappings verified successfully")
            logger.info(f"   📊 Total mappings configured: 2")
            return True
        else:
            logger.error("   ❌ Failed to verify team mappings")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error configuring team mappings: {e}")
        return False

def verify_bot_admin_status():
    """Verify that the bot is admin in both chats."""
    logger.info("\n🔍 Verifying bot admin status...")
    logger.info("   ⚠️  Please ensure the bot is added as an admin in both chats:")
    logger.info(f"      Main Chat: {MAIN_CHAT_ID}")
    logger.info(f"      Leadership Chat: {LEADERSHIP_CHAT_ID}")
    logger.info("   📋 Required permissions:")
    logger.info("      - Send Messages")
    logger.info("      - Read Messages")
    logger.info("      - Delete Messages (optional)")
    logger.info("      - Pin Messages (optional)")

def main():
    """Main function."""
    logger.info("🤖 KICKAI Team Mapping Configuration")
    logger.info("=" * 50)
    
    success = configure_team_mappings()
    
    if success:
        verify_bot_admin_status()
        logger.info("\n✅ Team mapping configuration completed successfully!")
        logger.info("🚀 The bot should now be able to start without validation errors.")
    else:
        logger.error("\n❌ Team mapping configuration failed!")
        logger.error("   Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 