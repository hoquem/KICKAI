#!/usr/bin/env python3
"""
End-to-End Testing Framework for KICKAI

This framework provides comprehensive testing capabilities for:
- Telegram bot automation
- Firestore data validation
- Natural language processing
- Command execution
- User interaction flows
"""

import asyncio
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import re

# Telegram imports
from telegram import Update, User, Chat, Message
from telegram.ext import Application, ContextTypes
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Message

# Firebase imports
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin

# Testing imports
from unittest.mock import Mock, AsyncMock, patch
import pytest
import pytest_asyncio
from src.core.improved_config_system import get_improved_config

logger = logging.getLogger(__name__)


def get_chat_ids():
    """Get chat IDs from configuration manager."""
    config = get_improved_config()
    default_team_id = config.configuration.teams.default_team_id
    team_config = config.get_team_config(default_team_id)
    main_chat_id = team_config.main_chat_id if team_config else None
    leadership_chat_id = team_config.leadership_chat_id if team_config else None
    return main_chat_id, leadership_chat_id


class TestType(Enum):
    """Types of tests supported."""
    COMMAND = "command"
    NATURAL_LANGUAGE = "natural_language"
    USER_FLOW = "user_flow"
    DATA_VALIDATION = "data_validation"
    INTEGRATION = "integration"
    VALIDATION = "validation"


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


class TelegramBotTester:
    """Automated Telegram bot testing framework."""
    
    def __init__(self, bot_token: str, api_id: str, api_hash: str, session_string: str):
        self.bot_token = bot_token
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_string = session_string
        
        # Initialize Telegram client
        self.client = TelegramClient(
            StringSession(session_string),
            int(api_id),
            api_hash
        )
        
        # Test data storage
        self.test_data: Dict[str, Any] = {}
        self.results: List[TestResult] = []
        
        logger.info("✅ TelegramBotTester initialized")
    
    async def start(self):
        """Start the Telegram client."""
        await self.client.start()
        logger.info("✅ Telegram client started")
    
    async def stop(self):
        """Stop the Telegram client."""
        await self.client.disconnect()
        logger.info("✅ Telegram client stopped")
    
    async def send_message(self, chat_id: str, message: str) -> Message:
        """Send a message to a chat."""
        try:
            # Convert chat_id to int for proper Telethon compatibility
            chat_id_int = int(chat_id)
            result = await self.client.send_message(chat_id_int, message)
            logger.info(f"✅ Message sent: {message[:50]}...")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            raise
    
    async def get_messages(self, chat_id: str, limit: int = 10) -> List[Message]:
        """Get recent messages from a chat."""
        try:
            # Convert chat_id to int for proper Telethon compatibility
            chat_id_int = int(chat_id)
            messages = await self.client.get_messages(chat_id_int, limit=limit)
            return messages
        except Exception as e:
            logger.error(f"❌ Failed to get messages: {e}")
            return []
    
    async def wait_for_response(self, chat_id: str, timeout: int = 30) -> Optional[Message]:
        """Wait for a response in a chat."""
        start_time = time.time()
        last_message_count = 0
        
        # Get current user info once
        current_user = await self.client.get_me()
        
        while time.time() - start_time < timeout:
            messages = await self.get_messages(chat_id, limit=10)
            
            # Filter out messages from the current user (bot responses only)
            bot_messages = [msg for msg in messages if msg.from_id != current_user.id]
            
            if len(bot_messages) > last_message_count:
                # New bot message received
                return bot_messages[0]  # Most recent bot message
            
            last_message_count = len(bot_messages)
            await asyncio.sleep(1)
        
        logger.warning(f"⏰ Timeout waiting for response in chat {chat_id}")
        return None
    
    async def test_command(self, command: str, context: TelegramTestContext) -> TestResult:
        """Test a slash command."""
        start_time = time.time()
        
        try:
            # Send command
            await self.send_message(context.chat_id, command)
            
            # Wait for response
            response = await self.wait_for_response(context.chat_id)
            
            if response:
                duration = time.time() - start_time
                success = not response.text.startswith("❌")
                
                return TestResult(
                    test_name=f"Command: {command}",
                    test_type=TestType.COMMAND,
                    success=success,
                    duration=duration,
                    message=response.text,
                    metadata={
                        "command": command,
                        "user_id": context.user_id,
                        "chat_id": context.chat_id,
                        "response_length": len(response.text)
                    }
                )
            else:
                return TestResult(
                    test_name=f"Command: {command}",
                    test_type=TestType.COMMAND,
                    success=False,
                    duration=time.time() - start_time,
                    message="No response received",
                    errors=["Timeout waiting for response"]
                )
                
        except Exception as e:
            return TestResult(
                test_name=f"Command: {command}",
                test_type=TestType.COMMAND,
                success=False,
                duration=time.time() - start_time,
                message=f"Test failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def test_natural_language(self, message: str, context: TelegramTestContext) -> TestResult:
        """Test natural language processing."""
        start_time = time.time()
        
        try:
            # Send natural language message
            await self.send_message(context.chat_id, message)
            
            # Wait for response
            response = await self.wait_for_response(context.chat_id)
            
            if response:
                duration = time.time() - start_time
                success = not response.text.startswith("❌")
                
                return TestResult(
                    test_name=f"NL: {message}",
                    test_type=TestType.NATURAL_LANGUAGE,
                    success=success,
                    duration=duration,
                    message=response.text,
                    metadata={
                        "input_message": message,
                        "user_id": context.user_id,
                        "chat_id": context.chat_id,
                        "response_length": len(response.text)
                    }
                )
            else:
                return TestResult(
                    test_name=f"NL: {message}",
                    test_type=TestType.NATURAL_LANGUAGE,
                    success=False,
                    duration=time.time() - start_time,
                    message="No response received",
                    errors=["Timeout waiting for response"]
                )
                
        except Exception as e:
            return TestResult(
                test_name=f"NL: {message}",
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
            # Check if this is a query-based validation
            if context.document_id.startswith("query_"):
                return await self._validate_document_by_query(context, start_time)
            
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
            
            # Validate against expected data
            validation_errors = []
            validated_data = {}
            
            for field, expected_value in context.expected_data.items():
                if field in data:
                    actual_value = data[field]
                    validated_data[field] = actual_value
                    
                    # Apply validation rules
                    if field in context.validation_rules:
                        rule = context.validation_rules[field]
                        if not self._validate_field(actual_value, rule):
                            validation_errors.append(f"Field '{field}' failed validation rule: {rule}")
                else:
                    validation_errors.append(f"Required field '{field}' not found")
            
            success = len(validation_errors) == 0
            duration = time.time() - start_time
            
            return TestResult(
                test_name=f"Firestore: {context.collection}/{context.document_id}",
                test_type=TestType.DATA_VALIDATION,
                success=success,
                duration=duration,
                message=f"Document validation {'passed' if success else 'failed'}",
                data_validated=validated_data,
                errors=validation_errors,
                metadata={
                    "collection": context.collection,
                    "document_id": context.document_id,
                    "fields_validated": len(validated_data)
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
    
    async def _validate_document_by_query(self, context: FirestoreTestContext, start_time: float) -> TestResult:
        """Validate a document by querying with filters."""
        try:
            # Find the query rule
            query_rule = None
            for field, rule in context.validation_rules.items():
                if rule.get('type') == 'query':
                    query_rule = rule
                    break
            
            if not query_rule or 'filters' not in query_rule:
                return TestResult(
                    test_name=f"Firestore: {context.collection}/query",
                    test_type=TestType.DATA_VALIDATION,
                    success=False,
                    duration=time.time() - start_time,
                    message="Invalid query rule",
                    errors=["No valid query filters found"]
                )
            
            # Build query
            query = self.db.collection(context.collection)
            for filter_item in query_rule['filters']:
                field = filter_item['field']
                operator = filter_item['operator']
                value = filter_item['value']
                query = query.where(field, operator, value)
            
            # Execute query
            docs = query.stream()
            documents = list(docs)
            
            if not documents:
                return TestResult(
                    test_name=f"Firestore: {context.collection}/query",
                    test_type=TestType.DATA_VALIDATION,
                    success=False,
                    duration=time.time() - start_time,
                    message="No documents found matching query",
                    errors=["Query returned no results"]
                )
            
            # Validate the first document found
            data = documents[0].to_dict()
            data['id'] = documents[0].id
            
            # Validate against expected data
            validation_errors = []
            validated_data = {}
            
            for field, expected_value in context.expected_data.items():
                if field in data:
                    actual_value = data[field]
                    validated_data[field] = actual_value
                    
                    # Apply validation rules (excluding query rules)
                    if field in context.validation_rules and context.validation_rules[field].get('type') != 'query':
                        rule = context.validation_rules[field]
                        if not self._validate_field(actual_value, rule):
                            validation_errors.append(f"Field '{field}' failed validation rule: {rule}")
                else:
                    validation_errors.append(f"Required field '{field}' not found")
            
            success = len(validation_errors) == 0
            duration = time.time() - start_time
            
            return TestResult(
                test_name=f"Firestore: {context.collection}/query",
                test_type=TestType.DATA_VALIDATION,
                success=success,
                duration=duration,
                message=f"Query validation {'passed' if success else 'failed'}",
                data_validated=validated_data,
                errors=validation_errors,
                metadata={
                    "collection": context.collection,
                    "document_id": documents[0].id,
                    "fields_validated": len(validated_data),
                    "query_filters": query_rule['filters']
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name=f"Firestore: {context.collection}/query",
                test_type=TestType.DATA_VALIDATION,
                success=False,
                duration=time.time() - start_time,
                message=f"Query validation failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _validate_field(self, value: Any, rule: Dict[str, Any]) -> bool:
        """Validate a field against a rule."""
        rule_type = rule.get('type', 'exact')
        
        if rule_type == 'exact':
            return value == rule.get('value')
        elif rule_type == 'regex':
            pattern = rule.get('pattern')
            return bool(re.match(pattern, str(value)))
        elif rule_type == 'range':
            min_val = rule.get('min')
            max_val = rule.get('max')
            return (min_val is None or value >= min_val) and (max_val is None or value <= max_val)
        elif rule_type == 'exists':
            return value is not None
        elif rule_type == 'type':
            expected_type = rule.get('expected_type')
            return isinstance(value, expected_type)
        
        return True
    
    async def create_test_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Create a test document in Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.set(data)
            logger.info(f"✅ Created test document: {collection}/{document_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create test document: {e}")
            return False
    
    async def delete_test_document(self, collection: str, document_id: str) -> bool:
        """Delete a test document from Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.delete()
            logger.info(f"✅ Deleted test document: {collection}/{document_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete test document: {e}")
            return False


class E2ETestRunner:
    """End-to-end test runner that combines Telegram and Firestore testing."""
    
    def __init__(self, telegram_tester: TelegramBotTester, firestore_validator: FirestoreValidator):
        self.telegram_tester = telegram_tester
        self.firestore_validator = firestore_validator
        self.test_suite: List[Dict[str, Any]] = []
        self.results: List[TestResult] = []
        
        logger.info("✅ E2ETestRunner initialized")
    
    def add_test(self, test_config: Dict[str, Any]):
        """Add a test to the test suite."""
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
    
    def add_user_flow_test(self, steps: List[Dict[str, Any]], context: TelegramTestContext):
        """Add a user flow test with multiple steps."""
        test_config = {
            "type": "user_flow",
            "steps": steps,
            "telegram_context": context
        }
        self.add_test(test_config)
    
    async def run_tests(self) -> List[TestResult]:
        """Run all tests in the test suite."""
        logger.info(f"🚀 Starting E2E test suite with {len(self.test_suite)} tests")
        
        results = []
        
        for i, test_config in enumerate(self.test_suite, 1):
            logger.info(f"📋 Running test {i}/{len(self.test_suite)}: {test_config['type']}")
            
            try:
                if test_config['type'] == 'command':
                    result = await self._run_command_test(test_config)
                elif test_config['type'] == 'natural_language':
                    result = await self._run_nl_test(test_config)
                elif test_config['type'] == 'user_flow':
                    result = await self._run_user_flow_test(test_config)
                elif test_config['type'] == 'validation':
                    result = await self._run_validation_test(test_config)
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
        telegram_result = await self.telegram_tester.test_command(command, context)
        
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
        telegram_result = await self.telegram_tester.test_natural_language(message, context)
        
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
    
    async def _run_user_flow_test(self, test_config: Dict[str, Any]) -> TestResult:
        """Run a user flow test with multiple steps."""
        steps = test_config['steps']
        context = test_config['telegram_context']
        
        start_time = time.time()
        all_errors = []
        step_results = []
        
        for i, step in enumerate(steps, 1):
            try:
                if step['type'] == 'send_message':
                    await self.telegram_tester.send_message(context.chat_id, step['message'])
                elif step['type'] == 'wait_for_response':
                    response = await self.telegram_tester.wait_for_response(context.chat_id, step.get('timeout', 30))
                    if response:
                        step_results.append(response.text)
                    else:
                        all_errors.append(f"Step {i}: No response received")
                elif step['type'] == 'validate_response':
                    if step_results and step_results[-1] != step['expected']:
                        all_errors.append(f"Step {i}: Expected '{step['expected']}', got '{step_results[-1]}'")
                
            except Exception as e:
                all_errors.append(f"Step {i}: {str(e)}")
        
        duration = time.time() - start_time
        success = len(all_errors) == 0
        
        return TestResult(
            test_name=f"User Flow: {len(steps)} steps",
            test_type=TestType.USER_FLOW,
            success=success,
            duration=duration,
            message=f"User flow {'completed successfully' if success else 'failed'}",
            errors=all_errors,
            metadata={
                "steps_executed": len(steps),
                "step_results": step_results
            }
        )
    
    async def _run_validation_test(self, test_config: Dict[str, Any]) -> TestResult:
        """Run a validation test for configuration and environment variables."""
        validation_data = test_config['validation']
        start_time = time.time()
        errors = []
        
        try:
            # Validate chat ID configuration
            if 'main_chat_id' in validation_data:
                main_chat_id = validation_data['main_chat_id']
                leadership_chat_id = validation_data['leadership_chat_id']
                expected_main = validation_data['expected_main']
                expected_leadership = validation_data['expected_leadership']
                
                if main_chat_id != expected_main:
                    errors.append(f"Main chat ID mismatch: expected {expected_main}, got {main_chat_id}")
                
                if leadership_chat_id != expected_leadership:
                    errors.append(f"Leadership chat ID mismatch: expected {expected_leadership}, got {leadership_chat_id}")
                
                # Validate naming convention
                naming = validation_data.get('naming_convention', {})
                if naming:
                    logger.info(f"Chat naming convention: Main='{naming.get('main')}', Leadership='{naming.get('leadership')}'")
            
            # Validate environment variables
            if 'env_vars' in validation_data:
                env_vars = validation_data['env_vars']
                for var_name, var_value in env_vars.items():
                    if not var_value:
                        errors.append(f"Missing environment variable: {var_name}")
                    else:
                        logger.info(f"✅ {var_name}: {var_value}")
            
            duration = time.time() - start_time
            success = len(errors) == 0
            
            return TestResult(
                test_name=f"Validation: {test_config.get('name', 'Configuration')}",
                test_type=TestType.VALIDATION,
                success=success,
                duration=duration,
                message=f"Configuration validation {'passed' if success else 'failed'}",
                errors=errors,
                metadata={
                    "validation_data": validation_data,
                    "errors_count": len(errors)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=f"Validation: {test_config.get('name', 'Configuration')}",
                test_type=TestType.VALIDATION,
                success=False,
                duration=duration,
                message=f"Validation test failed with exception: {str(e)}",
                errors=[str(e)]
            )
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        if not self.results:
            return "No test results available"
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - passed_tests
        
        # Calculate statistics
        avg_duration = sum(r.duration for r in self.results) / total_tests
        test_types = {}
        for result in self.results:
            test_type = result.test_type.value
            test_types[test_type] = test_types.get(test_type, 0) + 1
        
        # Generate report
        report = f"""
🧪 KICKAI E2E Test Report
{'=' * 50}

📊 Summary:
• Total Tests: {total_tests}
• Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)
• Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)
• Average Duration: {avg_duration:.2f}s

📋 Test Types:
"""
        
        for test_type, count in test_types.items():
            report += f"• {test_type.title()}: {count}\n"
        
        report += f"""
⏱️ Performance:
• Total Duration: {sum(r.duration for r in self.results):.2f}s
• Fastest Test: {min(r.duration for r in self.results):.2f}s
• Slowest Test: {max(r.duration for r in self.results):.2f}s

❌ Failed Tests:
"""
        
        for result in self.results:
            if not result.success:
                report += f"• {result.test_name}\n"
                for error in result.errors:
                    report += f"  - {error}\n"
        
        return report


# Pytest fixtures for easy integration
@pytest.fixture
async def telegram_tester():
    """Fixture for Telegram bot tester."""
    # These should be set as environment variables
    bot_token = "YOUR_BOT_TOKEN"
    api_id = "YOUR_API_ID"
    api_hash = "YOUR_API_HASH"
    session_string = "YOUR_SESSION_STRING"
    
    tester = TelegramBotTester(bot_token, api_id, api_hash, session_string)
    await tester.start()
    yield tester
    await tester.stop()


@pytest.fixture
def firestore_validator():
    """Fixture for Firestore validator."""
    project_id = "YOUR_PROJECT_ID"
    validator = FirestoreValidator(project_id)
    return validator


@pytest.fixture
async def e2e_runner(telegram_tester, firestore_validator):
    """Fixture for E2E test runner."""
    runner = E2ETestRunner(telegram_tester, firestore_validator)
    return runner 