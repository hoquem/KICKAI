#!/usr/bin/env python3
"""
Playwright MCP Server for Mock Telegram Bot Testing

This module provides a Playwright-based testing framework that interacts with
the mock Telegram tester UI to test the KICKAI bot functionality.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from loguru import logger


@dataclass
class MockTelegramTestUser:
    """Test user for mock Telegram testing"""
    user_id: int
    username: str
    first_name: str
    last_name: str
    role: str = "player"


@dataclass
class TestResult:
    """Test execution result"""
    success: bool
    message: str
    screenshot_path: Optional[str] = None
    response_time: float = 0.0
    error: Optional[str] = None


class MockTelegramPlaywrightMCP:
    """Playwright MCP server for mock Telegram bot testing"""
    
    def __init__(self, headless: bool = False, slow_mo: int = 100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_connected = False
        self.current_chat: Optional[str] = None
        
    async def start_browser(self, browser_type: str = "chromium") -> bool:
        """
        Start browser and navigate to mock Telegram tester.
        
        Args:
            browser_type: "chromium", "firefox", or "webkit"
            
        Returns:
            True if browser started successfully
        """
        try:
            self.playwright = await async_playwright().start()
            
            if browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo
                )
            elif browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo
                )
            elif browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo
                )
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            # Create context
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            # Navigate to mock Telegram tester
            await self.page.goto("http://localhost:8001")
            
            logger.info(f"✅ Browser started successfully with {browser_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            return False
    
    async def connect_to_mock_telegram(self) -> bool:
        """
        Connect to the mock Telegram tester interface.
        
        Returns:
            True if connection successful
        """
        try:
            if not self.page:
                raise ValueError("Browser not started. Call start_browser() first.")
            
            # Wait for the mock Telegram interface to load
            await self.page.wait_for_selector("#chatMessages", timeout=10000)
            
            # Wait for the page to be fully loaded
            await self.page.wait_for_load_state("networkidle")
            
            self.is_connected = True
            logger.info("✅ Connected to mock Telegram tester")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to mock Telegram: {e}")
            return False
    
    async def select_chat(self, chat_name: str) -> bool:
        """
        Select a chat in the mock Telegram interface.
        
        Args:
            chat_name: Name of the chat to select (e.g., "KickAI Testing")
            
        Returns:
            True if chat selection successful
        """
        try:
            if not self.page or not self.is_connected:
                raise ValueError("Not connected. Call connect_to_mock_telegram() first.")
            
            # Look for chat selector dropdown
            chat_selector = await self.page.wait_for_selector("#chatSelect", timeout=10000)
            
            # Select the chat
            await chat_selector.select_option(label=chat_name)
            
            # Wait for chat messages to load
            await self.page.wait_for_selector("#chatMessages", timeout=10000)
            
            self.current_chat = chat_name
            logger.info(f"✅ Selected chat: {chat_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to select chat {chat_name}: {e}")
            return False
    
    async def send_message(self, message: str) -> bool:
        """
        Send a message in the current chat.
        
        Args:
            message: Message to send
            
        Returns:
            True if message sent successfully
        """
        try:
            if not self.page or not self.is_connected:
                raise ValueError("Not connected. Call connect_to_mock_telegram() first.")
            
            # Find message input
            message_input = await self.page.wait_for_selector("#messageInput", timeout=10000)
            await message_input.fill(message)
            
            # Send message using the Send button
            send_button = await self.page.wait_for_selector("button[onclick='sendMessage()']", timeout=10000)
            await send_button.click()
            
            # Wait for message to appear in chat
            await self.page.wait_for_selector(f"text={message}", timeout=10000)
            
            logger.info(f"✅ Message sent: {message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return False
    
    async def wait_for_bot_response(self, timeout: int = 30) -> Optional[str]:
        """
        Wait for bot response in the current chat.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Bot response text or None if timeout
        """
        try:
            if not self.page or not self.is_connected:
                raise ValueError("Not connected. Call connect_to_mock_telegram() first.")
            
            # Wait for new message from bot
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Look for new messages from bot
                messages = await self.page.query_selector_all(".message.bot")
                if messages:
                    # Get the latest message
                    latest_message = messages[-1]
                    message_text = await latest_message.text_content()
                    
                    if message_text and message_text.strip():
                        logger.info(f"🤖 Bot response: {message_text}")
                        return message_text.strip()
                
                await asyncio.sleep(1)
            
            logger.warning(f"⚠️ No bot response received within {timeout} seconds")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error waiting for bot response: {e}")
            return None
    
    async def take_screenshot(self, filename: str = None) -> str:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Optional filename for screenshot
            
        Returns:
            Path to screenshot file
        """
        try:
            if not self.page:
                raise ValueError("Browser not started. Call start_browser() first.")
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"mock_telegram_test_{timestamp}.png"
            
            screenshot_path = f"tests/screenshots/{filename}"
            
            # Create screenshots directory if it doesn't exist
            import os
            os.makedirs("tests/screenshots", exist_ok=True)
            
            await self.page.screenshot(path=screenshot_path)
            logger.info(f"📸 Screenshot saved: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            logger.error(f"❌ Failed to take screenshot: {e}")
            return ""
    
    async def test_bot_command(self, command: str, expected_response: str = None, timeout: int = 30) -> TestResult:
        """
        Test a bot command and verify response.
        
        Args:
            command: Command to send to bot
            expected_response: Expected response text (optional)
            timeout: Timeout for bot response
            
        Returns:
            TestResult with success status and details
        """
        start_time = time.time()
        
        try:
            # Send command
            success = await self.send_message(command)
            if not success:
                return TestResult(
                    success=False,
                    message="Failed to send command",
                    error="Send message failed"
                )
            
            # Wait for bot response
            response = await self.wait_for_bot_response(timeout)
            
            # Take screenshot
            screenshot_path = await self.take_screenshot(f"test_{command.replace('/', '_')}_{int(time.time())}.png")
            
            response_time = time.time() - start_time
            
            if response:
                # Check if response matches expected
                if expected_response and expected_response not in response:
                    return TestResult(
                        success=False,
                        message=f"Bot response doesn't match expected: {response}",
                        screenshot_path=screenshot_path,
                        response_time=response_time,
                        error="Response mismatch"
                    )
                
                return TestResult(
                    success=True,
                    message=f"Bot responded: {response}",
                    screenshot_path=screenshot_path,
                    response_time=response_time
                )
            else:
                return TestResult(
                    success=False,
                    message="No bot response received",
                    screenshot_path=screenshot_path,
                    response_time=response_time,
                    error="No response"
                )
                
        except Exception as e:
            return TestResult(
                success=False,
                message=f"Test failed: {e}",
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def close(self):
        """Close browser and cleanup resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            logger.info("✅ Browser closed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error closing browser: {e}")


class MockTelegramBotTester:
    """High-level tester for mock Telegram bot functionality"""
    
    def __init__(self, headless: bool = False):
        self.mcp = MockTelegramPlaywrightMCP(headless=headless)
        self.test_results: List[TestResult] = []
    
    async def setup(self) -> bool:
        """Setup browser and connect to mock Telegram."""
        success = await self.mcp.start_browser()
        if success:
            success = await self.mcp.connect_to_mock_telegram()
        return success
    
    async def test_help_command(self, chat_name: str = "KickAI Testing") -> TestResult:
        """Test the /help command."""
        try:
            # Select chat
            await self.mcp.select_chat(chat_name)
            
            # Test /help command
            result = await self.mcp.test_bot_command(
                "/help",
                expected_response="Available commands",
                timeout=30
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            result = TestResult(success=False, message=str(e), error=str(e))
            self.test_results.append(result)
            return result
    
    async def test_myinfo_command(self, chat_name: str = "KickAI Testing") -> TestResult:
        """Test the /myinfo command."""
        try:
            await self.mcp.select_chat(chat_name)
            
            result = await self.mcp.test_bot_command(
                "/myinfo",
                expected_response="Your Information",
                timeout=30
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            result = TestResult(success=False, message=str(e), error=str(e))
            self.test_results.append(result)
            return result
    
    async def run_all_tests(self, chat_name: str = "KickAI Testing") -> Dict[str, Any]:
        """Run all available tests."""
        logger.info("🚀 Starting mock Telegram bot tests...")
        
        if not await self.setup():
            return {"success": False, "error": "Failed to setup browser/connection"}
        
        try:
            # Run tests
            await self.test_help_command(chat_name)
            await self.test_myinfo_command(chat_name)
            
            # Calculate results
            total_tests = len(self.test_results)
            passed_tests = sum(1 for r in self.test_results if r.success)
            failed_tests = total_tests - passed_tests
            
            return {
                "success": True,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "results": [{"success": r.success, "message": r.message, "error": r.error} for r in self.test_results]
            }
            
        finally:
            await self.mcp.close()


# Example usage
async def main():
    """Example usage of the mock Telegram Playwright MCP server."""
    tester = MockTelegramBotTester(headless=False)
    
    results = await tester.run_all_tests("KickAI Testing")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
