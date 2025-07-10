#!/usr/bin/env python3
"""
Cleanup script for test data in Firestore.

This script removes test data created during E2E testing to keep the database clean.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load test environment
load_dotenv('.env.test')

# Add src to path
sys.path.insert(0, 'src')

from src.database.firebase_client import get_firebase_client

async def cleanup_test_data():
    """Clean up test data from Firestore."""
    print("🧹 Starting test data cleanup...")
    
    try:
        # Get Firebase client
        firebase_client = get_firebase_client()
        
        # Test data to clean up
        test_data = {
            "players": [
                "JS",  # Expected player ID from test
                "JS1",  # Alternative player ID format
                "JS2",  # Another alternative
            ],
            "teams": [
                "test-team-123",
                "TEST"
            ],
            "matches": [
                "match_123",
                "MATCH123"
            ],
            "payments": [
                "payment_123",
                "PAYMENT123"
            ]
        }
        
        # Clean up each collection
        for collection, document_ids in test_data.items():
            print(f"📁 Cleaning up {collection} collection...")
            
            for doc_id in document_ids:
                try:
                    # Check if document exists
                    doc = await firebase_client.get_document(collection, doc_id)
                    if doc:
                        await firebase_client.delete_document(collection, doc_id)
                        print(f"  ✅ Deleted {collection}/{doc_id}")
                    else:
                        print(f"  ℹ️  {collection}/{doc_id} not found")
                except Exception as e:
                    print(f"  ❌ Error deleting {collection}/{doc_id}: {e}")
        
        print("✅ Test data cleanup completed!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_test_data()) 