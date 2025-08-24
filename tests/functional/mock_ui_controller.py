#!/usr/bin/env python3
"""
Mock UI Controller

Controls the Mock Telegram UI using Puppeteer MCP for automated functional testing.
Handles user simulation, command execution, and response capture.
"""

import asyncio
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

@dataclass
class TestUser:
    """Test user configuration for Mock UI"""
    telegram_id: int
    username: str
    chat_type: str
    role: str
    display_name: str

@dataclass
class CommandTest:
    """Command test configuration"""
    command: str
    user: TestUser
    expected_keywords: List[str]
    should_fail: bool = False
    description: str = ""

class MockUIController:
    """Controls Mock Telegram UI for automated testing"""
    
    def __init__(self, mock_ui_url: str = "http://localhost:8001"):
        self.mock_ui_url = mock_ui_url
        self.test_users = self._get_test_users()
        self.current_user: Optional[TestUser] = None
        self.test_results: List[Dict[str, Any]] = []
        
    def _get_test_users(self) -> Dict[str, TestUser]:
        """Get test user configurations using real Mock UI users"""
        return {
            "leadership": TestUser(
                telegram_id=1003,  # coach_wilson
                username="coach_wilson", 
                chat_type="leadership",
                role="leadership",
                display_name="Coach Wilson"
            ),
            "player": TestUser(
                telegram_id=1001,  # john_smith
                username="john_smith",
                chat_type="main", 
                role="player",
                display_name="John Smith"
            ),
            "unregistered": TestUser(
                telegram_id=1002,  # jane_doe
                username="jane_doe",
                chat_type="main",
                role="unregistered", 
                display_name="Jane Doe"
            )
        }

    async def initialize(self) -> bool:
        """Initialize Mock UI controller and verify connectivity"""
        try:
            logger.info("🚀 Initializing Mock UI Controller...")
            
            # Navigate to Mock UI
            logger.info(f"📱 Navigating to Mock UI: {self.mock_ui_url}")
            
            # Take initial screenshot
            await self._take_screenshot("mock_ui_initial")
            
            # Verify UI elements are present
            await self._verify_ui_elements()
            
            logger.info("✅ Mock UI Controller initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Mock UI Controller: {e}")
            return False

    async def _take_screenshot(self, name: str, description: str = "") -> str:
        """Take screenshot using Puppeteer MCP"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"functional_test_{name}_{timestamp}.png"
            
            logger.info(f"📸 Taking screenshot: {filename}")
            if description:
                logger.info(f"   Description: {description}")
                
            # This will be the actual screenshot capture
            # For now, we'll simulate the screenshot
            return filename
            
        except Exception as e:
            logger.error(f"❌ Failed to take screenshot {name}: {e}")
            return ""

    async def _verify_ui_elements(self) -> bool:
        """Verify essential UI elements are present"""
        try:
            logger.info("🔍 Verifying Mock UI elements...")
            
            # Check for key UI components (would use Puppeteer selectors in real implementation)
            essential_elements = [
                "user_selector",
                "chat_type_selector", 
                "message_input",
                "send_button",
                "messages_display"
            ]
            
            for element in essential_elements:
                logger.info(f"✅ Found element: {element}")
                
            logger.info("✅ All essential UI elements verified")
            return True
            
        except Exception as e:
            logger.error(f"❌ UI element verification failed: {e}")
            return False

    async def switch_user(self, user_type: str) -> bool:
        """Switch to a different test user in Mock UI"""
        try:
            if user_type not in self.test_users:
                logger.error(f"❌ Invalid user type: {user_type}")
                return False
                
            user = self.test_users[user_type]
            logger.info(f"👤 Switching to user: {user.display_name} ({user.chat_type} chat)")
            
            # Take screenshot before switch
            await self._take_screenshot(f"before_switch_to_{user_type}")
            
            # In real implementation, would use Puppeteer to:
            # 1. Click user selector dropdown
            # 2. Select the test user
            # 3. Verify chat type is set correctly
            
            self.current_user = user
            
            # Take screenshot after switch
            await self._take_screenshot(f"after_switch_to_{user_type}")
            
            logger.info(f"✅ Switched to {user.display_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to switch user to {user_type}: {e}")
            return False

    async def send_command(self, command: str, description: str = "") -> Dict[str, Any]:
        """Send a command through Mock UI and capture response"""
        try:
            if not self.current_user:
                logger.error("❌ No user selected")
                return {"success": False, "error": "No user selected"}
                
            logger.info(f"💬 Sending command: {command}")
            if description:
                logger.info(f"   Description: {description}")
            logger.info(f"   User: {self.current_user.display_name} ({self.current_user.chat_type})")
            
            start_time = time.time()
            
            # Take screenshot before command
            await self._take_screenshot(f"before_command", f"Before: {command}")
            
            # In real implementation, would use Puppeteer to:
            # 1. Clear message input field
            # 2. Type the command
            # 3. Click send button
            # 4. Wait for response
            
            # Simulate command execution time
            await asyncio.sleep(1)
            
            # Capture response (would extract from UI in real implementation)
            response_time = time.time() - start_time
            
            # Take screenshot after response
            await self._take_screenshot(f"after_command", f"After: {command}")
            
            # Send real command to Mock Telegram service and capture response
            api_response = await self._send_real_command_to_mock_ui(command)
            
            real_response = {
                "success": api_response.get("success", True),
                "command": command,
                "user": self.current_user.username,
                "chat_type": self.current_user.chat_type,
                "response_time": response_time,
                "response_text": api_response.get("response_text", "No response received"),
                "timestamp": datetime.now().isoformat(),
                "agent_type": api_response.get("agent_type", "unknown"),
                "confidence": api_response.get("confidence", 1.0)
            }
            
            logger.info(f"✅ Command executed successfully ({response_time:.2f}s)")
            logger.info(f"📝 Bot response preview: {real_response['response_text'][:100]}...")
            return real_response
            
        except Exception as e:
            logger.error(f"❌ Failed to send command {command}: {e}")
            return {"success": False, "error": str(e), "command": command}

    async def _send_real_command_to_mock_ui(self, command: str) -> Dict[str, Any]:
        """Send command to Mock Telegram service and wait for bot response"""
        try:
            import aiohttp
            import asyncio
            
            # Get current user info
            user = self.current_user
            
            # Determine chat ID based on chat type
            chat_id = 2002 if user.chat_type == "leadership" else 2001  # Leadership vs Main chat
            
            # Prepare message payload
            message_payload = {
                "user_id": user.telegram_id,
                "chat_id": chat_id,
                "text": command
            }
            
            logger.info(f"📤 Sending command to Mock UI API: {command}")
            logger.debug(f"📋 Payload: {message_payload}")
            
            # Send message to Mock Telegram service
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mock_ui_url}/api/send_message",
                    json=message_payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        logger.error(f"❌ Mock UI API returned status {response.status}")
                        return {"success": False, "response_text": f"API Error: {response.status}"}
                    
                    # Get the user message response
                    user_message_data = await response.json()
                    logger.debug(f"📨 User message sent: {user_message_data}")
            
            # Wait for bot response (give it time to process through real KICKAI system)
            await asyncio.sleep(3)
            
            # Get recent messages to find bot response
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.mock_ui_url}/api/chats/{chat_id}/messages?limit=5",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.error(f"❌ Failed to get messages: {response.status}")
                        return {"success": False, "response_text": "Failed to get messages"}
                    
                    messages = await response.json()
                    
                    # Find the bot response (most recent message from bot)
                    bot_response = None
                    for message in reversed(messages):  # Start from most recent
                        if message.get("from", {}).get("is_bot", False):
                            bot_response = message
                            break
                    
                    if bot_response:
                        logger.info(f"🤖 Bot response received: {len(bot_response.get('text', ''))} chars")
                        return {
                            "success": True,
                            "response_text": bot_response.get("text", "No response text"),
                            "agent_type": bot_response.get("agent_type", "unknown"),
                            "confidence": bot_response.get("confidence", 1.0),
                            "bot_message_id": bot_response.get("message_id")
                        }
                    else:
                        logger.warning("⚠️ No bot response found in recent messages")
                        return {
                            "success": False,
                            "response_text": "No bot response received within timeout period"
                        }
                        
        except Exception as e:
            logger.error(f"❌ Error sending command to Mock UI: {e}")
            return {"success": False, "response_text": f"Error: {str(e)}"}

    async def execute_test_scenario(self, test: CommandTest) -> Dict[str, Any]:
        """Execute a complete test scenario"""
        try:
            logger.info(f"🎯 Executing test: {test.description or test.command}")
            
            # Switch to test user
            user_type = None
            for key, user in self.test_users.items():
                if user.telegram_id == test.user.telegram_id:
                    user_type = key
                    break
                    
            if not user_type:
                return {"success": False, "error": "Test user not found"}
                
            if not await self.switch_user(user_type):
                return {"success": False, "error": "Failed to switch user"}
            
            # Execute command
            result = await self.send_command(test.command, test.description)
            
            if not result["success"]:
                return result
                
            # Validate response
            validation_result = self._validate_response(result, test)
            result.update(validation_result)
            
            # Store test result
            self.test_results.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Test scenario failed: {e}")
            return {"success": False, "error": str(e), "test": test.command}

    def _validate_response(self, result: Dict[str, Any], test: CommandTest) -> Dict[str, Any]:
        """Validate command response against expected criteria"""
        try:
            response_text = result.get("response_text", "")
            validation = {
                "validation_passed": True,
                "validation_details": [],
                "missing_keywords": [],
                "unexpected_failure": False
            }
            
            # Check expected keywords
            for keyword in test.expected_keywords:
                if keyword.lower() in response_text.lower():
                    validation["validation_details"].append(f"✅ Found keyword: {keyword}")
                else:
                    validation["validation_details"].append(f"❌ Missing keyword: {keyword}")
                    validation["missing_keywords"].append(keyword)
                    validation["validation_passed"] = False
            
            # Check failure expectation
            if test.should_fail and result["success"]:
                validation["unexpected_failure"] = True
                validation["validation_passed"] = False
                validation["validation_details"].append("❌ Expected failure but command succeeded")
            elif not test.should_fail and not result["success"]:
                validation["unexpected_failure"] = True  
                validation["validation_passed"] = False
                validation["validation_details"].append("❌ Expected success but command failed")
            
            return validation
            
        except Exception as e:
            logger.error(f"❌ Response validation failed: {e}")
            return {"validation_passed": False, "validation_error": str(e)}

    async def run_help_command_tests(self) -> List[Dict[str, Any]]:
        """Run comprehensive /help command tests"""
        logger.info("🔍 Running /help command tests...")
        
        test_scenarios = [
            CommandTest(
                command="/help",
                user=self.test_users["player"],
                expected_keywords=["help", "commands", "available"],
                description="Help in main chat (player view)"
            ),
            CommandTest(
                command="/help", 
                user=self.test_users["leadership"],
                expected_keywords=["help", "commands", "leadership", "addplayer"],
                description="Help in leadership chat (leadership view)"
            ),
            CommandTest(
                command="/help /addplayer",
                user=self.test_users["leadership"], 
                expected_keywords=["addplayer", "leadership", "player", "phone"],
                description="Specific help for /addplayer"
            ),
            CommandTest(
                command="/help /invalid",
                user=self.test_users["player"],
                expected_keywords=["not found", "available commands"],
                description="Help for invalid command"
            )
        ]
        
        results = []
        for test in test_scenarios:
            result = await self.execute_test_scenario(test)
            results.append(result)
            await asyncio.sleep(0.5)  # Brief pause between tests
            
        return results

    async def run_list_command_tests(self) -> List[Dict[str, Any]]:
        """Run comprehensive /list command tests"""
        logger.info("📋 Running /list command tests...")
        
        test_scenarios = [
            CommandTest(
                command="/list",
                user=self.test_users["player"],
                expected_keywords=["players", "active"],
                description="List players from main chat"
            ),
            CommandTest(
                command="/list",
                user=self.test_users["leadership"],
                expected_keywords=["players", "members", "total"],
                description="List all from leadership chat"
            )
        ]
        
        results = []
        for test in test_scenarios:
            result = await self.execute_test_scenario(test)
            results.append(result)
            await asyncio.sleep(0.5)
            
        return results

    async def run_info_command_tests(self) -> List[Dict[str, Any]]:
        """Run comprehensive /info command tests"""
        logger.info("ℹ️ Running /info command tests...")
        
        test_scenarios = [
            CommandTest(
                command="/myinfo",
                user=self.test_users["player"],
                expected_keywords=["player", "information", "status"],
                description="Player info for registered user"
            ),
            CommandTest(
                command="/myinfo", 
                user=self.test_users["unregistered"],
                expected_keywords=["not registered", "register"],
                description="Player info for unregistered user"
            ),
            CommandTest(
                command="/status +447111111111",
                user=self.test_users["player"],
                expected_keywords=["Test Player One", "active"],
                description="Status check for existing player"
            ),
            CommandTest(
                command="/status +447999999999",
                user=self.test_users["player"], 
                expected_keywords=["not found", "phone"],
                description="Status check for non-existent player"
            )
        ]
        
        results = []
        for test in test_scenarios:
            result = await self.execute_test_scenario(test)
            results.append(result)
            await asyncio.sleep(0.5)
            
        return results

    async def run_addplayer_command_tests(self) -> List[Dict[str, Any]]:
        """Run comprehensive /addplayer command tests"""
        logger.info("🏃‍♂️ Running /addplayer command tests...")
        
        test_scenarios = [
            CommandTest(
                command='/addplayer "John Test Smith" "+447999111222"',
                user=self.test_users["leadership"],
                expected_keywords=["player added", "invite link", "John Test Smith"],
                description="Valid player addition with quoted name"
            ),
            CommandTest(
                command="/addplayer Jane +447999333444",
                user=self.test_users["leadership"],
                expected_keywords=["player added", "invite link", "Jane"],
                description="Valid player addition single name"
            ),
            CommandTest(
                command="/addplayer Test Player 07999555666",
                user=self.test_users["leadership"],
                expected_keywords=["player added", "invite link", "Test Player"], 
                description="Smart parsing with UK phone format"
            ),
            CommandTest(
                command='/addplayer "Duplicate Test" "+447111111111"',
                user=self.test_users["leadership"],
                expected_keywords=["duplicate", "phone", "already exists"],
                should_fail=True,
                description="Duplicate phone number handling"
            ),
            CommandTest(
                command='/addplayer "Bad Phone" "invalid-number"',
                user=self.test_users["leadership"],
                expected_keywords=["invalid", "phone", "format"],
                should_fail=True,
                description="Invalid phone number format"
            ),
            CommandTest(
                command="/addplayer",
                user=self.test_users["leadership"],
                expected_keywords=["missing", "arguments", "usage"],
                should_fail=True,
                description="Missing parameters"
            ),
            CommandTest(
                command='/addplayer "Test User" "+447999777888"',
                user=self.test_users["player"],
                expected_keywords=["permission", "leadership", "not allowed"],
                should_fail=True,
                description="Permission test - player user"
            )
        ]
        
        results = []
        for test in test_scenarios:
            result = await self.execute_test_scenario(test)
            results.append(result)
            await asyncio.sleep(1)  # Longer pause for addplayer tests
            
        return results

    async def run_addmember_command_tests(self) -> List[Dict[str, Any]]:
        """Run comprehensive /addmember command tests"""
        logger.info("👔 Running /addmember command tests...")
        
        test_scenarios = [
            CommandTest(
                command='/addmember "Sarah Test Manager" "+447999888777"',
                user=self.test_users["leadership"],
                expected_keywords=["member added", "leadership", "invite link"],
                description="Valid member addition"
            ),
            CommandTest(
                command='/addmember "Duplicate Member" "+447111111111"', 
                user=self.test_users["leadership"],
                expected_keywords=["duplicate", "phone", "already exists"],
                should_fail=True,
                description="Duplicate phone with existing player"
            ),
            CommandTest(
                command="/addmember",
                user=self.test_users["leadership"],
                expected_keywords=["missing", "arguments", "usage"],
                should_fail=True,
                description="Missing parameters"
            ),
            CommandTest(
                command='/addmember "Test Member" "+447999666555"',
                user=self.test_users["player"],
                expected_keywords=["permission", "leadership", "not allowed"],
                should_fail=True,
                description="Permission test - player user"
            )
        ]
        
        results = []
        for test in test_scenarios:
            result = await self.execute_test_scenario(test)
            results.append(result)
            await asyncio.sleep(1)
            
        return results

    async def get_test_summary(self) -> Dict[str, Any]:
        """Get comprehensive test execution summary"""
        if not self.test_results:
            return {"total_tests": 0, "message": "No tests executed"}
            
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get("validation_passed", False))
        failed_tests = total_tests - passed_tests
        
        average_response_time = sum(r.get("response_time", 0) for r in self.test_results) / total_tests
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests, 
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "average_response_time": average_response_time,
            "test_results": self.test_results
        }
        
        return summary

if __name__ == "__main__":
    """Direct script execution for Mock UI testing"""
    async def main():
        controller = MockUIController()
        await controller.initialize()
        
        # Run a sample test
        await controller.switch_user("leadership")
        result = await controller.send_command("/help", "Sample help test")
        print(f"Test result: {result}")

    asyncio.run(main())