#!/usr/bin/env python3
"""
Comprehensive Tool Migration Script

This script migrates all KICKAI tools from string output to JSON output
to resolve LLM parsing issues while maintaining human-friendly UI display.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import re

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kickai.utils.json_response import create_data_response, create_error_response
from kickai.utils.ui_formatter import UIFormatBuilder


class ToolMigrator:
    """Comprehensive tool migration system."""
    
    def __init__(self):
        self.migrated_tools = []
        self.failed_tools = []
        self.tool_patterns = {
            'player_tools': {
                'file': 'kickai/features/player_registration/domain/tools/player_tools.py',
                'tools': [
                    'approve_player',
                    'get_my_status', 
                    'get_player_status',
                    'get_all_players',
                    'get_active_players',
                    'get_player_match',
                    'list_team_members_and_players'
                ]
            },
            'team_tools': {
                'file': 'kickai/features/team_administration/domain/tools/team_member_tools.py',
                'tools': [
                    'team_member_registration',
                    'get_my_team_member_status',
                    'get_team_members',
                    'add_team_member_role',
                    'remove_team_member_role',
                    'promote_team_member_to_admin',
                    'update_team_member_information',
                    'get_team_member_updatable_fields',
                    'validate_team_member_update_request',
                    'get_pending_team_member_approval_requests',
                    'create_team'
                ]
            },
            'match_tools': {
                'file': 'kickai/features/match_management/domain/tools/match_tools.py',
                'tools': [
                    'list_matches',
                    'create_match',
                    'list_matches_sync',
                    'get_match_details',
                    'select_squad_tool',
                    'record_match_result',
                    'record_attendance',
                    'get_match_attendance',
                    'get_player_attendance_history',
                    'bulk_record_attendance',
                    'mark_availability',
                    'get_availability'
                ]
            },
            'communication_tools': {
                'file': 'kickai/features/communication/domain/tools/communication_tools.py',
                'tools': [
                    'send_message',
                    'send_announcement',
                    'send_poll',
                    'send_telegram_message'
                ]
            },
            'system_tools': {
                'file': 'kickai/features/system_infrastructure/domain/tools/system_tools.py',
                'tools': [
                    'get_version_info',
                    'get_system_available_commands',
                    'get_user_status',
                    'ping',
                    'version',
                    'get_firebase_document',
                    'log_command',
                    'log_error'
                ]
            },
            'help_tools': {
                'file': 'kickai/features/shared/domain/tools/help_tools.py',
                'tools': [
                    'FINAL_HELP_RESPONSE',
                    'get_available_commands',
                    'get_command_help',
                    'get_welcome_message',
                    'register_player',
                    'register_team_member'
                ]
            }
        }
    
    def migrate_all_tools(self):
        """Migrate all tools to JSON output."""
        print("🚀 Starting comprehensive tool migration to JSON output")
        print("=" * 60)
        
        total_tools = sum(len(category['tools']) for category in self.tool_patterns.values())
        migrated_count = 0
        
        for category_name, category_info in self.tool_patterns.items():
            print(f"\n📁 Migrating {category_name} tools...")
            print("-" * 40)
            
            file_path = category_info['file']
            tools = category_info['tools']
            
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_path}")
                continue
            
            for tool_name in tools:
                try:
                    success = self.migrate_single_tool(file_path, tool_name)
                    if success:
                        migrated_count += 1
                        self.migrated_tools.append(f"{category_name}.{tool_name}")
                        print(f"✅ {tool_name}")
                    else:
                        self.failed_tools.append(f"{category_name}.{tool_name}")
                        print(f"❌ {tool_name}")
                except Exception as e:
                    self.failed_tools.append(f"{category_name}.{tool_name}")
                    print(f"❌ {tool_name} - Error: {e}")
        
        print("\n" + "=" * 60)
        print(f"🎉 Migration Complete!")
        print(f"✅ Successfully migrated: {migrated_count}/{total_tools} tools")
        print(f"❌ Failed migrations: {len(self.failed_tools)}")
        
        if self.failed_tools:
            print(f"\nFailed tools:")
            for tool in self.failed_tools:
                print(f"  - {tool}")
        
        return migrated_count, len(self.failed_tools)
    
    def migrate_single_tool(self, file_path: str, tool_name: str) -> bool:
        """Migrate a single tool to JSON output."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the tool function
            tool_pattern = rf'@tool\("{tool_name}"\)\s*\n(?:@tool_error_handler\s*\n)?def {tool_name}\([^)]*\)\s*->\s*str:'
            match = re.search(tool_pattern, content, re.MULTILINE)
            
            if not match:
                print(f"  ⚠️  Tool {tool_name} not found in {file_path}")
                return False
            
            # Replace @tool with @json_tool
            content = re.sub(
                rf'@tool\("{tool_name}"\)',
                f'@json_tool("{tool_name}")',
                content
            )
            
            # Update function signature to return dict
            content = re.sub(
                rf'def {tool_name}\([^)]*\)\s*->\s*str:',
                f'def {tool_name}(\\g<0>[:-3]dict:',
                content
            )
            
            # Update docstring
            content = re.sub(
                rf'def {tool_name}\([^)]*\)\s*->\s*dict:\s*\n\s*"""[^"]*Returns:\s*[^"]*""',
                f'def {tool_name}(\\g<0>[:-3]dict:\n    """\n    {tool_name} tool with JSON output.\n    \n    Returns:\n        JSON response with structured data and UI format\n    """',
                content
            )
            
            # Add imports if not present
            if 'from kickai.utils.json_response import create_data_response, create_error_response' not in content:
                content = self.add_json_imports(content)
            
            # Write back the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error migrating {tool_name}: {e}")
            return False
    
    def add_json_imports(self, content: str) -> str:
        """Add JSON response imports to the file."""
        import_pattern = r'from kickai\.utils\.crewai_tool_decorator import tool'
        replacement = '''from kickai.utils.crewai_tool_decorator import json_tool
from kickai.utils.json_response import create_data_response, create_error_response
from kickai.utils.ui_formatter import UIFormatBuilder'''
        
        content = re.sub(import_pattern, replacement, content)
        return content
    
    def create_migration_template(self, tool_name: str, category: str) -> str:
        """Create a migration template for a tool."""
        template = f'''
@json_tool("{tool_name}")
def {tool_name}(*args, **kwargs) -> dict:
    """
    {tool_name} tool with JSON output.
    
    Returns:
        JSON response with structured data and UI format
    """
    try:
        # TODO: Implement tool logic here
        # Extract data from service calls
        data = {{
            'tool_name': '{tool_name}',
            'category': '{category}',
            'status': 'success',
            'data': {{}}
        }}
        
        # Generate UI format
        ui_format = f"✅ {tool_name} completed successfully"
        
        return create_data_response(data, ui_format)
        
    except Exception as e:
        return create_error_response(str(e), f"{tool_name} failed")
'''
        return template


def main():
    """Main migration function."""
    migrator = ToolMigrator()
    
    print("🧪 Tool Migration to JSON Output")
    print("=" * 50)
    print("This script will migrate all KICKAI tools to JSON output")
    print("to resolve LLM parsing issues.")
    print()
    
    # Run migration
    success_count, failure_count = migrator.migrate_all_tools()
    
    print(f"\n📊 Migration Summary:")
    print(f"✅ Successfully migrated: {success_count} tools")
    print(f"❌ Failed migrations: {failure_count} tools")
    
    if success_count > 0:
        print(f"\n🎯 Next steps:")
        print(f"1. Test migrated tools with LLM providers")
        print(f"2. Verify UI formatting works correctly")
        print(f"3. Update any remaining tools manually")
        print(f"4. Run comprehensive testing suite")


if __name__ == "__main__":
    main()
