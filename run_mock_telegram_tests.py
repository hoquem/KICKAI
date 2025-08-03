#!/usr/bin/env python3
"""
Mock Telegram Bot Service Test Runner

This script demonstrates how to use the MockTelegramBotService for isolated testing.
It runs comprehensive tests and provides a detailed report of the mock bot functionality.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Add src to Python path
sys.path.insert(0, 'src')

from kickai.features.communication.infrastructure.mock_telegram_bot_service import (
    MockTelegramBotService,
    MockAgenticMessageRouter
)
from kickai.core.enums import ChatType


class MockTelegramTestRunner:
    """Test runner for MockTelegramBotService."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run a comprehensive test of the MockTelegramBotService."""
        print("🚀 Starting MockTelegramBotService Comprehensive Test")
        print("=" * 60)
        
        # Initialize mock bot service
        bot_service = MockTelegramBotService(
            token="mock-token-123",
            team_id="test-team",
            main_chat_id="-1001234567890",
            leadership_chat_id="-1001234567891"
        )
        
        test_results = {
            "initialization": await self._test_initialization(bot_service),
            "polling": await self._test_polling(bot_service),
            "message_sending": await self._test_message_sending(bot_service),
            "command_handling": await self._test_command_handling(bot_service),
            "natural_language": await self._test_natural_language(bot_service),
            "contact_sharing": await self._test_contact_sharing(bot_service),
            "error_handling": await self._test_error_handling(bot_service),
            "integration": await self._test_integration(bot_service)
        }
        
        # Cleanup
        if bot_service.is_running():
            await bot_service.stop()
        
        return test_results
    
    async def _test_initialization(self, bot_service: MockTelegramBotService) -> Dict[str, Any]:
        """Test bot service initialization."""
        print("📋 Testing Initialization...")
        
        try:
            assert bot_service.token == "mock-token-123"
            assert bot_service.team_id == "test-team"
            assert bot_service.main_chat_id == "-1001234567890"
            assert bot_service.leadership_chat_id == "-1001234567891"
            assert not bot_service.is_running()
            assert bot_service.get_error_count() == 0
            
            return {"success": True, "message": "Initialization successful"}
        except Exception as e:
            return {"success": False, "message": f"Initialization failed: {str(e)}"}
    
    async def _test_polling(self, bot_service: MockTelegramBotService) -> Dict[str, Any]:
        """Test polling functionality."""
        print("🔄 Testing Polling...")
        
        try:
            # Test start polling
            await bot_service.start_polling()
            assert bot_service.is_running()
            
            # Test stop polling
            await bot_service.stop()
            assert not bot_service.is_running()
            
            return {"success": True, "message": "Polling functionality working"}
        except Exception as e:
            return {"success": False, "message": f"Polling failed: {str(e)}"}
    
    async def _test_message_sending(self, bot_service: MockTelegramBotService) -> Dict[str, Any]:
        """Test message sending functionality."""
        print("📤 Testing Message Sending...")
        
        try:
            await bot_service.start_polling()
            
            # Test regular message sending
            await bot_service.send_message("-1001234567890", "Hello, world!")
            sent_messages = bot_service.get_sent_messages()
            assert len(sent_messages) == 1
            assert sent_messages[0]['text'] == "Hello, world!"
            
            # Test contact share button
            await bot_service.send_contact_share_button("-1001234567890", "Share contact")
            sent_messages = bot_service.get_sent_messages()
            assert len(sent_messages) == 2
            assert sent_messages[1]['type'] == 'contact_share_button'
            
            await bot_service.stop()
            return {"success": True, "message": "Message sending working", "messages_sent": len(sent_messages)}
        except Exception as e:
            return {"success": False, "message": f"Message sending failed: {str(e)}"}
    
    async def _test_command_handling(self, bot_service: MockTelegramBotService) -> Dict[str, Any]:
        """Test command handling."""
        print("⚡ Testing Command Handling...")
        
        try:
            await bot_service.start_polling()
            
            commands = ["/start", "/help", "/myinfo", "/list"]
            responses = []
            
            for command in commands:
                await bot_service.simulate_message(
                    text=command,
                    chat_id="-1001234567890",
                    user_id="123456789",
                    username="testuser"
                )
                responses.extend(bot_service.get_agentic_responses())
            
            # Verify all commands were processed
            received_messages = bot_service.get_received_messages()
            assert len(received_messages) == len(commands)
            
            # Verify all responses are successful
            for response in responses:
                assert response.success
            
            await bot_service.stop()
            return {
                "success": True, 
                "message": "Command handling working", 
                "commands_tested": len(commands),
                "responses_generated": len(responses)
            }
        except Exception as e:
            return {"success": False, "message": f"Command handling failed: {str(e)}"}
    
    async def _test_natural_language(self, bot_service: MockTelegramBotService) -> Dict[str, Any]:
        """Test natural language processing."""
        print("💬 Testing Natural Language...")
        
        try:
            await bot_service.start_polling()
            
            messages = ["hello", "what's my phone number", "how are you"]
            responses = []
            
            for message in messages:
                await bot_service.simulate_message(
                    text=message,
                    chat_id="-1001234567890",
                    user_id="123456789",
                    username="testuser"
                )
                responses.extend(bot_service.get_agentic_responses())
            
            # Verify all messages were processed
            received_messages = bot_service.get_received_messages()
            responses = bot_service.get_agentic_responses()
            
            # Basic validation - ensure we have some responses
            if len(responses) > 0:
                await bot_service.stop()
                return {
                    "success": True, 
                    "message": "Natural language processing working", 
                    "messages_tested": len(messages),
                    "responses_generated": len(responses)
                }
            else:
                await bot_service.stop()
                return {
                    "success": False, 
                    "message": "No responses generated for natural language messages",
                    "messages_tested": len(messages),
                    "responses_generated": len(responses)
                }
        except Exception as e:
            return {"success": False, "message": f"Natural language failed: {str(e)}", "exception": str(e)}
    
    async def _test_contact_sharing(self, bot_service: MockTelegramBotService) -> Dict[str, Any]:
        """Test contact sharing functionality."""
        print("📱 Testing Contact Sharing...")
        
        try:
            await bot_service.start_polling()
            
            # Test contact sharing
            await bot_service.simulate_contact_share(
                phone="+1234567890",
                chat_id="-1001234567890",
                user_id="123456789",
                username="testuser"
            )
            
            responses = bot_service.get_agentic_responses()
            
            # Basic validation - ensure we have a response and it's successful
            if len(responses) > 0 and responses[0].success:
                await bot_service.stop()
                return {"success": True, "message": "Contact sharing working", "responses_generated": len(responses)}
            else:
                await bot_service.stop()
                return {"success": False, "message": "Contact sharing failed - no successful response", "responses_generated": len(responses)}
        except Exception as e:
            return {"success": False, "message": f"Contact sharing failed: {str(e)}", "exception": str(e)}
    
    async def _test_error_handling(self, bot_service: MockTelegramBotService) -> Dict[str, Any]:
        """Test error handling."""
        print("❌ Testing Error Handling...")
        
        try:
            await bot_service.start_polling()
            
            # Simulate an error
            from unittest.mock import patch
            with patch.object(bot_service.agentic_router, 'route_message', side_effect=Exception("Test error")):
                await bot_service.simulate_message(
                    text="error test",
                    chat_id="-1001234567890",
                    user_id="123456789"
                )
            
            # Verify error was handled
            assert bot_service.get_error_count() > 0
            assert bot_service.is_running()  # Should still be running
            
            await bot_service.stop()
            return {"success": True, "message": "Error handling working"}
        except Exception as e:
            return {"success": False, "message": f"Error handling failed: {str(e)}"}
    
    async def _test_integration(self, bot_service: MockTelegramBotService) -> Dict[str, Any]:
        """Test integration scenarios."""
        print("🔗 Testing Integration...")
        
        try:
            await bot_service.start_polling()
            
            # Test complete user flow
            user_flow = [
                ("/start", "Welcome"),
                ("hello", "Hello"),
                ("/help", "Available commands"),
                ("what's my phone number", "phone number"),
                ("/myinfo", "Your Information")
            ]
            
            for message, expected_content in user_flow:
                await bot_service.simulate_message(
                    text=message,
                    chat_id="-1001234567890",
                    user_id="123456789",
                    username="testuser"
                )
            
            # Verify complete flow
            received_messages = bot_service.get_received_messages()
            responses = bot_service.get_agentic_responses()
            
            # Basic validation - ensure we have responses for all steps
            if len(responses) >= len(user_flow):
                await bot_service.stop()
                return {
                    "success": True, 
                    "message": "Integration test successful", 
                    "flow_steps": len(user_flow),
                    "responses_generated": len(responses)
                }
            else:
                await bot_service.stop()
                return {
                    "success": False, 
                    "message": f"Integration failed - expected {len(user_flow)} responses, got {len(responses)}",
                    "flow_steps": len(user_flow),
                    "responses_generated": len(responses)
                }
        except Exception as e:
            return {"success": False, "message": f"Integration failed: {str(e)}", "exception": str(e)}
    
    def generate_report(self, test_results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report."""
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get('success', False))
        failed_tests = total_tests - passed_tests
        
        report = f"""
🧪 MockTelegramBotService Test Report
{'=' * 60}

📊 Summary:
• Total Tests: {total_tests}
• Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)
• Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)
• Duration: {time.time() - self.start_time:.2f}s

📋 Test Results:
"""
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            report += f"• {test_name.title()}: {status}\n"
            report += f"  - {result.get('message', 'No message')}\n"
            
            # Add additional details if available
            for key, value in result.items():
                if key not in ['success', 'message']:
                    report += f"  - {key}: {value}\n"
        
        if failed_tests > 0:
            report += "\n❌ Failed Tests:\n"
            for test_name, result in test_results.items():
                if not result.get('success', False):
                    report += f"• {test_name}: {result.get('message', 'Unknown error')}\n"
        
        return report


async def main():
    """Main test runner function."""
    print("🚀 MockTelegramBotService Test Runner")
    print("=" * 60)
    
    runner = MockTelegramTestRunner()
    
    try:
        # Run comprehensive test
        test_results = await runner.run_comprehensive_test()
        
        # Generate and display report
        report = runner.generate_report(test_results)
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mock_telegram_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_results": test_results,
                "summary": {
                    "total_tests": len(test_results),
                    "passed_tests": sum(1 for r in test_results.values() if r.get('success', False)),
                    "failed_tests": sum(1 for r in test_results.values() if not r.get('success', False)),
                    "duration": time.time() - runner.start_time
                }
            }, f, indent=2)
        
        print(f"📄 Test report saved to: {filename}")
        
        # Return exit code based on test results
        failed_tests = sum(1 for r in test_results.values() if not r.get('success', False))
        if failed_tests > 0:
            print(f"❌ {failed_tests} tests failed")
            return 1
        else:
            print("✅ All tests passed!")
            return 0
            
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 