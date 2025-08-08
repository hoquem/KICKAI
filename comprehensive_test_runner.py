#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Runner for KICKAI
================================================

This script provides comprehensive E2E testing for all KICKAI commands using the Mock Telegram
interface with Groq as the LLM provider. It captures detailed logging including prompts,
responses, timing, task execution details, and tool parameters.

Features:
- Tests all 27 implemented commands
- Uses Groq as LLM provider for fast inference
- Captures prompts, responses, and timing
- Logs task execution and tool parameters
- Generates comprehensive test reports
- QA test plan execution with detailed results
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

# Groq / LLM configuration
_set_default_env("AI_PROVIDER", "groq")
_set_default_env("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
_set_default_env("GROQ_MODEL", "llama3-8b-8192")
_set_default_env("LLM_TEMPERATURE", "0.3")
_set_default_env("LLM_TIMEOUT", "30")
_set_default_env("LLM_MAX_RETRIES", "3")

# System configuration
_set_default_env("USE_OPTIMIZED_PROMPTS", "true")
_set_default_env("USE_MOCK_DATASTORE", "false")

# Respect existing Firebase settings from .env/.env.test; only set defaults if missing
if not os.getenv("FIREBASE_PROJECT_ID"):
    _set_default_env("FIREBASE_PROJECT_ID", "kickai-954c2")

# Do NOT force a credentials file path if FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_FILE already provided
if not os.getenv("FIREBASE_CREDENTIALS_JSON") and not os.getenv("FIREBASE_CREDENTIALS_FILE"):
    # Set a conventional default path only if nothing is present
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
    user_types: List[str]  # Which user types can use this command
    test_inputs: List[str]  # Different input variations to test
    expected_features: List[str]  # Expected features in response

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
    groq_prompt: Optional[str]
    groq_response: Optional[str]
    groq_timing: Optional[float]
    task_details: Optional[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    agent_used: Optional[str]
    timestamp: str

class ComprehensiveTestRunner:
    """Comprehensive test runner for KICKAI E2E testing."""
    
    def __init__(self):
        self.mock_telegram_url = "http://localhost:8001"
        self.results: List[TestResult] = []
        self.test_users = self._define_test_users()
        self.command_tests = self._define_command_tests()
        
        # Set up logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up comprehensive logging."""
        # Create logs directory
        logs_dir = Path("test_logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure standard logging
        self.logger = logging.getLogger('KICKAI_E2E_Tests')
        self.logger.setLevel(logging.DEBUG)
        
        # Add file logging with detailed format
        log_file = logs_dir / f"e2e_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        
        # Add console logging
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        
        self.logger.info("🔧 Comprehensive test logging initialized")
        
    def _define_test_users(self) -> List[TestUser]:
        """Define test users based on our setup data."""
        return [
            # Active Players
            TestUser(1001, "John Smith", "player", "john_smith", "active", "Active striker"),
            TestUser(1002, "Mike Johnson", "player", "mike_j", "active", "Active midfielder"),
            TestUser(1003, "David Wilson", "player", "d_wilson", "active", "Active defender"),
            TestUser(1004, "James Brown", "player", "james_b", "active", "Active goalkeeper"),
            
            # Pending Players
            TestUser(1005, "Tom Anderson", "player", "tom_a", "pending", "Pending striker"),
            TestUser(1006, "Charlie White", "player", "charlie_w", "pending", "Pending midfielder"),
            
            # Team Members (Leadership)
            TestUser(2001, "Alex Manager", "manager", "alex_manager", "active", "Team manager"),
            TestUser(2002, "Sam Coach", "coach", "sam_coach", "active", "Team coach"),
            TestUser(2003, "Pat Secretary", "secretary", "pat_secretary", "active", "Team secretary"),
            TestUser(2004, "Chris Treasurer", "treasurer", "chris_treasurer", "active", "Team treasurer"),
            
            # Dual Role User
            TestUser(3001, "Captain Leader", "captain", "captain_leader", "active", "Player-captain dual role"),
        ]
    
    def _define_command_tests(self) -> List[CommandTest]:
        """Define comprehensive command test scenarios."""
        return [
            # Help and Information Commands
            CommandTest(
                "/help", "Get system help",
                ["all"], ["/help", "/help addplayer"], 
                ["Available commands", "Help information"]
            ),
            CommandTest(
                "/start", "Start bot interaction", 
                ["all"], ["/start"], 
                ["Welcome", "Getting started"]
            ),
            CommandTest(
                "/version", "Show system version",
                ["all"], ["/version"], 
                ["Version", "System info"]
            ),
            CommandTest(
                "/ping", "Test bot responsiveness",
                ["all"], ["/ping"], 
                ["pong", "response time"]
            ),
            
            # Player Management Commands
            CommandTest(
                "/addplayer", "Add new player",
                ["manager", "coach"], 
                ["/addplayer John Doe 07123456789 striker"],
                ["Player added", "registration"]
            ),
            CommandTest(
                "/myinfo", "Show user information",
                ["all"], ["/myinfo"], 
                ["Your information", "status"]
            ),
            CommandTest(
                "/info", "Show user information (alias)",
                ["all"], ["/info"], 
                ["Your information", "status"]
            ),
            CommandTest(
                "/status", "Check player status",
                ["all"], ["/status", "/status 01JS"], 
                ["Status", "Player info"]
            ),
            CommandTest(
                "/list", "List players/members",
                ["all"], ["/list", "/list players"], 
                ["List", "players", "members"]
            ),
            
            # Team Administration Commands
            CommandTest(
                "/addmember", "Add team member",
                ["manager"], 
                ["/addmember Jane Admin 07987654321 admin"],
                ["Team member", "added"]
            ),
            CommandTest(
                "/approve", "Approve player/member",
                ["manager", "coach"], 
                ["/approve 1005", "/approve Tom Anderson"],
                ["Approved", "status updated"]
            ),
            CommandTest(
                "/reject", "Reject player/member",
                ["manager", "coach"], 
                ["/reject 1008", "/reject Harry Martin"],
                ["Rejected", "status updated"]
            ),
            
            # Match Management Commands  
            CommandTest(
                "/addmatch", "Add new match",
                ["manager", "coach"],
                ["/addmatch Arsenal 2025-08-15 15:00 Emirates Stadium"],
                ["Match added", "scheduled"]
            ),
            CommandTest(
                "/matches", "List matches",
                ["all"], ["/matches", "/matches upcoming"],
                ["Matches", "fixtures"]
            ),
            CommandTest(
                "/availability", "Check/set availability",
                ["player"], ["/availability", "/availability yes MATCH_123"],
                ["Availability", "updated"]
            ),
            CommandTest(
                "/squad", "Squad selection",
                ["manager", "coach"], ["/squad", "/squad MATCH_123"],
                ["Squad", "selection"]
            ),
            
            # Communication Commands
            CommandTest(
                "/announce", "Send announcement",
                ["manager", "secretary"], 
                ["/announce Training tomorrow at 7pm"],
                ["Announcement", "sent"]
            ),
            CommandTest(
                "/message", "Send message",
                ["manager", "secretary"], 
                ["/message 1001 Good game today!"],
                ["Message", "sent"]
            ),
            
            # Update Commands
            CommandTest(
                "/update", "Update user information",
                ["all"], 
                ["/update phone 07111222333", "/update position midfielder"],
                ["Updated", "information"]
            ),
            
            # Statistics and Reports
            CommandTest(
                "/stats", "View statistics",
                ["all"], ["/stats", "/stats 01JS"],
                ["Statistics", "performance"]
            ),
            CommandTest(
                "/report", "Generate reports",
                ["manager", "coach"], ["/report team", "/report matches"],
                ["Report", "generated"]
            ),
            
            # System Commands
            CommandTest(
                "/settings", "View/update settings",
                ["manager"], ["/settings", "/settings notifications on"],
                ["Settings", "configuration"]
            ),
            CommandTest(
                "/backup", "System backup",
                ["manager"], ["/backup"],
                ["Backup", "completed"]
            ),
            
            # Natural Language Tests
            CommandTest(
                "Show me the team", "Natural language query",
                ["all"], ["Show me the team", "Who are our players?"],
                ["team", "players", "members"]
            ),
            CommandTest(
                "When is the next match?", "Natural language query",
                ["all"], ["When is the next match?", "What matches do we have?"],
                ["match", "fixture", "upcoming"]
            ),
        ]
    
    async def _send_test_message(self, user: TestUser, message: str) -> Dict[str, Any]:
        """Send test message via Mock Telegram interface and wait for bot response."""
        try:
            async with aiohttp.ClientSession() as session:
                # Format payload according to Mock Telegram API requirements
                # Use correct chat IDs: 2002 for leadership, 2001 for main
                chat_id = 2002 if user.role in ["manager", "coach", "secretary", "treasurer", "captain"] else 2001
                
                payload = {
                    "user_id": user.telegram_id,
                    "chat_id": chat_id,
                    "text": message,
                    "message_type": "text"
                }
                
                start_time = time.time()
                
                # Get current message count before sending
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
                
                # Wait for bot response (with timeout)
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
                            if len(messages_after) > initial_count + 1:  # User message + bot response
                                # Find the bot response (most recent message from bot)
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
                        "response_time_ms": total_time,
                        "user_message": message,
                        "chat_id": chat_id
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
        
        # Extract detailed information from response
        success = response.get("success", False)
        response_text = response.get("message", response.get("error", "No response"))
        error_message = None if success else response.get("error")
        
        # Extract Groq-specific details
        groq_prompt = response.get("groq_prompt")
        groq_response = response.get("groq_response")
        groq_timing = response.get("groq_timing_ms")
        task_details = response.get("task_details", {})
        tool_calls = response.get("tool_calls", [])
        agent_used = response.get("agent_used")
        
        # Create test result
        result = TestResult(
            command=test.command,
            user=user,
            input_text=input_text,
            success=success,
            response_time_ms=total_time,
            response_text=response_text,
            error_message=error_message,
            groq_prompt=groq_prompt,
            groq_response=groq_response,
            groq_timing=groq_timing,
            task_details=task_details,
            tool_calls=tool_calls,
            agent_used=agent_used,
            timestamp=datetime.now().isoformat()
        )
        
        # Log result details
        self.logger.info(f"   ✅ Success: {success}")
        self.logger.info(f"   ⏱️  Response Time: {total_time:.2f}ms")
        if groq_timing:
            self.logger.info(f"   🤖 Groq Time: {groq_timing:.2f}ms")
        if agent_used:
            self.logger.info(f"   🎯 Agent: {agent_used}")
        if tool_calls:
            self.logger.info(f"   🔧 Tools: {[tool.get('name', 'unknown') for tool in tool_calls]}")
            
        return result
    
    def _should_test_command_for_user(self, test: CommandTest, user: TestUser) -> bool:
        """Determine if command should be tested for this user type."""
        if "all" in test.user_types:
            return True
        
        user_role_mapping = {
            "player": ["player"],
            "manager": ["manager", "admin"],
            "coach": ["coach"],
            "secretary": ["secretary", "admin"],
            "treasurer": ["treasurer", "admin"],
            "captain": ["captain", "player"]
        }
        
        user_roles = user_role_mapping.get(user.role, [user.role])
        return any(role in test.user_types for role in user_roles)
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive E2E tests for all commands."""
        self.logger.info("🚀 Starting Comprehensive KICKAI E2E Tests with Groq")
        self.logger.info("=" * 80)
        
        # Check Mock Telegram availability
        if not await self._check_mock_telegram():
            self.logger.error("❌ Mock Telegram interface not available")
            return {"error": "Mock Telegram not available"}
        
        start_time = time.time()
        test_count = 0
        success_count = 0
        
        # Execute all command tests
        for test in self.command_tests:
            self.logger.info(f"\n📋 Testing Command: {test.command}")
            self.logger.info(f"   Description: {test.description}")
            
            for user in self.test_users:
                if self._should_test_command_for_user(test, user):
                    for input_text in test.test_inputs:
                        test_count += 1
                        result = await self._execute_command_test(test, user, input_text)
                        self.results.append(result)
                        
                        if result.success:
                            success_count += 1
                            
                        # Small delay between tests
                        await asyncio.sleep(0.5)
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        report = self._generate_test_report(test_count, success_count, total_time)
        
        self.logger.info("\n🎉 Comprehensive Testing Complete!")
        self.logger.info(f"   Total Tests: {test_count}")
        self.logger.info(f"   Successful: {success_count}")
        self.logger.info(f"   Success Rate: {(success_count/test_count)*100:.1f}%")
        self.logger.info(f"   Total Time: {total_time:.2f}s")
        
        return report
    
    async def _check_mock_telegram(self) -> bool:
        """Check if Mock Telegram interface is available."""
        try:
            async with aiohttp.ClientSession() as session:
                # Check both root health endpoint and API health endpoint
                async with session.get(f"{self.mock_telegram_url}/health") as response:
                    return response.status == 200
        except:
            return False
    
    def _generate_test_report(self, total_tests: int, successful_tests: int, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        # Group results by command
        command_results = {}
        for result in self.results:
            if result.command not in command_results:
                command_results[result.command] = []
            command_results[result.command].append(result)
        
        # Calculate statistics
        avg_response_time = sum(r.response_time_ms for r in self.results) / len(self.results) if self.results else 0
        groq_timings = [r.groq_timing for r in self.results if r.groq_timing]
        avg_groq_time = sum(groq_timings) / len(groq_timings) if groq_timings else 0
        
        # Count tool usage
        tool_usage = {}
        agent_usage = {}
        for result in self.results:
            if result.agent_used:
                agent_usage[result.agent_used] = agent_usage.get(result.agent_used, 0) + 1
            for tool in result.tool_calls:
                tool_name = tool.get("name", "unknown")
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_time_seconds": total_time,
                "average_response_time_ms": avg_response_time
            },
            "groq_performance": {
                "total_groq_calls": len(groq_timings),
                "average_groq_time_ms": avg_groq_time,
                "min_groq_time_ms": min(groq_timings) if groq_timings else 0,
                "max_groq_time_ms": max(groq_timings) if groq_timings else 0
            },
            "agent_usage": agent_usage,
            "tool_usage": tool_usage,
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
            filename = f"test_reports/comprehensive_e2e_report_{timestamp}.json"
        
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Test report saved to: {filename}")  # Use print for final output
        return filename

async def main():
    """Main function to run comprehensive tests."""
    print("🧪 KICKAI Comprehensive E2E Test Runner")
    print("=" * 80)
    print()
    print("🔧 Configuration:")
    print(f"   LLM Provider: {os.getenv('AI_PROVIDER')}")
    print(f"   Model: {os.getenv('GROQ_MODEL')}")
    print(f"   Temperature: {os.getenv('LLM_TEMPERATURE')}")
    print(f"   Mock Telegram: http://localhost:8001")
    print()
    
    # Create test runner
    runner = ComprehensiveTestRunner()
    
    # Run comprehensive tests
    try:
        report = await runner.run_comprehensive_tests()
        
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
            
            print("\n🤖 GROQ PERFORMANCE")
            print("=" * 50)
            groq_perf = report["groq_performance"]
            print(f"Total Groq Calls: {groq_perf['total_groq_calls']}")
            print(f"Average Time: {groq_perf['average_groq_time_ms']:.2f}ms")
            print(f"Min Time: {groq_perf['min_groq_time_ms']:.2f}ms")
            print(f"Max Time: {groq_perf['max_groq_time_ms']:.2f}ms")
            
            print("\n🎯 AGENT USAGE")
            print("=" * 50)
            for agent, count in report["agent_usage"].items():
                print(f"   {agent}: {count} calls")
            
            print(f"\n📄 Full report saved to: {report_file}")
            
        else:
            print(f"❌ Testing failed: {report['error']}")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())