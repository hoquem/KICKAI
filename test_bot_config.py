#!/usr/bin/env python3
"""
Test script for the new bot configuration system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.bot_config_manager import get_bot_config_manager, BotType
from core.config import get_config


def test_configuration_loading():
    """Test basic configuration loading."""
    print("🧪 Testing Configuration Loading")
    print("=" * 40)
    
    try:
        # Get configuration manager
        manager = get_bot_config_manager()
        print("✅ Bot config manager initialized")
        
        # Load configuration
        config = manager.load_configuration()
        print(f"✅ Configuration loaded for environment: {config.environment}")
        
        # Show teams
        if config.teams:
            print(f"✅ Found {len(config.teams)} teams:")
            for team_id, team_config in config.teams.items():
                print(f"   • {team_id}: {team_config.name}")
                print(f"     Bots: {len(team_config.bots)}")
        else:
            print("⚠️ No teams configured")
        
        # Show default team
        if config.default_team:
            print(f"✅ Default team: {config.default_team}")
        else:
            print("⚠️ No default team set")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False


def test_bot_credentials():
    """Test bot credential retrieval."""
    print("\n🤖 Testing Bot Credentials")
    print("=" * 40)
    
    try:
        manager = get_bot_config_manager()
        config = manager.load_configuration()
        
        if not config.teams:
            print("⚠️ No teams to test")
            return True
        
        # Test with first team
        team_id = list(config.teams.keys())[0]
        team_config = config.teams[team_id]
        
        print(f"Testing team: {team_id} ({team_config.name})")
        
        # Test main bot
        main_bot = manager.get_bot_config(team_id, BotType.MAIN)
        if main_bot:
            print(f"✅ Main bot: @{main_bot.username}")
            print(f"   Chat ID: {main_bot.chat_id}")
            print(f"   Active: {main_bot.is_active}")
        else:
            print("⚠️ No main bot configured")
        
        # Test leadership bot
        leadership_bot = manager.get_bot_config(team_id, BotType.LEADERSHIP)
        if leadership_bot:
            print(f"✅ Leadership bot: @{leadership_bot.username}")
            print(f"   Chat ID: {leadership_bot.chat_id}")
            print(f"   Active: {leadership_bot.is_active}")
        else:
            print("⚠️ No leadership bot configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot credentials test failed: {e}")
        return False


def test_validation():
    """Test configuration validation."""
    print("\n🔍 Testing Configuration Validation")
    print("=" * 40)
    
    try:
        manager = get_bot_config_manager()
        errors = manager.validate_configuration()
        
        if not errors:
            print("✅ Configuration is valid")
            return True
        else:
            print("⚠️ Configuration validation issues:")
            for error in errors:
                print(f"   • {error}")
            return False
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False


def test_environment_detection():
    """Test environment detection."""
    print("\n🌍 Testing Environment Detection")
    print("=" * 40)
    
    try:
        config = get_config()
        print(f"✅ Environment: {config.environment.value}")
        
        if config.is_development():
            print("✅ Development environment detected")
        elif config.is_production():
            print("✅ Production environment detected")
        elif config.is_testing():
            print("✅ Testing environment detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment detection failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 KICKAI Bot Configuration System Test")
    print("=" * 50)
    
    tests = [
        test_environment_detection,
        test_configuration_loading,
        test_bot_credentials,
        test_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n📊 Test Results")
    print("=" * 40)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 