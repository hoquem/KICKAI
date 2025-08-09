#!/usr/bin/env python3
"""
Comprehensive KICKAI Bot Test Runner

This script executes a comprehensive test suite for the KICKAI bot using:
- Mock Telegram Tester
- Groq LLM
- Real Firebase Firestore
- All 5 KICKAI agents

The test suite covers:
- System initialization
- Player registration
- Team member management
- Match management
- Natural language processing
- Error handling
- Cross-chat functionality
"""

import os
import sys
import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import requests
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from kickai.core.dependency_container import get_container, ensure_container_initialized
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.features.match_management.domain.services.match_service import MatchService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestResult:
    test_id: str
    test_name: str
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    command: Optional[str] = None
    response: Optional[str] = None
    agent_used: Optional[str] = None
    llm_calls: List[Dict[str, Any]] = None
    error: Optional[str] = None
    firestore_validation: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.llm_calls is None:
            self.llm_calls = []

    def to_dict(self):
        return asdict(self)


@dataclass
class LLMCall:
    timestamp: datetime
    prompt: str
    response: str
    model: str
    duration: float
    tokens_used: Optional[int] = None


class ComprehensiveTestRunner:
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.llm_calls: List[LLMCall] = []
        self.mock_server_url = "http://localhost:8001"
        self.test_teams = {
            "TEST1": {
                "name": "KickAI Test Team 1",
                "main_chat_id": "2001",
                "leadership_chat_id": "2002"
            },
            "TEST2": {
                "name": "KickAI Test Team 2", 
                "main_chat_id": "2003",
                "leadership_chat_id": "2004"
            }
        }
        self.test_players = {
            "JS": {"name": "John Smith", "phone": "+447123456789", "position": "Forward"},
            "SJ": {"name": "Sarah Johnson", "phone": "+447123456790", "position": "Midfielder"},
            "MD": {"name": "Mike Davis", "phone": "+447123456791", "position": "Defender"}
        }
        self.test_members = {
            "CW": {"name": "Coach Wilson", "phone": "+447123456792", "role": "Head Coach"},
            "MB": {"name": "Manager Brown", "phone": "+447123456793", "role": "Team Manager"}
        }
        
        # Initialize services
        self.container = ensure_container_initialized()
        self.player_service = self.container.get_service("PlayerService")
        self.team_service = self.container.get_service("TeamService")
        self.match_service = self.container.get_service("MatchService")

    async def setup_test_environment(self):
        """Set up the test environment with clean data"""
        logger.info("🔧 Setting up test environment...")
        
        # Clean up existing test data
        await self.cleanup_test_data()
        
        # Create test teams
        for team_id, team_data in self.test_teams.items():
            await self.create_test_team(team_id, team_data)
        
        # Create test players
        for player_id, player_data in self.test_players.items():
            await self.create_test_player(team_id="TEST1", player_id=player_id, **player_data)
        
        # Create test team members
        for member_id, member_data in self.test_members.items():
            await self.create_test_team_member(team_id="TEST1", member_id=member_id, **member_data)
        
        # Create test users and chats in mock server
        await self.setup_mock_server_data()
        
        logger.info("✅ Test environment setup complete")

    async def setup_mock_server_data(self):
        """Set up test users and chats in the mock server"""
        logger.info("🔧 Setting up mock server data...")
        
        # Create test users
        test_users = [
            {"username": "test_user_1", "first_name": "Test User 1", "id": 1001},
            {"username": "test_user_2", "first_name": "Test User 2", "id": 1002},
            {"username": "test_user_3", "first_name": "Test User 3", "id": 1003},
            {"username": "test_user_4", "first_name": "Test User 4", "id": 1004},
            {"username": "test_user_5", "first_name": "Test User 5", "id": 1005},
            {"username": "test_user_6", "first_name": "Test User 6", "id": 1006},
            {"username": "test_coach_1", "first_name": "Test Coach 1", "id": 2001},
        ]
        
        for user_data in test_users:
            await self.create_mock_user(user_data)
        
        # Create test chats
        test_chats = [
            {"id": 2001, "type": "group", "title": "KickAI Test Team 1 - Main", "is_main_chat": True},
            {"id": 2002, "type": "group", "title": "KickAI Test Team 1 - Leadership", "is_leadership_chat": True},
        ]
        
        for chat_data in test_chats:
            await self.create_mock_chat(chat_data)
        
        logger.info("✅ Mock server data setup complete")

    async def create_mock_user(self, user_data: Dict[str, Any]):
        """Create a test user in the mock server"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "username": user_data["username"],
                    "first_name": user_data["first_name"],
                    "role": "player"
                }
                
                async with session.post(f"{self.mock_server_url}/api/users", json=payload) as response:
                    if response.status == 200:
                        logger.info(f"✅ Created mock user: {user_data['username']}")
                    else:
                        logger.warning(f"⚠️ Could not create mock user {user_data['username']}: {await response.text()}")
        except Exception as e:
            logger.warning(f"⚠️ Could not create mock user {user_data['username']}: {e}")

    async def create_mock_chat(self, chat_data: Dict[str, Any]):
        """Create a test chat in the mock server"""
        try:
            # The mock server creates chats automatically when messages are sent
            # We'll just log that we're expecting these chats
            logger.info(f"✅ Expecting mock chat: {chat_data['title']} (ID: {chat_data['id']})")
        except Exception as e:
            logger.warning(f"⚠️ Could not create mock chat {chat_data['id']}: {e}")

    async def cleanup_test_data(self):
        """Clean up test data from Firestore"""
        logger.info("🧹 Cleaning up test data...")
        
        # Clean up test teams
        for team_id in self.test_teams.keys():
            try:
                # Delete team and all related data
                await self.team_service.delete_team(team_id)
            except Exception as e:
                logger.warning(f"Could not delete team {team_id}: {e}")

    async def create_test_team(self, team_id: str, team_data: Dict[str, Any]):
        """Create a test team"""
        try:
            from kickai.features.team_administration.domain.services.team_service import TeamCreateParams
            params = TeamCreateParams(
                name=team_data["name"],
                main_chat_id=team_data["main_chat_id"],
                leadership_chat_id=team_data["leadership_chat_id"],
                created_by="test_runner"
            )
            team = await self.team_service.create_team(params)
            logger.info(f"✅ Created test team: {team_id}")
        except Exception as e:
            logger.error(f"❌ Failed to create test team {team_id}: {e}")

    async def create_test_player(self, team_id: str, player_id: str, name: str, phone: str, position: str):
        """Create a test player"""
        try:
            from kickai.features.player_registration.domain.services.player_service import PlayerCreateParams
            params = PlayerCreateParams(
                name=name,
                phone=phone,
                position=position,
                team_id=team_id,
                created_by="test_runner"
            )
            player = await self.player_service.create_player(params)
            logger.info(f"✅ Created test player: {player_id} ({name})")
        except Exception as e:
            logger.error(f"❌ Failed to create test player {player_id}: {e}")

    async def create_test_team_member(self, team_id: str, member_id: str, name: str, phone: str, role: str):
        """Create a test team member"""
        try:
            member = await self.team_service.add_team_member(
                team_id=team_id,
                user_id=f"test_{member_id}",
                role=role,
                name=name,
                phone=phone
            )
            logger.info(f"✅ Created test team member: {member_id} ({name})")
        except Exception as e:
            logger.error(f"❌ Failed to create test team member {member_id}: {e}")

    async def send_message(self, chat_id: str, user_id: str, text: str) -> Dict[str, Any]:
        """Send a message to the mock Telegram service"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "text": text,
                    "timestamp": datetime.now().isoformat()
                }
                
                async with session.post(f"{self.mock_server_url}/api/send_message", json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            raise

    async def get_bot_response(self, chat_id: str, user_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Get the bot's response from the mock service"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    async with session.get(f"{self.mock_server_url}/api/get_messages?chat_id={chat_id}&user_id={user_id}") as response:
                        if response.status == 200:
                            messages = await response.json()
                            if messages:
                                return messages[-1]  # Return the latest message
                    
                    await asyncio.sleep(1)  # Wait 1 second before checking again
                
                return None
        except Exception as e:
            logger.error(f"❌ Failed to get bot response: {e}")
            return None

    async def run_test(self, test_id: str, test_name: str, command: str, chat_id: str, user_id: str, 
                      expected_agent: Optional[str] = None, validation_func: Optional[callable] = None) -> TestResult:
        """Run a single test"""
        result = TestResult(
            test_id=test_id,
            test_name=test_name,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            command=command
        )
        
        logger.info(f"🧪 Running test: {test_name}")
        logger.info(f"   Command: {command}")
        logger.info(f"   Chat: {chat_id}, User: {user_id}")
        
        try:
            # Send the command
            await self.send_message(chat_id, user_id, command)
            
            # Get bot response
            response = await self.get_bot_response(chat_id, user_id)
            
            if response:
                result.response = response.get("text", "")
                result.agent_used = response.get("agent_used", "unknown")
                result.end_time = datetime.now()
                result.duration = (result.end_time - result.start_time).total_seconds()
                
                # Validate response
                if validation_func:
                    validation_result = await validation_func(response)
                    result.firestore_validation = validation_result
                
                # Check if expected agent was used
                if expected_agent and result.agent_used != expected_agent:
                    result.status = TestStatus.FAILED
                    result.error = f"Expected agent {expected_agent}, got {result.agent_used}"
                else:
                    result.status = TestStatus.PASSED
                
                logger.info(f"✅ Test {test_name} completed in {result.duration:.2f}s")
                logger.info(f"   Agent: {result.agent_used}")
                logger.info(f"   Response: {result.response[:100]}...")
                
            else:
                result.status = TestStatus.FAILED
                result.error = "No response received from bot"
                result.end_time = datetime.now()
                result.duration = (result.end_time - result.start_time).total_seconds()
                logger.error(f"❌ Test {test_name} failed: No response")
                
        except Exception as e:
            result.status = TestStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            logger.error(f"❌ Test {test_name} failed: {e}")
        
        self.test_results.append(result)
        return result

    async def validate_player_registration(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that a player was registered correctly"""
        try:
            # Check if player exists in Firestore
            players = await self.player_service.get_all_players("TEST1")
            return {
                "players_count": len(players),
                "players": [{"name": p.full_name, "status": p.status} for p in players]
            }
        except Exception as e:
            return {"error": str(e)}

    async def validate_team_member_registration(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that a team member was registered correctly"""
        try:
            # Check if team member exists in Firestore
            members = await self.team_service.get_team_members("TEST1")
            return {
                "members_count": len(members),
                "members": [{"name": m.full_name, "role": m.role} for m in members]
            }
        except Exception as e:
            return {"error": str(e)}

    async def run_system_initialization_tests(self):
        """Run system initialization tests"""
        logger.info("🚀 Running System Initialization Tests")
        
        # Test 1.1: Bot Startup
        await self.run_test(
            test_id="1.1",
            test_name="Bot Startup",
            command="/start",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1001",
            expected_agent="message_processor"
        )
        
        # Test 1.2: Help System
        await self.run_test(
            test_id="1.2",
            test_name="Help System",
            command="/help",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1001",
            expected_agent="help_assistant"
        )
        
        # Test 1.3: Command Help
        await self.run_test(
            test_id="1.3",
            test_name="Command Help",
            command="/help register",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1001",
            expected_agent="help_assistant"
        )

    async def run_player_registration_tests(self):
        """Run player registration tests"""
        logger.info("👤 Running Player Registration Tests")
        
        # Test 2.1: Player Registration (Slash Command)
        await self.run_test(
            test_id="2.1",
            test_name="Player Registration (Slash)",
            command="/register JS",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1002",
            expected_agent="player_coordinator",
            validation_func=self.validate_player_registration
        )
        
        # Test 2.2: Player Registration (Natural Language)
        await self.run_test(
            test_id="2.2",
            test_name="Player Registration (NL)",
            command="I want to register as a player with ID SJ",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1003",
            expected_agent="player_coordinator",
            validation_func=self.validate_player_registration
        )
        
        # Test 2.3: Duplicate Registration
        await self.run_test(
            test_id="2.3",
            test_name="Duplicate Registration",
            command="/register JS",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1004",
            expected_agent="player_coordinator"
        )
        
        # Test 2.4: Player Status Check
        await self.run_test(
            test_id="2.4",
            test_name="Player Status Check",
            command="/myinfo",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1002",
            expected_agent="message_processor"
        )

    async def run_team_member_tests(self):
        """Run team member management tests"""
        logger.info("👔 Running Team Member Tests")
        
        # Test 3.1: Team Member Registration (Leadership Chat)
        await self.run_test(
            test_id="3.1",
            test_name="Team Member Registration",
            command="/register Coach Wilson",
            chat_id=self.test_teams["TEST1"]["leadership_chat_id"],
            user_id="2001",
            expected_agent="player_coordinator",
            validation_func=self.validate_team_member_registration
        )
        
        # Test 3.2: Team Member Status
        await self.run_test(
            test_id="3.2",
            test_name="Team Member Status",
            command="/myinfo",
            chat_id=self.test_teams["TEST1"]["leadership_chat_id"],
            user_id="2001",
            expected_agent="message_processor"
        )

    async def run_player_management_tests(self):
        """Run player management tests"""
        logger.info("⚽ Running Player Management Tests")
        
        # Test 4.1: Player Approval (Leadership)
        await self.run_test(
            test_id="4.1",
            test_name="Player Approval",
            command="/approve SJ",
            chat_id=self.test_teams["TEST1"]["leadership_chat_id"],
            user_id="2001",
            expected_agent="player_coordinator"
        )
        
        # Test 4.2: Player List (Main Chat)
        await self.run_test(
            test_id="4.2",
            test_name="Player List (Main Chat)",
            command="/list",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1001",
            expected_agent="message_processor"
        )
        
        # Test 4.3: Player List (Leadership Chat)
        await self.run_test(
            test_id="4.3",
            test_name="Player List (Leadership Chat)",
            command="/list",
            chat_id=self.test_teams["TEST1"]["leadership_chat_id"],
            user_id="2001",
            expected_agent="message_processor"
        )
        
        # Test 4.4: Player Status by Phone
        await self.run_test(
            test_id="4.4",
            test_name="Player Status by Phone",
            command="/status +447123456789",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1001",
            expected_agent="message_processor"
        )

    async def run_natural_language_tests(self):
        """Run natural language processing tests"""
        logger.info("🗣️ Running Natural Language Tests")
        
        # Test 7.1: Status Query
        await self.run_test(
            test_id="7.1",
            test_name="Status Query (NL)",
            command="What's my current status?",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1002",
            expected_agent="message_processor"
        )
        
        # Test 7.2: Player Information
        await self.run_test(
            test_id="7.2",
            test_name="Player Information (NL)",
            command="Who are the active players?",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1001",
            expected_agent="message_processor"
        )
        
        # Test 7.3: Help Request
        await self.run_test(
            test_id="7.3",
            test_name="Help Request (NL)",
            command="How do I register as a player?",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1005",
            expected_agent="help_assistant"
        )

    async def run_error_handling_tests(self):
        """Run error handling tests"""
        logger.info("⚠️ Running Error Handling Tests")
        
        # Test 8.1: Invalid Command
        await self.run_test(
            test_id="8.1",
            test_name="Invalid Command",
            command="/invalidcommand",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1001",
            expected_agent="help_assistant"
        )
        
        # Test 8.2: Missing Parameters
        await self.run_test(
            test_id="8.2",
            test_name="Missing Parameters",
            command="/register",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1006",
            expected_agent="player_coordinator"
        )
        
        # Test 8.3: Unauthorized Access
        await self.run_test(
            test_id="8.3",
            test_name="Unauthorized Access",
            command="/approve JS",
            chat_id=self.test_teams["TEST1"]["main_chat_id"],
            user_id="1001",
            expected_agent="message_processor"
        )

    async def run_all_tests(self):
        """Run all test categories"""
        logger.info("🎯 Starting Comprehensive Test Suite")
        
        # Set up test environment
        await self.setup_test_environment()
        
        # Run test categories
        await self.run_system_initialization_tests()
        await self.run_player_registration_tests()
        await self.run_team_member_tests()
        await self.run_player_management_tests()
        await self.run_natural_language_tests()
        await self.run_error_handling_tests()
        
        # Generate report
        await self.generate_test_report()

    async def generate_test_report(self):
        """Generate a comprehensive test report"""
        logger.info("📊 Generating Test Report")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == TestStatus.PASSED])
        failed_tests = len([r for r in self.test_results if r.status == TestStatus.FAILED])
        skipped_tests = len([r for r in self.test_results if r.status == TestStatus.SKIPPED])
        
        total_duration = sum([r.duration or 0 for r in self.test_results])
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        # Agent usage statistics
        agent_usage = {}
        for result in self.test_results:
            if result.agent_used:
                agent_usage[result.agent_used] = agent_usage.get(result.agent_used, 0) + 1
        
        # Create report
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration,
                "average_duration": avg_duration
            },
            "agent_usage": agent_usage,
            "test_results": [result.to_dict() for result in self.test_results],
            "llm_calls": [asdict(call) for call in self.llm_calls],
            "timestamp": datetime.now().isoformat()
        }
        
        # Save report to file
        report_file = f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*60)
        print("🎯 COMPREHENSIVE TEST REPORT")
        print("="*60)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️  Skipped: {skipped_tests}")
        print(f"📈 Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        print(f"⏱️  Average Duration: {avg_duration:.2f}s")
        print("\n🤖 Agent Usage:")
        for agent, count in agent_usage.items():
            print(f"   {agent}: {count} tests")
        print(f"\n📄 Full report saved to: {report_file}")
        print("="*60)
        
        # Print failed tests
        failed_results = [r for r in self.test_results if r.status == TestStatus.FAILED]
        if failed_results:
            print("\n❌ FAILED TESTS:")
            for result in failed_results:
                print(f"   {result.test_id}: {result.test_name}")
                print(f"      Error: {result.error}")
                print()

        logger.info(f"📄 Test report saved to: {report_file}")


async def main():
    """Main entry point"""
    print("🚀 Starting KICKAI Comprehensive Test Suite")
    print("="*60)
    print("🔧 Environment: Mock Telegram + Groq LLM + Real Firestore")
    print("🤖 Agents: All 5 KICKAI agents")
    print("📊 Coverage: System, Registration, Management, NLP, Errors")
    print("="*60)
    
    # Check if mock server is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code != 200:
            print("❌ Mock Telegram server is not running")
            print("Please start the mock server first:")
            print("   python tests/mock_telegram/start_mock_tester.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Mock Telegram server is not running")
        print("Please start the mock server first:")
        print("   python tests/mock_telegram/start_mock_tester.py")
        return
    
    print("✅ Mock Telegram server is running")
    
    # Create and run test runner
    runner = ComprehensiveTestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
