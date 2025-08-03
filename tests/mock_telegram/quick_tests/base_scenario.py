"""
Base Scenario

Abstract base class for all quick test scenarios with enhanced logging and common functionality.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from loguru import logger


class TestStatus(str, Enum):
    """Status of test execution"""
    PENDING = "pending"
    SETUP = "setup"
    EXECUTING = "executing"
    VALIDATING = "validating"
    CLEANING_UP = "cleaning_up"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TestResult:
    """Result of a test scenario execution"""
    scenario_name: str
    status: TestStatus
    start_time: datetime
    end_time: datetime
    duration_seconds: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    validation_results: Optional[Dict[str, Any]] = None
    cleanup_results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.duration_seconds is None and self.start_time and self.end_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        if self.details is None:
            self.details = {}
        
        if self.validation_results is None:
            self.validation_results = {}
        
        if self.cleanup_results is None:
            self.cleanup_results = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "scenario_name": self.scenario_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "details": self.details,
            "validation_results": self.validation_results,
            "cleanup_results": self.cleanup_results,
            "error_message": self.error_message
        }


class BaseScenario(ABC):
    """
    Abstract base class for all quick test scenarios.
    
    Provides common functionality for:
    - Test lifecycle management (setup -> execute -> validate -> cleanup)
    - Enhanced logging with detailed tracing
    - Error handling and timeout management
    - Common utilities for mock service interaction
    - Bot integration helpers
    - Validation helpers
    """
    
    def __init__(self, 
                 mock_service, 
                 bot_integration, 
                 test_data_manager, 
                 validation_engine, 
                 cleanup_handler):
        """
        Initialize the base scenario.
        
        Args:
            mock_service: Mock Telegram service instance
            bot_integration: Bot integration layer instance
            test_data_manager: Test data manager instance
            validation_engine: Validation engine instance
            cleanup_handler: Cleanup handler instance
        """
        self.mock_service = mock_service
        self.bot_integration = bot_integration
        self.test_data_manager = test_data_manager
        self.validation_engine = validation_engine
        self.cleanup_handler = cleanup_handler
        self.team_id: Optional[str] = None  # Team ID for real data loading
        
        # Scenario metadata
        self.scenario_name = self.__class__.__name__.replace("Scenario", "").lower()
        self.scenario_id = f"{self.scenario_name}_{uuid.uuid4().hex[:8]}"
        
        # Test state
        self.current_status = TestStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.test_context: Dict[str, Any] = {}
        self.execution_log: List[Dict[str, Any]] = []
        
        # Configuration
        self.timeout_seconds = self.get_default_timeout()
        self.retry_attempts = 3
        self.retry_delay_seconds = 2
        
        logger.debug(f"🎯 Initialized scenario: {self.scenario_name} ({self.scenario_id})")
    
    # Abstract methods that must be implemented by subclasses
    
    @abstractmethod
    async def setup(self) -> Dict[str, Any]:
        """
        Set up the test environment and prepare test data.
        
        Returns:
            Setup context dictionary containing test fixtures and data
        """
        pass
    
    @abstractmethod
    async def execute(self) -> TestResult:
        """
        Execute the main test scenario logic.
        
        Returns:
            TestResult with execution details
        """
        pass
    
    @abstractmethod
    async def validate(self, execution_result: TestResult) -> Dict[str, Any]:
        """
        Validate the test execution results.
        
        Args:
            execution_result: Result from execute() method
            
        Returns:
            Validation results dictionary
        """
        pass
    
    @abstractmethod
    async def cleanup(self, test_context: Dict[str, Any]) -> None:
        """
        Clean up test artifacts and restore initial state.
        
        Args:
            test_context: Test context from setup phase
        """
        pass
    
    # Configuration methods that can be overridden
    
    def get_default_timeout(self) -> int:
        """Get default timeout in seconds for this scenario"""
        return 60
    
    def get_retry_attempts(self) -> int:
        """Get number of retry attempts for failed operations"""
        return 3
    
    def get_expected_outcomes(self) -> Dict[str, Any]:
        """Get expected outcomes for this scenario"""
        return {}
    
    def get_validation_criteria(self) -> Dict[str, Any]:
        """Get validation criteria for this scenario"""
        return {}
    
    def set_team_id(self, team_id: Optional[str]):
        """Set the team ID for real data loading"""
        self.team_id = team_id
        logger.debug(f"🏆 Set team ID for scenario {self.scenario_name}: {team_id}")
    
    def get_team_id(self) -> Optional[str]:
        """Get the current team ID"""
        return self.team_id
    
    # Common utility methods
    
    async def run_full_scenario(self) -> TestResult:
        """
        Run the complete scenario lifecycle with error handling and logging.
        
        Returns:
            Complete test result
        """
        logger.info(f"🚀 Starting full scenario run: {self.scenario_name}")
        
        self.start_time = datetime.now(timezone.utc)
        self.current_status = TestStatus.SETUP
        
        try:
            # Load REAL test data from Firestore
            test_data = await self.test_data_manager.load_scenario_data(self.scenario_name)
            self.timeout_seconds = test_data.get("timeout_seconds", self.get_default_timeout())
            
            # Run with timeout
            result = await asyncio.wait_for(
                self._run_scenario_phases(test_data),
                timeout=self.timeout_seconds
            )
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ Scenario timeout after {self.timeout_seconds}s: {self.scenario_name}")
            return self._create_timeout_result()
            
        except Exception as e:
            logger.error(f"❌ Critical error in scenario {self.scenario_name}: {e}")
            return self._create_error_result(str(e))
        
        finally:
            self.end_time = datetime.now(timezone.utc)
            logger.info(
                f"🏁 Scenario completed: {self.scenario_name} | "
                f"Status: {self.current_status.value} | "
                f"Duration: {(self.end_time - self.start_time).total_seconds():.2f}s"
            )
    
    async def _run_scenario_phases(self, test_data: Dict[str, Any]) -> TestResult:
        """Run all scenario phases in sequence"""
        
        # Phase 1: Setup
        logger.info(f"🔧 Setup phase: {self.scenario_name}")
        self.current_status = TestStatus.SETUP
        self._log_phase("setup", "starting")
        
        try:
            setup_context = await self.setup()
            self.test_context.update(setup_context)
            self._log_phase("setup", "completed", {"context_keys": list(setup_context.keys())})
        except Exception as e:
            logger.error(f"❌ Setup failed for {self.scenario_name}: {e}")
            self._log_phase("setup", "failed", {"error": str(e)})
            raise
        
        # Phase 2: Execute
        logger.info(f"⚡ Execute phase: {self.scenario_name}")
        self.current_status = TestStatus.EXECUTING
        self._log_phase("execute", "starting")
        
        try:
            execution_result = await self.execute()
            self._log_phase("execute", "completed", {
                "status": execution_result.status.value,
                "details_keys": list(execution_result.details.keys()) if execution_result.details else []
            })
        except Exception as e:
            logger.error(f"❌ Execution failed for {self.scenario_name}: {e}")
            self._log_phase("execute", "failed", {"error": str(e)})
            raise
        
        # Phase 3: Validate
        logger.info(f"✅ Validate phase: {self.scenario_name}")
        self.current_status = TestStatus.VALIDATING
        self._log_phase("validate", "starting")
        
        try:
            validation_results = await self.validate(execution_result)
            execution_result.validation_results = validation_results
            self._log_phase("validate", "completed", {
                "validation_keys": list(validation_results.keys())
            })
        except Exception as e:
            logger.error(f"❌ Validation failed for {self.scenario_name}: {e}")
            self._log_phase("validate", "failed", {"error": str(e)})
            # Continue to cleanup even if validation fails
            execution_result.validation_results = {"error": str(e)}
        
        # Phase 4: Cleanup
        logger.info(f"🧹 Cleanup phase: {self.scenario_name}")
        self.current_status = TestStatus.CLEANING_UP
        self._log_phase("cleanup", "starting")
        
        try:
            await self.cleanup(self.test_context)
            self._log_phase("cleanup", "completed")
            self.current_status = TestStatus.COMPLETED
        except Exception as e:
            logger.error(f"❌ Cleanup failed for {self.scenario_name}: {e}")
            self._log_phase("cleanup", "failed", {"error": str(e)})
            # Don't fail the entire test due to cleanup issues
            execution_result.cleanup_results = {"error": str(e)}
        
        return execution_result
    
    def _log_phase(self, phase: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Log phase execution with structured data"""
        log_entry = {
            "scenario": self.scenario_name,
            "scenario_id": self.scenario_id,
            "phase": phase,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {}
        }
        
        self.execution_log.append(log_entry)
        
        logger.debug(f"📝 Phase log: {phase} - {status}", extra=log_entry)
    
    def _create_timeout_result(self) -> TestResult:
        """Create a timeout test result"""
        end_time = datetime.now(timezone.utc)
        return TestResult(
            scenario_name=self.scenario_name,
            status=TestStatus.TIMEOUT,
            start_time=self.start_time or end_time,
            end_time=end_time,
            error_message=f"Scenario timed out after {self.timeout_seconds} seconds",
            details={"execution_log": self.execution_log}
        )
    
    def _create_error_result(self, error_message: str) -> TestResult:
        """Create an error test result"""
        end_time = datetime.now(timezone.utc)
        return TestResult(
            scenario_name=self.scenario_name,
            status=TestStatus.FAILED,
            start_time=self.start_time or end_time,
            end_time=end_time,
            error_message=error_message,
            details={"execution_log": self.execution_log}
        )
    
    # Mock service helper methods
    
    async def send_mock_message(self, 
                               user_id: int, 
                               chat_id: int, 
                               text: str, 
                               timeout: float = 10.0) -> Dict[str, Any]:
        """
        Send a message through the mock service with error handling.
        
        Args:
            user_id: ID of the user sending the message
            chat_id: ID of the chat to send to
            text: Message text
            timeout: Timeout for the operation
            
        Returns:
            Message response dictionary
        """
        logger.debug(f"📤 Sending mock message: {user_id} -> {chat_id}: {text[:50]}...")
        
        try:
            from ..backend.mock_telegram_service import SendMessageRequest
            
            request = SendMessageRequest(
                user_id=user_id,
                chat_id=chat_id,
                text=text
            )
            
            # Send message with timeout
            message = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, self.mock_service.send_message, request
                ),
                timeout=timeout
            )
            
            logger.debug(f"✅ Message sent successfully: {message.message_id}")
            return message.to_dict()
            
        except Exception as e:
            logger.error(f"❌ Error sending mock message: {e}")
            raise
    
    async def wait_for_bot_response(self, 
                                   timeout: float = 10.0, 
                                   expected_keywords: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Wait for bot response with optional keyword matching.
        
        Args:
            timeout: Timeout for waiting
            expected_keywords: Optional keywords to look for in response
            
        Returns:
            Bot response dictionary or None if timeout
        """
        logger.debug(f"⏳ Waiting for bot response (timeout: {timeout}s)")
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                # Check for recent bot responses
                # This would integrate with WebSocket or polling mechanism
                # For now, simulate with delay
                await asyncio.sleep(0.5)
                
                # Placeholder for actual bot response checking
                # In real implementation, this would check for recent bot messages
                
            except Exception as e:
                logger.debug(f"Error while waiting for bot response: {e}")
        
        logger.warning(f"⏰ Bot response timeout after {timeout}s")
        return None
    
    async def simulate_user_join(self, 
                                user_id: int, 
                                chat_id: int, 
                                invitation_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Simulate a user joining a chat via invite link.
        
        Args:
            user_id: ID of the user joining
            chat_id: ID of the chat being joined
            invitation_context: Optional invitation context data
            
        Returns:
            True if join simulation succeeded, False otherwise
        """
        logger.debug(f"👥 Simulating user join: {user_id} -> {chat_id}")
        
        try:
            # Create new_chat_members event simulation
            event_data = {
                "message_id": int(datetime.now().timestamp()),
                "from": {
                    "id": user_id,
                    "is_bot": False
                },
                "chat": {
                    "id": chat_id,
                    "type": "group"
                },
                "date": int(datetime.now().timestamp()),
                "new_chat_members": [
                    {
                        "id": user_id,
                        "is_bot": False
                    }
                ]
            }
            
            # Add invitation context if provided
            if invitation_context:
                event_data["invitation_context"] = invitation_context
            
            # Process through bot integration
            if hasattr(self.bot_integration, 'process_mock_message'):
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self.bot_integration.process_mock_message, event_data
                )
                logger.debug(f"✅ User join simulation completed: {response}")
                return True
            else:
                logger.warning("⚠️ Bot integration not available for user join simulation")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error simulating user join: {e}")
            return False
    
    # Validation helper methods
    
    def check_response_contains_keywords(self, 
                                       response: str, 
                                       keywords: List[str], 
                                       case_sensitive: bool = False) -> bool:
        """
        Check if response contains expected keywords.
        
        Args:
            response: Response text to check
            keywords: List of keywords to look for
            case_sensitive: Whether to do case-sensitive matching
            
        Returns:
            True if all keywords found, False otherwise
        """
        if not case_sensitive:
            response = response.lower()
            keywords = [k.lower() for k in keywords]
        
        found_keywords = [kw for kw in keywords if kw in response]
        
        logger.debug(f"🔍 Keyword check: {len(found_keywords)}/{len(keywords)} found")
        
        return len(found_keywords) == len(keywords)
    
    def extract_invite_link_from_response(self, response: str) -> Optional[str]:
        """
        Extract invite link from bot response.
        
        Args:
            response: Bot response text
            
        Returns:
            Extracted invite link or None if not found
        """
        import re
        
        # Look for Telegram invite links
        telegram_pattern = r'https?://t\.me/[^\s]+'
        match = re.search(telegram_pattern, response)
        if match:
            return match.group()
        
        # Look for mock invite links
        mock_pattern = r'http://localhost:8001/\?[^\s]+'
        match = re.search(mock_pattern, response)
        if match:
            return match.group()
        
        logger.debug("🔍 No invite link found in response")
        return None
    
    def extract_player_id_from_response(self, response: str) -> Optional[str]:
        """
        Extract player ID from bot response.
        
        Args:
            response: Bot response text
            
        Returns:
            Extracted player ID or None if not found
        """
        import re
        
        # Look for player ID pattern (e.g., "Player ID: ABC123")
        patterns = [
            r'Player ID[:\s]+([A-Z0-9_]+)',
            r'ID[:\s]+([A-Z0-9_]+)',
            r'created with ID[:\s]+([A-Z0-9_]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                player_id = match.group(1)
                logger.debug(f"🔍 Found player ID: {player_id}")
                return player_id
        
        logger.debug("🔍 No player ID found in response")
        return None
    
    # Test context management
    
    def add_to_test_context(self, key: str, value: Any):
        """Add data to test context"""
        self.test_context[key] = value
        logger.debug(f"📝 Added to test context: {key}")
    
    def get_from_test_context(self, key: str, default: Any = None) -> Any:
        """Get data from test context"""
        return self.test_context.get(key, default)
    
    def update_test_context(self, data: Dict[str, Any]):
        """Update test context with multiple values"""
        self.test_context.update(data)
        logger.debug(f"📝 Updated test context with {len(data)} items")
    
    # Retry mechanism
    
    async def retry_operation(self, 
                            operation, 
                            *args, 
                            max_attempts: Optional[int] = None, 
                            delay_seconds: Optional[float] = None,
                            **kwargs) -> Any:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: Async function to retry
            *args: Arguments for the operation
            max_attempts: Maximum retry attempts (uses instance default if None)
            delay_seconds: Delay between retries (uses instance default if None)
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: Last exception if all retries fail
        """
        max_attempts = max_attempts or self.retry_attempts
        delay_seconds = delay_seconds or self.retry_delay_seconds
        
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                logger.debug(f"🔄 Retry attempt {attempt + 1}/{max_attempts}")
                result = await operation(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"✅ Operation succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                logger.debug(f"⚠️ Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_attempts - 1:
                    wait_time = delay_seconds * (2 ** attempt)  # Exponential backoff
                    logger.debug(f"⏳ Waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
        
        logger.error(f"❌ All {max_attempts} attempts failed")
        raise last_exception
    
    # Timing utilities
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since scenario start"""
        if not self.start_time:
            return 0.0
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()
    
    def get_remaining_time(self) -> float:
        """Get remaining time before timeout"""
        elapsed = self.get_elapsed_time()
        return max(0.0, self.timeout_seconds - elapsed)
    
    def is_timeout_approaching(self, buffer_seconds: float = 10.0) -> bool:
        """Check if timeout is approaching within buffer"""
        return self.get_remaining_time() <= buffer_seconds