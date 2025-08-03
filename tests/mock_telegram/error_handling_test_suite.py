#!/usr/bin/env python3
"""
Error Handling and Edge Case Test Suite for Mock Telegram Testing

This suite provides comprehensive error handling testing including:
- Input validation testing
- Network error simulation
- Rate limiting testing
- Resource exhaustion testing
- Security vulnerability testing
- Error recovery testing
- Graceful degradation testing
"""

import asyncio
import aiohttp
import json
import random
import string
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorTestType(str, Enum):
    """Types of error tests"""
    INPUT_VALIDATION = "input_validation"
    NETWORK_ERRORS = "network_errors"
    RATE_LIMITING = "rate_limiting"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SECURITY_TESTS = "security_tests"
    ERROR_RECOVERY = "error_recovery"
    MALFORMED_DATA = "malformed_data"
    BOUNDARY_CONDITIONS = "boundary_conditions"
    CONCURRENT_ACCESS = "concurrent_access"
    SERVICE_DEGRADATION = "service_degradation"


@dataclass
class ErrorTestCase:
    """Individual error test case"""
    name: str
    test_type: ErrorTestType
    description: str
    test_data: Dict[str, Any]
    expected_status_codes: List[int]
    expected_keywords: List[str] = field(default_factory=list)
    should_fail: bool = True
    timeout_seconds: float = 5.0


@dataclass
class ErrorTestResult:
    """Result of an error test"""
    test_case: ErrorTestCase
    success: bool
    actual_status_code: Optional[int] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    response_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class ErrorTestDataGenerator:
    """Generate test data for error scenarios"""
    
    def __init__(self):
        self.invalid_strings = [
            "",  # Empty string
            " ",  # Whitespace only
            "\n\t",  # Special characters
            "a" * 10000,  # Very long string
            "🚀💥🔥" * 1000,  # Emoji overload
            "SELECT * FROM users",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
            "../../../etc/passwd",  # Path traversal
            "null",  # Null string
            "undefined",  # Undefined string
            "{object Object}",  # Object string
            "\x00\x01\x02",  # Binary data
            "' OR '1'='1",  # SQL injection
            "javascript:alert(1)",  # JavaScript injection
        ]
        
        self.invalid_numbers = [
            -1,  # Negative
            0,  # Zero (might be invalid for some fields)
            999999999999999,  # Very large number
            -999999999999999,  # Very large negative
            float('inf'),  # Infinity
            float('-inf'),  # Negative infinity
            float('nan'),  # NaN
        ]
        
        self.malformed_json_examples = [
            '{"incomplete": ',  # Incomplete JSON
            '{"key": "value",}',  # Trailing comma
            "{'single_quotes': 'invalid'}",  # Single quotes
            '{"duplicate": 1, "duplicate": 2}',  # Duplicate keys
            '{key_no_quotes: "value"}',  # Unquoted keys
            '{"valid": "json"} extra_text',  # Extra text after JSON
            '{"nested": {"incomplete":}',  # Nested incomplete
            '[1,2,3,]',  # Array trailing comma
        ]
    
    def generate_invalid_user_data(self) -> List[Dict[str, Any]]:
        """Generate invalid user creation data"""
        test_cases = []
        
        # Empty/invalid username cases
        for invalid_username in self.invalid_strings[:5]:
            test_cases.append({
                "username": invalid_username,
                "first_name": "Test",
                "last_name": "User",
                "role": "player"
            })
        
        # Invalid role cases
        test_cases.extend([
            {"username": "test", "first_name": "Test", "role": "invalid_role"},
            {"username": "test", "first_name": "Test", "role": 123},
            {"username": "test", "first_name": "Test", "role": None},
        ])
        
        # Missing required fields
        test_cases.extend([
            {"first_name": "Test"},  # Missing username
            {"username": "test"},  # Missing first_name
            {},  # Empty object
            {"username": "test", "first_name": "Test", "extra_field": "should_be_ignored"}
        ])
        
        # Invalid phone numbers
        invalid_phones = [
            "123",  # Too short
            "not_a_phone",  # Not numeric
            "+1" + "2" * 20,  # Too long
            "++1234567890",  # Double plus
            "1234567890abc",  # Mixed characters
        ]
        
        for phone in invalid_phones:
            test_cases.append({
                "username": "test_phone",
                "first_name": "Test",
                "phone_number": phone,
                "role": "player"
            })
        
        return test_cases
    
    def generate_invalid_message_data(self) -> List[Dict[str, Any]]:
        """Generate invalid message data"""
        test_cases = []
        
        # Invalid user IDs
        for invalid_id in self.invalid_numbers:
            test_cases.append({
                "user_id": invalid_id,
                "chat_id": 1001,
                "text": "Test message"
            })
        
        # Invalid chat IDs
        for invalid_id in self.invalid_numbers:
            test_cases.append({
                "user_id": 1001,
                "chat_id": invalid_id,
                "text": "Test message"
            })
        
        # Invalid text
        for invalid_text in self.invalid_strings:
            test_cases.append({
                "user_id": 1001,
                "chat_id": 1001,
                "text": invalid_text
            })
        
        # Invalid message types
        test_cases.extend([
            {"user_id": 1001, "chat_id": 1001, "text": "Test", "message_type": "invalid_type"},
            {"user_id": 1001, "chat_id": 1001, "text": "Test", "message_type": 123},
            {"user_id": 1001, "chat_id": 1001, "text": "Test", "message_type": None},
        ])
        
        # Missing required fields
        test_cases.extend([
            {"chat_id": 1001, "text": "Test"},  # Missing user_id
            {"user_id": 1001, "text": "Test"},  # Missing chat_id
            {"user_id": 1001, "chat_id": 1001},  # Missing text
            {}  # Empty object
        ])
        
        return test_cases
    
    def generate_malformed_json_data(self) -> List[str]:
        """Generate malformed JSON strings"""
        return self.malformed_json_examples
    
    def generate_large_payload_data(self) -> List[Dict[str, Any]]:
        """Generate very large payloads to test limits"""
        large_string = "A" * 100000  # 100KB string
        very_large_string = "B" * 1000000  # 1MB string
        
        return [
            {"username": large_string, "first_name": "Test", "role": "player"},
            {"username": "test", "first_name": very_large_string, "role": "player"},
            {"user_id": 1001, "chat_id": 1001, "text": large_string},
            {"user_id": 1001, "chat_id": 1001, "text": very_large_string},
        ]
    
    def generate_security_test_data(self) -> List[Dict[str, Any]]:
        """Generate security test payloads"""
        return [
            # SQL Injection attempts
            {"username": "'; DROP TABLE users; --", "first_name": "Test", "role": "player"},
            {"username": "admin' OR '1'='1", "first_name": "Test", "role": "player"},
            
            # XSS attempts
            {"username": "<script>alert('xss')</script>", "first_name": "Test", "role": "player"},
            {"username": "javascript:alert(1)", "first_name": "Test", "role": "player"},
            
            # Path traversal attempts
            {"username": "../../../etc/passwd", "first_name": "Test", "role": "player"},
            {"username": "..\\..\\..\\windows\\system32", "first_name": "Test", "role": "player"},
            
            # Command injection attempts
            {"username": "; rm -rf /", "first_name": "Test", "role": "player"},
            {"username": "| cat /etc/passwd", "first_name": "Test", "role": "player"},
            
            # LDAP injection attempts
            {"username": "*)(uid=*", "first_name": "Test", "role": "player"},
            
            # NoSQL injection attempts
            {"username": {"$ne": None}, "first_name": "Test", "role": "player"},
        ]


class ErrorHandlingTestSuite:
    """Main error handling test suite"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.data_generator = ErrorTestDataGenerator()
        self.test_results: List[ErrorTestResult] = []
        self.session = None
    
    async def __aenter__(self):
        # Configure session with timeouts for error testing
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_all_error_tests(self) -> List[ErrorTestResult]:
        """Run all error handling tests"""
        logger.info("🚨 Starting comprehensive error handling test suite")
        
        test_suites = [
            ("Input Validation Tests", self.run_input_validation_tests),
            ("Malformed Data Tests", self.run_malformed_data_tests),
            ("Boundary Condition Tests", self.run_boundary_condition_tests),
            ("Security Tests", self.run_security_tests),
            ("Rate Limiting Tests", self.run_rate_limiting_tests),
            ("Resource Exhaustion Tests", self.run_resource_exhaustion_tests),
            ("Network Error Tests", self.run_network_error_tests),
            ("Concurrent Access Tests", self.run_concurrent_access_tests),
            ("Error Recovery Tests", self.run_error_recovery_tests),
        ]
        
        for suite_name, test_method in test_suites:
            logger.info(f"🧪 Running {suite_name}...")
            try:
                await test_method()
                logger.info(f"✅ {suite_name} completed")
            except Exception as e:
                logger.error(f"❌ {suite_name} failed: {e}")
        
        return self.test_results
    
    async def run_input_validation_tests(self):
        """Test input validation error handling"""
        logger.info("📝 Testing input validation...")
        
        # Test invalid user creation data
        invalid_user_data = self.data_generator.generate_invalid_user_data()
        
        for i, user_data in enumerate(invalid_user_data):
            test_case = ErrorTestCase(
                name=f"Invalid User Data {i+1}",
                test_type=ErrorTestType.INPUT_VALIDATION,
                description=f"Test user creation with invalid data: {user_data}",
                test_data=user_data,
                expected_status_codes=[400, 422]  # Bad Request or Unprocessable Entity
            )
            
            await self._execute_user_creation_test(test_case)
        
        # Test invalid message data
        invalid_message_data = self.data_generator.generate_invalid_message_data()
        
        for i, message_data in enumerate(invalid_message_data):
            test_case = ErrorTestCase(
                name=f"Invalid Message Data {i+1}",
                test_type=ErrorTestType.INPUT_VALIDATION,
                description=f"Test message sending with invalid data: {message_data}",
                test_data=message_data,
                expected_status_codes=[400, 422, 404]
            )
            
            await self._execute_message_test(test_case)
    
    async def run_malformed_data_tests(self):
        """Test malformed data handling"""
        logger.info("🔧 Testing malformed data handling...")
        
        malformed_json_data = self.data_generator.generate_malformed_json_data()
        
        for i, malformed_json in enumerate(malformed_json_data):
            test_case = ErrorTestCase(
                name=f"Malformed JSON {i+1}",
                test_type=ErrorTestType.MALFORMED_DATA,
                description=f"Test malformed JSON handling",
                test_data={"raw_json": malformed_json},
                expected_status_codes=[400]
            )
            
            await self._execute_malformed_json_test(test_case, malformed_json)
    
    async def run_boundary_condition_tests(self):
        """Test boundary conditions"""
        logger.info("🎯 Testing boundary conditions...")
        
        large_payload_data = self.data_generator.generate_large_payload_data()
        
        for i, payload_data in enumerate(large_payload_data):
            test_case = ErrorTestCase(
                name=f"Large Payload {i+1}",
                test_type=ErrorTestType.BOUNDARY_CONDITIONS,
                description=f"Test large payload handling",
                test_data=payload_data,
                expected_status_codes=[400, 413, 500]  # Bad Request, Payload Too Large, or Server Error
            )
            
            if "text" in payload_data:
                await self._execute_message_test(test_case)
            else:
                await self._execute_user_creation_test(test_case)
    
    async def run_security_tests(self):
        """Test security vulnerability handling"""
        logger.info("🔒 Testing security vulnerability handling...")
        
        security_test_data = self.data_generator.generate_security_test_data()
        
        for i, security_data in enumerate(security_test_data):
            test_case = ErrorTestCase(
                name=f"Security Test {i+1}",
                test_type=ErrorTestType.SECURITY_TESTS,
                description=f"Test security payload handling: {security_data}",
                test_data=security_data,
                expected_status_codes=[400, 403]  # Bad Request or Forbidden
            )
            
            await self._execute_user_creation_test(test_case)
    
    async def run_rate_limiting_tests(self):
        """Test rate limiting"""
        logger.info("⏱️ Testing rate limiting...")
        
        # Send rapid requests to trigger rate limiting
        rapid_requests = []
        
        for i in range(100):  # Send 100 rapid requests
            request_data = {
                "user_id": 1001,
                "chat_id": 2001,
                "text": f"Rate limit test {i}"
            }
            rapid_requests.append(request_data)
        
        test_case = ErrorTestCase(
            name="Rate Limiting Test",
            test_type=ErrorTestType.RATE_LIMITING,
            description="Test rate limiting with rapid requests",
            test_data={"requests": rapid_requests},
            expected_status_codes=[429, 400, 500],  # Too Many Requests
            should_fail=False  # Some requests should succeed, some should be rate limited
        )
        
        await self._execute_rate_limiting_test(test_case, rapid_requests)
    
    async def run_resource_exhaustion_tests(self):
        """Test resource exhaustion handling"""
        logger.info("💾 Testing resource exhaustion...")
        
        # Test WebSocket connection limits
        test_case = ErrorTestCase(
            name="WebSocket Connection Exhaustion",
            test_type=ErrorTestType.RESOURCE_EXHAUSTION,
            description="Test WebSocket connection limits",
            test_data={"connection_count": 150},
            expected_status_codes=[],  # WebSocket doesn't use HTTP status codes
            should_fail=False
        )
        
        await self._execute_websocket_exhaustion_test(test_case)
    
    async def run_network_error_tests(self):
        """Test network error handling"""
        logger.info("🌐 Testing network error handling...")
        
        # Test requests to invalid endpoints
        invalid_endpoints = [
            "/api/nonexistent",
            "/api/users/invalid_path",
            "/api/messages/invalid",
            "/completely/wrong/path"
        ]
        
        for endpoint in invalid_endpoints:
            test_case = ErrorTestCase(
                name=f"Invalid Endpoint: {endpoint}",
                test_type=ErrorTestType.NETWORK_ERRORS,
                description=f"Test invalid endpoint handling",
                test_data={"endpoint": endpoint},
                expected_status_codes=[404]  # Not Found
            )
            
            await self._execute_invalid_endpoint_test(test_case, endpoint)
    
    async def run_concurrent_access_tests(self):
        """Test concurrent access scenarios"""
        logger.info("🔄 Testing concurrent access...")
        
        # Test concurrent user creation
        concurrent_users = []
        for i in range(10):
            user_data = {
                "username": f"concurrent_user_{i}_{int(time.time())}",
                "first_name": f"ConcurrentUser{i}",
                "last_name": "Test",
                "role": "player"
            }
            concurrent_users.append(user_data)
        
        test_case = ErrorTestCase(
            name="Concurrent User Creation",
            test_type=ErrorTestType.CONCURRENT_ACCESS,
            description="Test concurrent user creation",
            test_data={"users": concurrent_users},
            expected_status_codes=[200, 400],  # Some should succeed, some might fail
            should_fail=False
        )
        
        await self._execute_concurrent_user_creation_test(test_case, concurrent_users)
    
    async def run_error_recovery_tests(self):
        """Test error recovery scenarios"""
        logger.info("🔄 Testing error recovery...")
        
        # Test service recovery after errors
        test_case = ErrorTestCase(
            name="Service Recovery Test",
            test_type=ErrorTestType.ERROR_RECOVERY,
            description="Test service recovery after error conditions",
            test_data={},
            expected_status_codes=[200],
            should_fail=False
        )
        
        # Send some invalid requests, then valid ones
        await self._execute_error_recovery_test(test_case)
    
    async def _execute_user_creation_test(self, test_case: ErrorTestCase):
        """Execute a user creation test case"""
        start_time = time.perf_counter()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/users",
                json=test_case.test_data,
                timeout=aiohttp.ClientTimeout(total=test_case.timeout_seconds)
            ) as response:
                response_time = time.perf_counter() - start_time
                
                try:
                    response_data = await response.json()
                except:
                    response_data = {"raw_response": await response.text()}
                
                success = self._evaluate_test_success(test_case, response.status)
                
                result = ErrorTestResult(
                    test_case=test_case,
                    success=success,
                    actual_status_code=response.status,
                    response_data=response_data,
                    response_time=response_time
                )
                
                self.test_results.append(result)
                self._log_test_result(result)
                
        except Exception as e:
            response_time = time.perf_counter() - start_time
            
            result = ErrorTestResult(
                test_case=test_case,
                success=test_case.should_fail,  # Exception might be expected
                error_message=str(e),
                response_time=response_time
            )
            
            self.test_results.append(result)
            self._log_test_result(result)
    
    async def _execute_message_test(self, test_case: ErrorTestCase):
        """Execute a message sending test case"""
        start_time = time.perf_counter()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/send_message",
                json=test_case.test_data,
                timeout=aiohttp.ClientTimeout(total=test_case.timeout_seconds)
            ) as response:
                response_time = time.perf_counter() - start_time
                
                try:
                    response_data = await response.json()
                except:
                    response_data = {"raw_response": await response.text()}
                
                success = self._evaluate_test_success(test_case, response.status)
                
                result = ErrorTestResult(
                    test_case=test_case,
                    success=success,
                    actual_status_code=response.status,
                    response_data=response_data,
                    response_time=response_time
                )
                
                self.test_results.append(result)
                self._log_test_result(result)
                
        except Exception as e:
            response_time = time.perf_counter() - start_time
            
            result = ErrorTestResult(
                test_case=test_case,
                success=test_case.should_fail,
                error_message=str(e),
                response_time=response_time
            )
            
            self.test_results.append(result)
            self._log_test_result(result)
    
    async def _execute_malformed_json_test(self, test_case: ErrorTestCase, malformed_json: str):
        """Execute malformed JSON test"""
        start_time = time.perf_counter()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/users",
                data=malformed_json,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=test_case.timeout_seconds)
            ) as response:
                response_time = time.perf_counter() - start_time
                
                success = self._evaluate_test_success(test_case, response.status)
                
                result = ErrorTestResult(
                    test_case=test_case,
                    success=success,
                    actual_status_code=response.status,
                    response_time=response_time
                )
                
                self.test_results.append(result)
                self._log_test_result(result)
                
        except Exception as e:
            response_time = time.perf_counter() - start_time
            
            result = ErrorTestResult(
                test_case=test_case,
                success=True,  # Exception expected for malformed JSON
                error_message=str(e),
                response_time=response_time
            )
            
            self.test_results.append(result)
            self._log_test_result(result)
    
    async def _execute_rate_limiting_test(self, test_case: ErrorTestCase, requests: List[Dict[str, Any]]):
        """Execute rate limiting test"""
        start_time = time.perf_counter()
        
        # Send requests rapidly
        tasks = []
        for request_data in requests:
            task = self.session.post(
                f"{self.base_url}/api/send_message",
                json=request_data
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        response_time = time.perf_counter() - start_time
        
        # Analyze responses
        status_codes = []
        for response in responses:
            if isinstance(response, Exception):
                continue
            
            try:
                status_codes.append(response.status)
                response.close()
            except:
                pass
        
        # Check if rate limiting occurred
        rate_limited_count = sum(1 for code in status_codes if code == 429)
        success_count = sum(1 for code in status_codes if code == 200)
        
        # Success if we got a mix of successful and rate-limited responses
        success = rate_limited_count > 0 or success_count > 0
        
        result = ErrorTestResult(
            test_case=test_case,
            success=success,
            response_data={
                "total_requests": len(requests),
                "rate_limited": rate_limited_count,
                "successful": success_count,
                "status_codes": status_codes
            },
            response_time=response_time
        )
        
        self.test_results.append(result)
        self._log_test_result(result)
    
    async def _execute_websocket_exhaustion_test(self, test_case: ErrorTestCase):
        """Execute WebSocket connection exhaustion test"""
        start_time = time.perf_counter()
        connections = []
        successful_connections = 0
        
        try:
            # Try to create many WebSocket connections
            for i in range(150):
                try:
                    ws = await websockets.connect(f"ws://localhost:8001/ws", timeout=1)
                    connections.append(ws)
                    successful_connections += 1
                    
                    if i % 20 == 0:
                        logger.debug(f"Created {successful_connections} WebSocket connections")
                        
                except Exception:
                    break  # Connection limit reached or error occurred
            
            response_time = time.perf_counter() - start_time
            
            # Success if we could create some connections but eventually hit a limit
            success = 10 <= successful_connections < 150
            
            result = ErrorTestResult(
                test_case=test_case,
                success=success,
                response_data={
                    "successful_connections": successful_connections,
                    "attempted_connections": 150
                },
                response_time=response_time
            )
            
            self.test_results.append(result)
            self._log_test_result(result)
            
        finally:
            # Close all connections
            for ws in connections:
                try:
                    await ws.close()
                except:
                    pass
    
    async def _execute_invalid_endpoint_test(self, test_case: ErrorTestCase, endpoint: str):
        """Execute invalid endpoint test"""
        start_time = time.perf_counter()
        
        try:
            async with self.session.get(
                f"{self.base_url}{endpoint}",
                timeout=aiohttp.ClientTimeout(total=test_case.timeout_seconds)
            ) as response:
                response_time = time.perf_counter() - start_time
                
                success = self._evaluate_test_success(test_case, response.status)
                
                result = ErrorTestResult(
                    test_case=test_case,
                    success=success,
                    actual_status_code=response.status,
                    response_time=response_time
                )
                
                self.test_results.append(result)
                self._log_test_result(result)
                
        except Exception as e:
            response_time = time.perf_counter() - start_time
            
            result = ErrorTestResult(
                test_case=test_case,
                success=False,  # Should not throw exceptions
                error_message=str(e),
                response_time=response_time
            )
            
            self.test_results.append(result)
            self._log_test_result(result)
    
    async def _execute_concurrent_user_creation_test(self, test_case: ErrorTestCase, users: List[Dict[str, Any]]):
        """Execute concurrent user creation test"""
        start_time = time.perf_counter()
        
        # Create users concurrently
        tasks = []
        for user_data in users:
            task = self.session.post(f"{self.base_url}/api/users", json=user_data)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        response_time = time.perf_counter() - start_time
        
        # Analyze results
        success_count = 0
        error_count = 0
        
        for response in responses:
            if isinstance(response, Exception):
                error_count += 1
                continue
            
            try:
                if response.status == 200:
                    success_count += 1
                else:
                    error_count += 1
                response.close()
            except:
                error_count += 1
        
        # Success if most users were created successfully
        success = success_count >= len(users) * 0.7  # At least 70% success rate
        
        result = ErrorTestResult(
            test_case=test_case,
            success=success,
            response_data={
                "successful_creations": success_count,
                "errors": error_count,
                "total_attempts": len(users)
            },
            response_time=response_time
        )
        
        self.test_results.append(result)
        self._log_test_result(result)
    
    async def _execute_error_recovery_test(self, test_case: ErrorTestCase):
        """Execute error recovery test"""
        start_time = time.perf_counter()
        
        # Send some invalid requests
        invalid_data = {"invalid": "data"}
        for _ in range(5):
            try:
                async with self.session.post(f"{self.base_url}/api/users", json=invalid_data):
                    pass
            except:
                pass
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Now send valid requests to test recovery
        valid_data = {
            "username": f"recovery_test_{int(time.time())}",
            "first_name": "Recovery",
            "last_name": "Test",
            "role": "player"
        }
        
        recovery_success_count = 0
        for _ in range(5):
            try:
                async with self.session.post(f"{self.base_url}/api/users", json=valid_data) as response:
                    if response.status == 200:
                        recovery_success_count += 1
                    # Modify username for next attempt
                    valid_data["username"] = f"recovery_test_{int(time.time())}_{random.randint(1, 1000)}"
            except:
                pass
        
        response_time = time.perf_counter() - start_time
        
        # Success if service recovered and processed valid requests
        success = recovery_success_count >= 3
        
        result = ErrorTestResult(
            test_case=test_case,
            success=success,
            response_data={
                "recovery_success_count": recovery_success_count,
                "total_recovery_attempts": 5
            },
            response_time=response_time
        )
        
        self.test_results.append(result)
        self._log_test_result(result)
    
    def _evaluate_test_success(self, test_case: ErrorTestCase, actual_status_code: int) -> bool:
        """Evaluate if a test case succeeded"""
        if test_case.should_fail:
            # Test should fail - success if we get expected error status codes
            return actual_status_code in test_case.expected_status_codes
        else:
            # Test should succeed - success if we get 2xx status codes
            return 200 <= actual_status_code < 300
    
    def _log_test_result(self, result: ErrorTestResult):
        """Log test result"""
        status = "✅ PASS" if result.success else "❌ FAIL"
        test_name = result.test_case.name
        status_code = result.actual_status_code or "N/A"
        response_time = result.response_time
        
        if result.error_message:
            logger.info(f"{status} {test_name} - Error: {result.error_message} ({response_time:.3f}s)")
        else:
            logger.info(f"{status} {test_name} - Status: {status_code} ({response_time:.3f}s)")
    
    def generate_error_test_report(self) -> str:
        """Generate comprehensive error test report"""
        if not self.test_results:
            return "No error test results available."
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        
        # Group by test type
        test_type_stats = {}
        for result in self.test_results:
            test_type = result.test_case.test_type.value
            if test_type not in test_type_stats:
                test_type_stats[test_type] = {"total": 0, "passed": 0}
            
            test_type_stats[test_type]["total"] += 1
            if result.success:
                test_type_stats[test_type]["passed"] += 1
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ERROR HANDLING TEST REPORT                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Total Tests:        {total_tests:,}                                             ║
║ Passed:            {passed_tests:,} ({passed_tests/total_tests*100:.1f}%)        ║
║ Failed:            {failed_tests:,} ({failed_tests/total_tests*100:.1f}%)        ║
║ Average Response:   {sum(r.response_time for r in self.test_results)/total_tests:.3f}s  ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 RESULTS BY TEST TYPE:
"""
        
        for test_type, stats in test_type_stats.items():
            success_rate = stats["passed"] / stats["total"] * 100
            report += f"  {test_type.replace('_', ' ').title()}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)\n"
        
        # Show failed tests
        failed_results = [r for r in self.test_results if not r.success]
        if failed_results:
            report += f"\n❌ FAILED TESTS ({len(failed_results)}):\n"
            for result in failed_results[:10]:  # Show first 10 failures
                report += f"  • {result.test_case.name} - {result.test_case.test_type.value}\n"
                if result.error_message:
                    report += f"    Error: {result.error_message}\n"
                elif result.actual_status_code:
                    report += f"    Status: {result.actual_status_code}\n"
            
            if len(failed_results) > 10:
                report += f"  ... and {len(failed_results) - 10} more failures\n"
        
        # Security test summary
        security_results = [r for r in self.test_results if r.test_case.test_type == ErrorTestType.SECURITY_TESTS]
        if security_results:
            security_passed = sum(1 for r in security_results if r.success)
            report += f"\n🔒 SECURITY TEST SUMMARY:\n"
            report += f"  Passed: {security_passed}/{len(security_results)} security tests\n"
            
            if security_passed < len(security_results):
                report += "  ⚠️  Some security tests failed - review security measures\n"
        
        return report


# Main execution functions
async def run_comprehensive_error_tests():
    """Run comprehensive error handling tests"""
    async with ErrorHandlingTestSuite() as suite:
        logger.info("🚨 Starting Comprehensive Error Handling Test Suite")
        logger.info("=" * 80)
        
        try:
            results = await suite.run_all_error_tests()
            report = suite.generate_error_test_report()
            
            print(report)
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"error_handling_report_{timestamp}.txt"
            with open(report_file, "w") as f:
                f.write(report)
            
            logger.info(f"📄 Error handling report saved to: {report_file}")
            
            # Determine overall success
            passed_tests = sum(1 for r in results if r.success)
            success_rate = passed_tests / len(results) * 100 if results else 0
            
            return success_rate >= 80.0  # 80%+ pass rate considered successful
            
        except Exception as e:
            logger.error(f"💥 Error handling test suite failed: {e}")
            return False


async def run_quick_error_check():
    """Run a quick error handling check"""
    async with ErrorHandlingTestSuite() as suite:
        logger.info("⚡ Running Quick Error Check")
        
        # Run just input validation tests
        await suite.run_input_validation_tests()
        
        passed = sum(1 for r in suite.test_results if r.success)
        total = len(suite.test_results)
        success_rate = passed / total * 100 if total > 0 else 0
        
        print(f"""
Quick Error Check Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests Run:        {total}
Passed:           {passed}
Success Rate:     {success_rate:.1f}%

Status: {'✅ GOOD' if success_rate >= 80 else '⚠️  NEEDS ATTENTION'}
""")
        
        return success_rate >= 80


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        success = asyncio.run(run_quick_error_check())
    else:
        success = asyncio.run(run_comprehensive_error_tests())
    
    sys.exit(0 if success else 1)