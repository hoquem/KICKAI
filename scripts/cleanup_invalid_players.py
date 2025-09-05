#!/usr/bin/env python3
"""
Cleanup script to remove invalid Player entries from Firestore.

This script identifies and removes/fixes Player entities that violate data integrity rules:
- Missing player_id (primary key violation) 
- Missing team_id (required field)
- Invalid telegram_id data types
- Invalid enum values for status/position

The script prioritizes data preservation through normalization where possible,
but removes entries with critical violations that cannot be fixed.
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kickai.core.dependency_container import ensure_container_initialized, get_container
from kickai.features.player_registration.domain.entities.player import Player
from kickai.core.enums import PlayerPosition


async def identify_critical_violations(team_id: str = "KTI") -> List[Dict[str, Any]]:
    """
    Identify Player entries with critical violations that must be deleted.
    
    Critical violations:
    - Missing player_id (primary key violation)
    - Missing team_id (required field)
    - Entries that cannot be loaded as Player entities at all
    """
    print(f"🔍 Identifying critical Player violations for team {team_id}...")
    
    # Initialize container
    ensure_container_initialized()
    
    # Get Firebase client from container
    container = get_container()
    client = container.get_service("DataStoreInterface")
    
    # Query all players
    collection_name = f"kickai_{team_id}_players"
    
    try:
        # Get all documents
        all_players = await client.query_documents(
            collection=collection_name,
            filters=[{"field": "team_id", "operator": "==", "value": team_id}]
        )
        
        print(f"📊 Found {len(all_players)} total player entries")
        
        critical_violations = []
        for player_doc in all_players:
            violations = []
            
            # Check for missing player_id (primary key violation)
            player_id = player_doc.get('player_id')
            if not player_id or not str(player_id).strip():
                violations.append("Missing or empty player_id (primary key violation)")
            
            # Check for missing team_id (required field)
            team_id_field = player_doc.get('team_id')
            if not team_id_field or not str(team_id_field).strip():
                violations.append("Missing or empty team_id (required field)")
            
            # Try to create Player entity to check if document is fundamentally broken
            try:
                Player.from_database_dict(player_doc)
            except Exception as e:
                violations.append(f"Cannot create Player entity: {e}")
            
            if violations:
                critical_violations.append({
                    'document': player_doc,
                    'violations': violations,
                    'doc_id': player_doc.get('player_id', f"unknown_{hash(str(player_doc))}")
                })
        
        print(f"❌ Found {len(critical_violations)} entries with critical violations:")
        for i, violation_data in enumerate(critical_violations, 1):
            doc = violation_data['document']
            violations = violation_data['violations']
            print(f"   {i}. {doc.get('name', 'N/A')} (ID: {doc.get('player_id', 'None')}, Telegram: {doc.get('telegram_id', 'None')})")
            for violation in violations:
                print(f"      - {violation}")
        
        return critical_violations
        
    except Exception as e:
        print(f"❌ Error querying players: {e}")
        return []


async def identify_data_type_issues(team_id: str = "KTI") -> List[Dict[str, Any]]:
    """
    Identify Player entries with data type issues that can potentially be fixed.
    
    Data type issues:
    - telegram_id as non-convertible strings
    - Invalid status values
    - Invalid position values
    """
    print(f"🔍 Identifying data type issues for team {team_id}...")
    
    # Get Firebase client from container
    container = get_container()
    client = container.get_service("DataStoreInterface")
    collection_name = f"kickai_{team_id}_players"
    
    try:
        # Get all documents (excluding critical violations)
        all_players = await client.query_documents(
            collection=collection_name,
            filters=[{"field": "team_id", "operator": "==", "value": team_id}]
        )
        
        data_type_issues = []
        valid_statuses = ["pending", "approved", "rejected", "active", "inactive"]
        valid_positions = [pos.value for pos in PlayerPosition]
        
        for player_doc in all_players:
            # Skip entries with critical violations
            player_id = player_doc.get('player_id')
            team_id_field = player_doc.get('team_id')
            if not player_id or not str(player_id).strip() or not team_id_field or not str(team_id_field).strip():
                continue
            
            issues = []
            fixable = True
            
            # Check telegram_id conversion
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
            
            # Check status values
            status = player_doc.get('status')
            if status and status not in valid_statuses:
                if status.lower() in [s.lower() for s in valid_statuses]:
                    issues.append(f"status '{status}' - can normalize case")
                else:
                    issues.append(f"status '{status}' - invalid, will set to 'pending'")
            
            # Check position values
            position = player_doc.get('position')
            if position and position.lower() not in valid_positions:
                if any(position.lower() == pos.lower() for pos in valid_positions):
                    issues.append(f"position '{position}' - can normalize case")
                else:
                    issues.append(f"position '{position}' - invalid, will set to null")
            
            if issues:
                data_type_issues.append({
                    'document': player_doc,
                    'issues': issues,
                    'fixable': fixable,
                    'doc_id': player_doc.get('player_id')
                })
        
        fixable_count = sum(1 for item in data_type_issues if item['fixable'])
        unfixable_count = len(data_type_issues) - fixable_count
        
        print(f"🔧 Found {len(data_type_issues)} entries with data type issues:")
        print(f"   ✅ Fixable: {fixable_count}")
        print(f"   ❌ Unfixable: {unfixable_count}")
        
        for i, issue_data in enumerate(data_type_issues, 1):
            doc = issue_data['document']
            issues = issue_data['issues']
            fixable = "✅" if issue_data['fixable'] else "❌"
            print(f"   {i}. {fixable} {doc.get('name', 'N/A')} (ID: {doc.get('player_id', 'None')})")
            for issue in issues[:2]:  # Show first 2 issues to avoid clutter
                print(f"      - {issue}")
        
        return data_type_issues
        
    except Exception as e:
        print(f"❌ Error analyzing data types: {e}")
        return []


async def attempt_data_normalization(data_type_issues: List[Dict[str, Any]], team_id: str = "KTI", dry_run: bool = True) -> Tuple[int, int]:
    """
    Attempt to fix data type issues through normalization.
    
    Returns: (fixed_count, unfixable_count)
    """
    if not data_type_issues:
        print("✅ No data type issues to normalize")
        return 0, 0
    
    fixable_issues = [item for item in data_type_issues if item['fixable']]
    unfixable_issues = [item for item in data_type_issues if not item['fixable']]
    
    if dry_run:
        print(f"🔧 DRY RUN: Would normalize {len(fixable_issues)} entries")
        print(f"❌ DRY RUN: Would mark {len(unfixable_issues)} entries for deletion")
        return len(fixable_issues), len(unfixable_issues)
    
    print(f"🔧 Normalizing {len(fixable_issues)} entries...")
    
    # Get Firebase client from container
    container = get_container()
    client = container.get_service("DataStoreInterface")
    collection_name = f"kickai_{team_id}_players"
    
    fixed_count = 0
    valid_statuses = ["pending", "approved", "rejected", "active", "inactive"]
    valid_positions = [pos.value for pos in PlayerPosition]
    
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
            
            fixed_count += 1
            print(f"   ✅ Normalized {doc.get('name', 'N/A')} (ID: {doc_id})")
            
        except Exception as e:
            print(f"   ❌ Error normalizing {issue_data['doc_id']}: {e}")
    
    print(f"✅ Successfully normalized {fixed_count} entries")
    return fixed_count, len(unfixable_issues)


async def delete_unfixable_entries(critical_violations: List[Dict[str, Any]], unfixable_issues: List[Dict[str, Any]], team_id: str = "KTI", dry_run: bool = True) -> int:
    """Delete entries that cannot be fixed."""
    all_deletions = critical_violations + unfixable_issues
    
    if not all_deletions:
        print("✅ No entries to delete")
        return 0
    
    if dry_run:
        print(f"🗑️  DRY RUN: Would delete {len(all_deletions)} entries")
        print("   Critical violations:", len(critical_violations))
        print("   Unfixable data issues:", len(unfixable_issues))
        return 0
    
    print(f"🗑️  Deleting {len(all_deletions)} unfixable entries...")
    
    # Get Firebase client from container
    container = get_container()
    client = container.get_service("DataStoreInterface")
    collection_name = f"kickai_{team_id}_players"
    
    deleted_count = 0
    for entry_data in all_deletions:
        try:
            doc_id = entry_data['doc_id']
            doc = entry_data['document']
            
            await client.delete_document(collection=collection_name, document_id=doc_id)
            deleted_count += 1
            print(f"   ✅ Deleted {doc.get('name', 'N/A')} (ID: {doc_id})")
            
        except Exception as e:
            print(f"   ❌ Error deleting {entry_data['doc_id']}: {e}")
    
    print(f"✅ Successfully deleted {deleted_count} entries")
    return deleted_count


async def audit_final_data_quality(team_id: str = "KTI") -> Dict[str, Any]:
    """Audit final Player data quality after cleanup."""
    print(f"🔍 Final audit of Player data quality for team {team_id}...")
    
    # Get Firebase client from container
    container = get_container()
    client = container.get_service("DataStoreInterface")
    collection_name = f"kickai_{team_id}_players"
    
    try:
        # Get all remaining players
        all_players = await client.query_documents(
            collection=collection_name,
            filters=[{"field": "team_id", "operator": "==", "value": team_id}]
        )
        
        print(f"📊 Auditing {len(all_players)} remaining players...")
        
        valid_players = []
        remaining_issues = []
        
        for player_doc in all_players:
            try:
                # Try to create Player entity
                player = Player.from_database_dict(player_doc)
                valid_players.append(player_doc)
                
                # Additional validation checks
                issues = []
                if not player.player_id or not str(player.player_id).strip():
                    issues.append("Missing player_id")
                if not player.team_id or not str(player.team_id).strip():
                    issues.append("Missing team_id")
                
                if issues:
                    remaining_issues.append({
                        'player': player_doc,
                        'issues': issues
                    })
                    
            except Exception as e:
                remaining_issues.append({
                    'player': player_doc,
                    'issues': [f"Cannot create Player entity: {e}"]
                })
        
        print(f"✅ Valid players: {len(valid_players)}")
        print(f"⚠️  Players with remaining issues: {len(remaining_issues)}")
        
        if remaining_issues:
            print("\n⚠️  Remaining data quality issues:")
            for i, issue_data in enumerate(remaining_issues, 1):
                player = issue_data['player']
                issues = issue_data['issues']
                print(f"   {i}. {player.get('name', 'N/A')} (ID: {player.get('player_id', 'None')})")
                for issue in issues:
                    print(f"      - {issue}")
        
        return {
            'total_players': len(all_players),
            'valid_players': len(valid_players),
            'remaining_issues': len(remaining_issues),
            'issue_details': remaining_issues
        }
        
    except Exception as e:
        print(f"❌ Error auditing players: {e}")
        return {
            'total_players': 0,
            'valid_players': 0,
            'remaining_issues': 0,
            'issue_details': []
        }


async def main():
    """Main cleanup function."""
    print("🚀 KICKAI Player Data Cleanup")
    print("=" * 50)
    
    team_id = "KTI"
    
    # Step 1: Identify critical violations
    critical_violations = await identify_critical_violations(team_id)
    
    # Step 2: Identify data type issues
    data_type_issues = await identify_data_type_issues(team_id)
    
    if not critical_violations and not data_type_issues:
        print("✅ No Player data issues found!")
        return
    
    # Step 3: Show what would be done (dry run)
    print("\n🔧 DRY RUN - Preview of operations:")
    fixed_count, unfixable_count = await attempt_data_normalization(data_type_issues, team_id, dry_run=True)
    
    unfixable_data_issues = [item for item in data_type_issues if not item['fixable']]
    total_deletions = len(critical_violations) + len(unfixable_data_issues)
    
    await delete_unfixable_entries(critical_violations, unfixable_data_issues, team_id, dry_run=True)
    
    # Summary
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"   Will normalize: {fixed_count} entries")
    print(f"   Will delete: {total_deletions} entries")
    print(f"     - Critical violations: {len(critical_violations)}")
    print(f"     - Unfixable data issues: {len(unfixable_data_issues)}")
    
    if total_deletions > 0:
        print(f"\n⚠️  This will permanently delete {total_deletions} Player entries from Firestore.")
        confirm = input("Continue with cleanup? (yes/no): ").lower().strip()
        
        if confirm != 'yes':
            print("❌ Cleanup cancelled by user")
            return
    
    # Step 4: Execute actual cleanup
    print("\n" + "=" * 50)
    print("🚀 Executing cleanup operations...")
    
    # Fix data type issues
    actual_fixed, actual_unfixable = await attempt_data_normalization(data_type_issues, team_id, dry_run=False)
    
    # Delete unfixable entries
    actual_deleted = await delete_unfixable_entries(critical_violations, unfixable_data_issues, team_id, dry_run=False)
    
    # Step 5: Final audit
    print("\n" + "=" * 50)
    audit_results = await audit_final_data_quality(team_id)
    
    print(f"\n✅ Player data cleanup completed!")
    print(f"   Normalized entries: {actual_fixed}")
    print(f"   Deleted entries: {actual_deleted}")
    print(f"   Remaining valid players: {audit_results['valid_players']}")
    print(f"   Remaining issues: {audit_results['remaining_issues']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())