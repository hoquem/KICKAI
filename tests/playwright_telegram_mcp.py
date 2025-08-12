#!/usr/bin/env python3
"""
Playwright MCP Server for Telegram Bot Testing

This module provides a Playwright-based testing framework that interacts with
the actual Telegram Web interface to test the KICKAI bot functionality.
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
class TelegramTestUser:
    """Test user for Telegram testing"""
    phone_number: str
    name: str
    username: Optional[str] = None
    role: str = "player"


@dataclass
class TestResult:
    """Test execution result"""
    success: bool
    message: str
    screenshot_path: Optional[str] = None
    response_time: float = 0.0
    error: Optional[str] = None


class TelegramPlaywrightMCP:
    """Playwright MCP server for Telegram bot testing"""
    
    def __init__(self, headless: bool = False, slow_mo: int = 100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        self.current_user: Optional[TelegramTestUser] = None
        
    async def start_browser(self, browser_type: str = "chromium") -> bool:
        """
        Start browser and navigate to Telegram Web.
        
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
            
            # Create context with user agent
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Navigate to Telegram Web
            await self.page.goto("https://web.telegram.org/")
            
            logger.info(f"✅ Browser started successfully with {browser_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            return False
    
    async def login_to_telegram(self, phone_number: str, code: Optional[str] = None) -> bool:
        """
        Login to Telegram Web with phone number.
        
        Args:
            phone_number: Phone number for login
            code: Verification code (if provided)
            
        Returns:
            True if login successful
        """
        try:
            if not self.page:
                raise ValueError("Browser not started. Call start_browser() first.")
            
            # Wait for login form to appear
            await self.page.wait_for_selector("input[type='tel']", timeout=10000)
            
            # Enter phone number
            await self.page.fill("input[type='tel']", phone_number)
            
            # Click next button
            await self.page.click("button[type='submit']")
            
            # Wait for code input or QR code
            try:
                # Check if code input is required
                code_input = await self.page.wait_for_selector("input[type='text']", timeout=5000)
                if code_input and code:
                    await self.page.fill("input[type='text']", code)
                    await self.page.click("button[type='submit']")
                else:
                    logger.warning("⚠️ Verification code required but not provided")
                    return False
                    
            except Exception:
                # QR code login or other method
                logger.info("📱 QR code login detected or code not required")
            
            # Wait for main chat interface
            await self.page.wait_for_selector(".chat-list", timeout=30000)
            
            self.is_logged_in = True
            logger.info(f"✅ Successfully logged in with {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False
    
    async def navigate_to_chat(self, chat_name: str) -> bool:
        """
        Navigate to a specific chat by name.
        
        Args:
            chat_name: Name of the chat to navigate to
            
        Returns:
            True if navigation successful
        """
        try:
            if not self.page or not self.is_logged_in:
                raise ValueError("Not logged in. Call login_to_telegram() first.")
            
            # Search for chat
            await self.page.click(".search-input")
            await self.page.fill(".search-input", chat_name)
            
            # Wait for search results and click on the chat
            await self.page.wait_for_selector(f"text={chat_name}", timeout=10000)
            await self.page.click(f"text={chat_name}")
            
            # Wait for chat to load
            await self.page.wait_for_selector(".message-list", timeout=10000)
            
            logger.info(f"✅ Navigated to chat: {chat_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to navigate to chat {chat_name}: {e}")
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
            if not self.page or not self.is_logged_in:
                raise ValueError("Not logged in. Call login_to_telegram() first.")
            
            # Find message input
            message_input = await self.page.wait_for_selector(".input-message-input", timeout=10000)
            await message_input.fill(message)
            
            # Send message (Enter key or send button)
            await self.page.keyboard.press("Enter")
            
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
            if not self.page or not self.is_logged_in:
                raise ValueError("Not logged in. Call login_to_telegram() first.")
            
            # Wait for new message from bot
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Look for new messages from bot
                messages = await self.page.query_selector_all(".message")
                if messages:
                    # Get the latest message
                    latest_message = messages[-1]
                    message_text = await latest_message.text_content()
                    
                    # Check if it's from bot (not from current user)
                    is_from_bot = await latest_message.query_selector(".message-outgoing") is None
                    
                    if is_from_bot and message_text:
                        logger.info(f"🤖 Bot response: {message_text}")
                        return message_text
                
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
                filename = f"telegram_test_{timestamp}.png"
            
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


class TelegramBotTester:
    """High-level tester for Telegram bot functionality"""
    
    def __init__(self, phone_number: str, headless: bool = False):
        self.phone_number = phone_number
        self.mcp = TelegramPlaywrightMCP(headless=headless)
        self.test_results: List[TestResult] = []
    
    async def setup(self) -> bool:
        """Setup browser and login to Telegram."""
        success = await self.mcp.start_browser()
        if success:
            success = await self.mcp.login_to_telegram(self.phone_number)
        return success
    
    async def test_player_registration(self, chat_name: str = "KickAI Testing") -> TestResult:
        """Test player registration flow."""
        try:
            # Navigate to chat
            await self.mcp.navigate_to_chat(chat_name)
            
            # Test /addplayer command
            result = await self.mcp.test_bot_command(
                "/addplayer John Smith +447123456789 Forward",
                expected_response="✅ Player added successfully"
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            result = TestResult(success=False, message=str(e), error=str(e))
            self.test_results.append(result)
            return result
    
    async def test_help_command(self, chat_name: str = "KickAI Testing") -> TestResult:
        """Test help command."""
        try:
            await self.mcp.navigate_to_chat(chat_name)
            
            result = await self.mcp.test_bot_command(
                "/help",
                expected_response="Available commands"
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            result = TestResult(success=False, message=str(e), error=str(e))
            self.test_results.append(result)
            return result
    
    async def test_status_command(self, chat_name: str = "KickAI Testing") -> TestResult:
        """Test status command."""
        try:
            await self.mcp.navigate_to_chat(chat_name)
            
            result = await self.mcp.test_bot_command(
                "/status +447123456789",
                expected_response="Player status"
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            result = TestResult(success=False, message=str(e), error=str(e))
            self.test_results.append(result)
            return result
    
    async def run_all_tests(self, chat_name: str = "KickAI Testing") -> Dict[str, Any]:
        """Run all available tests."""
        logger.info("🚀 Starting Telegram bot tests...")
        
        if not await self.setup():
            return {"success": False, "error": "Failed to setup browser/login"}
        
        try:
            # Run tests
            await self.test_help_command(chat_name)
            await self.test_player_registration(chat_name)
            await self.test_status_command(chat_name)
            
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
    """Example usage of the Playwright MCP server."""
    tester = TelegramBotTester(
        phone_number="+447123456789",  # Replace with your phone number
        headless=False  # Set to True for headless mode
    )
    
    results = await tester.run_all_tests("KickAI Testing")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
