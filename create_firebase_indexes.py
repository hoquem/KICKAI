#!/usr/bin/env python3
"""
Firebase Index Creation Script

This script helps identify and create the necessary Firebase Firestore indexes
to resolve the "400 The query requires an index" error.

The error occurs when making composite queries (multiple where clauses) without
the proper indexes in place.
"""

import json
from typing import List, Dict

def get_required_indexes() -> List[Dict]:
    """Get the list of required Firebase indexes based on the codebase queries."""
    
    indexes = [
        # Players collection indexes
        {
            "collection": "players",
            "fields": ["team_id", "phone_number"],
            "description": "For player lookup by team_id and phone_number",
            "query_example": "players_ref.where('team_id', '==', team_id).where('phone_number', '==', phone_number)"
        },
        {
            "collection": "players", 
            "fields": ["team_id", "is_active"],
            "description": "For getting active players in a team",
            "query_example": "players_ref.where('team_id', '==', team_id).where('is_active', '==', True)"
        },
        
        # Team members collection indexes
        {
            "collection": "team_members",
            "fields": ["team_id", "telegram_user_id", "is_active"],
            "description": "For finding team members by telegram user ID",
            "query_example": "members_ref.where('team_id', '==', team_id).where('telegram_user_id', '==', user_id).where('is_active', '==', True)"
        },
        {
            "collection": "team_members",
            "fields": ["team_id", "phone_number"],
            "description": "For finding team members by phone number",
            "query_example": "members_ref.where('team_id', '==', team_id).where('phone_number', '==', phone_number)"
        },
        {
            "collection": "team_members",
            "fields": ["team_id", "is_active"],
            "description": "For getting active team members",
            "query_example": "members_ref.where('team_id', '==', team_id).where('is_active', '==', True)"
        },
        
        # Bots collection indexes
        {
            "collection": "bots",
            "fields": ["team_id", "is_active"],
            "description": "For getting active bots for a team",
            "query_example": "bots_ref.where('team_id', '==', team_id).where('is_active', '==', True)"
        },
        
        # Fixtures collection indexes
        {
            "collection": "fixtures",
            "fields": ["team_id", "match_date"],
            "description": "For getting fixtures ordered by date",
            "query_example": "fixtures_ref.where('team_id', '==', team_id).order_by('match_date')"
        }
    ]
    
    return indexes

def print_index_instructions():
    """Print instructions for creating Firebase indexes."""
    
    print("🔥 Firebase Index Creation Instructions")
    print("=" * 50)
    print()
    print("The error '400 The query requires an index' occurs because your code")
    print("is making composite queries that require Firebase indexes.")
    print()
    print("To fix this, you need to create the following indexes in Firebase:")
    print()
    
    indexes = get_required_indexes()
    
    for i, index in enumerate(indexes, 1):
        print(f"{i}. Collection: {index['collection']}")
        print(f"   Fields: {', '.join(index['fields'])}")
        print(f"   Description: {index['description']}")
        print(f"   Query: {index['query_example']}")
        print()
    
    print("📋 Steps to Create Indexes:")
    print("1. Go to Firebase Console: https://console.firebase.google.com")
    print("2. Select your project")
    print("3. Go to Firestore Database")
    print("4. Click on 'Indexes' tab")
    print("5. Click 'Create Index'")
    print("6. For each index above:")
    print("   - Collection ID: [collection_name]")
    print("   - Fields: Add each field with 'Ascending' order")
    print("   - Click 'Create'")
    print()
    print("⏱️ Index Creation Time:")
    print("- Small collections: 1-5 minutes")
    print("- Large collections: 10-30 minutes")
    print("- You'll receive an email when indexes are ready")
    print()
    print("🔗 Direct Links:")
    print("- Firebase Console: https://console.firebase.google.com")
    print("- Firestore Indexes: https://console.firebase.google.com/project/_/firestore/indexes")
    print()
    print("💡 Alternative Solution:")
    print("If you want to avoid creating indexes, you can modify the queries")
    print("to use single where clauses and filter in Python code instead.")
    print()
    print("Example:")
    print("Instead of: .where('team_id', '==', team_id).where('phone_number', '==', phone)")
    print("Use: .where('team_id', '==', team_id) and filter phone_number in Python")

def generate_index_json():
    """Generate a JSON file with index definitions for programmatic creation."""
    
    indexes = get_required_indexes()
    
    # Convert to Firebase index format
    firebase_indexes = []
    
    for index in indexes:
        firebase_index = {
            "collectionGroup": index["collection"],
            "queryScope": "COLLECTION",
            "fields": []
        }
        
        for field in index["fields"]:
            firebase_index["fields"].append({
                "fieldPath": field,
                "order": "ASCENDING"
            })
        
        firebase_indexes.append(firebase_index)
    
    # Save to file
    with open("firebase_indexes.json", "w") as f:
        json.dump(firebase_indexes, f, indent=2)
    
    print("📄 Generated firebase_indexes.json with index definitions")
    print("You can use this file with Firebase CLI or gcloud to create indexes programmatically")

if __name__ == "__main__":
    print_index_instructions()
    print()
    generate_index_json()
    print()
    print("✅ Index creation script completed!") 