#!/usr/bin/env python3
"""
Interactive Bot Configuration Setup

This script helps set up bot configurations interactively for different environments.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.bot_config_manager import BotConfiguration, TeamConfig, BotConfig, ChatType


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


def get_input(prompt: str, required: bool = True, default: str = "") -> str:
    """Get user input with validation."""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not user_input and required:
            print_error("This field is required")
            continue
        
        return user_input


def get_environment() -> str:
    """Get the target environment."""
    print("\n🌍 Select Environment:")
    print("1. Testing")
    print("2. Staging")
    print("3. Development")
    
    while True:
        choice = input("Enter choice (1-3): ").strip()
        if choice == "1":
            return "testing"
        elif choice == "2":
            return "staging"
        elif choice == "3":
            return "development"
        else:
            print_error("Invalid choice. Please enter 1, 2, or 3.")


def setup_team() -> Dict[str, Any]:
    """Set up a team configuration."""
    print("\n🏆 Team Configuration")
    print("=" * 30)
    
    team_id = get_input("Team ID (e.g., my-team)")
    name = get_input("Team Name")
    description = get_input("Team Description", required=False)
    
    # Bot configuration
    print("\n🤖 Bot Configuration (Single Bot with Dual Chats)")
    print("=" * 50)
    
    # Single bot with dual chats
    bot_token = get_input("Bot Token")
    bot_username = get_input("Bot Username (without @)")
    main_chat_id = get_input("Main Chat ID (for general team chat)")
    leadership_chat_id = get_input("Leadership Chat ID (for leadership group)")
    
    bot_config = {
        "token": bot_token,
        "username": bot_username,
        "main_chat_id": main_chat_id,
        "leadership_chat_id": leadership_chat_id,
        "is_active": True
    }
    
    # Team settings
    print("\n⚙️ Team Settings")
    print("=" * 30)
    
    settings = {}
    ai_provider = get_input("AI Provider", required=False, default="google_gemini")
    if ai_provider:
        settings["ai_provider"] = ai_provider
    
    ai_model = get_input("AI Model", required=False, default="gemini-pro")
    if ai_model:
        settings["ai_model"] = ai_model
    
    max_members = get_input("Max Members", required=False, default="50")
    if max_members:
        settings["max_members"] = int(max_members)
    
    allow_public = get_input("Allow Public Join (y/n)", required=False, default="n")
    settings["allow_public_join"] = allow_public.lower() == "y"
    
    return {
        "name": name,
        "description": description,
        "bot": bot_config,
        "settings": settings
    }


def setup_firebase_config() -> Dict[str, Any]:
    """Set up Firebase configuration."""
    print("\n🔥 Firebase Configuration")
    print("=" * 30)
    
    project_id = get_input("Firebase Project ID", required=False)
    
    return {
        "project_id": project_id or "",
        "credentials_path": None
    }


def setup_ai_config() -> Dict[str, Any]:
    """Set up AI configuration."""
    print("\n🧠 AI Configuration")
    print("=" * 30)
    
    provider = get_input("AI Provider", required=False, default="google_gemini")
    api_key = get_input("API Key", required=False)
    model = get_input("Model", required=False, default="gemini-pro")
    temperature = get_input("Temperature (0.0-2.0)", required=False, default="0.7")
    max_tokens = get_input("Max Tokens", required=False, default="1000")
    
    return {
        "provider": provider,
        "api_key": api_key or "",
        "model": model,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens)
    }


def save_configuration(config: Dict[str, Any], environment: str):
    """Save configuration to file."""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    if environment == "testing":
        config_file = config_dir / "bot_config.json"
    elif environment == "staging":
        config_file = config_dir / "bot_config.staging.json"
    else:
        config_file = config_dir / f"bot_config.{environment}.json"
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_success(f"Configuration saved to {config_file}")
        return True
        
    except Exception as e:
        print_error(f"Failed to save configuration: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 KICKAI Bot Configuration Setup")
    print("=" * 40)
    print("This script will help you set up bot configurations for your environment.")
    print()
    
    # Get environment
    environment = get_environment()
    print_info(f"Setting up configuration for {environment} environment")
    
    # Set up teams
    teams = {}
    while True:
        team_config = setup_team()
        team_id = get_input("Team ID")
        teams[team_id] = team_config
        
        add_another = input("\nAdd another team? (y/n): ").strip().lower()
        if add_another != 'y':
            break
    
    if not teams:
        print_error("At least one team is required")
        return
    
    # Set default team
    if len(teams) == 1:
        default_team = list(teams.keys())[0]
    else:
        print("\n🎯 Default Team")
        print("=" * 30)
        print("Available teams:")
        for i, team_id in enumerate(teams.keys(), 1):
            print(f"{i}. {team_id} ({teams[team_id]['name']})")
        
        while True:
            try:
                choice = int(input(f"Select default team (1-{len(teams)}): "))
                if 1 <= choice <= len(teams):
                    default_team = list(teams.keys())[choice - 1]
                    break
                else:
                    print_error(f"Please enter a number between 1 and {len(teams)}")
            except ValueError:
                print_error("Please enter a valid number")
    
    # Set up Firebase config
    firebase_config = setup_firebase_config()
    
    # Set up AI config
    ai_config = setup_ai_config()
    
    # Create final configuration
    config = {
        "environment": environment,
        "teams": teams,
        "default_team": default_team,
        "firebase_config": firebase_config,
        "ai_config": ai_config
    }
    
    # Show summary
    print("\n📋 Configuration Summary")
    print("=" * 40)
    print(f"Environment: {environment}")
    print(f"Teams: {len(teams)}")
    for team_id, team_config in teams.items():
        print(f"  • {team_id}: {team_config['name']}")
        print(f"    Bots: {len(team_config['bot'])}")
    print(f"Default Team: {default_team}")
    print(f"AI Provider: {ai_config['provider']}")
    
    # Confirm and save
    print("\n💾 Save Configuration")
    print("=" * 40)
    confirm = input("Save this configuration? (y/n): ").strip().lower()
    
    if confirm == 'y':
        if save_configuration(config, environment):
            print_success("Configuration setup completed!")
            print_info("You can now use the manage_bot_config.py script to manage your configuration")
            print_info("Remember to update the bot tokens and chat IDs with real values")
        else:
            print_error("Failed to save configuration")
    else:
        print_info("Configuration not saved")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1) 