#!/usr/bin/env python3
"""
Update All Tools with Robust Validation and Error Handling

This script systematically updates all tools in the codebase to use the new
validation and error handling system following CrewAI best practices.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "kickai"))

from loguru import logger


class ToolUpdater:
    """Systematic tool updater for validation and error handling."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "kickai"
        self.tool_files = []
        self.updated_files = []
        self.errors = []
        
    def find_tool_files(self) -> List[Path]:
        """Find all Python files containing @tool decorators."""
        tool_files = []
        
        for py_file in self.base_path.rglob("*.py"):
            if py_file.is_file():
                content = py_file.read_text(encoding='utf-8')
                if "@tool" in content:
                    tool_files.append(py_file)
        
        return tool_files
    
    def get_tool_imports(self, file_path: Path) -> Dict[str, List[str]]:
        """Analyze tool file and determine required imports."""
        content = file_path.read_text(encoding='utf-8')
        
        # Check what validation functions are needed
        needed_validators = []
        
        # Common patterns that indicate what validators are needed
        if "team_id" in content:
            needed_validators.append("validate_team_id")
        if "user_id" in content:
            needed_validators.append("validate_user_id")
        if "telegram_id" in content:
            needed_validators.append("validate_telegram_id")
        if "player_id" in content:
            needed_validators.append("validate_player_id")
        if "phone" in content:
            needed_validators.append("validate_phone_number")
        if "message" in content:
            needed_validators.append("validate_message_content")
        if "match_id" in content:
            needed_validators.append("validate_match_id")
        if "chat_type" in content:
            needed_validators.append("validate_chat_type")
        if "user_role" in content:
            needed_validators.append("validate_user_role")
        if "email" in content:
            needed_validators.append("validate_email")
        
        # Always include core validation functions
        core_validators = [
            "tool_error_handler",
            "validate_context_requirements",
            "log_tool_execution",
            "create_tool_response",
            "ToolValidationError",
            "ToolExecutionError"
        ]
        
        return {
            'validators': needed_validators,
            'core': core_validators
        }
    
    def update_tool_imports(self, file_path: Path) -> bool:
        """Update imports in a tool file."""
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Get required imports
        imports = self.get_tool_imports(file_path)
        
        # Check if validation imports already exist
        if "from kickai.utils.tool_validation import" in content:
            logger.info(f"✅ {file_path.name}: Validation imports already present")
            return False
        
        # Find the tool_helpers import
        tool_helpers_pattern = r'from kickai\.utils\.tool_helpers import\s*\(([^)]*)\)'
        match = re.search(tool_helpers_pattern, content)
        
        if match:
            # Add validation imports after tool_helpers
            validation_import = f"""from kickai.utils.tool_validation import (
    {', '.join(imports['core'])},
    {', '.join(imports['validators'])},
)"""
            
            # Insert after tool_helpers import
            insert_pos = match.end()
            content = content[:insert_pos] + "\n" + validation_import + content[insert_pos:]
        else:
            # Add at the top if no tool_helpers import
            validation_import = f"""from kickai.utils.tool_validation import (
    {', '.join(imports['core'])},
    {', '.join(imports['validators'])},
)"""
            
            # Find the last import statement
            import_pattern = r'^(from|import)\s+.*$'
            lines = content.split('\n')
            last_import_line = 0
            
            for i, line in enumerate(lines):
                if re.match(import_pattern, line.strip()):
                    last_import_line = i
            
            # Insert after last import
            lines.insert(last_import_line + 1, validation_import)
            content = '\n'.join(lines)
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"✅ {file_path.name}: Updated imports")
            return True
        
        return False
    
    def update_tool_function(self, content: str, func_name: str) -> str:
        """Update a single tool function with validation and error handling."""
        # Add @tool_error_handler decorator
        if "@tool_error_handler" not in content:
            content = content.replace("@tool(", "@tool_error_handler\n@tool(")
        
        # Remove try/except blocks and replace with validation
        # This is a simplified approach - in practice, each tool needs custom logic
        return content
    
    def update_tool_file(self, file_path: Path) -> bool:
        """Update a single tool file with validation and error handling."""
        logger.info(f"🔄 Processing {file_path.name}")
        
        try:
            # Update imports
            imports_updated = self.update_tool_imports(file_path)
            
            # For now, just update imports
            # Full function updates would require more complex parsing
            if imports_updated:
                self.updated_files.append(file_path)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error updating {file_path.name}: {e}")
            self.errors.append((file_path, str(e)))
            return False
    
    def run(self):
        """Run the tool updater."""
        logger.info("🚀 Starting tool validation update")
        
        # Find all tool files
        self.tool_files = self.find_tool_files()
        logger.info(f"📁 Found {len(self.tool_files)} tool files")
        
        # Update each file
        for file_path in self.tool_files:
            self.update_tool_file(file_path)
        
        # Summary
        logger.info(f"✅ Updated {len(self.updated_files)} files")
        if self.errors:
            logger.error(f"❌ {len(self.errors)} errors occurred:")
            for file_path, error in self.errors:
                logger.error(f"   {file_path.name}: {error}")
        
        return len(self.updated_files), len(self.errors)


def main():
    """Main function."""
    updater = ToolUpdater()
    updated, errors = updater.run()
    
    if errors == 0:
        logger.info("🎉 All tools updated successfully!")
        return 0
    else:
        logger.error(f"⚠️  {errors} errors occurred during update")
        return 1


if __name__ == "__main__":
    sys.exit(main())



