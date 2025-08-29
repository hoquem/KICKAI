#!/usr/bin/env python3
"""
Comprehensive QA Testing Script for KICKAI Bot
Tests all shared, player, and team management commands using Playwright and Mock Telegram UI

Author: Expert QA Engineer
Date: 2025-08-25
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from playwright.async_api import async_playwright, Page, Browser
from dataclasses import dataclass, asdict
from enum import Enum

class TestStatus(Enum):
    PASSED = "✅ PASSED"
    FAILED = "❌ FAILED"
    SKIPPED = "⏭️ SKIPPED"
    ERROR = "💥 ERROR"

@dataclass
class TestResult:
    command: str
    test_case: str
    status: TestStatus
    duration: float
    error_message: str = ""
    response_received: bool = False
    response_content: str = ""
    expected_patterns: List[str] = None
    actual_response: str = ""

@dataclass
class CommandTestReport:
    command_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    test_results: List[TestResult]
    success_rate: float
    average_response_time: float

class KICKAIQATester:
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.test_results: List[TestResult] = []
        self.current_test_start = 0
        
    async def setup(self):
        """Initialize Playwright and navigate to mock Telegram UI"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False, slow_mo=100)
        self.page = await self.browser.new_page()
        
        # Navigate to mock Telegram UI
        await self.page.goto("http://localhost:8001")
        await self.page.wait_for_load_state("networkidle")
        
        print("🔧 QA Testing Environment Setup Complete")
        
    async def teardown(self):
        """Clean up Playwright resources"""
        if self.browser:
            await self.browser.close()
            
    async def start_test(self, command: str, test_case: str):
        """Start timing a test"""
        self.current_test_start = time.time()
        print(f"🧪 Testing: {command} - {test_case}")
        
    async def end_test(self, command: str, test_case: str, status: TestStatus, 
                      error_message: str = "", response_content: str = "", 
                      expected_patterns: List[str] = None) -> TestResult:
        """End timing and record test result"""
        duration = time.time() - self.current_test_start
        
        result = TestResult(
            command=command,
            test_case=test_case,
            status=status,
            duration=duration,
            error_message=error_message,
            response_received=bool(response_content),
            response_content=response_content,
            expected_patterns=expected_patterns or [],
            actual_response=response_content
        )
        
        self.test_results.append(result)
        
        status_emoji = "✅" if status == TestStatus.PASSED else "❌" if status == TestStatus.FAILED else "⏭️" if status == TestStatus.SKIPPED else "💥"
        print(f"{status_emoji} {command} - {test_case} ({duration:.2f}s)")
        
        return result
        
    async def send_message(self, message: str) -> str:
        """Send a message in the mock Telegram UI and wait for response"""
        try:
            # Find the input field and send message
            await self.page.fill('input[placeholder*="message"]', message)
            await self.page.press('input[placeholder*="message"]', 'Enter')
            
            # Wait for response (adjust selector based on mock UI structure)
            await self.page.wait_for_timeout(2000)  # Wait for bot processing
            
            # Get the last message in the chat
            messages = await self.page.query_selector_all('.message, .bot-message, .response')
            if messages:
                last_message = messages[-1]
                response_text = await last_message.text_content()
                return response_text.strip() if response_text else ""
            
            return ""
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return ""
            
    async def test_help_commands(self):
        """Test help and system commands"""
        print("\n📋 TESTING HELP & SYSTEM COMMANDS")
        
        # Test /help command
        await self.start_test("/help", "Basic help command")
        response = await self.send_message("/help")
        await self.end_test("/help", "Basic help command", 
                           TestStatus.PASSED if "KICKAI Help" in response else TestStatus.FAILED,
                           response_content=response,
                           expected_patterns=["KICKAI Help", "Available Commands"])
        
        # Test /help with specific command
        await self.start_test("/help", "Help for specific command")
        response = await self.send_message("/help addplayer")
        await self.end_test("/help", "Help for specific command",
                           TestStatus.PASSED if response else TestStatus.FAILED,
                           response_content=response)
        
        # Test /version command
        await self.start_test("/version", "Version information")
        response = await self.send_message("/version")
        await self.end_test("/version", "Version information",
                           TestStatus.PASSED if "version" in response.lower() else TestStatus.FAILED,
                           response_content=response,
                           expected_patterns=["version", "KICKAI"])
        
        # Test /ping command
        await self.start_test("/ping", "Bot status check")
        response = await self.send_message("/ping")
        await self.end_test("/ping", "Bot status check",
                           TestStatus.PASSED if "pong" in response.lower() or "online" in response.lower() else TestStatus.FAILED,
                           response_content=response)
        
    async def test_player_management_commands(self):
        """Test player management commands"""
        print("\n👤 TESTING PLAYER MANAGEMENT COMMANDS")
        
        # Test /myinfo command
        await self.start_test("/myinfo", "Get user information")
        response = await self.send_message("/myinfo")
        await self.end_test("/myinfo", "Get user information",
                           TestStatus.PASSED if response else TestStatus.FAILED,
                           response_content=response)
        
        # Test /list command (main chat context)
        await self.start_test("/list", "List players in main chat")
        response = await self.send_message("/list")
        await self.end_test("/list", "List players in main chat",
                           TestStatus.PASSED if response else TestStatus.FAILED,
                           response_content=response,
                           expected_patterns=["players", "list"])
        
        # Test /status command
        await self.start_test("/status", "Get player status")
        response = await self.send_message("/status")
        await self.end_test("/status", "Get player status",
                           TestStatus.PASSED if response else TestStatus.FAILED,
                           response_content=response)
        
        # Test natural language queries
        await self.start_test("Natural Language", "What's my phone number?")
        response = await self.send_message("What's my phone number?")
        await self.end_test("Natural Language", "What's my phone number?",
                           TestStatus.PASSED if response else TestStatus.FAILED,
                           response_content=response)
        
    async def test_team_administration_commands(self):
        """Test team administration commands (leadership context)"""
        print("\n👔 TESTING TEAM ADMINISTRATION COMMANDS")
        
        # Test /addplayer command
        await self.start_test("/addplayer", "Add new player")
        response = await self.send_message("/addplayer John Smith +447123456789")
        await self.end_test("/addplayer", "Add new player",
                           TestStatus.PASSED if "player" in response.lower() or "added" in response.lower() else TestStatus.FAILED,
                           response_content=response,
                           expected_patterns=["player", "added", "created"])
        
        # Test /addmember command
        await self.start_test("/addmember", "Add team member")
        response = await self.send_message("/addmember Sarah Johnson +447987654321")
        await self.end_test("/addmember", "Add team member",
                           TestStatus.PASSED if "member" in response.lower() or "added" in response.lower() else TestStatus.FAILED,
                           response_content=response,
                           expected_patterns=["member", "added", "created"])
        
        # Test /list command (leadership context)
        await self.start_test("/list", "List all in leadership chat")
        response = await self.send_message("/list")
        await self.end_test("/list", "List all in leadership chat",
                           TestStatus.PASSED if response else TestStatus.FAILED,
                           response_content=response)
        
    async def test_player_update_commands(self):
        """Test player update commands"""
        print("\n📝 TESTING PLAYER UPDATE COMMANDS")
        
        # Test /update phone command
        await self.start_test("/update", "Update phone number")
        response = await self.send_message("/update phone +447123456789")
        await self.end_test("/update", "Update phone number",
                           TestStatus.PASSED if "updated" in response.lower() or "phone" in response.lower() else TestStatus.FAILED,
                           response_content=response,
                           expected_patterns=["updated", "phone"])
        
        # Test /update position command
        await self.start_test("/update", "Update position")
        response = await self.send_message("/update position midfielder")
        await self.end_test("/update", "Update position",
                           TestStatus.PASSED if "updated" in response.lower() or "position" in response.lower() else TestStatus.FAILED,
                           response_content=response,
                           expected_patterns=["updated", "position"])
        
        # Test /update with invalid field
        await self.start_test("/update", "Invalid field update")
        response = await self.send_message("/update invalid_field test_value")
        await self.end_test("/update", "Invalid field update",
                           TestStatus.PASSED if "error" in response.lower() or "invalid" in response.lower() else TestStatus.FAILED,
                           response_content=response)
        
    async def test_permission_commands(self):
        """Test permission and access control"""
        print("\n🔒 TESTING PERMISSION & ACCESS CONTROL")
        
        # Test unauthorized command access
        await self.start_test("Permission", "Unauthorized command access")
        response = await self.send_message("/admin_only_command")
        await self.end_test("Permission", "Unauthorized command access",
                           TestStatus.PASSED if "denied" in response.lower() or "unauthorized" in response.lower() else TestStatus.FAILED,
                           response_content=response)
        
        # Test invalid command
        await self.start_test("Invalid Command", "Non-existent command")
        response = await self.send_message("/nonexistentcommand")
        await self.end_test("Invalid Command", "Non-existent command",
                           TestStatus.PASSED if "not found" in response.lower() or "unknown" in response.lower() else TestStatus.FAILED,
                           response_content=response)
        
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n⚠️ TESTING ERROR HANDLING")
        
        # Test empty command
        await self.start_test("Error Handling", "Empty command")
        response = await self.send_message("")
        await self.end_test("Error Handling", "Empty command",
                           TestStatus.PASSED if not response or "error" in response.lower() else TestStatus.FAILED,
                           response_content=response)
        
        # Test malformed command
        await self.start_test("Error Handling", "Malformed command")
        response = await self.send_message("/update")
        await self.end_test("Error Handling", "Malformed command",
                           TestStatus.PASSED if "error" in response.lower() or "missing" in response.lower() else TestStatus.FAILED,
                           response_content=response)
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("\n📊 GENERATING COMPREHENSIVE TEST REPORT")
        
        # Group results by command
        command_results = {}
        for result in self.test_results:
            if result.command not in command_results:
                command_results[result.command] = []
            command_results[result.command].append(result)
        
        # Generate command-specific reports
        command_reports = []
        for command, results in command_results.items():
            total = len(results)
            passed = len([r for r in results if r.status == TestStatus.PASSED])
            failed = len([r for r in results if r.status == TestStatus.FAILED])
            skipped = len([r for r in results if r.status == TestStatus.SKIPPED])
            error = len([r for r in results if r.status == TestStatus.ERROR])
            
            success_rate = (passed / total * 100) if total > 0 else 0
            avg_time = sum(r.duration for r in results) / total if total > 0 else 0
            
            report = CommandTestReport(
                command_name=command,
                total_tests=total,
                passed_tests=passed,
                failed_tests=failed,
                skipped_tests=skipped,
                error_tests=error,
                test_results=results,
                success_rate=success_rate,
                average_response_time=avg_time
            )
            command_reports.append(asdict(report))
        
        # Overall statistics
        total_tests = len(self.test_results)
        total_passed = len([r for r in self.test_results if r.status == TestStatus.PASSED])
        total_failed = len([r for r in self.test_results if r.status == TestStatus.FAILED])
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "test_session": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": total_failed,
                "overall_success_rate": overall_success_rate,
                "test_duration": sum(r.duration for r in self.test_results)
            },
            "command_reports": command_reports,
            "detailed_results": [asdict(r) for r in self.test_results]
        }
        
        return report
        
    async def run_all_tests(self):
        """Execute all test suites"""
        print("🚀 STARTING COMPREHENSIVE QA TESTING")
        print("=" * 60)
        
        try:
            await self.setup()
            
            # Run all test suites
            await self.test_help_commands()
            await self.test_player_management_commands()
            await self.test_team_administration_commands()
            await self.test_player_update_commands()
            await self.test_permission_commands()
            await self.test_error_handling()
            
            # Generate and save report
            report = self.generate_report()
            
            # Save report to file
            with open("qa_test_report.json", "w") as f:
                json.dump(report, f, indent=2)
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 QA TESTING SUMMARY")
            print("=" * 60)
            print(f"Total Tests: {report['test_session']['total_tests']}")
            print(f"Passed: {report['test_session']['passed_tests']}")
            print(f"Failed: {report['test_session']['failed_tests']}")
            print(f"Success Rate: {report['test_session']['overall_success_rate']:.1f}%")
            print(f"Total Duration: {report['test_session']['test_duration']:.2f}s")
            print(f"Report saved to: qa_test_report.json")
            
            # Print command-specific results
            print("\n📋 COMMAND-SPECIFIC RESULTS:")
            for cmd_report in report['command_reports']:
                status = "✅" if cmd_report['success_rate'] >= 80 else "⚠️" if cmd_report['success_rate'] >= 50 else "❌"
                print(f"{status} {cmd_report['command_name']}: {cmd_report['success_rate']:.1f}% ({cmd_report['passed_tests']}/{cmd_report['total_tests']})")
            
        except Exception as e:
            print(f"💥 Testing failed with error: {e}")
        finally:
            await self.teardown()

async def main():
    """Main function to run QA testing"""
    tester = KICKAIQATester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
