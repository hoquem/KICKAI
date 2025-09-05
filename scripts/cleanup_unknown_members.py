#!/usr/bin/env python3
"""
Cleanup script to remove bad 'Unknown' member entries from Firestore.

This script identifies and removes team member entries that have:
- Name: 'Unknown'
- ID: None or missing
- No meaningful member data

These entries pollute the team roster and need to be cleaned up.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kickai.core.dependency_container import ensure_container_initialized, get_container


async def identify_unknown_members(team_id: str = "KTI"):
    """Identify Unknown member entries that need cleanup."""
    print(f"🔍 Identifying Unknown member entries for team {team_id}...")
    
    # Initialize container
    ensure_container_initialized()
    
    # Get Firebase client from container
    container = get_container()
    client = container.get_service("DataStoreInterface")
    
    # Query all team members
    collection_name = f"kickai_{team_id}_team_members"
    
    try:
        # Get all documents
        all_members = await client.query_documents(
            collection=collection_name,
            filters=[{"field": "team_id", "operator": "==", "value": team_id}]
        )
        
        print(f"📊 Found {len(all_members)} total team members")
        
        # Identify Unknown entries
        unknown_entries = []
        for member in all_members:
            # Check for Unknown entries with missing/null data
            if (member.get('name') in ['Unknown'] and 
                (member.get('id') is None or member.get('member_id') is None)):
                unknown_entries.append(member)
        
        print(f"❌ Found {len(unknown_entries)} Unknown entries to clean:")
        for i, entry in enumerate(unknown_entries, 1):
            print(f"   {i}. Name: {entry.get('name', 'N/A')}, ID: {entry.get('id', 'None')}, Member ID: {entry.get('member_id', 'None')}")
        
        return unknown_entries
        
    except Exception as e:
        print(f"❌ Error querying team members: {e}")
        return []


async def delete_unknown_entries(unknown_entries: list, team_id: str = "KTI", dry_run: bool = True):
    """Delete the identified Unknown entries."""
    if not unknown_entries:
        print("✅ No Unknown entries to delete")
        return
    
    if dry_run:
        print(f"🔧 DRY RUN: Would delete {len(unknown_entries)} Unknown entries")
        return
    
    print(f"🗑️  Deleting {len(unknown_entries)} Unknown entries...")
    
    # Get Firebase client from container
    container = get_container()
    client = container.get_service("DataStoreInterface")
    collection_name = f"kickai_{team_id}_team_members"
    
    deleted_count = 0
    for entry in unknown_entries:
        try:
            # Use the document ID from Firestore
            doc_id = entry.get('id')
            if doc_id:
                await client.delete_document(collection=collection_name, document_id=doc_id)
                deleted_count += 1
                print(f"   ✅ Deleted entry with ID: {doc_id}")
            else:
                print(f"   ⚠️  Skipped entry - no document ID found")
        except Exception as e:
            print(f"   ❌ Error deleting entry {entry.get('id', 'unknown')}: {e}")
    
    print(f"✅ Successfully deleted {deleted_count} Unknown entries")


async def audit_remaining_data(team_id: str = "KTI"):
    """Audit remaining team member data for integrity."""
    print(f"🔍 Auditing remaining team member data for team {team_id}...")
    
    # Get Firebase client from container
    container = get_container()
    client = container.get_service("DataStoreInterface")
    collection_name = f"kickai_{team_id}_team_members"
    
    try:
        # Get all remaining members
        all_members = await client.query_documents(
            collection=collection_name,
            filters=[{"field": "team_id", "operator": "==", "value": team_id}]
        )
        
        print(f"📊 Auditing {len(all_members)} remaining members...")
        
        issues = []
        valid_members = []
        
        for member in all_members:
            member_issues = []
            
            # Check essential fields
            if not member.get('name') or member.get('name') == 'Unknown':
                member_issues.append("Missing or invalid name")
            
            if not member.get('id'):
                member_issues.append("Missing document ID")
                
            if not member.get('member_id'):
                member_issues.append("Missing member_id")
                
            if not member.get('role'):
                member_issues.append("Missing role")
                
            if not member.get('status'):
                member_issues.append("Missing status")
            
            if member_issues:
                issues.append({
                    'member': member,
                    'issues': member_issues
                })
            else:
                valid_members.append(member)
        
        print(f"✅ Valid members: {len(valid_members)}")
        print(f"⚠️  Members with issues: {len(issues)}")
        
        if issues:
            print("\n⚠️  Data quality issues found:")
            for i, issue_data in enumerate(issues, 1):
                member = issue_data['member']
                member_issues = issue_data['issues']
                print(f"   {i}. {member.get('name', 'N/A')} (ID: {member.get('id', 'None')})")
                for issue in member_issues:
                    print(f"      - {issue}")
        
        return {'valid': valid_members, 'issues': issues}
        
    except Exception as e:
        print(f"❌ Error auditing team members: {e}")
        return {'valid': [], 'issues': []}


async def main():
    """Main cleanup function."""
    print("🚀 KICKAI Team Member Data Cleanup")
    print("=" * 50)
    
    team_id = "KTI"
    
    # Step 1: Identify Unknown entries
    unknown_entries = await identify_unknown_members(team_id)
    
    if not unknown_entries:
        print("✅ No Unknown entries found to clean up")
    else:
        # Step 2: Show what would be deleted (dry run)
        print("\n🔧 DRY RUN - Preview of deletions:")
        await delete_unknown_entries(unknown_entries, team_id, dry_run=True)
        
        # Confirm deletion
        print(f"\n⚠️  This will permanently delete {len(unknown_entries)} Unknown entries from Firestore.")
        confirm = input("Continue with deletion? (yes/no): ").lower().strip()
        
        if confirm == 'yes':
            # Step 3: Actually delete the entries
            await delete_unknown_entries(unknown_entries, team_id, dry_run=False)
        else:
            print("❌ Deletion cancelled by user")
            return
    
    # Step 4: Audit remaining data
    print("\n" + "=" * 50)
    audit_results = await audit_remaining_data(team_id)
    
    print(f"\n✅ Cleanup completed!")
    print(f"   Valid members: {len(audit_results['valid'])}")
    print(f"   Members with issues: {len(audit_results['issues'])}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())