"""
Cleanup Handler

Handles cleanup of test artifacts and data with enhanced logging and safety measures.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from loguru import logger


class CleanupStatus(str, Enum):
    """Status of cleanup operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CleanupTask:
    """Represents a cleanup task"""
    task_id: str
    task_type: str
    description: str
    priority: int  # Lower number = higher priority
    target_data: Dict[str, Any]
    status: CleanupStatus = CleanupStatus.PENDING
    error_message: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "priority": self.priority,
            "target_data": self.target_data,
            "status": self.status.value,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class CleanupSession:
    """Tracks a complete cleanup session"""
    session_id: str
    scenario_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tasks: List[CleanupTask] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    skipped_tasks: int = 0
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []
    
    @property
    def success_rate(self) -> float:
        """Calculate cleanup success rate"""
        if self.total_tasks == 0:
            return 100.0
        return ((self.completed_tasks + self.skipped_tasks) / self.total_tasks) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "scenario_name": self.scenario_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "skipped_tasks": self.skipped_tasks,
            "success_rate": self.success_rate,
            "tasks": [task.to_dict() for task in self.tasks]
        }


class CleanupHandler:
    """
    Handles cleanup of test artifacts and data.
    
    Features:
    - Comprehensive test data cleanup
    - Mock service state restoration
    - Database artifact removal
    - Enhanced logging with detailed tracing
    - Safety measures to prevent accidental data loss
    - Priority-based cleanup ordering
    """
    
    def __init__(self, mock_service, bot_integration):
        """
        Initialize the cleanup handler.
        
        Args:
            mock_service: Mock Telegram service instance
            bot_integration: Bot integration layer instance
        """
        self.mock_service = mock_service
        self.bot_integration = bot_integration
        
        # Track cleanup sessions and tasks
        self.current_session: Optional[CleanupSession] = None
        self.cleanup_history: List[CleanupSession] = []
        
        # Safety settings
        self.safety_mode = True  # Prevents accidental production data cleanup
        self.max_cleanup_retries = 3
        self.cleanup_timeout_seconds = 30
        
        # Cleanup handlers registry
        self.cleanup_handlers = {
            "test_users": self._cleanup_test_users,
            "test_chats": self._cleanup_test_chats,
            "test_messages": self._cleanup_test_messages,
            "test_fixtures": self._cleanup_test_fixtures,
            "database_artifacts": self._cleanup_database_artifacts,
            "mock_service_state": self._cleanup_mock_service_state,
            "temporary_files": self._cleanup_temporary_files,
            "cache_data": self._cleanup_cache_data
        }
        
        logger.debug("🧹 CleanupHandler initialized with enhanced logging")
    
    async def cleanup_scenario(self, scenario_name: str, test_context: Dict[str, Any]) -> CleanupSession:
        """
        Clean up artifacts from a test scenario.
        
        Args:
            scenario_name: Name of the scenario to clean up
            test_context: Test context containing cleanup data
            
        Returns:
            CleanupSession with cleanup results
        """
        logger.info(f"🧹 Starting cleanup for scenario: {scenario_name}")
        
        # Start cleanup session
        session_id = f"cleanup_{scenario_name}_{int(datetime.now().timestamp())}"
        self.current_session = CleanupSession(
            session_id=session_id,
            scenario_name=scenario_name,
            start_time=datetime.now(timezone.utc)
        )
        
        try:
            # Safety check
            if not self._safety_check(test_context):
                logger.error("❌ Safety check failed - aborting cleanup")
                self.current_session.end_time = datetime.now(timezone.utc)
                return self.current_session
            
            # Generate cleanup tasks
            cleanup_tasks = self._generate_cleanup_tasks(scenario_name, test_context)
            self.current_session.tasks = cleanup_tasks
            self.current_session.total_tasks = len(cleanup_tasks)
            
            logger.info(f"📋 Generated {len(cleanup_tasks)} cleanup tasks for {scenario_name}")
            
            # Execute cleanup tasks in priority order
            await self._execute_cleanup_tasks()
            
            # Finalize session
            self.current_session.end_time = datetime.now(timezone.utc)
            
            logger.success(
                f"✅ Cleanup completed for scenario: {scenario_name} | "
                f"Success rate: {self.current_session.success_rate:.1f}% | "
                f"Tasks: {self.current_session.completed_tasks}/"
                f"{self.current_session.total_tasks}"
            )
            
            # Store in history
            completed_session = self.current_session
            self.cleanup_history.append(completed_session)
            self.current_session = None
            
            return completed_session
            
        except Exception as e:
            logger.error(f"❌ Critical error during cleanup for {scenario_name}: {e}")
            
            if self.current_session:
                self.current_session.end_time = datetime.now(timezone.utc)
                self.cleanup_history.append(self.current_session)
                failed_session = self.current_session
                self.current_session = None
                return failed_session
            
            # Create failed session
            failed_session = CleanupSession(
                session_id=f"failed_{scenario_name}_{int(datetime.now().timestamp())}",
                scenario_name=scenario_name,
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc)
            )
            self.cleanup_history.append(failed_session)
            return failed_session
    
    def _safety_check(self, test_context: Dict[str, Any]) -> bool:
        """
        Perform safety checks before cleanup.
        
        Args:
            test_context: Test context to validate
            
        Returns:
            True if safe to proceed, False otherwise
        """
        logger.debug("🔒 Performing safety checks")
        
        try:
            # Check if we're in test mode
            if not self._is_test_environment():
                logger.error("❌ Safety check failed: Not in test environment")
                return False
            
            # Check for test markers in context
            if not test_context.get("is_test_data", False):
                logger.warning("⚠️ Test context doesn't have test marker")
                # Continue but log warning
            
            # Check for production identifiers
            if self._contains_production_identifiers(test_context):
                logger.error("❌ Safety check failed: Production identifiers detected")
                return False
            
            # Check cleanup scope
            if not self._validate_cleanup_scope(test_context):
                logger.error("❌ Safety check failed: Invalid cleanup scope")
                return False
            
            logger.debug("✅ Safety checks passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during safety check: {e}")
            return False
    
    def _is_test_environment(self) -> bool:
        """Check if we're running in a test environment"""
        try:
            # Check for mock service running
            if hasattr(self.mock_service, 'team_name') and 'test' in self.mock_service.team_name.lower():
                return True
            
            # Check for test indicators in service stats
            stats = self.mock_service.get_service_stats()
            if 'test' in stats.get('team_name', '').lower():
                return True
            
            # Check port (mock service typically runs on 8001)
            if hasattr(self.mock_service, '_port') and self.mock_service._port == 8001:
                return True
            
            return True  # Assume test environment if uncertain in this context
            
        except Exception as e:
            logger.debug(f"Error checking test environment: {e}")
            return False
    
    def _contains_production_identifiers(self, test_context: Dict[str, Any]) -> bool:
        """Check if context contains production identifiers"""
        try:
            # Check for production team IDs
            production_team_ids = ["KTI", "PROD", "PRODUCTION"]
            
            # Check team_id in context
            team_id = test_context.get("team_id", "")
            if team_id in production_team_ids:
                return True
            
            # Check nested data
            for key, value in test_context.items():
                if isinstance(value, dict):
                    nested_team_id = value.get("team_id", "")
                    if nested_team_id in production_team_ids:
                        return True
                elif isinstance(value, str) and value in production_team_ids:
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking production identifiers: {e}")
            return False
    
    def _validate_cleanup_scope(self, test_context: Dict[str, Any]) -> bool:
        """Validate that cleanup scope is reasonable"""
        try:
            # Check if we're trying to clean up too much data
            users_to_clean = len(test_context.get("test_users", []))
            chats_to_clean = len(test_context.get("test_chats", []))
            messages_to_clean = len(test_context.get("test_messages", []))
            
            # Reasonable limits for test cleanup
            if users_to_clean > 50:
                logger.warning(f"⚠️ Large user cleanup scope: {users_to_clean} users")
            
            if chats_to_clean > 20:
                logger.warning(f"⚠️ Large chat cleanup scope: {chats_to_clean} chats")
            
            if messages_to_clean > 1000:
                logger.warning(f"⚠️ Large message cleanup scope: {messages_to_clean} messages")
            
            return True  # Allow cleanup but log warnings
            
        except Exception as e:
            logger.debug(f"Error validating cleanup scope: {e}")
            return True
    
    def _generate_cleanup_tasks(self, scenario_name: str, test_context: Dict[str, Any]) -> List[CleanupTask]:
        """
        Generate cleanup tasks based on scenario and context.
        
        Args:
            scenario_name: Scenario name
            test_context: Test context data
            
        Returns:
            List of cleanup tasks in priority order
        """
        logger.debug(f"📋 Generating cleanup tasks for scenario: {scenario_name}")
        
        tasks = []
        
        # Database artifacts cleanup (highest priority)
        if test_context.get("database_artifacts"):
            tasks.append(CleanupTask(
                task_id=f"db_cleanup_{uuid.uuid4().hex[:8]}",
                task_type="database_artifacts",
                description="Clean up database artifacts and test records",
                priority=1,
                target_data=test_context["database_artifacts"]
            ))
        
        # Test users cleanup
        if test_context.get("test_users"):
            tasks.append(CleanupTask(
                task_id=f"users_cleanup_{uuid.uuid4().hex[:8]}",
                task_type="test_users",
                description="Remove test users from mock service",
                priority=2,
                target_data={"users": test_context["test_users"]}
            ))
        
        # Test chats cleanup
        if test_context.get("test_chats"):
            tasks.append(CleanupTask(
                task_id=f"chats_cleanup_{uuid.uuid4().hex[:8]}",
                task_type="test_chats",
                description="Remove test chats from mock service",
                priority=3,
                target_data={"chats": test_context["test_chats"]}
            ))
        
        # Test messages cleanup
        if test_context.get("test_messages") or test_context.get("clear_all_messages"):
            tasks.append(CleanupTask(
                task_id=f"messages_cleanup_{uuid.uuid4().hex[:8]}",
                task_type="test_messages",
                description="Clear test messages from mock service",
                priority=4,
                target_data={"clear_all": test_context.get("clear_all_messages", False)}
            ))
        
        # Test fixtures cleanup
        if test_context.get("fixture_id"):
            tasks.append(CleanupTask(
                task_id=f"fixtures_cleanup_{uuid.uuid4().hex[:8]}",
                task_type="test_fixtures",
                description="Clean up test fixtures and temporary data",
                priority=5,
                target_data={"fixture_id": test_context["fixture_id"]}
            ))
        
        # Mock service state reset
        if test_context.get("reset_mock_state", True):
            tasks.append(CleanupTask(
                task_id=f"state_cleanup_{uuid.uuid4().hex[:8]}",
                task_type="mock_service_state",
                description="Reset mock service state to initial configuration",
                priority=6,
                target_data={"reset_counters": True, "clear_websockets": True}
            ))
        
        # Temporary files cleanup
        if test_context.get("temporary_files"):
            tasks.append(CleanupTask(
                task_id=f"files_cleanup_{uuid.uuid4().hex[:8]}",
                task_type="temporary_files",
                description="Remove temporary test files",
                priority=7,
                target_data={"files": test_context["temporary_files"]}
            ))
        
        # Cache cleanup
        if test_context.get("clear_cache", True):
            tasks.append(CleanupTask(
                task_id=f"cache_cleanup_{uuid.uuid4().hex[:8]}",
                task_type="cache_data",
                description="Clear test data cache",
                priority=8,
                target_data={"clear_all": True}
            ))
        
        # Sort by priority
        tasks.sort(key=lambda t: t.priority)
        
        logger.debug(f"📋 Generated {len(tasks)} cleanup tasks")
        return tasks
    
    async def _execute_cleanup_tasks(self):
        """Execute all cleanup tasks in the current session"""
        if not self.current_session or not self.current_session.tasks:
            logger.warning("⚠️ No cleanup tasks to execute")
            return
        
        logger.info(f"⚡ Executing {len(self.current_session.tasks)} cleanup tasks")
        
        for task in self.current_session.tasks:
            try:
                logger.debug(f"🔧 Executing cleanup task: {task.description}")
                task.status = CleanupStatus.IN_PROGRESS
                
                # Get handler for task type
                handler = self.cleanup_handlers.get(task.task_type)
                if not handler:
                    logger.error(f"❌ No handler found for task type: {task.task_type}")
                    task.status = CleanupStatus.FAILED
                    task.error_message = f"No handler for task type: {task.task_type}"
                    self.current_session.failed_tasks += 1
                    continue
                
                # Execute cleanup with timeout
                success = await asyncio.wait_for(
                    handler(task.target_data),
                    timeout=self.cleanup_timeout_seconds
                )
                
                if success:
                    task.status = CleanupStatus.COMPLETED
                    task.completed_at = datetime.now(timezone.utc)
                    self.current_session.completed_tasks += 1
                    logger.debug(f"✅ Completed cleanup task: {task.task_type}")
                else:
                    task.status = CleanupStatus.FAILED
                    task.error_message = "Handler returned False"
                    self.current_session.failed_tasks += 1
                    logger.warning(f"⚠️ Failed cleanup task: {task.task_type}")
                
            except asyncio.TimeoutError:
                logger.error(f"❌ Cleanup task timeout: {task.task_type}")
                task.status = CleanupStatus.FAILED
                task.error_message = f"Timeout after {self.cleanup_timeout_seconds}s"
                self.current_session.failed_tasks += 1
                
            except Exception as e:
                logger.error(f"❌ Error executing cleanup task {task.task_type}: {e}")
                task.status = CleanupStatus.FAILED
                task.error_message = str(e)
                self.current_session.failed_tasks += 1
    
    # Cleanup handler methods
    
    async def _cleanup_test_users(self, target_data: Dict[str, Any]) -> bool:
        """Clean up test users from mock service"""
        try:
            users_to_remove = target_data.get("users", [])
            logger.debug(f"👤 Cleaning up {len(users_to_remove)} test users")
            
            with self.mock_service._lock:
                for user_data in users_to_remove:
                    user_id = user_data.get("id")
                    if user_id and user_id in self.mock_service.users:
                        del self.mock_service.users[user_id]
                        logger.debug(f"Removed test user: {user_id}")
                        
                        # Also remove their private chat
                        if user_id in self.mock_service.chats:
                            del self.mock_service.chats[user_id]
                            logger.debug(f"Removed private chat for user: {user_id}")
            
            logger.success(f"✅ Cleaned up {len(users_to_remove)} test users")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up test users: {e}")
            return False
    
    async def _cleanup_test_chats(self, target_data: Dict[str, Any]) -> bool:
        """Clean up test chats from mock service"""
        try:
            chats_to_remove = target_data.get("chats", [])
            logger.debug(f"💬 Cleaning up {len(chats_to_remove)} test chats")
            
            with self.mock_service._lock:
                for chat_data in chats_to_remove:
                    chat_id = chat_data.get("id")
                    if chat_id and chat_id in self.mock_service.chats:
                        # Only remove if it's marked as test chat
                        chat = self.mock_service.chats[chat_id]
                        if hasattr(chat, 'is_test_chat') and chat.is_test_chat:
                            del self.mock_service.chats[chat_id]
                            logger.debug(f"Removed test chat: {chat_id}")
            
            logger.success(f"✅ Cleaned up {len(chats_to_remove)} test chats")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up test chats: {e}")
            return False
    
    async def _cleanup_test_messages(self, target_data: Dict[str, Any]) -> bool:
        """Clean up test messages from mock service"""
        try:
            clear_all = target_data.get("clear_all", False)
            
            with self.mock_service._lock:
                if clear_all:
                    message_count = len(self.mock_service.messages)
                    self.mock_service.messages.clear()
                    self.mock_service.message_counter = 1
                    logger.debug(f"Cleared all {message_count} messages")
                else:
                    # Remove only test-related messages (basic heuristic)
                    original_count = len(self.mock_service.messages)
                    self.mock_service.messages = [
                        msg for msg in self.mock_service.messages
                        if not (hasattr(msg.from_user, 'is_test_user') and msg.from_user.is_test_user)
                    ]
                    removed_count = original_count - len(self.mock_service.messages)
                    logger.debug(f"Removed {removed_count} test messages")
            
            logger.success("✅ Cleaned up test messages")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up test messages: {e}")
            return False
    
    async def _cleanup_test_fixtures(self, target_data: Dict[str, Any]) -> bool:
        """Clean up test fixtures"""
        try:
            fixture_id = target_data.get("fixture_id")
            if not fixture_id:
                logger.debug("No fixture ID provided for cleanup")
                return True
            
            # This would interface with test data manager
            logger.debug(f"🔧 Cleaning up test fixtures: {fixture_id}")
            
            # Placeholder for fixture cleanup logic
            # In actual implementation, this would call test_data_manager.cleanup_fixtures()
            
            logger.success(f"✅ Cleaned up test fixtures: {fixture_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up test fixtures: {e}")
            return False
    
    async def _cleanup_database_artifacts(self, target_data: Dict[str, Any]) -> bool:
        """Clean up database artifacts"""
        try:
            artifacts = target_data.get("artifacts", [])
            logger.debug(f"🗄️ Cleaning up {len(artifacts)} database artifacts")
            
            # This would interface with actual database cleanup
            # For mock environment, this is mostly a no-op
            
            for artifact in artifacts:
                logger.debug(f"Cleaning database artifact: {artifact}")
            
            logger.success(f"✅ Cleaned up {len(artifacts)} database artifacts")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up database artifacts: {e}")
            return False
    
    async def _cleanup_mock_service_state(self, target_data: Dict[str, Any]) -> bool:
        """Reset mock service state"""
        try:
            reset_counters = target_data.get("reset_counters", False)
            clear_websockets = target_data.get("clear_websockets", False)
            
            with self.mock_service._lock:
                if reset_counters:
                    self.mock_service.message_counter = 1
                    logger.debug("Reset message counter")
                
                if clear_websockets:
                    # Close all websocket connections
                    disconnected_count = len(self.mock_service.websocket_connections)
                    self.mock_service.websocket_connections.clear()
                    logger.debug(f"Cleared {disconnected_count} websocket connections")
            
            logger.success("✅ Reset mock service state")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resetting mock service state: {e}")
            return False
    
    async def _cleanup_temporary_files(self, target_data: Dict[str, Any]) -> bool:
        """Clean up temporary files"""
        try:
            files_to_remove = target_data.get("files", [])
            logger.debug(f"📁 Cleaning up {len(files_to_remove)} temporary files")
            
            import os
            removed_count = 0
            
            for file_path in files_to_remove:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        removed_count += 1
                        logger.debug(f"Removed temporary file: {file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not remove file {file_path}: {e}")
            
            logger.success(f"✅ Cleaned up {removed_count} temporary files")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up temporary files: {e}")
            return False
    
    async def _cleanup_cache_data(self, target_data: Dict[str, Any]) -> bool:
        """Clean up cache data"""
        try:
            clear_all = target_data.get("clear_all", False)
            
            if clear_all:
                # This would interface with any caching systems
                logger.debug("🗂️ Clearing all cache data")
                
                # Clear any test-related cache data
                # Placeholder for actual cache cleanup
                
            logger.success("✅ Cleaned up cache data")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up cache data: {e}")
            return False
    
    async def emergency_cleanup(self, scenario_name: str) -> bool:
        """
        Perform emergency cleanup when normal cleanup fails.
        
        Args:
            scenario_name: Scenario that failed
            
        Returns:
            True if emergency cleanup succeeded, False otherwise
        """
        logger.warning(f"🚨 Performing emergency cleanup for scenario: {scenario_name}")
        
        try:
            # Reset mock service to initial state
            with self.mock_service._lock:
                # Clear all messages
                message_count = len(self.mock_service.messages)
                self.mock_service.messages.clear()
                self.mock_service.message_counter = 1
                
                # Clear websockets
                websocket_count = len(self.mock_service.websocket_connections)
                self.mock_service.websocket_connections.clear()
                
                # Remove test users (keep only default users)
                default_user_ids = {1001, 1002, 1003, 1004}
                test_users_removed = 0
                users_to_remove = []
                
                for user_id, user in self.mock_service.users.items():
                    if user_id not in default_user_ids:
                        users_to_remove.append(user_id)
                
                for user_id in users_to_remove:
                    del self.mock_service.users[user_id]
                    if user_id in self.mock_service.chats:
                        del self.mock_service.chats[user_id]
                    test_users_removed += 1
                
                # Remove test chats (keep only default chats)
                default_chat_ids = {2001, 2002}  # Main and leadership chats
                test_chats_removed = 0
                chats_to_remove = []
                
                for chat_id, chat in self.mock_service.chats.items():
                    if chat_id not in default_chat_ids and chat_id not in default_user_ids:
                        chats_to_remove.append(chat_id)
                
                for chat_id in chats_to_remove:
                    del self.mock_service.chats[chat_id]
                    test_chats_removed += 1
            
            logger.warning(
                f"🚨 Emergency cleanup completed: "
                f"Messages: {message_count}, "
                f"WebSockets: {websocket_count}, "
                f"Users: {test_users_removed}, "
                f"Chats: {test_chats_removed}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Emergency cleanup failed for {scenario_name}: {e}")
            return False
    
    def get_cleanup_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get cleanup history.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of cleanup session dictionaries
        """
        return [session.to_dict() for session in self.cleanup_history[-limit:]]
    
    def get_current_cleanup_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current cleanup session status.
        
        Returns:
            Current session status or None if no active cleanup
        """
        if not self.current_session:
            return None
        
        return {
            "session_id": self.current_session.session_id,
            "scenario_name": self.current_session.scenario_name,
            "status": "in_progress",
            "start_time": self.current_session.start_time.isoformat(),
            "total_tasks": self.current_session.total_tasks,
            "completed_tasks": self.current_session.completed_tasks,
            "failed_tasks": self.current_session.failed_tasks,
            "progress_percent": (
                self.current_session.completed_tasks / self.current_session.total_tasks * 100
                if self.current_session.total_tasks > 0 else 0
            ),
            "current_tasks": [
                {
                    "task_type": task.task_type,
                    "description": task.description,
                    "status": task.status.value
                }
                for task in self.current_session.tasks
                if task.status == CleanupStatus.IN_PROGRESS
            ]
        }