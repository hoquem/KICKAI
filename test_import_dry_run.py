#!/usr/bin/env python3
"""
Test script for dry run of GitHub tasks import
"""

import os
import sys
from import_github_tasks import GitHubTaskImporter

def test_dry_run():
    """Test the import process in dry run mode"""
    print("🧪 Testing GitHub Tasks Import (Dry Run)")
    print("========================================")
    
    # Check if the import file exists
    file_path = "github_project_import.md"
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found!")
        return False
    
    # Create a test importer (we won't actually use the GitHub API)
    test_importer = GitHubTaskImporter("test-owner", "test-repo", "test-token")
    
    try:
        # Test parsing the markdown file
        print(f"📖 Reading tasks from {file_path}...")
        tasks = test_importer.parse_tasks_from_markdown(file_path)
        
        print(f"📋 Found {len(tasks)} tasks to import")
        
        if not tasks:
            print("❌ No tasks found in the file!")
            return False
        
        # Display first few tasks as examples
        print("\n📝 Sample tasks found:")
        for i, task in enumerate(tasks[:3], 1):
            print(f"\n{i}. {task.get('title', 'No title')}")
            print(f"   Description: {task.get('description', 'No description')[:100]}...")
            print(f"   Labels: {', '.join(task.get('labels', []))}")
            print(f"   Column: {task.get('column', 'Not specified')}")
            
            if task.get('checklist'):
                print(f"   Checklist items: {len(task['checklist'])}")
        
        if len(tasks) > 3:
            print(f"\n... and {len(tasks) - 3} more tasks")
        
        # Test issue body formatting for first task
        if tasks:
            print(f"\n📄 Sample issue body for first task:")
            sample_body = test_importer.format_issue_body(tasks[0])
            print("=" * 50)
            print(sample_body[:500] + "..." if len(sample_body) > 500 else sample_body)
            print("=" * 50)
        
        print(f"\n✅ Dry run completed successfully!")
        print(f"   Total tasks found: {len(tasks)}")
        print(f"   File format: ✅ Valid")
        print(f"   Parsing: ✅ Working")
        print(f"   Body formatting: ✅ Working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during dry run: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dry_run()
    sys.exit(0 if success else 1) 