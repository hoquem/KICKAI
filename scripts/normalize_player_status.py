#!/usr/bin/env python3
"""
Script to normalize player status fields in Firestore.

This script:
1. Finds all player records with 'onboarding_status' field
2. Copies the value to 'status' field
3. Removes the 'onboarding_status' field
4. Ensures consistent status values across all players
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from kickai.database.firebase_client import get_firebase_client
from kickai.core.dependency_container import get_container, ensure_container_initialized
from google.cloud.firestore import DELETE_FIELD


async def get_all_player_collections() -> List[str]:
    """Get all player collection names from Firestore."""
    collections = [
        "kickai_KTI_players",  # Main KTI players collection
        "kickai_KTI_team_members",  # Team members collection (may have players)
        # Add other team collections as needed
    ]
    return collections


async def normalize_status_field(db_client, collection_name: str, dry_run: bool = True) -> Dict[str, Any]:
    """
    Normalize status fields in a collection.
    
    Args:
        db_client: Firebase client instance
        collection_name: Name of the collection to process
        dry_run: If True, only report what would be changed without modifying
        
    Returns:
        Statistics about the normalization process
    """
    stats = {
        "collection": collection_name,
        "total_documents": 0,
        "documents_with_onboarding_status": 0,
        "documents_with_both_fields": 0,
        "documents_updated": 0,
        "documents_failed": 0,
        "status_mapping": {}
    }
    
    try:
        # Get all documents in the collection
        logger.info(f"Processing collection: {collection_name}")
        
        # Query all documents
        docs = await db_client.query_documents(
            collection=collection_name,
            filters=[]
        )
        
        stats["total_documents"] = len(docs)
        logger.info(f"Found {len(docs)} documents in {collection_name}")
        
        for doc in docs:
            doc_id = doc.get('id') or doc.get('player_id') or doc.get('telegram_id')
            
            # Check if document has onboarding_status
            if 'onboarding_status' in doc:
                stats["documents_with_onboarding_status"] += 1
                onboarding_status = doc['onboarding_status']
                
                # Track status mapping
                if onboarding_status not in stats["status_mapping"]:
                    stats["status_mapping"][onboarding_status] = 0
                stats["status_mapping"][onboarding_status] += 1
                
                # Check if it also has status field
                if 'status' in doc:
                    stats["documents_with_both_fields"] += 1
                    logger.warning(
                        f"Document {doc_id} has both 'status' ({doc['status']}) "
                        f"and 'onboarding_status' ({onboarding_status})"
                    )
                
                if not dry_run:
                    try:
                        # Prepare update data to add status field and remove onboarding_status
                        update_data = {
                            'status': onboarding_status,
                            'onboarding_status': DELETE_FIELD,  # Delete the field
                            'updated_at': datetime.utcnow().isoformat()
                        }
                        
                        # Update the document in one operation
                        await db_client.update_document(
                            collection=collection_name,
                            document_id=str(doc_id),
                            data=update_data
                        )
                        
                        stats["documents_updated"] += 1
                        logger.success(
                            f"✅ Updated document {doc_id}: "
                            f"onboarding_status '{onboarding_status}' -> status '{onboarding_status}' "
                            f"(onboarding_status field removed)"
                        )
                        
                    except Exception as e:
                        stats["documents_failed"] += 1
                        logger.error(f"❌ Failed to update document {doc_id}: {e}")
                else:
                    logger.info(
                        f"[DRY RUN] Would update document {doc_id}: "
                        f"onboarding_status '{onboarding_status}' -> status '{onboarding_status}'"
                    )
    
    except Exception as e:
        logger.error(f"Error processing collection {collection_name}: {e}")
        
    return stats


async def verify_normalization(db_client, collection_name: str) -> Dict[str, Any]:
    """
    Verify that normalization was successful.
    
    Args:
        db_client: Firebase client instance
        collection_name: Name of the collection to verify
        
    Returns:
        Verification statistics
    """
    verification = {
        "collection": collection_name,
        "documents_with_status": 0,
        "documents_with_onboarding_status": 0,
        "status_values": {}
    }
    
    try:
        docs = await db_client.query_documents(
            collection=collection_name,
            filters=[]
        )
        
        for doc in docs:
            if 'status' in doc:
                verification["documents_with_status"] += 1
                status = doc['status']
                if status not in verification["status_values"]:
                    verification["status_values"][status] = 0
                verification["status_values"][status] += 1
                
            if 'onboarding_status' in doc:
                verification["documents_with_onboarding_status"] += 1
                
    except Exception as e:
        logger.error(f"Error verifying collection {collection_name}: {e}")
        
    return verification


async def main():
    """Main function to run the normalization process."""
    # Parse command line arguments
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    verify_only = '--verify' in sys.argv or '-v' in sys.argv
    
    if dry_run:
        logger.info("🔍 Running in DRY RUN mode - no changes will be made")
    elif verify_only:
        logger.info("✓ Running in VERIFY mode - checking current status")
    else:
        logger.warning("⚠️  Running in LIVE mode - changes WILL be made to the database")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Aborted by user")
            return
    
    # Initialize the container and get database client
    logger.info("Initializing database connection...")
    await ensure_container_initialized()
    container = get_container()
    db_client = get_firebase_client()
    
    # Get all player collections
    collections = await get_all_player_collections()
    
    if verify_only:
        # Just verify the current state
        logger.info("\n" + "="*60)
        logger.info("VERIFICATION RESULTS")
        logger.info("="*60)
        
        for collection in collections:
            verification = await verify_normalization(db_client, collection)
            
            logger.info(f"\n📊 Collection: {verification['collection']}")
            logger.info(f"  Documents with 'status': {verification['documents_with_status']}")
            logger.info(f"  Documents with 'onboarding_status': {verification['documents_with_onboarding_status']}")
            
            if verification['status_values']:
                logger.info("  Status value distribution:")
                for status, count in verification['status_values'].items():
                    logger.info(f"    - {status}: {count}")
    else:
        # Process each collection
        all_stats = []
        
        for collection in collections:
            stats = await normalize_status_field(db_client, collection, dry_run=dry_run)
            all_stats.append(stats)
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("NORMALIZATION SUMMARY")
        logger.info("="*60)
        
        for stats in all_stats:
            logger.info(f"\n📊 Collection: {stats['collection']}")
            logger.info(f"  Total documents: {stats['total_documents']}")
            logger.info(f"  Documents with onboarding_status: {stats['documents_with_onboarding_status']}")
            logger.info(f"  Documents with both fields: {stats['documents_with_both_fields']}")
            
            if not dry_run:
                logger.info(f"  Documents updated: {stats['documents_updated']}")
                logger.info(f"  Documents failed: {stats['documents_failed']}")
            
            if stats['status_mapping']:
                logger.info("  Status values found:")
                for status, count in stats['status_mapping'].items():
                    logger.info(f"    - {status}: {count}")
        
        if not dry_run:
            logger.info("\n" + "="*60)
            logger.info("VERIFICATION AFTER UPDATE")
            logger.info("="*60)
            
            for collection in collections:
                verification = await verify_normalization(db_client, collection)
                
                logger.info(f"\n✅ Collection: {verification['collection']}")
                logger.info(f"  Documents with 'status': {verification['documents_with_status']}")
                logger.info(f"  Documents with 'onboarding_status': {verification['documents_with_onboarding_status']}")
                
                if verification['documents_with_onboarding_status'] > 0:
                    logger.warning(f"  ⚠️  Still {verification['documents_with_onboarding_status']} documents with onboarding_status!")
                else:
                    logger.success("  ✅ All documents normalized successfully!")


if __name__ == "__main__":
    # Print usage information
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
Usage: python normalize_player_status.py [OPTIONS]

Options:
  --dry-run, -n    Run without making changes (preview what would be done)
  --verify, -v     Verify current status without making changes
  --help, -h       Show this help message

Examples:
  python normalize_player_status.py --dry-run    # Preview changes
  python normalize_player_status.py --verify     # Check current state
  python normalize_player_status.py              # Apply changes (with confirmation)
        """)
        sys.exit(0)
    
    # Run the script
    asyncio.run(main())