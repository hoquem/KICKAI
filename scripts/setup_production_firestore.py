# SECURITY WARNING: Never store Telegram bot tokens or secrets in code. Use Railway environment variables or Firestore only.
# Replace any hardcoded tokens with placeholders.

import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Initialize Firebase Admin SDK for production
cred = credentials.Certificate('firebase_creds_production.json')
firebase_admin.initialize_app(cred, {
    'projectId': 'kickai-production'
})

db = firestore.client()

# Create BP Hatters FC team
team_data = {
    'name': 'BP Hatters FC',
    'description': 'Production team for BP Hatters FC',
    'is_active': True,
    'created_at': firestore.SERVER_TIMESTAMP,
    'settings': {
        'ai_provider': 'openai',
        'ai_model': 'gpt-4',
        'max_members': 200,
        'allow_public_join': False
    }
}

# Add team to Firestore
team_ref = db.collection('teams').document('bp-hatters-fc')
team_ref.set(team_data)

# Create main bot configuration
main_bot_data = {
    'team_id': 'bp-hatters-fc',
    'bot_type': 'main',
    'bot_token': 'YOUR_PRODUCTION_BOT_TOKEN_HERE',
    'bot_username': 'kickai_bp_hatters_main_bot',
    'chat_id': '-1001234567890',  # You'll need to update this
    'is_active': True,
    'created_at': firestore.SERVER_TIMESTAMP
}

# Add main bot to Firestore
main_bot_ref = db.collection('team_bots').document('bp-hatters-fc-main')
main_bot_ref.set(main_bot_data)

# Create leadership bot configuration (using testing leadership bot token)
leadership_bot_data = {
    'team_id': 'bp-hatters-fc',
    'bot_type': 'leadership',
    'bot_token': '7884439531:AAE1lv2akcI7s0Rr2IdYS-btBc1tN3nXkHc',  # From testing
    'bot_username': 'kickai_bp_hatters_leadership_bot',
    'chat_id': '-1001234567890',  # You'll need to update this
    'is_active': True,
    'created_at': firestore.SERVER_TIMESTAMP
}

# Add leadership bot to Firestore
leadership_bot_ref = db.collection('team_bots').document('bp-hatters-fc-leadership')
leadership_bot_ref.set(leadership_bot_data)

print("✅ Production Firestore setup completed!")
print("   Team: BP Hatters FC")
print("   Main Bot: kickai_bp_hatters_main_bot")
print("   Leadership Bot: kickai_bp_hatters_leadership_bot")
print("   Note: You'll need to update chat IDs for both bots")
