#!/usr/bin/env python3
"""
Robust cleanup script for unused tools.

This script removes unused tool implementations from the codebase.
"""

import os
import re
from pathlib import Path

def remove_tool_from_file(file_path: str, tool_name: str) -> bool:
    """Remove a tool implementation from a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # First, find the @tool decorator
        decorator_pattern = rf'@tool\([\'"]({re.escape(tool_name)})[\'"]\)'
        decorator_match = re.search(decorator_pattern, content)
        
        if not decorator_match:
            print(f"⚠️  Could not find @tool decorator for '{tool_name}' in {file_path}")
            return False
        
        # Find the function definition that follows the decorator
        # Look for the next function definition after the decorator
        decorator_pos = decorator_match.start()
        remaining_content = content[decorator_pos:]
        
        # Find the function definition
        func_pattern = r'@tool\([\'"][^\'"]+[\'"]\)\s*\n\s*def\s+(\w+)\s*\([^)]*\):'
        func_match = re.search(func_pattern, remaining_content)
        
        if not func_match:
            print(f"⚠️  Could not find function definition for '{tool_name}' in {file_path}")
            return False
        
        function_name = func_match.group(1)
        
        # Find the entire function (from decorator to next function or end of file)
        # Look for the next function definition after this one
        function_start = decorator_pos
        function_end = len(content)
        
        # Find the next function definition after this one
        next_func_pattern = rf'\n\s*def\s+\w+\s*\('
        next_func_match = re.search(next_func_pattern, content[function_start + 1:])
        if next_func_match:
            function_end = function_start + 1 + next_func_match.start()
        
        # Extract the function content
        function_content = content[function_start:function_end]
        
        # Remove the function from the original content
        new_content = content[:function_start] + content[function_end:]
        
        # Clean up any extra newlines
        new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Removed tool '{tool_name}' (function: {function_name}) from {file_path}")
        return True
            
    except Exception as e:
        print(f"❌ Error removing tool '{tool_name}' from {file_path}: {e}")
        return False

def main():
    """Main cleanup function."""
    print("🧹 Starting robust unused tool cleanup...")
    
    # List of unused tools to remove with their file paths
    unused_tools_with_files = [
        ("add_player", "kickai/features/player_registration/domain/tools/player_tools.py"),
        ("get_player_match", "kickai/features/player_registration/domain/tools/player_tools.py"),
        ("list_team_members_and_players", "kickai/features/player_registration/domain/tools/player_tools.py"),
        ("create_team", "kickai/features/team_administration/domain/tools/team_management_tools.py"),
        ("get_my_team_member_status", "kickai/features/team_administration/domain/tools/team_member_tools.py"),
        ("get_team_members", "kickai/features/team_administration/domain/tools/team_member_tools.py"),
        ("add_team_member_role", "kickai/features/team_administration/domain/tools/team_member_tools.py"),
        ("remove_team_member_role", "kickai/features/team_administration/domain/tools/team_member_tools.py"),
        ("promote_team_member_to_admin", "kickai/features/team_administration/domain/tools/team_member_tools.py"),
        ("send_telegram_message", "kickai/features/communication/domain/tools/telegram_tools.py"),
        ("get_version_info", "kickai/features/system_infrastructure/domain/tools/help_tools.py"),
        ("get_system_available_commands", "kickai/features/system_infrastructure/domain/tools/help_tools.py"),
        ("log_command", "kickai/features/system_infrastructure/domain/tools/logging_tools.py"),
        ("log_error", "kickai/features/system_infrastructure/domain/tools/logging_tools.py"),
        ("get_firebase_document", "kickai/features/system_infrastructure/domain/tools/firebase_tools.py"),
        ("FINAL_HELP_RESPONSE", "kickai/features/shared/domain/tools/help_tools.py"),
        ("get_new_member_welcome_message", "kickai/features/shared/domain/tools/help_tools.py"),
        ("register_player", "kickai/features/shared/domain/tools/simple_onboarding_tools.py"),
        ("register_team_member", "kickai/features/shared/domain/tools/simple_onboarding_tools.py"),
        ("registration_guidance", "kickai/features/shared/domain/tools/simple_onboarding_tools.py"),
        ("team_member_guidance", "kickai/features/shared/domain/tools/onboarding_tools.py"),
    ]
    
    # Remove each unused tool
    removed_count = 0
    for tool_name, file_path in unused_tools_with_files:
        if remove_tool_from_file(file_path, tool_name):
            removed_count += 1
    
    print(f"✅ Cleanup complete. Removed {removed_count} unused tools.")

if __name__ == "__main__":
    main()
