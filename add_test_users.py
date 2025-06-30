#!/usr/bin/env python3
"""
Add Test Users Script
Adds test users to the database for development and testing.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.tools.firebase_tools import get_firebase_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_firebase_client():
    """Get Firebase client with proper error handling."""
    try:
        return get_firebase_client()
    except Exception as e:
        logger.error(f"Failed to get Firebase client: {e}")
        raise

def add_test_users():
    """Add test users to the database."""
    try:
        firebase = get_firebase_client()
        
        # Test users data
        test_users = [
            {
                'name': 'John Smith',
                'phone_number': '+1234567890',
                'role': 'admin',
                'team_id': '0854829d-445c-4138-9fd3-4db562ea46ee',  # BP Hatters FC
                'joined_at': datetime.now(),
                'is_active': True
            },
            {
                'name': 'Mike Johnson',
                'phone_number': '+1234567891',
                'role': 'captain',
                'team_id': '0854829d-445c-4138-9fd3-4db562ea46ee',
                'joined_at': datetime.now(),
                'is_active': True
            },
            {
                'name': 'David Wilson',
                'phone_number': '+1234567892',
                'role': 'player',
                'team_id': '0854829d-445c-4138-9fd3-4db562ea46ee',
                'joined_at': datetime.now(),
                'is_active': True
            },
            {
                'name': 'Sarah Brown',
                'phone_number': '+1234567893',
                'role': 'player',
                'team_id': '0854829d-445c-4138-9fd3-4db562ea46ee',
                'joined_at': datetime.now(),
                'is_active': True
            },
            {
                'name': 'Tom Davis',
                'phone_number': '+1234567894',
                'role': 'player',
                'team_id': '0854829d-445c-4138-9fd3-4db562ea46ee',
                'joined_at': datetime.now(),
                'is_active': True
            }
        ]
        
        # Add users to database
        members_ref = firebase.collection('team_members')
        added_count = 0
        
        for user_data in test_users:
            try:
                # Check if user already exists
                existing_query = members_ref.where('team_id', '==', user_data['team_id']).where('phone_number', '==', user_data['phone_number'])
                existing_docs = existing_query.get()
                
                if existing_docs:
                    logger.info(f"User {user_data['name']} already exists, skipping...")
                    continue
                
                # Add new user
                doc_ref = members_ref.document()
                doc_ref.set(user_data)
                added_count += 1
                logger.info(f"Added user: {user_data['name']} ({user_data['role']})")
                
            except Exception as e:
                logger.error(f"Failed to add user {user_data['name']}: {e}")
        
        logger.info(f"✅ Successfully added {added_count} test users")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add test users: {e}")
        return False

def list_users():
    """List all users in the database."""
    try:
        firebase = get_firebase_client()
        members_ref = firebase.collection('team_members')
        query = members_ref.where('is_active', '==', True)
        response = query.get()
        
        if not response:
            logger.info("No users found in database")
            return
        
        logger.info("📋 Users in database:")
        for doc in response:
            user_data = doc.to_dict()
            logger.info(f"• {user_data['name']} ({user_data['phone_number']}) - {user_data['role']}")
        
    except Exception as e:
        logger.error(f"Failed to list users: {e}")

def main():
    """Main function."""
    logger.info("👥 Starting Test Users Script")
    
    # Add test users
    logger.info("\n➕ Adding test users...")
    success = add_test_users()
    
    if success:
        # List users
        logger.info("\n📋 Listing all users...")
        list_users()
    else:
        logger.error("❌ Failed to add test users")

if __name__ == "__main__":
    main() 