#!/usr/bin/env python3
"""
Migration Script: Player Registration Handler to Modular System

This script helps migrate from the massive player_registration_handler.py (90KB, 2005 lines)
to the new modular command parsing system.

The new system provides:
- Clean command parsing using a dedicated parser
- Modular handlers with single responsibility
- Base handler for common functionality
- Better error handling and logging
- Easier testing and maintenance
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def main():
    """Main migration function."""
    print("🔄 KICKAI Player Registration Handler Migration")
    print("=" * 50)
    
    # Check current structure
    current_handler = Path("src/telegram/player_registration_handler.py")
    new_handlers_dir = Path("src/telegram/handlers")
    
    if not current_handler.exists():
        print("❌ Current player_registration_handler.py not found!")
        return False
    
    print(f"📁 Current handler: {current_handler} ({current_handler.stat().st_size / 1024:.1f}KB)")
    
    # Create backup
    backup_path = current_handler.with_suffix(f".py.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    print(f"💾 Creating backup: {backup_path}")
    shutil.copy2(current_handler, backup_path)
    
    # Create new directory structure
    print("\n📂 Creating new modular structure...")
    new_handlers_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    (new_handlers_dir / "__init__.py").touch()
    
    # Check if new files exist
    new_files = [
        "src/telegram/command_parser.py",
        "src/telegram/handlers/base_handler.py", 
        "src/telegram/handlers/player_registration_handler.py",
        "src/telegram/modular_message_handler.py"
    ]
    
    missing_files = []
    for file_path in new_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing new files: {missing_files}")
        print("Please ensure all new modular files are created before running migration.")
        return False
    
    print("✅ All new modular files found!")
    
    # Create integration guide
    create_integration_guide()
    
    # Create test migration
    create_test_migration()
    
    print("\n🎉 Migration preparation complete!")
    print("\n📋 Next steps:")
    print("1. Update your bot's message handler to use the new modular system")
    print("2. Test the new system with a small subset of commands")
    print("3. Gradually migrate all commands to the new system")
    print("4. Remove the old player_registration_handler.py when confident")
    
    return True

def create_integration_guide():
    """Create an integration guide for the new system."""
    guide_content = """# KICKAI Modular Handler Integration Guide

## Overview

This guide helps you integrate the new modular command handling system into your existing KICKAI bot.

## What Changed

### Old System (player_registration_handler.py)
- ❌ 90KB, 2005 lines in a single file
- ❌ Complex regex patterns scattered throughout
- ❌ Hard to maintain and test
- ❌ Mixed concerns (parsing, handling, validation)

### New System (Modular)
- ✅ Clean separation of concerns
- ✅ Dedicated command parser
- ✅ Base handler for common functionality
- ✅ Specialized handlers for different command types
- ✅ Better error handling and logging
- ✅ Easier testing and maintenance

## New File Structure

```
src/telegram/
├── command_parser.py              # Clean command parsing
├── modular_message_handler.py     # Main message router
└── handlers/
    ├── base_handler.py            # Common handler functionality
    └── player_registration_handler.py  # Player-specific commands
```

## Integration Steps

### 1. Update Your Bot's Message Handler

Replace your current message handler with the new modular system:

```python
# OLD: Direct import of massive handler
from src.telegram.player_registration_handler import handle_message

# NEW: Use modular system
from src.telegram.modular_message_handler import handle_message
```

### 2. Update Command Handlers

```python
# OLD: Complex regex matching
import re
match = re.match(r'/add\s+(.+?)\s+((?:\+|0)7\d{9,10})\s+(\w+)(?:\s+(true|yes|y))?', text)

# NEW: Clean command parsing
from src.telegram.command_parser import parse_command
parsed_command = parse_command(text)
if parsed_command.command_type == CommandType.ADD_PLAYER:
    # Handle add player command
```

### 3. Add New Command Types

To add new commands, simply:

1. Add to CommandType enum in command_parser.py
2. Add command definition with patterns and parameters
3. Create handler method in appropriate handler class
4. Route in modular_message_handler.py

### 4. Testing

The new system is much easier to test:

```python
# Test command parsing
from src.telegram.command_parser import parse_command
result = parse_command("/add John Smith +447123456789 midfielder")
assert result.command_type == CommandType.ADD_PLAYER
assert result.parameters["name"] == "John Smith"

# Test handlers
from src.telegram.handlers.player_registration_handler import PlayerRegistrationHandler
handler = PlayerRegistrationHandler()
result = await handler.handle(context, parsed_command=result)
```

## Benefits

1. **Maintainability**: Each handler has a single responsibility
2. **Testability**: Easy to unit test individual components
3. **Extensibility**: Easy to add new commands and handlers
4. **Error Handling**: Consistent error handling across all commands
5. **Logging**: Comprehensive logging with context
6. **Documentation**: Self-documenting command definitions

## Migration Checklist

- [ ] Backup current player_registration_handler.py
- [ ] Update bot to use new modular_message_handler.py
- [ ] Test basic commands (/start, /help, /register)
- [ ] Test player management commands (/add, /remove, /approve)
- [ ] Test list commands (/list, /pending, /status)
- [ ] Verify error handling works correctly
- [ ] Check logging output
- [ ] Remove old handler when confident

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all new files are in the correct locations
2. **Command Not Recognized**: Check command patterns in command_parser.py
3. **Handler Not Found**: Verify routing in modular_message_handler.py
4. **Parameter Validation**: Check parameter definitions in command_parser.py

### Getting Help

- Check the command parser logs for parsing issues
- Check handler logs for execution issues
- Use the help system: `/help` and `/help [command]`
"""
    
    guide_path = Path("MIGRATION_GUIDE.md")
    with open(guide_path, 'w') as f:
        f.write(guide_content)
    
    print(f"📖 Created integration guide: {guide_path}")

def create_test_migration():
    """Create a test script to verify the migration."""
    test_content = """#!/usr/bin/env python3
\"\"\"
Test Migration Script

This script tests the new modular command handling system to ensure
it works correctly before fully migrating.
\"\"\"

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telegram.command_parser import parse_command, CommandType
from telegram.handlers.base_handler import HandlerContext, HandlerResult
from telegram.handlers.player_registration_handler import PlayerRegistrationHandler

async def test_command_parsing():
    \"\"\"Test command parsing functionality.\"\"\"
    print("🧪 Testing Command Parsing...")
    
    test_commands = [
        "/start",
        "/help",
        "/register John Smith +447123456789 midfielder",
        "/add Jane Doe 07123456789 defender true",
        "/remove +447123456789",
        "/approve JS1",
        "/reject JS1 Not available",
        "/invite +447123456789",
        "/status +447123456789",
        "/list",
        "/list pending",
        "/pending"
    ]
    
    for command in test_commands:
        try:
            parsed = parse_command(command)
            print(f"✅ {command} -> {parsed.command_type.value}")
            if parsed.parameters:
                print(f"   Parameters: {parsed.parameters}")
        except Exception as e:
            print(f"❌ {command} -> Error: {e}")
    
    print()

async def test_handler_creation():
    \"\"\"Test handler creation and basic functionality.\"\"\"
    print("🧪 Testing Handler Creation...")
    
    try:
        handler = PlayerRegistrationHandler()
        print("✅ PlayerRegistrationHandler created successfully")
        
        # Test context creation
        context = HandlerContext(
            user_id="123456",
            chat_id="789012",
            team_id="test_team"
        )
        print("✅ HandlerContext created successfully")
        
    except Exception as e:
        print(f"❌ Handler creation failed: {e}")
    
    print()

async def test_help_system():
    \"\"\"Test the help system.\"\"\"
    print("🧪 Testing Help System...")
    
    try:
        from telegram.command_parser import get_help_text
        
        # Test general help
        general_help = get_help_text()
        print("✅ General help generated")
        print(f"   Length: {len(general_help)} characters")
        
        # Test specific command help
        add_help = get_help_text(CommandType.ADD_PLAYER)
        print("✅ Add player help generated")
        print(f"   Length: {len(add_help)} characters")
        
    except Exception as e:
        print(f"❌ Help system failed: {e}")
    
    print()

async def main():
    \"\"\"Run all tests.\"\"\"
    print("🚀 Testing New Modular System")
    print("=" * 40)
    
    await test_command_parsing()
    await test_handler_creation()
    await test_help_system()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    test_path = Path("test_modular_migration.py")
    with open(test_path, 'w') as f:
        f.write(test_content)
    
    # Make it executable
    test_path.chmod(0o755)
    
    print(f"🧪 Created test script: {test_path}")
    print("   Run with: python test_modular_migration.py")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 