#!/usr/bin/env python3
"""
Setup Fixtures Database
=======================

This script sets up the fixtures table in Supabase for KICKAI.
Run this after deploying the fixture management system.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from tools.supabase_tools import create_supabase_client

def setup_fixtures_table():
    """Set up the fixtures table in Supabase."""
    print("🏆 Setting up Fixtures Table in Supabase")
    print("=" * 50)
    
    try:
        # Create Supabase client
        print("🔧 Connecting to Supabase...")
        supabase = create_supabase_client()
        print("✅ Connected to Supabase")
        
        # Read SQL script
        print("📖 Reading SQL script...")
        sql_file = Path(__file__).parent / 'setup_fixtures_table.sql'
        
        if not sql_file.exists():
            print("❌ SQL file not found: setup_fixtures_table.sql")
            return False
        
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        print("✅ SQL script loaded")
        
        # Execute SQL script
        print("🚀 Executing SQL script...")
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"  Executing statement {i}/{len(statements)}...")
                try:
                    # Execute the statement
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"  ✅ Statement {i} executed successfully")
                except Exception as e:
                    print(f"  ⚠️  Statement {i} failed (may already exist): {e}")
        
        print("✅ Database setup completed!")
        
        # Verify table exists
        print("🔍 Verifying fixtures table...")
        try:
            result = supabase.table('fixtures').select('count', count='exact').execute()
            count = result.count
            print(f"✅ Fixtures table verified - {count} records found")
        except Exception as e:
            print(f"❌ Error verifying table: {e}")
            return False
        
        print("\n🎉 Fixtures table setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Deploy the updated code to Railway")
        print("2. Test the /newfixture command in your leadership chat")
        print("3. Test the /listfixtures command")
        print("4. Check that fixtures are saved to the database")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up fixtures table: {e}")
        return False

if __name__ == "__main__":
    success = setup_fixtures_table()
    sys.exit(0 if success else 1) 