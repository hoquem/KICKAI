#!/usr/bin/env python3
"""
Multi-Client E2E Testing Framework

This framework uses multiple Telegram clients to simulate real user interactions:
- Bot Client: Handles commands and responses
- User Client: Acts as both player and admin in different chats
"""

import asyncio
import time
import logging
from typing import Any, List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Message
import firebase_admin
from firebase_admin import credentials, firestore
import os

logger = logging.getLogger(__name__)

from kickai.core.enums import TestType

@dataclass
class TestResult:
    """Result of a test execution."""
    test_name: str
    test_type: TestType
    success: bool
    duration: float
    message: str
    data_validated: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TelegramTestContext:
    """Context for Telegram bot testing."""
    user_id: str
    chat_id: str
    username: str
    is_leadership_chat: bool = False
    team_id: str = "test-team-123"
    user_role: str = "player"

@dataclass
class FirestoreTestContext:
    """Context for Firestore testing."""
    collection: str
    document_id: str
    expected_data: Dict[str, Any]
    validation_rules: Dict[str, Any] = field(default_factory=dict)

class MultiClientE2ETester:
    """Multi-client E2E testing framework."""
    
    def __init__(self, bot_token: str, api_id: str, api_hash: str, 
                 user_session_string: str):
        self.bot_token = bot_token
        self.api_id = api_id
        self.api_hash = api_hash
        self.user_session_string = user_session_string
        
        # Initialize clients
        self.bot_client = TelegramClient(
            StringSession(), int(api_id), api_hash
        )
        self.user_client = TelegramClient(
            StringSession(user_session_string), int(api_id), api_hash
        )
        
        # Test data storage
        self.test_data: Dict[str, Any] = {}
        self.results: List[TestResult] = []
        
        logger.info("✅ MultiClientE2ETester initialized")
    
    async def start(self):
        """Start all Telegram clients."""
        await self.bot_client.start(bot_token=self.bot_token)
        await self.user_client.start()
        logger.info("✅ All Telegram clients started")
    
    async def stop(self):
        """Stop all Telegram clients."""
        await self.bot_client.disconnect()
        await self.user_client.disconnect()
        logger.info("✅ All Telegram clients stopped")
    
    async def send_message_as_user(self, chat_id: str, message: str) -> Message:
        """Send a message as the user client."""
        try:
            chat_id_int = int(chat_id) if isinstance(chat_id, str) and chat_id.lstrip('-').isdigit() else chat_id
            result = await self.user_client.send_message(chat_id_int, message)
            logger.info(f"✅ User message sent: {message[:50]}...")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to send user message: {e}")
            raise
    
    async def wait_for_bot_response(self, chat_id: str, timeout: int = 30) -> Optional[Message]:
        """Wait for a bot response in a chat."""
        start_time = time.time()
        last_message_count = 0
        chat_id_int = int(chat_id) if isinstance(chat_id, str) and chat_id.lstrip('-').isdigit() else chat_id
        while time.time() - start_time < timeout:
            messages = await self.user_client.get_messages(chat_id_int, limit=5)
            if len(messages) > last_message_count:
                # New message received
                return messages[0]  # Most recent message
            last_message_count = len(messages)
            await asyncio.sleep(1)
        logger.warning(f"⏰ Timeout waiting for bot response in chat {chat_id}")
        return None
    
    async def test_command_as_user(self, command: str, context: TelegramTestContext) -> TestResult:
        """Test a command as the user client."""
        start_time = time.time()
        
        try:
            # Send command as user
            await self.send_message_as_user(context.chat_id, command)
            
            # Wait for bot response
            response = await self.wait_for_bot_response(context.chat_id)
            
            if response:
                duration = time.time() - start_time
                success = not response.text.startswith("❌")
                
                return TestResult(
                    test_name=f"User Command: {command}",
                    test_type=TestType.COMMAND,
                    success=success,
                    duration=duration,
                    message=response.text,
                    metadata={
                        "command": command,
                        "user_id": context.user_id,
                        "chat_id": context.chat_id,
                        "response_length": len(response.text),
                        "role": context.user_role
                    }
                )
            else:
                return TestResult(
                    test_name=f"User Command: {command}",
                    test_type=TestType.COMMAND,
                    success=False,
                    duration=time.time() - start_time,
                    message="No bot response received",
                    errors=["Timeout waiting for bot response"]
                )
                
        except Exception as e:
            return TestResult(
                test_name=f"User Command: {command}",
                test_type=TestType.COMMAND,
                success=False,
                duration=time.time() - start_time,
                message=f"Test failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def test_natural_language_as_user(self, message: str, context: TelegramTestContext) -> TestResult:
        """Test natural language processing as the user client."""
        start_time = time.time()
        
        try:
            # Send natural language message as user
            await self.send_message_as_user(context.chat_id, message)
            
            # Wait for bot response
            response = await self.wait_for_bot_response(context.chat_id)
            
            if response:
                duration = time.time() - start_time
                success = not response.text.startswith("❌")
                
                return TestResult(
                    test_name=f"User NL: {message}",
                    test_type=TestType.NATURAL_LANGUAGE,
                    success=success,
                    duration=duration,
                    message=response.text,
                    metadata={
                        "input_message": message,
                        "user_id": context.user_id,
                        "chat_id": context.chat_id,
                        "response_length": len(response.text),
                        "role": context.user_role
                    }
                )
            else:
                return TestResult(
                    test_name=f"User NL: {message}",
                    test_type=TestType.NATURAL_LANGUAGE,
                    success=False,
                    duration=time.time() - start_time,
                    message="No bot response received",
                    errors=["Timeout waiting for bot response"]
                )
                
        except Exception as e:
            return TestResult(
                test_name=f"User NL: {message}",
                test_type=TestType.NATURAL_LANGUAGE,
                success=False,
                duration=time.time() - start_time,
                message=f"Test failed: {str(e)}",
                errors=[str(e)]
            )

class FirestoreValidator:
    """Firestore data validation framework."""
    
    def __init__(self, project_id: str, credentials_path: str = None):
        self.project_id = project_id
        
        # Initialize Firebase
        if not firebase_admin._apps:
            cred_path = credentials_path or os.getenv('FIRESTORE_CREDENTIALS_PATH')
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {'projectId': project_id})
            else:
                firebase_admin.initialize_app({'projectId': project_id})
        
        self.db = firestore.client()
        logger.info(f"✅ FirestoreValidator initialized for project {project_id}")
    
    async def validate_document(self, context: FirestoreTestContext) -> TestResult:
        """Validate a Firestore document."""
        start_time = time.time()
        
        try:
            # Get document
            doc_ref = self.db.collection(context.collection).document(context.document_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return TestResult(
                    test_name=f"Firestore: {context.collection}/{context.document_id}",
                    test_type=TestType.DATA_VALIDATION,
                    success=False,
                    duration=time.time() - start_time,
                    message="Document does not exist",
                    errors=["Document not found"]
                )
            
            # Get document data
            data = doc.to_dict()
            
            # Validate expected data
            validation_errors = []
            data_validated = {}
            
            for field, expected_value in context.expected_data.items():
                if field in data:
                    actual_value = data[field]
                    if self._validate_field(actual_value, {"type": "exact", "value": expected_value}):
                        data_validated[field] = actual_value
                    else:
                        validation_errors.append(f"Field '{field}': expected {expected_value}, got {actual_value}")
                else:
                    validation_errors.append(f"Field '{field}' not found in document")
            
            # Validate with rules if provided
            for field, rule in context.validation_rules.items():
                if field in data:
                    if not self._validate_field(data[field], rule):
                        validation_errors.append(f"Field '{field}' failed validation rule: {rule}")
            
            success = len(validation_errors) == 0
            
            return TestResult(
                test_name=f"Firestore: {context.collection}/{context.document_id}",
                test_type=TestType.DATA_VALIDATION,
                success=success,
                duration=time.time() - start_time,
                message=f"Document validation {'passed' if success else 'failed'}",
                data_validated=data_validated,
                errors=validation_errors,
                metadata={
                    "collection": context.collection,
                    "document_id": context.document_id,
                    "fields_validated": len(data_validated)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name=f"Firestore: {context.collection}/{context.document_id}",
                test_type=TestType.DATA_VALIDATION,
                success=False,
                duration=time.time() - start_time,
                message=f"Validation failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _validate_field(self, value: Any, rule: Dict[str, Any]) -> bool:
        """Validate a field according to a rule."""
        rule_type = rule.get("type")
        
        if rule_type == "exact":
            return value == rule["value"]
        elif rule_type == "exists":
            return value is not None
        elif rule_type == "regex":
            import re
            pattern = rule["pattern"]
            return bool(re.match(pattern, str(value)))
        else:
            return True

class MultiClientE2ETestRunner:
    """Test runner for multi-client E2E tests."""
    
    def __init__(self, tester: MultiClientE2ETester, firestore_validator: FirestoreValidator):
        self.tester = tester
        self.firestore_validator = firestore_validator
        self.test_suite: List[Dict[str, Any]] = []
        self.results: List[TestResult] = []
        
        logger.info("✅ MultiClientE2ETestRunner initialized")
    
    def add_test(self, test_config: Dict[str, Any]):
        """Add a test to the suite."""
        self.test_suite.append(test_config)
    
    def add_command_test(self, command: str, context: TelegramTestContext, 
                        firestore_validation: Optional[FirestoreTestContext] = None):
        """Add a command test with optional Firestore validation."""
        test_config = {
            "type": "command",
            "command": command,
            "telegram_context": context,
            "firestore_validation": firestore_validation
        }
        self.add_test(test_config)
    
    def add_nl_test(self, message: str, context: TelegramTestContext,
                   firestore_validation: Optional[FirestoreTestContext] = None):
        """Add a natural language test with optional Firestore validation."""
        test_config = {
            "type": "natural_language",
            "message": message,
            "telegram_context": context,
            "firestore_validation": firestore_validation
        }
        self.add_test(test_config)
    
    async def run_tests(self) -> List[TestResult]:
        """Run all tests in the test suite."""
        logger.info(f"🚀 Starting multi-client E2E test suite with {len(self.test_suite)} tests")
        
        results = []
        
        for i, test_config in enumerate(self.test_suite, 1):
            logger.info(f"📋 Running test {i}/{len(self.test_suite)}: {test_config['type']}")
            
            try:
                if test_config['type'] == 'command':
                    result = await self._run_command_test(test_config)
                elif test_config['type'] == 'natural_language':
                    result = await self._run_nl_test(test_config)
                else:
                    result = TestResult(
                        test_name=f"Unknown test type: {test_config['type']}",
                        test_type=TestType.INTEGRATION,
                        success=False,
                        duration=0,
                        message="Unknown test type",
                        errors=["Invalid test configuration"]
                    )
                
                results.append(result)
                
                # Log result
                status = "✅ PASS" if result.success else "❌ FAIL"
                logger.info(f"{status} Test {i}: {result.test_name} ({result.duration:.2f}s)")
                
                if not result.success and result.errors:
                    for error in result.errors:
                        logger.error(f"  Error: {error}")
                
            except Exception as e:
                logger.error(f"❌ Test {i} failed with exception: {e}")
                results.append(TestResult(
                    test_name=f"Test {i}",
                    test_type=TestType.INTEGRATION,
                    success=False,
                    duration=0,
                    message=f"Test failed with exception: {str(e)}",
                    errors=[str(e)]
                ))
        
        self.results = results
        logger.info(f"🏁 Test suite completed. {len([r for r in results if r.success])}/{len(results)} tests passed")
        
        return results
    
    async def _run_command_test(self, test_config: Dict[str, Any]) -> TestResult:
        """Run a command test."""
        command = test_config['command']
        context = test_config['telegram_context']
        firestore_validation = test_config.get('firestore_validation')
        
        # Run Telegram test
        telegram_result = await self.tester.test_command_as_user(command, context)
        
        # Run Firestore validation if specified
        if firestore_validation and telegram_result.success:
            firestore_result = await self.firestore_validator.validate_document(firestore_validation)
            
            # Combine results
            combined_success = telegram_result.success and firestore_result.success
            combined_errors = telegram_result.errors + firestore_result.errors
            
            return TestResult(
                test_name=f"Command + Validation: {command}",
                test_type=TestType.INTEGRATION,
                success=combined_success,
                duration=telegram_result.duration + firestore_result.duration,
                message=f"Telegram: {telegram_result.message} | Firestore: {firestore_result.message}",
                data_validated=firestore_result.data_validated,
                errors=combined_errors,
                metadata={
                    **telegram_result.metadata,
                    **firestore_result.metadata
                }
            )
        
        return telegram_result
    
    async def _run_nl_test(self, test_config: Dict[str, Any]) -> TestResult:
        """Run a natural language test."""
        message = test_config['message']
        context = test_config['telegram_context']
        firestore_validation = test_config.get('firestore_validation')
        
        # Run Telegram test
        telegram_result = await self.tester.test_natural_language_as_user(message, context)
        
        # Run Firestore validation if specified
        if firestore_validation and telegram_result.success:
            firestore_result = await self.firestore_validator.validate_document(firestore_validation)
            
            # Combine results
            combined_success = telegram_result.success and firestore_result.success
            combined_errors = telegram_result.errors + firestore_result.errors
            
            return TestResult(
                test_name=f"NL + Validation: {message}",
                test_type=TestType.INTEGRATION,
                success=combined_success,
                duration=telegram_result.duration + firestore_result.duration,
                message=f"Telegram: {telegram_result.message} | Firestore: {firestore_result.message}",
                data_validated=firestore_result.data_validated,
                errors=combined_errors,
                metadata={
                    **telegram_result.metadata,
                    **firestore_result.metadata
                }
            )
        
        return telegram_result 