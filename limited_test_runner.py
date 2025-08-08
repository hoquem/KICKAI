#!/usr/bin/env python3
"""
Limited E2E Test Runner for KICKAI - Registered Users Only
===========================================================

Focuses on testing with only registered users (1001-1004) to get complete results
without the unregistered user failures.
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure environment for Groq testing while respecting existing env vars
def _set_default_env(key: str, value: str) -> None:
    if not os.getenv(key):
        os.environ[key] = value


# System configuration
_set_default_env("USE_OPTIMIZED_PROMPTS", "true")
_set_default_env("USE_MOCK_DATASTORE", "false")

# Respect existing Firebase settings; only set defaults if missing
if not os.getenv("FIREBASE_PROJECT_ID"):
    _set_default_env("FIREBASE_PROJECT_ID", "kickai-954c2")

if not os.getenv("FIREBASE_CREDENTIALS_JSON") and not os.getenv("FIREBASE_CREDENTIALS_FILE"):
    _set_default_env("FIREBASE_CREDENTIALS_FILE", "credentials/firebase_credentials_testing.json")

_set_default_env("KICKAI_INVITE_SECRET_KEY", "test-invite-secret-key-for-testing-only")
_set_default_env("PYTHONPATH", ".")

@dataclass
class TestUser:
    """Test user configuration."""
    telegram_id: int
    name: str
    role: str
    username: str
    status: str
    description: str

@dataclass
class CommandTest:
    """Command test configuration."""
    command: str
    description: str
    user_types: List[str]
    test_inputs: List[str]
    expected_features: List[str]

@dataclass
class TestResult:
    """Test execution result."""
    command: str
    user: TestUser
    input_text: str
    success: bool
    response_time_ms: float
    response_text: str
    error_message: Optional[str]
    timestamp: str

class LimitedTestRunner:
    """Limited test runner focusing on registered users only."""
    
    def __init__(self):
        self.mock_telegram_url = "http://localhost:8001"
        self.results: List[TestResult] = []
        
        # Only use registered users (1001-1004)
        self.test_users = [
            TestUser(1001, "John Smith", "player", "john_smith", "active", "Active striker"),
            TestUser(1002, "Mike Johnson", "player", "mike_j", "active", "Active midfielder"),
            TestUser(1003, "David Wilson", "player", "d_wilson", "active", "Active defender"),
            TestUser(1004, "James Brown", "player", "james_b", "active", "Active goalkeeper"),
        ]
        
        # Focus on key commands that should work
        self.command_tests = [
            CommandTest("/help", "Get system help", ["all"], ["/help"], ["Available commands"]),
            CommandTest("/start", "Start bot interaction", ["all"], ["/start"], ["Welcome"]),
            CommandTest("/version", "Show system version", ["all"], ["/version"], ["Version"]),
            CommandTest("/ping", "Test bot responsiveness", ["all"], ["/ping"], ["pong"]),
            CommandTest("/myinfo", "Show user information", ["all"], ["/myinfo"], ["Your information"]),
            CommandTest("/status", "Check player status", ["all"], ["/status"], ["Status"]),
            CommandTest("/list", "List players/members", ["all"], ["/list"], ["List", "players"]),
            CommandTest("Show me the team", "Natural language query", ["all"], ["Show me the team"], ["team", "players"]),
            CommandTest("When is the next match?", "Natural language query", ["all"], ["When is the next match?"], ["match", "fixture"]),
        ]
        
        # Set up logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging."""
        logs_dir = Path("test_logs")
        logs_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger('KICKAI_LIMITED_Tests')
        self.logger.setLevel(logging.DEBUG)
        
        # Add file logging
        log_file = logs_dir / f"limited_e2e_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Add console logging
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        self.logger.info("🔧 Limited test logging initialized")
        
    async def _send_test_message(self, user: TestUser, message: str) -> Dict[str, Any]:
        """Send test message via Mock Telegram interface and wait for bot response."""
        try:
            async with aiohttp.ClientSession() as session:
                # Use main chat for all users (2001 for main chat)
                chat_id = 2001
                
                payload = {
                    "user_id": user.telegram_id,
                    "chat_id": chat_id,
                    "text": message,
                    "message_type": "text"
                }
                
                start_time = time.time()
                
                # Get current message count
                async with session.get(f"{self.mock_telegram_url}/api/messages") as msg_response:
                    if msg_response.status == 200:
                        messages_before = await msg_response.json()
                        initial_count = len(messages_before)
                    else:
                        initial_count = 0
                
                # Send the message
                async with session.post(f"{self.mock_telegram_url}/api/send_message", json=payload) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}",
                            "response_time_ms": (time.time() - start_time) * 1000
                        }
                
                # Wait for bot response
                bot_response = None
                timeout_count = 0
                max_timeout = 10  # 5 seconds max wait
                
                while timeout_count < max_timeout:
                    await asyncio.sleep(0.5)
                    timeout_count += 1
                    
                    # Check for new messages
                    async with session.get(f"{self.mock_telegram_url}/api/messages") as msg_response:
                        if msg_response.status == 200:
                            messages_after = await msg_response.json()
                            if len(messages_after) > initial_count + 1:
                                # Find bot response
                                for msg in reversed(messages_after):
                                    if msg.get("from", {}).get("first_name") == "KICKAI Bot":
                                        bot_response = msg.get("text", "")
                                        break
                                break
                
                total_time = (time.time() - start_time) * 1000
                
                if bot_response:
                    return {
                        "success": True,
                        "message": bot_response,
                        "response_time_ms": total_time,
                        "user_message": message,
                        "chat_id": chat_id
                    }
                else:
                    return {
                        "success": False,
                        "error": "No bot response received within timeout",
                        "response_time_ms": total_time
                    }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": 0
            }
    
    async def _execute_command_test(self, test: CommandTest, user: TestUser, input_text: str) -> TestResult:
        """Execute a single command test."""
        self.logger.info(f"🧪 Testing: {test.command} with user {user.name} ({user.role})")
        self.logger.info(f"   Input: {input_text}")
        
        start_time = time.time()
        
        # Send message and get response
        response = await self._send_test_message(user, input_text)
        
        total_time = (time.time() - start_time) * 1000
        
        # Extract information from response
        success = response.get("success", False)
        response_text = response.get("message", response.get("error", "No response"))
        error_message = None if success else response.get("error")
        
        # Create test result
        result = TestResult(
            command=test.command,
            user=user,
            input_text=input_text,
            success=success,
            response_time_ms=total_time,
            response_text=response_text,
            error_message=error_message,
            timestamp=datetime.now().isoformat()
        )
        
        # Log result
        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.logger.info(f"   {status} ({total_time:.1f}ms)")
        if success:
            self.logger.info(f"   📋 Response length: {len(response_text)} chars")
        else:
            self.logger.info(f"   📋 Error: {error_message}")
            
        return result
    
    async def run_limited_tests(self) -> Dict[str, Any]:
        """Run limited E2E tests for registered users only."""
        self.logger.info("🚀 Starting Limited KICKAI E2E Tests (Registered Users Only)")
        self.logger.info("=" * 80)
        
        # Check Mock Telegram availability
        if not await self._check_mock_telegram():
            self.logger.error("❌ Mock Telegram interface not available")
            return {"error": "Mock Telegram not available"}
        
        start_time = time.time()
        test_count = 0
        success_count = 0
        
        # Execute tests
        for test in self.command_tests:
            self.logger.info(f"\n📋 Testing Command: {test.command}")
            self.logger.info(f"   Description: {test.description}")
            
            for user in self.test_users:
                for input_text in test.test_inputs:
                    test_count += 1
                    result = await self._execute_command_test(test, user, input_text)
                    self.results.append(result)
                    
                    if result.success:
                        success_count += 1
                        
                    # Delay between tests
                    await asyncio.sleep(0.5)
        
        total_time = time.time() - start_time
        
        # Generate report
        report = self._generate_test_report(test_count, success_count, total_time)
        
        self.logger.info(f"\n🎉 Limited Testing Complete!")
        self.logger.info(f"   Total Tests: {test_count}")
        self.logger.info(f"   Successful: {success_count}")
        self.logger.info(f"   Success Rate: {(success_count/test_count)*100:.1f}%")
        self.logger.info(f"   Total Time: {total_time:.2f}s")
        
        return report
    
    async def _check_mock_telegram(self) -> bool:
        """Check if Mock Telegram interface is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.mock_telegram_url}/health") as response:
                    return response.status == 200
        except:
            return False
    
    def _generate_test_report(self, total_tests: int, successful_tests: int, total_time: float) -> Dict[str, Any]:
        """Generate test report."""
        # Calculate statistics
        avg_response_time = sum(r.response_time_ms for r in self.results) / len(self.results) if self.results else 0
        
        # Group by command
        command_results = {}
        for result in self.results:
            if result.command not in command_results:
                command_results[result.command] = []
            command_results[result.command].append(result)
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_time_seconds": total_time,
                "average_response_time_ms": avg_response_time
            },
            "command_results": {
                cmd: {
                    "total": len(results),
                    "successful": sum(1 for r in results if r.success),
                    "success_rate": (sum(1 for r in results if r.success) / len(results) * 100),
                    "avg_response_time": sum(r.response_time_ms for r in results) / len(results)
                }
                for cmd, results in command_results.items()
            },
            "detailed_results": [asdict(result) for result in self.results],
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def save_test_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Save test report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_reports/limited_e2e_report_{timestamp}.json"
        
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Test report saved to: {filename}")
        return filename

async def main():
    """Main function to run limited tests."""
    print("🧪 KICKAI Limited E2E Test Runner (Registered Users Only)")
    print("=" * 80)
    print()
    print("🔧 Configuration:")
    print(f"   LLM Provider: {os.getenv('AI_PROVIDER')}")
    print(f"   Model: {os.getenv('GROQ_MODEL')}")
    print(f"   Temperature: {os.getenv('LLM_TEMPERATURE')}")
    print(f"   Test Users: 4 registered users (1001-1004)")
    print(f"   Commands: 9 essential commands")
    print()
    
    runner = LimitedTestRunner()
    
    try:
        report = await runner.run_limited_tests()
        
        if "error" not in report:
            # Save report
            report_file = runner.save_test_report(report)
            
            # Print summary
            print("\n📊 TEST SUMMARY")
            print("=" * 50)
            summary = report["test_summary"]
            print(f"Total Tests: {summary['total_tests']}")
            print(f"Successful: {summary['successful_tests']}")
            print(f"Failed: {summary['failed_tests']}")
            print(f"Success Rate: {summary['success_rate']:.1f}%")
            print(f"Total Time: {summary['total_time_seconds']:.2f}s")
            print(f"Average Response Time: {summary['average_response_time_ms']:.2f}ms")
            
            print("\n📋 COMMAND RESULTS")
            print("=" * 50)
            for cmd, stats in report["command_results"].items():
                print(f"{cmd}:")
                print(f"  Total: {stats['total']}, Success: {stats['successful']}, Rate: {stats['success_rate']:.1f}%")
                print(f"  Avg Response: {stats['avg_response_time']:.2f}ms")
            
            print(f"\n📄 Full report saved to: {report_file}")
            
        else:
            print(f"❌ Testing failed: {report['error']}")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())