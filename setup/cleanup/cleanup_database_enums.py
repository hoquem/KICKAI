#!/usr/bin/env python3
"""
Database Enum Cleanup Script

This script fixes invalid enum values in the Firestore database by converting them
to valid enum values for PlayerPosition and OnboardingStatus.
"""

import asyncio
import logging
from typing import Dict, Any, List
import firebase_admin
from firebase_admin import credentials, firestore
from src.database.models_improved import PlayerPosition, OnboardingStatus, Player

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseEnumCleaner:
    """Clean up invalid enum values in the database."""
    
    def __init__(self):
        """Initialize the database cleaner."""
        self.db = firestore.client()
        
    async def cleanup_player_positions(self) -> Dict[str, int]:
        """Clean up invalid player positions."""
        logger.info("🔧 Starting player position cleanup...")
        
        # Position mapping for invalid values
        position_mapping = {
            'Forward': 'forward',
            'FORWARD': 'forward',
            'FWD': 'forward',
            'Defender': 'defender',
            'DEFENDER': 'defender',
            'DEF': 'defender',
            'Midfielder': 'midfielder',
            'MIDFIELDER': 'midfielder',
            'MID': 'midfielder',
            'Goalkeeper': 'goalkeeper',
            'GOALKEEPER': 'goalkeeper',
            'GK': 'goalkeeper',
            'Striker': 'striker',
            'STRIKER': 'striker',
            'ST': 'striker',
            'Any': 'any',
            'ANY': 'any',
            'Utility': 'utility',
            'UTILITY': 'utility',
            'UTIL': 'utility'
        }
        
        stats = {'updated': 0, 'skipped': 0, 'errors': 0}
        
        try:
            # Get all players
            players_ref = self.db.collection('players')
            players = players_ref.stream()
            
            for player_doc in players:
                try:
                    player_data = player_doc.to_dict()
                    current_position = player_data.get('position')
                    
                    # Skip if position is already valid
                    if current_position in [pos.value for pos in PlayerPosition]:
                        stats['skipped'] += 1
                        continue
                    
                    # Check if we have a mapping for this position
                    if current_position in position_mapping:
                        new_position = position_mapping[current_position]
                        logger.info(f"🔄 Updating player {player_doc.id}: {current_position} → {new_position}")
                        
                        # Update the document
                        player_doc.reference.update({
                            'position': new_position
                        })
                        stats['updated'] += 1
                    else:
                        # Default to 'utility' for unknown positions
                        logger.warning(f"⚠️ Unknown position '{current_position}' for player {player_doc.id}, defaulting to 'utility'")
                        player_doc.reference.update({
                            'position': 'utility'
                        })
                        stats['updated'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing player {player_doc.id}: {e}")
                    stats['errors'] += 1
                    
        except Exception as e:
            logger.error(f"❌ Error during position cleanup: {e}")
            stats['errors'] += 1
            
        logger.info(f"✅ Position cleanup completed: {stats}")
        return stats
    
    async def cleanup_onboarding_status(self) -> Dict[str, int]:
        """Clean up invalid onboarding status values."""
        logger.info("🔧 Starting onboarding status cleanup...")
        
        # Status mapping for invalid values
        status_mapping = {
            'approved': 'completed',
            'APPROVED': 'completed',
            'complete': 'completed',
            'COMPLETE': 'completed',
            'done': 'completed',
            'DONE': 'completed',
            'finished': 'completed',
            'FINISHED': 'completed',
            'pending': 'pending',
            'PENDING': 'pending',
            'waiting': 'pending',
            'WAITING': 'pending',
            'new': 'pending',
            'NEW': 'pending',
            'in_progress': 'in_progress',
            'IN_PROGRESS': 'in_progress',
            'progress': 'in_progress',
            'PROGRESS': 'in_progress',
            'pending_approval': 'pending_approval',
            'PENDING_APPROVAL': 'pending_approval',
            'failed': 'failed',
            'FAILED': 'failed',
            'error': 'failed',
            'ERROR': 'failed'
        }
        
        stats = {'updated': 0, 'skipped': 0, 'errors': 0}
        
        try:
            # Get all players
            players_ref = self.db.collection('players')
            players = players_ref.stream()
            
            for player_doc in players:
                try:
                    player_data = player_doc.to_dict()
                    current_status = player_data.get('onboarding_status')
                    
                    # Skip if status is already valid
                    if current_status in [status.value for status in OnboardingStatus]:
                        stats['skipped'] += 1
                        continue
                    
                    # Check if we have a mapping for this status
                    if current_status in status_mapping:
                        new_status = status_mapping[current_status]
                        logger.info(f"🔄 Updating player {player_doc.id}: {current_status} → {new_status}")
                        
                        # Update the document
                        player_doc.reference.update({
                            'onboarding_status': new_status
                        })
                        stats['updated'] += 1
                    else:
                        # Default to 'pending' for unknown statuses
                        logger.warning(f"⚠️ Unknown status '{current_status}' for player {player_doc.id}, defaulting to 'pending'")
                        player_doc.reference.update({
                            'onboarding_status': 'pending'
                        })
                        stats['updated'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing player {player_doc.id}: {e}")
                    stats['errors'] += 1
                    
        except Exception as e:
            logger.error(f"❌ Error during status cleanup: {e}")
            stats['errors'] += 1
            
        logger.info(f"✅ Status cleanup completed: {stats}")
        return stats
    
    async def verify_cleanup(self) -> Dict[str, Any]:
        """Verify that all enum values are now valid."""
        logger.info("🔍 Verifying cleanup results...")
        
        try:
            players_ref = self.db.collection('players')
            players = players_ref.stream()
            
            invalid_positions = []
            invalid_statuses = []
            total_players = 0
            
            for player_doc in players:
                total_players += 1
                player_data = player_doc.to_dict()
                
                # Check position
                position = player_data.get('position')
                if position not in [pos.value for pos in PlayerPosition]:
                    invalid_positions.append(f"{player_doc.id}: {position}")
                
                # Check status
                status = player_data.get('onboarding_status')
                if status not in [status.value for status in OnboardingStatus]:
                    invalid_statuses.append(f"{player_doc.id}: {status}")
            
            result = {
                'total_players': total_players,
                'invalid_positions': invalid_positions,
                'invalid_statuses': invalid_statuses,
                'all_valid': len(invalid_positions) == 0 and len(invalid_statuses) == 0
            }
            
            if result['all_valid']:
                logger.info("✅ All enum values are now valid!")
            else:
                logger.warning(f"⚠️ Found {len(invalid_positions)} invalid positions and {len(invalid_statuses)} invalid statuses")
                if invalid_positions:
                    logger.warning(f"Invalid positions: {invalid_positions}")
                if invalid_statuses:
                    logger.warning(f"Invalid statuses: {invalid_statuses}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error during verification: {e}")
            return {'error': str(e)}

async def main():
    """Main cleanup function."""
    logger.info("🚀 Starting database enum cleanup...")
    
    # Initialize Firebase using the same pattern as the main app
    try:
        firebase_admin.get_app()
        logger.info("✅ Using existing Firebase app")
    except ValueError:
        logger.info("🔄 Initializing new Firebase app...")
        
        # Get credentials from environment variables (same as main app)
        import os
        import json
        
        firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
        creds_dict = None
        
        if firebase_creds_json:
            try:
                logger.info("🔄 Using FIREBASE_CREDENTIALS_JSON...")
                creds_dict = json.loads(firebase_creds_json)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Invalid JSON in FIREBASE_CREDENTIALS_JSON: {e}")
        else:
            firebase_creds_file = os.getenv('FIREBASE_CREDENTIALS_FILE')
            if firebase_creds_file:
                try:
                    logger.info(f"🔄 Using FIREBASE_CREDENTIALS_FILE: {firebase_creds_file} ...")
                    with open(firebase_creds_file, 'r') as f:
                        creds_dict = json.load(f)
                except Exception as e:
                    raise RuntimeError(f"Failed to load credentials from file {firebase_creds_file}: {e}")
            else:
                raise RuntimeError("Neither FIREBASE_CREDENTIALS_JSON nor FIREBASE_CREDENTIALS_FILE environment variable is set.")
        
        # Create credentials and initialize app
        try:
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
            logger.info("✅ Firebase app initialized successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase app: {e}")
    
    cleaner = DatabaseEnumCleaner()
    
    # Run cleanup
    position_stats = await cleaner.cleanup_player_positions()
    status_stats = await cleaner.cleanup_onboarding_status()
    
    # Verify results
    verification = await cleaner.verify_cleanup()
    
    # Summary
    logger.info("📊 Cleanup Summary:")
    logger.info(f"  Position updates: {position_stats['updated']}")
    logger.info(f"  Status updates: {status_stats['updated']}")
    logger.info(f"  Total players: {verification.get('total_players', 0)}")
    logger.info(f"  All valid: {verification.get('all_valid', False)}")
    
    if verification.get('all_valid', False):
        logger.info("✅ Database cleanup completed successfully!")
    else:
        logger.warning("⚠️ Some issues remain. Check the logs above.")

if __name__ == "__main__":
    asyncio.run(main()) 