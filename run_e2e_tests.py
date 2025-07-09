#!/usr/bin/env python3
"""
KICKAI End-to-End Test Runner

This script runs comprehensive E2E tests for the KICKAI Telegram bot,
validating both Telegram interactions and Firestore data consistency.
"""

import asyncio
import logging
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env.test')
except ImportError:
    pass

from src.testing.e2e_framework import E2ETestRunner, TelegramBotTester, FirestoreValidator
from src.testing.test_suites import load_test_suite, get_available_suites
from src.core.improved_config_system import get_improved_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'e2e_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    ]
)

logger = logging.getLogger(__name__)


def validate_environment():
    """Validate that all required environment variables are set."""
    logger.info("🔍 Validating environment configuration...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_API_ID', 
        'TELEGRAM_API_HASH',
        'ADMIN_SESSION_STRING',
        'TELEGRAM_MAIN_CHAT_ID',
        'TELEGRAM_LEADERSHIP_CHAT_ID',
        'DEFAULT_TEAM_ID',
        'FIREBASE_PROJECT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Mask sensitive values
            if 'TOKEN' in var or 'HASH' in var or 'SESSION' in var:
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                logger.info(f"✅ {var}: {masked_value}")
            else:
                logger.info(f"✅ {var}: {value}")
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("✅ Environment validation passed")
    return True


def log_chat_configuration():
    """Log chat ID configuration and naming convention."""
    logger.info("📱 Chat Configuration:")
    
    main_chat_id = os.getenv('TELEGRAM_MAIN_CHAT_ID')
    leadership_chat_id = os.getenv('TELEGRAM_LEADERSHIP_CHAT_ID')
    
    logger.info(f"   Main Chat ID: {main_chat_id} (KickAI Testing)")
    logger.info(f"   Leadership Chat ID: {leadership_chat_id} (KickAI Testing - Leadership)")
    logger.info("   Naming Convention: 'Team Name' for main, 'Team Name - Leadership' for leadership")


async def run_test_suite(suite_name: str, verbose: bool = False) -> bool:
    """Run a specific test suite."""
    logger.info(f"🚀 Starting test suite: {suite_name}")
    
    # Set E2E testing environment variable to ensure .env.test is loaded
    os.environ['E2E_TESTING'] = 'true'
    
    # Validate environment first
    if not validate_environment():
        return False
    
    # Log chat configuration
    log_chat_configuration()
    
    # Get configuration
    config = get_improved_config()
    team_id = config.configuration.teams.default_team_id
    logger.info(f"📋 Team ID: {team_id}")
    
    # Initialize test components
    logger.info("🔧 Initializing test components...")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    session_string = os.getenv('ADMIN_SESSION_STRING')
    project_id = os.getenv('FIREBASE_PROJECT_ID')
    
    # Create test components
    telegram_tester = TelegramBotTester(bot_token, api_id, api_hash, session_string)
    firestore_validator = FirestoreValidator(project_id)
    
    try:
        # Start Telegram tester
        logger.info("📱 Starting Telegram tester...")
        await telegram_tester.start()
        logger.info("✅ Telegram tester started successfully")
        
        # Create test runner
        runner = E2ETestRunner(telegram_tester, firestore_validator)
        
        # Load and add tests
        tests = load_test_suite(suite_name)
        logger.info(f"📋 Loaded {len(tests)} tests for suite '{suite_name}'")
        
        for i, test in enumerate(tests, 1):
            logger.info(f"   {i}. {test.get('name', f'Test {i}')}")
            if 'steps' in test:
                # Multi-step test
                runner.add_user_flow_test(test["steps"], test.get("telegram_context"))
            elif test.get("type") == "validation":
                # Handle validation tests
                runner.add_test(test)
            elif test.get("type") == "command":
                # Single command test
                runner.add_command_test(
                    test["command"],
                    test["telegram_context"],
                    test.get("firestore_validation")
                )
            elif test.get("type") == "natural_language":
                # Single natural language test
                runner.add_nl_test(
                    test["message"],
                    test["telegram_context"],
                    test.get("firestore_validation")
                )
            else:
                # Generic test
                runner.add_test(test)
        
        # Run tests
        logger.info("🧪 Running tests...")
        results = await runner.run_tests()
        
        # Generate and display report
        report = runner.generate_report()
        logger.info("\n" + report)
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"e2e_report_{suite_name}_{timestamp}.html"
        
        with open(report_filename, 'w') as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>KICKAI E2E Test Report - {suite_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>KICKAI E2E Test Report</h1>
    <h2>Suite: {suite_name}</h2>
    <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <pre>{report}</pre>
</body>
</html>
            """)
        
        logger.info(f"📄 Detailed report saved to: {report_filename}")
        
        # Return success if all tests passed
        all_passed = all(result.success for result in results)
        if all_passed:
            logger.info("🎉 All tests passed!")
        else:
            logger.error(f"❌ {len([r for r in results if not r.success])} tests failed")
        
        return all_passed
        
    except Exception as e:
        logger.error(f"❌ Test suite failed with exception: {e}")
        return False
        
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up...")
        await telegram_tester.stop()
        logger.info("✅ Cleanup completed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run KICKAI E2E tests')
    parser.add_argument('--suite', choices=get_available_suites(), 
                       default='smoke', help='Test suite to run')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"🧪 KICKAI E2E Test Runner")
    logger.info(f"📋 Available suites: {', '.join(get_available_suites())}")
    
    # Run the test suite
    success = asyncio.run(run_test_suite(args.suite, args.verbose))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 