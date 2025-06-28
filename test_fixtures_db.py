#!/usr/bin/env python3
"""
Test Fixtures Database
Quick test to verify fixtures table exists and works
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_fixtures_table():
    """Test if fixtures table exists and works."""
    print("🔍 Testing Fixtures Database")
    print("=" * 30)
    
    try:
        from tools.supabase_tools import get_supabase_client
        
        # Create Supabase client
        print("🔧 Connecting to Supabase...")
        supabase = get_supabase_client()
        print("✅ Connected to Supabase")
        
        # Test fixtures table
        print("\n📅 Testing fixtures table...")
        response = supabase.table('fixtures').select('*').limit(5).execute()
        
        if response.data:
            print(f"✅ Fixtures table exists - {len(response.data)} fixtures found")
            for fixture in response.data:
                print(f"   • {fixture['opponent']} on {fixture['match_date']}")
        else:
            print("⚠️  Fixtures table exists but no data found")
            
        # Test team_id query
        print("\n🔍 Testing team-specific query...")
        team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
        response = supabase.table('fixtures').select('*').eq('team_id', team_id).execute()
        
        if response.data:
            print(f"✅ Team fixtures found - {len(response.data)} fixtures")
        else:
            print("⚠️  No fixtures found for team")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing fixtures table: {e}")
        return False

if __name__ == "__main__":
    success = test_fixtures_table()
    sys.exit(0 if success else 1)
