#!/usr/bin/env python3
"""
KICKAI End-to-End Test Runner with Bot Service

This script provides comprehensive E2E testing by:
1. Starting the bot service using .env configuration
2. Running Telegram client tests that interact with the running bot
3. Validating bot responses and Firestore updates
4. Cleaning up after tests complete

Usage:
    python run_e2e_tests_with_bot.py --suite smoke
    python run_e2e_tests_with_bot.py --suite comprehensive --report html
"""

import asyncio
import argparse
import json
import os
import sys
import signal
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Any
import logging

# Load .env for bot service
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
except ImportError:
    pass

# Load .env.test for test configuration
try:
    load_dotenv('.env.test')
except ImportError:
    pass

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from testing.e2e_framework import (
    TelegramBotTester, FirestoreValidator, E2ETestRunner,
    TestResult
)
from testing.test_suites import (
    load_test_suite, get_available_suites
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('e2e_tests_with_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class BotServiceManager:
    """Manages the bot service lifecycle for E2E testing."""
    
    def __init__(self):
        self.bot_process = None
        self.bot_started = False
        
    async def start_bot_service(self):
        """Start the bot service using .env configuration."""
        logger.info("🚀 Starting bot service...")
        
        try:
            # Start the bot service with correct Python path
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
            
            self.bot_process = subprocess.Popen([
                sys.executable, "src/main.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            
            # Wait for bot to start
            await asyncio.sleep(5)
            
            # Check if process is still running
            if self.bot_process.poll() is None:
                self.bot_started = True
                logger.info("✅ Bot service started successfully")
            else:
                stdout, stderr = self.bot_process.communicate()
                logger.error(f"❌ Bot service failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start bot service: {e}")
            return False
            
        return True
    
    async def stop_bot_service(self):
        """Stop the bot service."""
        if self.bot_process and self.bot_started:
            logger.info("🛑 Stopping bot service...")
            
            try:
                # Send SIGTERM to gracefully stop
                self.bot_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.bot_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.bot_process.kill()
                    self.bot_process.wait()
                
                logger.info("✅ Bot service stopped")
                
            except Exception as e:
                logger.error(f"❌ Error stopping bot service: {e}")
            
            self.bot_started = False
    
    def is_bot_running(self):
        """Check if bot service is still running."""
        return self.bot_process and self.bot_process.poll() is None


class TestReporter:
    """Generate test reports in various formats."""
    
    @staticmethod
    def generate_text_report(results: List[TestResult]) -> str:
        """Generate a text report."""
        if not results:
            return "No test results available"
        
        total_tests = len(results)
        passed_tests = len([r for r in results if r.success])
        failed_tests = total_tests - passed_tests
        
        # Calculate statistics
        avg_duration = sum(r.duration for r in results) / total_tests
        test_types = {}
        for result in results:
            test_type = result.test_type.value
            test_types[test_type] = test_types.get(test_type, 0) + 1
        
        # Generate report
        report = f"""
🧪 KICKAI E2E Test Report (with Bot Service)
{'=' * 60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 Summary:
• Total Tests: {total_tests}
• Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)
• Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)
• Average Duration: {avg_duration:.2f}s

📋 Test Types:
"""
        
        for test_type, count in test_types.items():
            report += f"• {test_type.title()}: {count}\n"
        
        report += f"""
⏱️ Performance:
• Total Duration: {sum(r.duration for r in results):.2f}s
• Fastest Test: {min(r.duration for r in results):.2f}s
• Slowest Test: {max(r.duration for r in results):.2f}s

❌ Failed Tests:
"""
        
        for result in results:
            if not result.success:
                report += f"• {result.test_name}\n"
                for error in result.errors:
                    report += f"  - {error}\n"
        
        return report
    
    @staticmethod
    def generate_json_report(results: List[TestResult]) -> str:
        """Generate a JSON report."""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "e2e_with_bot",
            "summary": {
                "total_tests": len(results),
                "passed_tests": len([r for r in results if r.success]),
                "failed_tests": len([r for r in results if not result.success]),
                "total_duration": sum(r.duration for r in results),
                "average_duration": sum(r.duration for r in results) / len(results) if results else 0
            },
            "results": [
                {
                    "test_name": result.test_name,
                    "test_type": result.test_type.value,
                    "success": result.success,
                    "duration": result.duration,
                    "message": result.message,
                    "errors": result.errors,
                    "metadata": result.metadata
                }
                for result in results
            ]
        }
        
        return json.dumps(report_data, indent=2)
    
    @staticmethod
    def generate_html_report(results: List[TestResult]) -> str:
        """Generate an HTML report."""
        if not results:
            return "<html><body><h1>No test results available</h1></body></html>"
        
        total_tests = len(results)
        passed_tests = len([r for r in results if r.success])
        failed_tests = total_tests - passed_tests
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>KICKAI E2E Test Report (with Bot Service)</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .summary-item {{ text-align: center; padding: 10px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
        .test-passed {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
        .test-failed {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
        .error {{ color: red; margin-left: 20px; }}
        .metadata {{ font-size: 0.9em; color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 KICKAI E2E Test Report (with Bot Service)</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="summary-item">
            <h3>Total Tests</h3>
            <p>{total_tests}</p>
        </div>
        <div class="summary-item">
            <h3 class="passed">Passed</h3>
            <p class="passed">{passed_tests} ({passed_tests/total_tests*100:.1f}%)</p>
        </div>
        <div class="summary-item">
            <h3 class="failed">Failed</h3>
            <p class="failed">{failed_tests} ({failed_tests/total_tests*100:.1f}%)</p>
        </div>
        <div class="summary-item">
            <h3>Duration</h3>
            <p>{sum(r.duration for r in results):.2f}s</p>
        </div>
    </div>
    
    <h2>Test Results</h2>
"""
        
        for result in results:
            css_class = "test-passed" if result.success else "test-failed"
            status_icon = "✅" if result.success else "❌"
            
            html += f"""
    <div class="test-result {css_class}">
        <h3>{status_icon} {result.test_name}</h3>
        <p><strong>Type:</strong> {result.test_type.value}</p>
        <p><strong>Duration:</strong> {result.duration:.2f}s</p>
        <p><strong>Message:</strong> {result.message}</p>
"""
            
            if result.errors:
                html += '<p><strong>Errors:</strong></p><ul>'
                for error in result.errors:
                    html += f'<li class="error">{error}</li>'
                html += '</ul>'
            
            if result.metadata:
                html += f'<div class="metadata"><strong>Metadata:</strong> {json.dumps(result.metadata, indent=2)}</div>'
            
            html += '</div>'
        
        html += """
</body>
</html>
"""
        
        return html


async def run_test_suite_with_bot(suite_name: str, parallel: bool = False) -> List[TestResult]:
    """Run a specific test suite with bot service running."""
    logger.info(f"🚀 Starting test suite: {suite_name}")
    
    # Initialize bot service manager
    bot_manager = BotServiceManager()
    
    try:
        # Start bot service
        bot_started = await bot_manager.start_bot_service()
        if not bot_started:
            logger.error("❌ Failed to start bot service")
            return []
        
        # Load environment variables for testing
        # Bot token should come from Firestore team configuration, not environment variables
        bot_token = None  # Should be loaded from Firestore team document
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        session_string = os.getenv('TELEGRAM_SESSION_STRING')
        project_id = os.getenv('FIRESTORE_PROJECT_ID')
        
        if not all([bot_token, api_id, api_hash, session_string, project_id]):
            logger.error("❌ Missing required environment variables")
            logger.error("Required: Bot token from Firestore, TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_STRING, FIRESTORE_PROJECT_ID")
            return []
        
        # Initialize testers
        telegram_tester = TelegramBotTester(bot_token, api_id, api_hash, session_string)
        firestore_validator = FirestoreValidator(project_id)
        
        # Start Telegram client
        await telegram_tester.start()
        
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
        results = await runner.run_tests()
        
        # Stop Telegram client
        await telegram_tester.stop()
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Failed to run test suite: {e}")
        return []
    
    finally:
        # Always stop bot service
        await bot_manager.stop_bot_service()


def save_report(report: str, format_type: str, suite_name: str):
    """Save report to file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == 'json':
        filename = f"e2e_report_with_bot_{suite_name}_{timestamp}.json"
    elif format_type == 'html':
        filename = f"e2e_report_with_bot_{suite_name}_{timestamp}.html"
    else:
        filename = f"e2e_report_with_bot_{suite_name}_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(report)
    
    logger.info(f"📄 Report saved to: {filename}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='KICKAI E2E Test Runner with Bot Service')
    parser.add_argument('--suite', choices=get_available_suites(), default='smoke',
                       help='Test suite to run (default: smoke)')
    parser.add_argument('--report', choices=['text', 'json', 'html'], default='text',
                       help='Report format (default: text)')
    parser.add_argument('--parallel', action='store_true',
                       help='Run tests in parallel')
    parser.add_argument('--save', action='store_true',
                       help='Save report to file')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"🎯 Running test suite: {args.suite}")
    logger.info(f"📊 Report format: {args.report}")
    logger.info(f"⚡ Parallel execution: {args.parallel}")
    logger.info(f"🤖 Bot service will be started using .env configuration")
    
    # Run tests
    results = asyncio.run(run_test_suite_with_bot(args.suite, args.parallel))
    
    if not results:
        logger.error("❌ No test results generated")
        sys.exit(1)
    
    # Generate report
    if args.report == 'json':
        report = TestReporter.generate_json_report(results)
    elif args.report == 'html':
        report = TestReporter.generate_html_report(results)
    else:
        report = TestReporter.generate_text_report(results)
    
    # Display report
    print(report)
    
    # Save report if requested
    if args.save:
        save_report(report, args.report, args.suite)
    
    # Exit with appropriate code
    failed_tests = len([r for r in results if not r.success])
    if failed_tests > 0:
        logger.warning(f"⚠️ {failed_tests} tests failed")
        sys.exit(1)
    else:
        logger.info("✅ All tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    main() 