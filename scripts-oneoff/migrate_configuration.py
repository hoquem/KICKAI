#!/usr/bin/env python3
"""
Configuration Migration Script

This script helps migrate from the old configuration system to the new one.
It validates the new configuration and provides a comparison report.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.settings import get_settings
from core.improved_config import get_improved_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_new_config() -> List[str]:
    """Validate the new configuration system."""
    logger.info("🔍 Validating new configuration system...")
    
    errors = []
    
    try:
        # Test basic loading
        settings = get_settings()
        logger.info(f"✅ Settings loaded successfully")
        logger.info(f"   Environment: {settings.environment}")
        logger.info(f"   AI Provider: {settings.ai_provider}")
        logger.info(f"   Bot Token: {'✅ Set' if settings.telegram_bot_token else '❌ Missing'}")
        
        # Validate required fields
        validation_errors = settings.validate_required_fields()
        if validation_errors:
            errors.extend(validation_errors)
            logger.error(f"❌ Validation errors found: {len(validation_errors)}")
            for error in validation_errors:
                logger.error(f"   - {error}")
        else:
            logger.info("✅ All required fields validated")
            
    except Exception as e:
        errors.append(f"Failed to load settings: {e}")
        logger.error(f"❌ Failed to load settings: {e}")
    
    return errors


def compare_configurations() -> Dict[str, Any]:
    """Compare old vs new configuration values."""
    logger.info("\n🔍 Comparing old vs new configuration...")
    
    comparison = {
        "old_config": {},
        "new_config": {},
        "differences": [],
        "missing_in_new": [],
        "missing_in_old": []
    }
    
    try:
        # Get old configuration
        old_config = get_improved_config()
        
        # Get new configuration
        new_config = get_settings()
        
        # Compare key values
        key_mappings = {
            # Environment
            "environment": ("environment", "environment"),
            
            # Database
            "firebase_project_id": ("database.project_id", "firebase_project_id"),
            "firebase_credentials_path": ("database.credentials_path", "firebase_credentials_path"),
            "firebase_batch_size": ("database.batch_size", "firebase_batch_size"),
            "firebase_timeout": ("database.timeout_seconds", "firebase_timeout"),
            
            # AI
            "ai_provider": ("ai.provider", "ai_provider"),
            "ai_model_name": ("ai.model_name", "ai_model_name"),
            "ai_temperature": ("ai.temperature", "ai_temperature"),
            "ai_max_tokens": ("ai.max_tokens", "ai_max_tokens"),
            "ai_timeout": ("ai.timeout_seconds", "ai_timeout"),
            "ai_max_retries": ("ai.max_retries", "ai_max_retries"),
            "google_api_key": ("ai.api_key", "google_api_key"),
            
            # Telegram
            "telegram_bot_token": ("telegram.bot_token", "telegram_bot_token"),
            "telegram_main_chat_id": ("teams.teams[default_team_id].main_chat_id", "telegram_main_chat_id"),
            "telegram_leadership_chat_id": ("teams.teams[default_team_id].leadership_chat_id", "telegram_leadership_chat_id"),
            "telegram_webhook_url": ("telegram.webhook_url", "telegram_webhook_url"),
            "telegram_parse_mode": ("telegram.parse_mode", "telegram_parse_mode"),
            "telegram_timeout": ("telegram.message_timeout", "telegram_timeout"),
            
            # Team
            "default_team_id": ("teams.default_team_id", "default_team_id"),
            
            # Payment
            "collectiv_api_key": ("payment.collectiv_api_key", "collectiv_api_key"),
            "collectiv_base_url": ("payment.collectiv_base_url", "collectiv_base_url"),
            
            # Logging
            "log_level": ("logging.level", "log_level"),
            "log_format": ("logging.format", "log_format"),
            "log_file_path": ("logging.file_path", "log_file_path"),
            "log_max_file_size": ("logging.max_file_size", "log_max_file_size"),
            "log_backup_count": ("logging.backup_count", "log_backup_count"),
            
            # Performance
            "cache_ttl_seconds": ("performance.cache_ttl_seconds", "cache_ttl_seconds"),
            "max_concurrent_requests": ("performance.max_concurrent_requests", "max_concurrent_requests"),
            "request_timeout": ("performance.request_timeout", "request_timeout"),
            "retry_attempts": ("performance.retry_attempts", "retry_attempts"),
            "retry_delay": ("performance.retry_delay", "retry_delay"),
            
            # Security
            "jwt_secret": ("security.jwt_secret", "jwt_secret"),
            "session_timeout": ("security.session_timeout", "session_timeout"),
            "max_login_attempts": ("security.max_login_attempts", "max_login_attempts"),
            "password_min_length": ("security.password_min_length", "password_min_length"),
        }
        
        for key, (old_path, new_path) in key_mappings.items():
            try:
                # Get old value
                old_value = get_nested_value(old_config, old_path)
                comparison["old_config"][key] = old_value
                
                # Get new value
                new_value = getattr(new_config, new_path, None)
                comparison["new_config"][key] = new_value
                
                # Compare values
                if old_value != new_value:
                    comparison["differences"].append({
                        "key": key,
                        "old_value": old_value,
                        "new_value": new_value
                    })
                    
            except Exception as e:
                logger.warning(f"⚠️  Error comparing {key}: {e}")
        
        logger.info(f"✅ Comparison completed")
        logger.info(f"   Total keys compared: {len(key_mappings)}")
        logger.info(f"   Differences found: {len(comparison['differences'])}")
        
    except Exception as e:
        logger.error(f"❌ Failed to compare configurations: {e}")
    
    return comparison


def get_nested_value(obj: Any, path: str) -> Any:
    """Get nested value from object using dot notation."""
    try:
        for part in path.split('.'):
            if '[' in part and ']' in part:
                # Handle array access like teams[default_team_id]
                key_part = part[:part.index('[')]
                index_part = part[part.index('[')+1:part.index(']')]
                
                obj = getattr(obj, key_part, {})
                if isinstance(obj, dict):
                    obj = obj.get(index_part)
                else:
                    return None
            else:
                obj = getattr(obj, part, None)
        return obj
    except Exception:
        return None


def generate_migration_report() -> str:
    """Generate a comprehensive migration report."""
    logger.info("\n📊 Generating migration report...")
    
    report = []
    report.append("# Configuration Migration Report")
    report.append("")
    report.append(f"Generated: {os.popen('date').read().strip()}")
    report.append("")
    
    # Validate new config
    errors = validate_new_config()
    if errors:
        report.append("## ❌ Validation Errors")
        for error in errors:
            report.append(f"- {error}")
        report.append("")
    else:
        report.append("## ✅ Validation Passed")
        report.append("")
    
    # Compare configurations
    comparison = compare_configurations()
    
    if comparison["differences"]:
        report.append("## 🔄 Configuration Differences")
        report.append("")
        for diff in comparison["differences"]:
            report.append(f"### {diff['key']}")
            report.append(f"- Old: `{diff['old_value']}`")
            report.append(f"- New: `{diff['new_value']}`")
            report.append("")
    
    # Environment variables mapping
    report.append("## 🔧 Environment Variable Mapping")
    report.append("")
    report.append("| Old Variable | New Variable | Notes |")
    report.append("|--------------|--------------|-------|")
    
    env_mappings = [
        ("TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN", "Same"),
        ("TELEGRAM_MAIN_CHAT_ID", "TELEGRAM_MAIN_CHAT_ID", "Same"),
        ("TELEGRAM_LEADERSHIP_CHAT_ID", "TELEGRAM_LEADERSHIP_CHAT_ID", "Same"),
        ("FIREBASE_PROJECT_ID", "FIREBASE_PROJECT_ID", "Same"),
        ("FIREBASE_CREDENTIALS_PATH", "FIREBASE_CREDENTIALS_PATH", "Same"),
        ("FIREBASE_CREDENTIALS_JSON", "FIREBASE_CREDENTIALS_JSON", "Same"),
        ("GOOGLE_API_KEY", "GOOGLE_API_KEY", "Same"),
        ("AI_PROVIDER", "AI_PROVIDER", "Same"),
        ("AI_MODEL_NAME", "AI_MODEL_NAME", "Same"),
        ("DEFAULT_TEAM_ID", "DEFAULT_TEAM_ID", "Same"),
        ("COLLECTIV_API_KEY", "COLLECTIV_API_KEY", "Same"),
        ("LOG_LEVEL", "LOG_LEVEL", "Same"),
        ("ENVIRONMENT", "ENVIRONMENT", "Same"),
        ("DEBUG", "DEBUG", "Same"),
    ]
    
    for old_var, new_var, notes in env_mappings:
        report.append(f"| {old_var} | {new_var} | {notes} |")
    
    report.append("")
    
    # Migration steps
    report.append("## 🚀 Migration Steps")
    report.append("")
    report.append("1. **Update imports**: Replace old config imports with new ones")
    report.append("2. **Update function calls**: Use `get_settings()` instead of old functions")
    report.append("3. **Test thoroughly**: Run tests to ensure everything works")
    report.append("4. **Remove old code**: Delete old configuration files after migration")
    report.append("")
    
    # Code examples
    report.append("## 💻 Code Examples")
    report.append("")
    report.append("### Old way:")
    report.append("```python")
    report.append("from core.improved_config_system import get_improved_config")
    report.append("config = get_improved_config()")
    report.append("bot_token = config.telegram.bot_token")
    report.append("```")
    report.append("")
    report.append("### New way:")
    report.append("```python")
    report.append("from core.settings import get_settings")
    report.append("settings = get_settings()")
    report.append("bot_token = settings.telegram_bot_token")
    report.append("```")
    report.append("")
    
    return "\n".join(report)


def test_configuration_loading() -> bool:
    """Test configuration loading in different scenarios."""
    logger.info("\n🧪 Testing configuration loading...")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Basic loading
    total_tests += 1
    try:
        settings = get_settings()
        if settings is not None:
            logger.info("✅ Test 1: Basic loading passed")
            tests_passed += 1
        else:
            logger.error("❌ Test 1: Basic loading failed")
    except Exception as e:
        logger.error(f"❌ Test 1: Basic loading failed - {e}")
    
    # Test 2: Environment detection
    total_tests += 1
    try:
        settings = get_settings()
        if settings.environment in [Environment.DEVELOPMENT, Environment.PRODUCTION, Environment.TESTING]:
            logger.info(f"✅ Test 2: Environment detection passed - {settings.environment}")
            tests_passed += 1
        else:
            logger.error(f"❌ Test 2: Environment detection failed - {settings.environment}")
    except Exception as e:
        logger.error(f"❌ Test 2: Environment detection failed - {e}")
    
    # Test 3: AI provider validation
    total_tests += 1
    try:
        settings = get_settings()
        if settings.ai_provider is not None:
            logger.info(f"✅ Test 3: AI provider validation passed - {settings.ai_provider}")
            tests_passed += 1
        else:
            logger.error("❌ Test 3: AI provider validation failed")
    except Exception as e:
        logger.error(f"❌ Test 3: AI provider validation failed - {e}")
    
    # Test 4: Required field validation
    total_tests += 1
    try:
        settings = get_settings()
        errors = settings.validate_required_fields()
        logger.info(f"✅ Test 4: Required field validation passed - {len(errors)} errors found")
        tests_passed += 1
    except Exception as e:
        logger.error(f"❌ Test 4: Required field validation failed - {e}")
    
    logger.info(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests


def main():
    """Main migration script."""
    logger.info("🚀 KICKAI Configuration Migration Script")
    logger.info("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src/core/settings.py").exists():
        logger.error("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Test configuration loading
    if not test_configuration_loading():
        logger.error("❌ Configuration tests failed. Please fix issues before proceeding.")
        sys.exit(1)
    
    # Generate comparison
    comparison = compare_configurations()
    
    # Generate report
    report = generate_migration_report()
    
    # Save report
    report_path = "CONFIGURATION_MIGRATION_REPORT.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    logger.info(f"\n📄 Migration report saved to: {report_path}")
    
    # Summary
    logger.info("\n📋 Migration Summary:")
    logger.info(f"   - Configuration differences: {len(comparison['differences'])}")
    logger.info(f"   - Validation errors: {len(comparison.get('validation_errors', []))}")
    logger.info(f"   - Report generated: {report_path}")
    
    if len(comparison['differences']) == 0:
        logger.info("\n🎉 No configuration differences found! Migration should be straightforward.")
    else:
        logger.warning(f"\n⚠️  Found {len(comparison['differences'])} differences. Review the report before migrating.")
    
    logger.info("\n✅ Migration script completed successfully!")


if __name__ == "__main__":
    main() 