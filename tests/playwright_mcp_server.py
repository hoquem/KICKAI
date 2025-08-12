#!/usr/bin/env python3
"""
Playwright MCP Server for Telegram Bot Testing

This module provides an MCP (Model Context Protocol) server that can be used
to control Playwright for testing the KICKAI Telegram bot.
"""

import asyncio
import json
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from loguru import logger


@dataclass
class MCPRequest:
    """MCP request structure"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str = ""
    params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}


@dataclass
class MCPResponse:
    """MCP response structure"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class PlaywrightMCPServer:
    """MCP server for Playwright Telegram bot testing"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        self.current_chat: Optional[str] = None
        
    async def handle_request(self, request_data: str) -> str:
        """
        Handle incoming MCP request.
        
        Args:
            request_data: JSON string containing the request
            
        Returns:
            JSON string containing the response
        """
        try:
            request = MCPRequest(**json.loads(request_data))
            
            # Route to appropriate method
            if request.method == "start_browser":
                result = await self.start_browser(**request.params)
            elif request.method == "login_telegram":
                result = await self.login_telegram(**request.params)
            elif request.method == "navigate_chat":
                result = await self.navigate_chat(**request.params)
            elif request.method == "send_message":
                result = await self.send_message(**request.params)
            elif request.method == "wait_bot_response":
                result = await self.wait_bot_response(**request.params)
            elif request.method == "test_command":
                result = await self.test_command(**request.params)
            elif request.method == "take_screenshot":
                result = await self.take_screenshot(**request.params)
            elif request.method == "close_browser":
                result = await self.close_browser(**request.params)
            else:
                return json.dumps(MCPResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {request.method}"}
                ).__dict__)
            
            return json.dumps(MCPResponse(
                id=request.id,
                result=result
            ).__dict__)
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return json.dumps(MCPResponse(
                id=request.id if 'request' in locals() else None,
                error={"code": -32603, "message": str(e)}
            ).__dict__)
    
    async def start_browser(self, browser_type: str = "chromium", headless: bool = False) -> Dict[str, Any]:
        """Start browser and navigate to Telegram Web."""
        try:
            self.playwright = await async_playwright().start()
            
            if browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(headless=headless)
            elif browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(headless=headless)
            elif browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(headless=headless)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            await self.page.goto("https://web.telegram.org/")
            
            return {"success": True, "message": f"Browser started with {browser_type}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def login_telegram(self, phone_number: str, code: Optional[str] = None) -> Dict[str, Any]:
        """Login to Telegram Web."""
        try:
            if not self.page:
                raise ValueError("Browser not started")
            
            # Wait for login form
            await self.page.wait_for_selector("input[type='tel']", timeout=10000)
            await self.page.fill("input[type='tel']", phone_number)
            await self.page.click("button[type='submit']")
            
            # Handle verification code if needed
            if code:
                try:
                    code_input = await self.page.wait_for_selector("input[type='text']", timeout=5000)
                    await self.page.fill("input[type='text']", code)
                    await self.page.click("button[type='submit']")
                except:
                    pass
            
            # Wait for main interface
            await self.page.wait_for_selector(".chat-list", timeout=30000)
            self.is_logged_in = True
            
            return {"success": True, "message": "Logged in successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def navigate_chat(self, chat_name: str) -> Dict[str, Any]:
        """Navigate to a specific chat."""
        try:
            if not self.page or not self.is_logged_in:
                raise ValueError("Not logged in")
            
            # Search for chat
            await self.page.click(".search-input")
            await self.page.fill(".search-input", chat_name)
            await self.page.wait_for_selector(f"text={chat_name}", timeout=10000)
            await self.page.click(f"text={chat_name}")
            await self.page.wait_for_selector(".message-list", timeout=10000)
            
            self.current_chat = chat_name
            return {"success": True, "message": f"Navigated to {chat_name}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_message(self, message: str) -> Dict[str, Any]:
        """Send a message in the current chat."""
        try:
            if not self.page or not self.is_logged_in:
                raise ValueError("Not logged in")
            
            message_input = await self.page.wait_for_selector(".input-message-input", timeout=10000)
            await message_input.fill(message)
            await self.page.keyboard.press("Enter")
            await self.page.wait_for_selector(f"text={message}", timeout=10000)
            
            return {"success": True, "message": "Message sent"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def wait_bot_response(self, timeout: int = 30) -> Dict[str, Any]:
        """Wait for bot response."""
        try:
            if not self.page or not self.is_logged_in:
                raise ValueError("Not logged in")
            
            import time
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                messages = await self.page.query_selector_all(".message")
                if messages:
                    latest_message = messages[-1]
                    message_text = await latest_message.text_content()
                    is_from_bot = await latest_message.query_selector(".message-outgoing") is None
                    
                    if is_from_bot and message_text:
                        return {"success": True, "response": message_text}
                
                await asyncio.sleep(1)
            
            return {"success": False, "error": "No response received"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_command(self, command: str, expected_response: str = None, timeout: int = 30) -> Dict[str, Any]:
        """Test a bot command."""
        try:
            # Send command
            send_result = await self.send_message(command)
            if not send_result["success"]:
                return send_result
            
            # Wait for response
            response_result = await self.wait_bot_response(timeout)
            if not response_result["success"]:
                return response_result
            
            response_text = response_result["response"]
            
            # Check expected response
            if expected_response and expected_response not in response_text:
                return {
                    "success": False,
                    "error": f"Response mismatch. Expected: {expected_response}, Got: {response_text}"
                }
            
            return {
                "success": True,
                "command": command,
                "response": response_text,
                "expected_match": expected_response in response_text if expected_response else True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """Take a screenshot."""
        try:
            if not self.page:
                raise ValueError("Browser not started")
            
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"telegram_test_{timestamp}.png"
            
            import os
            os.makedirs("tests/screenshots", exist_ok=True)
            screenshot_path = f"tests/screenshots/{filename}"
            
            await self.page.screenshot(path=screenshot_path)
            return {"success": True, "screenshot_path": screenshot_path}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close_browser(self) -> Dict[str, Any]:
        """Close browser and cleanup."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            return {"success": True, "message": "Browser closed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


async def run_mcp_server():
    """Run the MCP server."""
    server = PlaywrightMCPServer()
    
    # Read from stdin, write to stdout
    while True:
        try:
            # Read request from stdin
            request_line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not request_line:
                break
            
            request_line = request_line.strip()
            if not request_line:
                continue
            
            # Handle request
            response = await server.handle_request(request_line)
            
            # Write response to stdout
            await asyncio.get_event_loop().run_in_executor(None, lambda: sys.stdout.write(response + "\n"))
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Server error: {e}")
            break
    
    # Cleanup
    await server.close_browser()


if __name__ == "__main__":
    asyncio.run(run_mcp_server())


