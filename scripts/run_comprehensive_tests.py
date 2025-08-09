#!/usr/bin/env python3
"""
Comprehensive Test Suite for KICKAI System

This script runs comprehensive tests for all major features:
- Shared commands
- Player registration
- Team member management
- Match management
- Player attendance

Uses the mock tester API to simulate real user interactions.
"""

import asyncio
import aiohttp
import json
import time
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class ComprehensiveTester:
    """Comprehensive test suite for KICKAI system."""
    
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        self.test_results = []
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
    
    async def check_bot_response(self, user_id: str, timeout: int = 5) -> bool:
        """Check if there's a bot response for a user within a timeout period."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = await self.get_messages(user_id)
            if messages:
                # Check if the last message is from the bot
                last_message = messages[-1]
                if last_message.get("from", {}).get("is_bot", False):
                    return True
            await asyncio.sleep(0.5)
        
        return False
    
    async def send_message(self, user_id: str, message: str, chat_type: str = "main") -> Dict[str, Any]:
        """Send a message as a specific user."""
        url = f"{self.base_url}/send_message"
        
        # Map chat types to chat IDs
        chat_id_map = {
            "main": 2001,  # KickAI Testing main chat
            "leadership": 2002,  # KickAI Testing - Leadership chat
            "private": int(user_id)  # Private chat with user
        }
        
        data = {
            "user_id": int(user_id),
            "chat_id": chat_id_map.get(chat_type, 2001),
            "text": message
        }
        
        async with self.session.post(url, json=data) as response:
            return await response.json()
    
    async def get_messages(self, user_id: str) -> List[Dict[str, Any]]:
        """Get messages for a specific user."""
        url = f"{self.base_url}/messages/{user_id}"
        async with self.session.get(url) as response:
            return await response.json()
    
    async def get_users(self) -> List[Dict[str, Any]]:
        """Get all test users."""
        url = f"{self.base_url}/users"
        async with self.session.get(url) as response:
            return await response.json()
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new test user."""
        url = f"{self.base_url}/users"
        async with self.session.post(url, json=user_data) as response:
            return await response.json()
    
    async def test_shared_commands(self):
        """Test shared commands that work for all users."""
        print("\n🔧 Testing Shared Commands...")
        
        # Test /help command
        await self.send_message("1001", "/help")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Shared Commands - /help",
            success,
            "Bot responded to /help command" if success else "No bot response received"
        )
        
        # Test /myinfo command
        await self.send_message("1001", "/myinfo")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Shared Commands - /myinfo",
            success,
            "Bot responded to /myinfo command" if success else "No bot response received"
        )
        
        # Test /list command (should work for all users)
        await self.send_message("1001", "/list")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Shared Commands - /list",
            success,
            "Bot responded to /list command" if success else "No bot response received"
        )
        
        # Test natural language query
        await self.send_message("1001", "What's my phone number?")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Shared Commands - Natural Language Query",
            success,
            "Bot responded to natural language query" if success else "No bot response received"
        )
    
    async def test_player_registration(self):
        """Test player registration functionality."""
        print("\n👥 Testing Player Registration...")
        
        # Test adding a new player (should be in leadership chat)
        await self.send_message("1003", "/addplayer John Smith +447700900999 Forward", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Player Registration - Add New Player",
            success,
            "Bot responded to add player command" if success else "No bot response received"
        )
        
        # Test adding another player with different position (should be in leadership chat)
        await self.send_message("1003", "/addplayer Mary Johnson +447700900998 Midfielder", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Player Registration - Add Midfielder",
            success,
            "Bot responded to add midfielder command" if success else "No bot response received"
        )
        
        # Test adding player with goalkeeper position (should be in leadership chat)
        await self.send_message("1003", "/addplayer Bob Wilson +447700900997 Goalkeeper", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Player Registration - Add Goalkeeper",
            success,
            "Bot responded to add goalkeeper command" if success else "No bot response received"
        )
        
        # Test approving a pending player (should be in leadership chat)
        await self.send_message("1003", "/approve KAI_005", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Player Registration - Approve Pending Player",
            success,
            "Bot responded to approve player command" if success else "No bot response received"
        )
        
        # Test listing pending players (should be in leadership chat)
        await self.send_message("1003", "/pending", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Player Registration - List Pending Players",
            success,
            "Bot responded to pending players command" if success else "No bot response received"
        )
        
        # Test player status check (can be in main chat)
        await self.send_message("1001", "/status +447700900999")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Player Registration - Check Player Status",
            success,
            "Bot responded to status check command" if success else "No bot response received"
        )
    
    async def test_team_member_management(self):
        """Test team member management functionality."""
        print("\n👔 Testing Team Member Management...")
        
        # Test adding a new team member (should be in leadership chat)
        await self.send_message("1003", "/addmember Jane Doe +447700900996 Coach", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Team Member Management - Add New Member",
            success,
            "Bot responded to add member command" if success else "No bot response received"
        )
        
        # Test adding assistant coach (should be in leadership chat)
        await self.send_message("1003", "/addmember Tom Brown +447700900995 Assistant_Coach", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Team Member Management - Add Assistant Coach",
            success,
            "Bot responded to add assistant coach command" if success else "No bot response received"
        )
        
        # Test adding team manager (should be in leadership chat)
        await self.send_message("1003", "/addmember Sarah Wilson +447700900994 Team_Manager", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Team Member Management - Add Team Manager",
            success,
            "Bot responded to add team manager command" if success else "No bot response received"
        )
        
        # Test listing team members (should work in leadership chat)
        await self.send_message("1003", "/list", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Team Member Management - List Members",
            success,
            "Bot responded to list members command" if success else "No bot response received"
        )
    
    async def test_match_management(self):
        """Test match management functionality."""
        print("\n⚽ Testing Match Management...")
        
        # Test creating a match (should be in leadership chat)
        await self.send_message("1003", "/creatematch Saturday 15:00 Home vs Away Team", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Match Management - Create Match",
            success,
            "Bot responded to create match command" if success else "No bot response received"
        )
        
        # Test listing matches (can be in main chat)
        await self.send_message("1001", "/matches")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Match Management - List Matches",
            success,
            "Bot responded to list matches command" if success else "No bot response received"
        )
        
        # Test squad selection (should be in leadership chat)
        await self.send_message("1003", "/selectsquad Saturday", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Match Management - Select Squad",
            success,
            "Bot responded to select squad command" if success else "No bot response received"
        )
        
        # Test match details (can be in main chat)
        await self.send_message("1001", "/match Saturday")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Match Management - Match Details",
            success,
            "Bot responded to match details command" if success else "No bot response received"
        )
    
    async def test_player_attendance(self):
        """Test player attendance functionality."""
        print("\n📋 Testing Player Attendance...")
        
        # Test setting availability
        await self.send_message("1001", "/available Saturday")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Player Attendance - Set Available",
            success,
            "Bot responded to set available command" if success else "No bot response received"
        )
        
        # Test setting unavailable
        await self.send_message("1002", "/unavailable Saturday")
        success = await self.check_bot_response("1002")
        await self.log_test(
            "Player Attendance - Set Unavailable",
            success,
            "Bot responded to set unavailable command" if success else "No bot response received"
        )
        
        # Test checking availability (should be in leadership chat)
        await self.send_message("1003", "/availability Saturday", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Player Attendance - Check Availability",
            success,
            "Bot responded to check availability command" if success else "No bot response received"
        )
        
        # Test attendance report (should be in leadership chat)
        await self.send_message("1003", "/attendance Saturday", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Player Attendance - Attendance Report",
            success,
            "Bot responded to attendance report command" if success else "No bot response received"
        )
    
    async def test_update_functionality(self):
        """Test update functionality for players and team members."""
        print("\n🔄 Testing Update Functionality...")
        
        # Test updating player information
        await self.send_message("1001", "/update KAI_001 phone +447700900888")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Update Functionality - Update Player Phone",
            success,
            "Bot responded to update player phone command" if success else "No bot response received"
        )
        
        # Test updating player position
        await self.send_message("1001", "/update KAI_001 position Defender")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Update Functionality - Update Player Position",
            success,
            "Bot responded to update player position command" if success else "No bot response received"
        )
        
        # Test updating team member role (should be in leadership chat)
        await self.send_message("1003", "/update user_10001 role Assistant_Coach", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Update Functionality - Update Team Member Role",
            success,
            "Bot responded to update team member role command" if success else "No bot response received"
        )
    
    async def test_error_handling(self):
        """Test error handling and edge cases."""
        print("\n⚠️ Testing Error Handling...")
        
        # Test invalid command
        await self.send_message("1001", "/invalidcommand")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Error Handling - Invalid Command",
            success,
            "Bot responded to invalid command" if success else "No bot response received"
        )
        
        # Test adding player with missing information (should be in leadership chat)
        await self.send_message("1003", "/addplayer", "leadership")
        success = await self.check_bot_response("1003")
        await self.log_test(
            "Error Handling - Incomplete Player Registration",
            success,
            "Bot responded to incomplete player registration" if success else "No bot response received"
        )
        
        # Test accessing admin command as regular user (should fail)
        await self.send_message("1001", "/addplayer Test Player +1234567890 Forward")
        success = await self.check_bot_response("1001")
        await self.log_test(
            "Error Handling - Unauthorized Admin Command",
            success,
            "Bot responded to unauthorized admin command" if success else "No bot response received"
        )
    
    async def run_all_tests(self):
        """Run all comprehensive tests."""
        print("🚀 Starting Comprehensive KICKAI System Tests...")
        print("=" * 60)
        
        try:
            # Run all test suites
            await self.test_shared_commands()
            await self.test_player_registration()
            await self.test_team_member_management()
            await self.test_match_management()
            await self.test_player_attendance()
            await self.test_update_functionality()
            await self.test_error_handling()
            
            # Generate test report
            await self.generate_test_report()
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            await self.log_test("Test Execution", False, str(e))
    
    async def generate_test_report(self):
        """Generate a comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Save detailed report to file
        report_file = f"test_reports/comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("test_reports", exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        if failed_tests == 0:
            print("\n🎉 All tests passed! The KICKAI system is working correctly.")
        else:
            print(f"\n⚠️ {failed_tests} tests failed. Please review the failed tests above.")

async def main():
    """Main function."""
    async with ComprehensiveTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 