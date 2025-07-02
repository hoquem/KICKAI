#!/usr/bin/env python3
"""
Bot Configuration Management CLI

This script provides a command-line interface for managing bot configurations
across different environments (testing, staging, production).

# NOTE: This script is for local setup only. Do not use file-based credential loading at runtime.
# All runtime Firebase credential loading must use environment variables only.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.bot_config_manager import (
    get_bot_config_manager, ChatType, BotConfig, TeamConfig, BotConfiguration
)
from core.config import Environment


def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")


def print_warning(message: str):
    """Print warning message."""
    print(f"⚠️ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"ℹ️ {message}")


def list_teams():
    """List all configured teams."""
    manager = get_bot_config_manager()
    config = manager.load_configuration()
    
    if not config.teams:
        print("No teams configured")
        return
    
    print(f"\n📋 Teams ({len(config.teams)}):")
    print("=" * 50)
    
    for team_id, team_config in config.teams.items():
        print(f"\n🏆 {team_config.name} (ID: {team_id})")
        print(f"   Description: {team_config.description}")
        
        if team_config.bot:
            status = "🟢 Active" if team_config.bot.is_active else "🔴 Inactive"
            print(f"   🤖 Bot: @{team_config.bot.username} {status}")
            print(f"     Main Chat ID: {team_config.bot.main_chat_id}")
            print(f"     Leadership Chat ID: {team_config.bot.leadership_chat_id}")
        else:
            print("   🤖 No bot configured")
        
        if team_config.settings:
            print(f"   Settings: {', '.join(team_config.settings.keys())}")
    
    if config.default_team:
        print(f"\n🎯 Default Team: {config.default_team}")


def show_team(team_id: str):
    """Show detailed information for a specific team."""
    manager = get_bot_config_manager()
    team_config = manager.get_team_config(team_id)
    
    if not team_config:
        print_error(f"Team '{team_id}' not found")
        return
    
    print(f"\n🏆 Team Details: {team_config.name}")
    print("=" * 50)
    print(f"ID: {team_id}")
    print(f"Description: {team_config.description}")
    
    if team_config.bot:
        print(f"\n🤖 Bot Configuration:")
        print(f"  Username: @{team_config.bot.username}")
        print(f"  Main Chat ID: {team_config.bot.main_chat_id}")
        print(f"  Leadership Chat ID: {team_config.bot.leadership_chat_id}")
        print(f"  Status: {'🟢 Active' if team_config.bot.is_active else '🔴 Inactive'}")
        print(f"  Token: {team_config.bot.token[:10]}..." if team_config.bot.token else "  Token: Not set")
    else:
        print("\n🤖 No bot configured")
    
    if team_config.settings:
        print(f"\n⚙️ Settings:")
        for key, value in team_config.settings.items():
            print(f"  {key}: {value}")


def add_team(team_id: str, name: str, description: str = ""):
    """Add a new team to the configuration."""
    manager = get_bot_config_manager()
    config = manager.load_configuration()
    
    if team_id in config.teams:
        print_error(f"Team '{team_id}' already exists")
        return
    
    # Create new team
    new_team = TeamConfig(
        name=name,
        description=description,
        bot=None,
        settings={}
    )
    
    config.teams[team_id] = new_team
    
    # Set as default if it's the first team
    if not config.default_team:
        config.default_team = team_id
    
    # Save configuration
    if manager.save_local_config(config):
        print_success(f"Team '{name}' (ID: {team_id}) added successfully")
        if config.default_team == team_id:
            print_info(f"Set as default team")
    else:
        print_error("Failed to save configuration")


def add_bot(team_id: str, token: str, username: str, main_chat_id: str, leadership_chat_id: str):
    """Add a bot to a team."""
    manager = get_bot_config_manager()
    config = manager.load_configuration()
    
    if team_id not in config.teams:
        print_error(f"Team '{team_id}' not found")
        return
    
    # Create bot configuration
    bot_config = BotConfig(
        token=token,
        username=username,
        main_chat_id=main_chat_id,
        leadership_chat_id=leadership_chat_id,
        is_active=True
    )
    
    config.teams[team_id].bot = bot_config
    
    # Save configuration
    if manager.save_local_config(config):
        print_success(f"Bot added to team '{team_id}'")
        print_info(f"Username: @{username}")
        print_info(f"Main Chat ID: {main_chat_id}")
        print_info(f"Leadership Chat ID: {leadership_chat_id}")
    else:
        print_error("Failed to save configuration")


def remove_bot(team_id: str):
    """Remove a bot from a team."""
    manager = get_bot_config_manager()
    config = manager.load_configuration()
    
    if team_id not in config.teams:
        print_error(f"Team '{team_id}' not found")
        return
    
    if not config.teams[team_id].bot:
        print_error(f"No bot configured for team '{team_id}'")
        return
    
    # Remove bot
    config.teams[team_id].bot = None
    
    # Save configuration
    if manager.save_local_config(config):
        print_success(f"Bot removed from team '{team_id}'")
    else:
        print_error("Failed to save configuration")


def set_default_team(team_id: str):
    """Set the default team."""
    manager = get_bot_config_manager()
    config = manager.load_configuration()
    
    if team_id not in config.teams:
        print_error(f"Team '{team_id}' not found")
        return
    
    config.default_team = team_id
    
    # Save configuration
    if manager.save_local_config(config):
        print_success(f"Default team set to '{team_id}'")
    else:
        print_error("Failed to save configuration")


def validate_config():
    """Validate the current configuration."""
    manager = get_bot_config_manager()
    errors = manager.validate_configuration()
    
    if not errors:
        print_success("Configuration is valid")
        return
    
    print_error("Configuration validation failed:")
    for error in errors:
        print(f"  • {error}")


def export_config(output_file: str):
    """Export configuration to a file."""
    manager = get_bot_config_manager()
    config = manager.load_configuration()
    
    try:
        # Convert to JSON-serializable format
        data = {
            'environment': config.environment,
            'teams': {},
            'default_team': config.default_team,
            'firebase_config': config.firebase_config,
            'ai_config': config.ai_config
        }
        
        for team_id, team_config in config.teams.items():
            data['teams'][team_id] = {
                'name': team_config.name,
                'description': team_config.description,
                'bot': team_config.bot,
                'settings': team_config.settings
            }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print_success(f"Configuration exported to {output_file}")
        
    except Exception as e:
        print_error(f"Failed to export configuration: {e}")


def import_config(input_file: str):
    """Import configuration from a file."""
    manager = get_bot_config_manager()
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Parse configuration
        teams = {}
        for team_id, team_data in data.get('teams', {}).items():
            teams[team_id] = manager._parse_team_config(team_id, team_data)
        
        config = BotConfiguration(
            environment=data.get('environment', 'testing'),
            teams=teams,
            default_team=data.get('default_team', ''),
            firebase_config=data.get('firebase_config', {}),
            ai_config=data.get('ai_config', {})
        )
        
        # Save configuration
        if manager.save_local_config(config):
            print_success(f"Configuration imported from {input_file}")
            print_info(f"Loaded {len(teams)} teams")
        else:
            print_error("Failed to save imported configuration")
        
    except Exception as e:
        print_error(f"Failed to import configuration: {e}")


def create_example_config():
    """Create an example configuration file."""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    example_config = {
        "environment": "testing",
        "teams": {
            "example-team": {
                "name": "Example Team",
                "description": "Example team for testing",
                "bot": {
                    "token": "YOUR_MAIN_BOT_TOKEN_HERE",
                    "username": "your_main_bot",
                    "main_chat_id": "YOUR_MAIN_CHAT_ID_HERE",
                    "leadership_chat_id": "YOUR_LEADERSHIP_CHAT_ID_HERE",
                    "is_active": True
                },
                "settings": {
                    "ai_provider": "google_gemini",
                    "ai_model": "gemini-pro",
                    "max_members": 50,
                    "allow_public_join": False
                }
            }
        },
        "default_team": "example-team",
        "firebase_config": {
            "project_id": "your-firebase-project-id"
        },
        "ai_config": {
            "provider": "google_gemini",
            "api_key": "YOUR_GOOGLE_AI_API_KEY_HERE",
            "model": "gemini-pro",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    
    example_file = config_dir / "bot_config.example.json"
    with open(example_file, 'w') as f:
        json.dump(example_config, f, indent=2)
    
    print_success(f"Example configuration created: {example_file}")
    print_info("Edit this file with your actual bot tokens and chat IDs")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='KICKAI Bot Configuration Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                    # List all teams
  %(prog)s show example-team       # Show team details
  %(prog)s add-team my-team "My Team" "Team description"  # Add new team
  %(prog)s add-bot my-team main "TOKEN" "username" "CHAT_ID"  # Add main bot
  %(prog)s add-bot my-team leadership "TOKEN" "username" "CHAT_ID"  # Add leadership bot
  %(prog)s validate                # Validate configuration
  %(prog)s export config.json      # Export configuration
  %(prog)s import config.json      # Import configuration
  %(prog)s create-example          # Create example configuration
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List all teams')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show team details')
    show_parser.add_argument('team_id', help='Team ID')
    
    # Add team command
    add_team_parser = subparsers.add_parser('add-team', help='Add a new team')
    add_team_parser.add_argument('team_id', help='Team ID')
    add_team_parser.add_argument('name', help='Team name')
    add_team_parser.add_argument('description', nargs='?', default='', help='Team description')
    
    # Add bot command
    add_bot_parser = subparsers.add_parser('add-bot', help='Add a bot to a team')
    add_bot_parser.add_argument('team_id', help='Team ID')
    add_bot_parser.add_argument('token', help='Bot token')
    add_bot_parser.add_argument('username', help='Bot username')
    add_bot_parser.add_argument('main_chat_id', help='Main Chat ID')
    add_bot_parser.add_argument('leadership_chat_id', help='Leadership Chat ID')
    
    # Remove bot command
    remove_bot_parser = subparsers.add_parser('remove-bot', help='Remove a bot from a team')
    remove_bot_parser.add_argument('team_id', help='Team ID')
    
    # Set default team command
    default_parser = subparsers.add_parser('set-default', help='Set default team')
    default_parser.add_argument('team_id', help='Team ID')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate configuration')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export configuration')
    export_parser.add_argument('output_file', help='Output file path')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import configuration')
    import_parser.add_argument('input_file', help='Input file path')
    
    # Create example command
    subparsers.add_parser('create-example', help='Create example configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_teams()
        elif args.command == 'show':
            show_team(args.team_id)
        elif args.command == 'add-team':
            add_team(args.team_id, args.name, args.description)
        elif args.command == 'add-bot':
            add_bot(args.team_id, args.token, args.username, args.main_chat_id, args.leadership_chat_id)
        elif args.command == 'remove-bot':
            remove_bot(args.team_id)
        elif args.command == 'set-default':
            set_default_team(args.team_id)
        elif args.command == 'validate':
            validate_config()
        elif args.command == 'export':
            export_config(args.output_file)
        elif args.command == 'import':
            import_config(args.input_file)
        elif args.command == 'create-example':
            create_example_config()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 