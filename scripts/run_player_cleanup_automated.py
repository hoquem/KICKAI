#!/usr/bin/env python3
"""
Automated Player Data Cleanup Script - Non-interactive version for CI/CD.

This script automatically proceeds with cleanup without user confirmation.
It identifies and fixes Player entities with data type issues.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kickai.core.dependency_container import ensure_container_initialized, get_container
from kickai.features.player_registration.domain.entities.player import Player
from kickai.core.enums import PlayerPosition


async def automated_player_cleanup(team_id: str = "KTI") -> dict:
    """
    Automated player data cleanup without user interaction.
    
    Returns:
        dict: Cleanup results summary
    """
    print("🚀 KICKAI Automated Player Data Cleanup")
    print("=" * 50)
    
    # Initialize container
    ensure_container_initialized()
    container = get_container()
    client = container.get_service("DataStoreInterface")
    collection_name = f"kickai_{team_id}_players"
    
    results = {
        "total_players": 0,
        "critical_violations": 0,
        "fixable_issues": 0,
        "fixed_count": 0,
        "deleted_count": 0,
        "remaining_valid": 0,
        "execution_time": 0
    }
    
    start_time = datetime.now()
    
    try:
        # Step 1: Get all players
        all_players = await client.query_documents(
            collection=collection_name,
            filters=[{"field": "team_id", "operator": "==", "value": team_id}]
        )
        
        results["total_players"] = len(all_players)
        print(f"📊 Found {len(all_players)} total player entries")
        
        # Step 2: Identify issues
        critical_violations = []
        fixable_issues = []
        unfixable_issues = []
        
        valid_statuses = ["pending", "approved", "rejected", "active", "inactive"]
        valid_positions = [pos.value for pos in PlayerPosition]
        
        for player_doc in all_players:
            violations = []
            issues = []
            fixable = True
            
            # Check for critical violations (missing primary key or team_id)
            player_id = player_doc.get('player_id')
            team_id_field = player_doc.get('team_id')
            
            if not player_id or not str(player_id).strip():
                violations.append("Missing or empty player_id (primary key violation)")
            if not team_id_field or not str(team_id_field).strip():
                violations.append("Missing or empty team_id (required field)")
            
            # Try to create Player entity
            try:
                Player.from_database_dict(player_doc)
            except Exception as e:
                violations.append(f"Cannot create Player entity: {e}")
            
            # If critical violations, mark for deletion
            if violations:
                critical_violations.append({
                    'document': player_doc,
                    'violations': violations,
                    'doc_id': player_doc.get('player_id', f"unknown_{hash(str(player_doc))}")
                })
                continue
            
            # Check data type issues that can be fixed
            # telegram_id conversion
            telegram_id = player_doc.get('telegram_id')
            if telegram_id is not None:
                try:
                    if isinstance(telegram_id, str):
                        int(telegram_id)  # Test conversion
                        issues.append(f"telegram_id is string '{telegram_id}' - can convert to int")
                    elif not isinstance(telegram_id, int):
                        issues.append(f"telegram_id has invalid type {type(telegram_id)} - cannot fix")
                        fixable = False
                except (ValueError, TypeError):
                    issues.append(f"telegram_id string '{telegram_id}' cannot convert to int - cannot fix")
                    fixable = False
            
            # status validation
            status = player_doc.get('status')
            if status and status not in valid_statuses:
                if status.lower() in [s.lower() for s in valid_statuses]:
                    issues.append(f"status '{status}' - can normalize case")
                else:
                    issues.append(f"status '{status}' - invalid, will set to 'pending'")
            
            # position validation
            position = player_doc.get('position')
            if position and position.lower() not in valid_positions:
                if any(position.lower() == pos.lower() for pos in valid_positions):
                    issues.append(f"position '{position}' - can normalize case")
                else:
                    issues.append(f"position '{position}' - invalid, will set to null")
            
            if issues:
                if fixable:
                    fixable_issues.append({
                        'document': player_doc,
                        'issues': issues,
                        'doc_id': player_doc.get('player_id')
                    })
                else:
                    unfixable_issues.append({
                        'document': player_doc,
                        'issues': issues,
                        'doc_id': player_doc.get('player_id')
                    })
        
        results["critical_violations"] = len(critical_violations)
        results["fixable_issues"] = len(fixable_issues)
        
        print(f"❌ Found {len(critical_violations)} entries with critical violations")
        print(f"🔧 Found {len(fixable_issues)} entries with fixable issues")
        print(f"❌ Found {len(unfixable_issues)} entries with unfixable issues")
        
        # Step 3: Fix data type issues
        if fixable_issues:
            print(f"🔧 Fixing {len(fixable_issues)} entries...")
            
            for issue_data in fixable_issues:
                try:
                    doc = issue_data['document'].copy()
                    doc_id = issue_data['doc_id']
                    
                    # Fix telegram_id conversion
                    telegram_id = doc.get('telegram_id')
                    if telegram_id is not None and isinstance(telegram_id, str):
                        try:
                            doc['telegram_id'] = int(telegram_id)
                        except (ValueError, TypeError):
                            pass  # Skip this fix if conversion fails
                    
                    # Fix status case normalization
                    status = doc.get('status')
                    if status:
                        normalized_status = None
                        for valid_status in valid_statuses:
                            if status.lower() == valid_status.lower():
                                normalized_status = valid_status
                                break
                        if normalized_status:
                            doc['status'] = normalized_status
                        elif status not in valid_statuses:
                            doc['status'] = 'pending'  # Default fallback
                    
                    # Fix position case normalization
                    position = doc.get('position')
                    if position:
                        normalized_position = None
                        for valid_position in valid_positions:
                            if position.lower() == valid_position.lower():
                                normalized_position = valid_position
                                break
                        if normalized_position:
                            doc['position'] = normalized_position
                        elif position.lower() not in valid_positions:
                            doc['position'] = None  # Remove invalid position
                    
                    # Update the document
                    await client.update_document(
                        collection=collection_name,
                        document_id=doc_id,
                        data=doc
                    )
                    
                    results["fixed_count"] += 1
                    print(f"   ✅ Fixed {doc.get('name', 'N/A')} (ID: {doc_id})")
                    
                except Exception as e:
                    print(f"   ❌ Error fixing {issue_data['doc_id']}: {e}")
        
        # Step 4: Delete unfixable entries
        all_deletions = critical_violations + unfixable_issues
        if all_deletions:
            print(f"🗑️  Deleting {len(all_deletions)} unfixable entries...")
            
            for entry_data in all_deletions:
                try:
                    doc_id = entry_data['doc_id']
                    doc = entry_data['document']
                    
                    await client.delete_document(collection=collection_name, document_id=doc_id)
                    results["deleted_count"] += 1
                    print(f"   ✅ Deleted {doc.get('name', 'N/A')} (ID: {doc_id})")
                    
                except Exception as e:
                    print(f"   ❌ Error deleting {entry_data['doc_id']}: {e}")
        
        # Step 5: Final verification
        remaining_players = await client.query_documents(
            collection=collection_name,
            filters=[{"field": "team_id", "operator": "==", "value": team_id}]
        )
        
        valid_count = 0
        for player_doc in remaining_players:
            try:
                Player.from_database_dict(player_doc)
                valid_count += 1
            except Exception:
                pass
        
        results["remaining_valid"] = valid_count
        end_time = datetime.now()
        results["execution_time"] = (end_time - start_time).total_seconds()
        
        # Summary
        print("\n" + "=" * 50)
        print("✅ Player data cleanup completed!")
        print(f"   Total players processed: {results['total_players']}")
        print(f"   Fixed entries: {results['fixed_count']}")
        print(f"   Deleted entries: {results['deleted_count']}")
        print(f"   Remaining valid players: {results['remaining_valid']}")
        print(f"   Execution time: {results['execution_time']:.2f}s")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        results["error"] = str(e)
        return results


if __name__ == "__main__":
    results = asyncio.run(automated_player_cleanup())
    
    # Exit with appropriate code
    if "error" in results:
        sys.exit(1)
    elif results["fixed_count"] > 0 or results["deleted_count"] > 0:
        print(f"\n🎉 Cleanup successful: {results['fixed_count']} fixed, {results['deleted_count']} deleted")
        sys.exit(0)
    else:
        print("\n✅ No cleanup needed - all players valid")
        sys.exit(0)