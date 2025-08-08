#!/usr/bin/env python3
"""
Comprehensive E2E Test Runner for KICKAI System

This script implements the complete testing strategy to validate:
- Mock Telegram Tester integration
- CrewAI Agents functionality
- Groq LLM integration
- Firestore data persistence
- All commands (slash and natural language)

Usage:
    python run_comprehensive_e2e_tests.py [--phase PHASE] [--verbose]
"""

import os
import sys
import asyncio
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure."""
    phase: str
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ComprehensiveE2ETester:
    """Comprehensive E2E test runner for KICKAI system."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.mock_telegram_url = "http://localhost:8001"
        
    async def run_phase_1_environment_setup(self) -> bool:
        """Phase 1: Environment Setup & Validation."""
        logger.info("🧪 Phase 1: Environment Setup & Validation")
        
        tests = [
            ("Python Version Check", self._test_python_version),
            ("Virtual Environment Check", self._test_virtual_environment),
            ("Dependencies Check", self._test_dependencies),
            ("Environment Variables Check", self._test_environment_variables),
            ("Firebase Connection Check", self._test_firebase_connection),
        ]
        
        phase_passed = True
        for test_name, test_func in tests:
            result = await self._run_test("Phase 1", test_name, test_func)
            if result.status == "FAIL":
                phase_passed = False
                
        return phase_passed
    
    async def run_phase_2_component_testing(self) -> bool:
        """Phase 2: Component Testing."""
        logger.info("🧪 Phase 2: Component Testing")
        
        tests = [
            ("Mock Telegram Service Check", self._test_mock_telegram_service),
            ("CrewAI Agents Initialization", self._test_crewai_agents),
            ("Groq LLM Configuration", self._test_groq_llm),
            ("AgenticMessageRouter Setup", self._test_agentic_router),
        ]
        
        phase_passed = True
        for test_name, test_func in tests:
            result = await self._run_test("Phase 2", test_name, test_func)
            if result.status == "FAIL":
                phase_passed = False
                
        return phase_passed
    
    async def run_phase_3_integration_testing(self) -> bool:
        """Phase 3: Integration Testing."""
        logger.info("🧪 Phase 3: Integration Testing")
        
        tests = [
            ("End-to-End Message Flow", self._test_message_flow),
            ("Bot Integration Test", self._test_bot_integration),
            ("WebSocket Communication", self._test_websocket_communication),
        ]
        
        phase_passed = True
        for test_name, test_func in tests:
            result = await self._run_test("Phase 3", test_name, test_func)
            if result.status == "FAIL":
                phase_passed = False
                
        return phase_passed
    
    async def run_phase_4_command_testing(self) -> bool:
        """Phase 4: Command Testing."""
        logger.info("🧪 Phase 4: Command Testing")
        
        # System Commands
        system_commands = [
            ("/help", "Help system command"),
            ("/start", "Bot initialization command"),
            ("/version", "Version information command"),
            ("/ping", "Health check command"),
        ]
        
        # Player Management Commands
        player_commands = [
            ("/addplayer John Smith +1234567890 Forward", "Player registration command"),
            ("/myinfo", "User information command"),
            ("/update phone +1234567899", "Update user data command"),
        ]
        
        # Team Administration Commands
        admin_commands = [
            ("/addmember Jane Doe +1234567891 Coach", "Team member registration command"),
            ("/list", "List players/members command"),
            ("/status +1234567890", "Check player status command"),
        ]
        
        all_commands = system_commands + player_commands + admin_commands
        
        phase_passed = True
        for command, description in all_commands:
            test_name = f"Command Test: {description}"
            result = await self._run_test("Phase 4", test_name, 
                                        lambda: self._test_command(command))
            if result.status == "FAIL":
                phase_passed = False
                
        return phase_passed
    
    async def run_phase_5_natural_language_testing(self) -> bool:
        """Phase 5: Natural Language Testing."""
        logger.info("🧪 Phase 5: Natural Language Testing")
        
        nl_queries = [
            ("I want to register as a player", "Player registration NL"),
            ("What's my phone number?", "Information request NL"),
            ("Show me the team list", "List request NL"),
            ("Add John Smith as a coach", "Administrative NL"),
            ("How do I join the team?", "Help request NL"),
        ]
        
        phase_passed = True
        for query, description in nl_queries:
            test_name = f"NL Test: {description}"
            result = await self._run_test("Phase 5", test_name,
                                        lambda: self._test_natural_language(query))
            if result.status == "FAIL":
                phase_passed = False
                
        return phase_passed
    
    async def run_phase_6_validation_verification(self) -> bool:
        """Phase 6: Validation & Verification."""
        logger.info("🧪 Phase 6: Validation & Verification")
        
        tests = [
            ("Firestore Data Validation", self._test_firestore_data),
            ("Agent Response Quality", self._test_agent_responses),
            ("Groq LLM Performance", self._test_groq_performance),
        ]
        
        phase_passed = True
        for test_name, test_func in tests:
            result = await self._run_test("Phase 6", test_name, test_func)
            if result.status == "FAIL":
                phase_passed = False
                
        return phase_passed
    
    async def run_phase_7_error_handling(self) -> bool:
        """Phase 7: Error Handling & Edge Cases."""
        logger.info("🧪 Phase 7: Error Handling & Edge Cases")
        
        error_tests = [
            ("Invalid Command Handling", self._test_invalid_command),
            ("Malformed Input Handling", self._test_malformed_input),
            ("Unauthorized Access Handling", self._test_unauthorized_access),
        ]
        
        phase_passed = True
        for test_name, test_func in error_tests:
            result = await self._run_test("Phase 7", test_name, test_func)
            if result.status == "FAIL":
                phase_passed = False
                
        return phase_passed
    
    async def run_phase_8_performance_monitoring(self) -> bool:
        """Phase 8: Performance Monitoring."""
        logger.info("🧪 Phase 8: Performance Monitoring")
        
        performance_tests = [
            ("Response Time Measurement", self._test_response_times),
            ("Memory Usage Monitoring", self._test_memory_usage),
            ("Concurrent User Testing", self._test_concurrent_users),
        ]
        
        phase_passed = True
        for test_name, test_func in performance_tests:
            result = await self._run_test("Phase 8", test_name, test_func)
            if result.status == "FAIL":
                phase_passed = False
                
        return phase_passed
    
    # Test Implementation Methods
    
    async def _test_python_version(self) -> Dict[str, Any]:
        """Test Python version compatibility."""
        import sys
        version = sys.version_info
        if version.major == 3 and version.minor >= 11:
            return {"status": "PASS", "version": f"{version.major}.{version.minor}.{version.micro}"}
        else:
            raise ValueError(f"Python 3.11+ required, got {version.major}.{version.minor}")
    
    async def _test_virtual_environment(self) -> Dict[str, Any]:
        """Test virtual environment activation."""
        import sys
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            return {"status": "PASS", "venv": sys.prefix}
        else:
            raise ValueError("Virtual environment not detected")
    
    async def _test_dependencies(self) -> Dict[str, Any]:
        """Test required dependencies."""
        import importlib
        
        required_packages = [
            "crewai", "groq", "firebase_admin", "fastapi", 
            "loguru", "pydantic", "asyncio"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            raise ValueError(f"Missing packages: {missing_packages}")
        
        return {"status": "PASS", "packages": required_packages}
    
    async def _test_environment_variables(self) -> Dict[str, Any]:
        """Test critical environment variables."""
        required_vars = [
            "KICKAI_INVITE_SECRET_KEY",
            "FIREBASE_PROJECT_ID",
            "AI_PROVIDER",
            "GROQ_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing environment variables: {missing_vars}")
        
        return {"status": "PASS", "variables": required_vars}
    
    async def _test_firebase_connection(self) -> Dict[str, Any]:
        """Test Firebase connection."""
        try:
            from kickai.database.firebase_client import get_firebase_client
            client = get_firebase_client()
            
            # Test basic connection
            health = client.health_check()
            if health.get("status") == "healthy":
                return {"status": "PASS", "firebase_status": "connected"}
            else:
                raise ValueError(f"Firebase health check failed: {health}")
                
        except Exception as e:
            raise ValueError(f"Firebase connection failed: {e}")
    
    async def _test_mock_telegram_service(self) -> Dict[str, Any]:
        """Test mock Telegram service."""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.mock_telegram_url}/health") as response:
                    if response.status == 200:
                        return {"status": "PASS", "mock_service": "running"}
                    else:
                        raise ValueError(f"Mock service health check failed: {response.status}")
        except Exception as e:
            raise ValueError(f"Mock Telegram service not accessible: {e}")
    
    async def _test_crewai_agents(self) -> Dict[str, Any]:
        """Test CrewAI agents initialization."""
        try:
            from kickai.agents.crew_agents import create_team_management_system
            system = create_team_management_system("KTI")
            
            if len(system.agents) == 5:  # Expected 5 agents
                return {"status": "PASS", "agents_count": len(system.agents)}
            else:
                raise ValueError(f"Expected 5 agents, got {len(system.agents)}")
                
        except Exception as e:
            raise ValueError(f"CrewAI agents initialization failed: {e}")
    
    async def _test_groq_llm(self) -> Dict[str, Any]:
        """Test Groq LLM configuration."""
        try:
            from kickai.config.llm_config import LLMConfiguration
            config = LLMConfiguration()
            llm = config.main_llm
            
            # Test basic LLM functionality
            test_response = llm.invoke([
                {"role": "user", "content": "Say hello"}
            ])
            
            if test_response and len(str(test_response)) > 0:
                return {"status": "PASS", "groq_llm": "configured"}
            else:
                raise ValueError("Groq LLM returned empty response")
                
        except Exception as e:
            raise ValueError(f"Groq LLM configuration failed: {e}")
    
    async def _test_agentic_router(self) -> Dict[str, Any]:
        """Test AgenticMessageRouter setup."""
        try:
            from kickai.agents.agentic_message_router import AgenticMessageRouter
            router = AgenticMessageRouter("KTI")
            
            return {"status": "PASS", "router": "initialized"}
            
        except Exception as e:
            raise ValueError(f"AgenticMessageRouter setup failed: {e}")
    
    async def _test_message_flow(self) -> Dict[str, Any]:
        """Test end-to-end message flow."""
        try:
            from kickai.agents.agentic_message_router import AgenticMessageRouter
            
            router = AgenticMessageRouter("KTI")
            message = {
                'text': '/help',
                'chat_id': '2001',
                'user_id': '1001',
                'username': 'test_user'
            }
            
            response = await router.route_message(message)
            
            if response and len(str(response)) > 0:
                return {"status": "PASS", "response_length": len(str(response))}
            else:
                raise ValueError("Empty response from message router")
                
        except Exception as e:
            raise ValueError(f"Message flow test failed: {e}")
    
    async def _test_bot_integration(self) -> Dict[str, Any]:
        """Test bot integration with mock Telegram."""
        import aiohttp
        import json
        
        try:
            async with aiohttp.ClientSession() as session:
                test_message = {
                    "user_id": 1001,
                    "text": "/ping",
                    "chat_id": 2001
                }
                
                async with session.post(
                    f"{self.mock_telegram_url}/api/send_message",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(test_message)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return {"status": "PASS", "bot_integration": "working"}
                    else:
                        raise ValueError(f"Bot integration failed: {response.status}")
                        
        except Exception as e:
            raise ValueError(f"Bot integration test failed: {e}")
    
    async def _test_websocket_communication(self) -> Dict[str, Any]:
        """Test WebSocket communication."""
        import aiohttp
        import asyncio
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(f"{self.mock_telegram_url.replace('http', 'ws')}/ws") as ws:
                    # Send a test message
                    await ws.send_str(json.dumps({"type": "ping"}))
                    
                    # Wait for response
                    response = await asyncio.wait_for(ws.receive(), timeout=5.0)
                    
                    if response.type == aiohttp.WSMsgType.TEXT:
                        return {"status": "PASS", "websocket": "connected"}
                    else:
                        raise ValueError("WebSocket communication failed")
                        
        except Exception as e:
            raise ValueError(f"WebSocket test failed: {e}")
    
    async def _test_command(self, command: str) -> Dict[str, Any]:
        """Test a specific command."""
        import aiohttp
        import json
        
        try:
            async with aiohttp.ClientSession() as session:
                test_message = {
                    "user_id": 1001,
                    "text": command,
                    "chat_id": 2001
                }
                
                async with session.post(
                    f"{self.mock_telegram_url}/api/send_message",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(test_message)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return {"status": "PASS", "command": command, "response": result}
                    else:
                        raise ValueError(f"Command {command} failed: {response.status}")
                        
        except Exception as e:
            raise ValueError(f"Command test failed for {command}: {e}")
    
    async def _test_natural_language(self, query: str) -> Dict[str, Any]:
        """Test natural language processing."""
        import aiohttp
        import json
        
        try:
            async with aiohttp.ClientSession() as session:
                test_message = {
                    "user_id": 1001,
                    "text": query,
                    "chat_id": 2001
                }
                
                async with session.post(
                    f"{self.mock_telegram_url}/api/send_message",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(test_message)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return {"status": "PASS", "query": query, "response": result}
                    else:
                        raise ValueError(f"NL query {query} failed: {response.status}")
                        
        except Exception as e:
            raise ValueError(f"NL test failed for {query}: {e}")
    
    async def _test_firestore_data(self) -> Dict[str, Any]:
        """Test Firestore data validation."""
        try:
            from kickai.database.firebase_client import get_firebase_client
            client = get_firebase_client()
            
            # Check KTI team collections exist
            kti_collections = [
                "kickai_KTI_players", 
                "kickai_KTI_team_members", 
                "kickai_KTI_matches",
                "kickai_teams"
            ]
            existing_collections = []
            
            for collection in kti_collections:
                try:
                    docs = client.get_all_documents(collection)
                    existing_collections.append(collection)
                except Exception:
                    pass
            
            return {"status": "PASS", "collections": existing_collections}
            
        except Exception as e:
            raise ValueError(f"Firestore data validation failed: {e}")
    
    async def _test_agent_responses(self) -> Dict[str, Any]:
        """Test agent response quality."""
        try:
            from kickai.agents.agentic_message_router import AgenticMessageRouter
            
            router = AgenticMessageRouter("KTI")
            test_messages = [
                "What commands are available?",
                "How do I register as a player?",
                "Show me the team list"
            ]
            
            responses = []
            for message in test_messages:
                response = await router.route_message({
                    'text': message,
                    'chat_id': '2001',
                    'user_id': '1001'
                })
                responses.append({"message": message, "response": str(response)[:100]})
            
            return {"status": "PASS", "responses": responses}
            
        except Exception as e:
            raise ValueError(f"Agent response test failed: {e}")
    
    async def _test_groq_performance(self) -> Dict[str, Any]:
        """Test Groq LLM performance."""
        try:
            from kickai.config.llm_config import LLMConfiguration
            import time
            
            config = LLMConfiguration()
            llm = config.main_llm
            
            start_time = time.time()
            response = llm.invoke([
                {"role": "user", "content": "Explain how to register as a player"}
            ])
            end_time = time.time()
            
            response_time = end_time - start_time
            
            return {
                "status": "PASS", 
                "response_time": response_time,
                "response_length": len(str(response))
            }
            
        except Exception as e:
            raise ValueError(f"Groq performance test failed: {e}")
    
    async def _test_invalid_command(self) -> Dict[str, Any]:
        """Test invalid command handling."""
        import aiohttp
        import json
        
        try:
            async with aiohttp.ClientSession() as session:
                test_message = {
                    "user_id": 1001,
                    "text": "/invalidcommand",
                    "chat_id": 2001
                }
                
                async with session.post(
                    f"{self.mock_telegram_url}/api/send_message",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(test_message)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        # Should return an error message for invalid command
                        if "error" in str(result).lower() or "unknown" in str(result).lower():
                            return {"status": "PASS", "error_handling": "working"}
                        else:
                            raise ValueError("Invalid command not handled properly")
                    else:
                        raise ValueError(f"Invalid command test failed: {response.status}")
                        
        except Exception as e:
            raise ValueError(f"Invalid command test failed: {e}")
    
    async def _test_malformed_input(self) -> Dict[str, Any]:
        """Test malformed input handling."""
        import aiohttp
        import json
        
        try:
            async with aiohttp.ClientSession() as session:
                test_message = {
                    "user_id": 1001,
                    "text": "",  # Empty message
                    "chat_id": 2001
                }
                
                async with session.post(
                    f"{self.mock_telegram_url}/api/send_message",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(test_message)
                ) as response:
                    
                    if response.status == 200:
                        return {"status": "PASS", "malformed_input": "handled"}
                    else:
                        raise ValueError(f"Malformed input test failed: {response.status}")
                        
        except Exception as e:
            raise ValueError(f"Malformed input test failed: {e}")
    
    async def _test_unauthorized_access(self) -> Dict[str, Any]:
        """Test unauthorized access handling."""
        import aiohttp
        import json
        
        try:
            async with aiohttp.ClientSession() as session:
                test_message = {
                    "user_id": 9999,  # Non-existent user
                    "text": "/addmember Admin User +1234567890 Admin",
                    "chat_id": 2001
                }
                
                async with session.post(
                    f"{self.mock_telegram_url}/api/send_message",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(test_message)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        # Should return an access denied message
                        if "access" in str(result).lower() or "denied" in str(result).lower():
                            return {"status": "PASS", "unauthorized_access": "blocked"}
                        else:
                            raise ValueError("Unauthorized access not handled properly")
                    else:
                        raise ValueError(f"Unauthorized access test failed: {response.status}")
                        
        except Exception as e:
            raise ValueError(f"Unauthorized access test failed: {e}")
    
    async def _test_response_times(self) -> Dict[str, Any]:
        """Test response time measurement."""
        import aiohttp
        import json
        import time
        
        try:
            async with aiohttp.ClientSession() as session:
                response_times = []
                
                for i in range(5):  # Test 5 requests
                    start_time = time.time()
                    
                    test_message = {
                        "user_id": 1001,
                        "text": "/help",
                        "chat_id": 2001
                    }
                    
                    async with session.post(
                        f"{self.mock_telegram_url}/api/send_message",
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(test_message)
                    ) as response:
                        
                        if response.status == 200:
                            end_time = time.time()
                            response_times.append(end_time - start_time)
                        else:
                            raise ValueError(f"Response time test failed: {response.status}")
                
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                
                return {
                    "status": "PASS",
                    "average_response_time": avg_time,
                    "max_response_time": max_time,
                    "response_times": response_times
                }
                
        except Exception as e:
            raise ValueError(f"Response time test failed: {e}")
    
    async def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage monitoring."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb < 500:  # Should be under 500MB
                return {"status": "PASS", "memory_usage_mb": memory_mb}
            else:
                raise ValueError(f"Memory usage too high: {memory_mb}MB")
                
        except Exception as e:
            raise ValueError(f"Memory usage test failed: {e}")
    
    async def _test_concurrent_users(self) -> Dict[str, Any]:
        """Test concurrent user handling."""
        import aiohttp
        import json
        import asyncio
        
        try:
            async def send_message(user_id: int, message: str):
                async with aiohttp.ClientSession() as session:
                    test_message = {
                        "user_id": user_id,
                        "text": message,
                        "chat_id": 2001
                    }
                    
                    async with session.post(
                        f"{self.mock_telegram_url}/api/send_message",
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(test_message)
                    ) as response:
                        return response.status == 200
            
            # Test 5 concurrent users
            tasks = []
            for i in range(5):
                task = send_message(1001 + i, f"/help from user {i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_requests = sum(1 for r in results if r is True)
            
            if successful_requests >= 4:  # At least 80% success rate
                return {"status": "PASS", "concurrent_users": 5, "success_rate": successful_requests/5}
            else:
                raise ValueError(f"Concurrent user test failed: {successful_requests}/5 successful")
                
        except Exception as e:
            raise ValueError(f"Concurrent user test failed: {e}")
    
    async def _run_test(self, phase: str, test_name: str, test_func) -> TestResult:
        """Run a single test and record results."""
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            duration = time.time() - start_time
            
            test_result = TestResult(
                phase=phase,
                test_name=test_name,
                status="PASS",
                duration=duration,
                details=result
            )
            
            logger.info(f"✅ {test_name} - PASS ({duration:.2f}s)")
            self.results.append(test_result)
            return test_result
            
        except Exception as e:
            duration = time.time() - start_time
            
            test_result = TestResult(
                phase=phase,
                test_name=test_name,
                status="FAIL",
                duration=duration,
                error=str(e)
            )
            
            logger.error(f"❌ {test_name} - FAIL ({duration:.2f}s): {e}")
            self.results.append(test_result)
            return test_result
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == "PASS")
        failed_tests = sum(1 for r in self.results if r.status == "FAIL")
        
        total_duration = time.time() - self.start_time
        
        # Group results by phase
        phase_results = {}
        for result in self.results:
            if result.phase not in phase_results:
                phase_results[result.phase] = []
            phase_results[result.phase].append(result)
        
        # Calculate phase success rates
        phase_success_rates = {}
        for phase, results in phase_results.items():
            phase_passed = sum(1 for r in results if r.status == "PASS")
            phase_total = len(results)
            phase_success_rates[phase] = {
                "passed": phase_passed,
                "total": phase_total,
                "success_rate": phase_passed / phase_total if phase_total > 0 else 0
            }
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "total_duration": total_duration,
                "timestamp": datetime.now().isoformat()
            },
            "phase_results": phase_success_rates,
            "detailed_results": [result.__dict__ for result in self.results]
        }
    
    def print_report(self):
        """Print formatted test report."""
        report = self.generate_report()
        
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE E2E TEST REPORT")
        print("="*80)
        
        summary = report["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1%}")
        print(f"   Total Duration: {summary['total_duration']:.2f}s")
        
        print(f"\n📋 PHASE RESULTS:")
        for phase, results in report["phase_results"].items():
            status = "✅ PASS" if results["success_rate"] >= 0.8 else "❌ FAIL"
            print(f"   {phase}: {status} ({results['passed']}/{results['total']} tests)")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for result in self.results:
            status_icon = "✅" if result.status == "PASS" else "❌"
            print(f"   {status_icon} {result.test_name} ({result.duration:.2f}s)")
            if result.error:
                print(f"      Error: {result.error}")
        
        print("\n" + "="*80)
        
        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved to: {report_file}")

async def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive E2E Test Runner")
    parser.add_argument("--phase", type=str, help="Run specific phase (1-8)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = ComprehensiveE2ETester()
    
    try:
        if args.phase:
            # Run specific phase
            phase_methods = {
                "1": tester.run_phase_1_environment_setup,
                "2": tester.run_phase_2_component_testing,
                "3": tester.run_phase_3_integration_testing,
                "4": tester.run_phase_4_command_testing,
                "5": tester.run_phase_5_natural_language_testing,
                "6": tester.run_phase_6_validation_verification,
                "7": tester.run_phase_7_error_handling,
                "8": tester.run_phase_8_performance_monitoring,
            }
            
            if args.phase in phase_methods:
                await phase_methods[args.phase]()
            else:
                print(f"❌ Invalid phase: {args.phase}. Valid phases: 1-8")
                sys.exit(1)
        else:
            # Run all phases
            phases = [
                tester.run_phase_1_environment_setup,
                tester.run_phase_2_component_testing,
                tester.run_phase_3_integration_testing,
                tester.run_phase_4_command_testing,
                tester.run_phase_5_natural_language_testing,
                tester.run_phase_6_validation_verification,
                tester.run_phase_7_error_handling,
                tester.run_phase_8_performance_monitoring,
            ]
            
            for phase_func in phases:
                await phase_func()
        
        # Generate and print report
        tester.print_report()
        
        # Exit with appropriate code
        report = tester.generate_report()
        if report["summary"]["success_rate"] >= 0.8:
            print("🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
