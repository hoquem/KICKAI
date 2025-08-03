"""
Player Registration Scenario

Tests the complete player onboarding flow from invite link creation to player registration.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from loguru import logger

from ..base_scenario import BaseScenario, TestResult, TestStatus


class PlayerRegistrationScenario(BaseScenario):
    """
    Player Registration Flow Test Scenario.
    
    Tests the complete player onboarding workflow:
    1. Leadership user creates invite link via /addplayer command
    2. System generates secure invite link and stores player record
    3. Player uses invite link to join chat
    4. System processes new_chat_members event with invite validation
    5. Player is automatically linked to existing record via phone number
    6. Welcome message is sent to player
    
    Expected Duration: ~60 seconds
    Success Criteria:
    - ✅ Invite link created and returned
    - ✅ Player record created in database
    - ✅ Telegram user linked to player record
    - ✅ Welcome message sent to player
    """
    
    def get_default_timeout(self) -> int:
        """Player registration should complete within 60 seconds"""
        return 60
    
    def get_expected_outcomes(self) -> Dict[str, Any]:
        """Define expected outcomes for player registration"""
        return {
            "invite_link_created": True,
            "player_record_created": True,
            "telegram_link_established": True,
            "welcome_message_sent": True
        }
    
    def get_validation_criteria(self) -> Dict[str, Any]:
        """Define validation criteria for player registration"""
        return {
            "response_time_max_seconds": 10,
            "required_response_keywords": ["welcome", "player"],
            "invite_link_format_valid": True,
            "player_id_format_valid": True
        }
    
    async def setup(self) -> Dict[str, Any]:
        """
        Set up the player registration test environment.
        
        Returns:
            Setup context with test fixtures and data
        """
        logger.info("🔧 Setting up player registration test environment")
        
        try:
            # Load REAL scenario test data from Firestore
            test_data = await self.test_data_manager.load_scenario_data("player_registration")
            
            # Validate prerequisites with real data
            if not await self.test_data_manager.validate_prerequisites("player_registration", test_data):
                raise ValueError("Prerequisites validation failed for player registration scenario with REAL data")
            
            # Create test fixtures with real data
            fixtures = await self.test_data_manager.create_test_fixtures("player_registration", test_data)
            
            # Extract key data (now with real Firestore structure)
            team_data = test_data["team_data"]
            leadership_user = test_data["leadership_user"]
            test_player = test_data["test_player"]
            test_chat = test_data["test_chat"]
            
            logger.info(f"🔥 Using REAL team data: {team_data['team_name']} (ID: {team_data['team_id']})")
            logger.info(f"👤 Using REAL leadership user: {leadership_user['first_name']} {leadership_user['last_name']} (ID: {leadership_user['id']})")
            
            # Verify REAL leadership user exists in mock service (create mock representation)
            leadership_telegram_id = leadership_user["id"]
            if leadership_telegram_id not in self.mock_service.users:
                logger.info(f"📝 Creating mock representation of REAL leadership user: {leadership_user['first_name']}")
                # Create mock representation of real leadership user
                from ...backend.mock_telegram_service import CreateUserRequest, UserRole
                
                create_request = CreateUserRequest(
                    user_id=leadership_telegram_id,  # Use real telegram ID
                    username=leadership_user["username"],
                    first_name=leadership_user["first_name"],
                    last_name=leadership_user.get("last_name", ""),
                    role=UserRole.LEADERSHIP,
                    phone_number=leadership_user.get("phone_number")
                )
                
                self.mock_service.create_user(create_request)
                logger.success(f"✅ Created mock representation of REAL leadership user: {leadership_user['username']}")
            
            # Verify REAL leadership chat exists (create mock representation)
            leadership_chat_id = test_chat["leadership_chat_id"]
            main_chat_id = test_chat["main_chat_id"]
            
            if leadership_chat_id not in self.mock_service.chats:
                logger.info(f"📝 Creating mock representation of REAL leadership chat: {leadership_chat_id}")
                # Create mock representation of real leadership chat
                from ...backend.mock_telegram_service import CreateChatRequest, ChatType
                
                create_chat_request = CreateChatRequest(
                    chat_id=leadership_chat_id,  # Use real chat ID
                    title=f"{team_data['team_name']} Leadership Chat",
                    chat_type=ChatType.GROUP,
                    is_leadership_chat=True
                )
                
                self.mock_service.create_chat(create_chat_request)
                logger.success(f"✅ Created mock representation of REAL leadership chat: {leadership_chat_id}")
                
            # Also ensure main chat exists
            if main_chat_id not in self.mock_service.chats:
                logger.info(f"📝 Creating mock representation of REAL main chat: {main_chat_id}")
                
                create_main_chat_request = CreateChatRequest(
                    chat_id=main_chat_id,  # Use real chat ID
                    title=f"{team_data['team_name']} Main Chat",
                    chat_type=ChatType.GROUP,
                    is_leadership_chat=False
                )
                
                self.mock_service.create_chat(create_main_chat_request)
                logger.success(f"✅ Created mock representation of REAL main chat: {main_chat_id}")
            
            # Prepare test context with REAL data
            setup_context = {
                "test_data": test_data,
                "fixtures": fixtures,
                "team_data": team_data,
                "leadership_user": leadership_user,
                "test_player": test_player,
                "test_chat": test_chat,
                "leadership_chat_id": leadership_chat_id,
                "main_chat_id": main_chat_id,
                "existing_players_count": test_data.get("existing_players_count", 0),
                "setup_timestamp": datetime.now(timezone.utc).isoformat(),
                "is_real_data": True,
                "scenario_type": "player_registration"
            }
            
            logger.success(f"✅ Player registration test environment setup completed with REAL data for team: {team_data['team_name']}")
            return setup_context
            
        except Exception as e:
            logger.error(f"❌ Error setting up player registration test with REAL data: {e}")
            raise
    
    async def execute(self) -> TestResult:
        """
        Execute the player registration test scenario.
        
        Returns:
            TestResult with execution details and outcomes
        """
        logger.info("⚡ Executing player registration scenario")
        
        start_time = datetime.now(timezone.utc)
        execution_details = {
            "steps_completed": [],
            "responses": [],
            "timings": {},
            "errors": []
        }
        
        try:
            # Get test data from context
            leadership_user = self.get_from_test_context("leadership_user")
            test_player = self.get_from_test_context("test_player")
            leadership_chat_id = self.get_from_test_context("leadership_chat_id")
            main_chat_id = self.get_from_test_context("main_chat_id")
            
            # Step 1: Send /addplayer command as leadership user
            logger.info("📤 Step 1: Sending /addplayer command")
            step_start = datetime.now(timezone.utc)
            
            addplayer_command = (
                f"/addplayer {test_player['name']} "
                f"{test_player['phone']} {test_player['position']}"
            )
            
            addplayer_response = await self.send_mock_message(
                user_id=leadership_user["id"],
                chat_id=leadership_chat_id,
                text=addplayer_command,
                timeout=15.0
            )
            
            execution_details["steps_completed"].append("addplayer_command_sent")
            execution_details["responses"].append({
                "step": "addplayer_command",
                "response": addplayer_response
            })
            execution_details["timings"]["addplayer_command"] = (
                datetime.now(timezone.utc) - step_start
            ).total_seconds()
            
            # Step 2: Wait for bot response with invite link
            logger.info("⏳ Step 2: Waiting for bot response with invite link")
            step_start = datetime.now(timezone.utc)
            
            # Give bot time to process the command
            await asyncio.sleep(2)
            
            # Check recent messages for bot response
            recent_messages = self.mock_service.get_chat_messages(leadership_chat_id, limit=5)
            bot_response = None
            invite_link = None
            player_id = None
            
            for message in reversed(recent_messages):
                message_dict = message.to_dict() if hasattr(message, 'to_dict') else message
                if (message_dict.get("from", {}).get("is_bot", False) and 
                    "invite" in message_dict.get("text", "").lower()):
                    bot_response = message_dict
                    break
            
            if bot_response:
                response_text = bot_response.get("text", "")
                invite_link = self.extract_invite_link_from_response(response_text)
                player_id = self.extract_player_id_from_response(response_text)
                
                execution_details["steps_completed"].append("bot_response_received")
                execution_details["responses"].append({
                    "step": "bot_response",
                    "response": bot_response,
                    "invite_link": invite_link,
                    "player_id": player_id
                })
                
                logger.success(f"✅ Bot response received with invite link: {invite_link}")
            else:
                logger.warning("⚠️ No bot response with invite link found")
                execution_details["errors"].append("No bot response with invite link")
            
            execution_details["timings"]["bot_response"] = (
                datetime.now(timezone.utc) - step_start
            ).total_seconds()
            
            # Step 3: Simulate player joining via invite link
            if invite_link and player_id:
                logger.info("👥 Step 3: Simulating player join via invite link")
                step_start = datetime.now(timezone.utc)
                
                # Create test user for the player
                test_user_id = 9999  # Temporary user ID for testing
                
                # Simulate joining the main chat with invitation context
                invitation_context = {
                    "invite_link": invite_link,
                    "player_id": player_id,
                    "player_phone": test_player["phone"],
                    "join_method": "invite_link"
                }
                
                join_success = await self.simulate_user_join(
                    user_id=test_user_id,
                    chat_id=main_chat_id,
                    invitation_context=invitation_context
                )
                
                if join_success:
                    execution_details["steps_completed"].append("player_join_simulated")
                    logger.success("✅ Player join simulation completed")
                else:
                    execution_details["errors"].append("Player join simulation failed")
                    logger.warning("⚠️ Player join simulation failed")
                
                execution_details["timings"]["player_join"] = (
                    datetime.now(timezone.utc) - step_start
                ).total_seconds()
                
                # Step 4: Wait for welcome message
                logger.info("⏳ Step 4: Waiting for welcome message")
                step_start = datetime.now(timezone.utc)
                
                await asyncio.sleep(3)  # Give bot time to process join
                
                # Check for welcome message in main chat
                main_chat_messages = self.mock_service.get_chat_messages(main_chat_id, limit=5)
                welcome_message = None
                
                for message in reversed(main_chat_messages):
                    message_dict = message.to_dict() if hasattr(message, 'to_dict') else message
                    message_text = message_dict.get("text", "").lower()
                    
                    if (message_dict.get("from", {}).get("is_bot", False) and 
                        ("welcome" in message_text or "joined" in message_text)):
                        welcome_message = message_dict
                        break
                
                if welcome_message:
                    execution_details["steps_completed"].append("welcome_message_received")
                    execution_details["responses"].append({
                        "step": "welcome_message",
                        "response": welcome_message
                    })
                    logger.success("✅ Welcome message received")
                else:
                    logger.warning("⚠️ No welcome message found")
                    execution_details["errors"].append("No welcome message received")
                
                execution_details["timings"]["welcome_message"] = (
                    datetime.now(timezone.utc) - step_start
                ).total_seconds()
            
            else:
                logger.error("❌ Cannot proceed without invite link and player ID")
                execution_details["errors"].append("Missing invite link or player ID")
            
            # Determine overall status
            end_time = datetime.now(timezone.utc)
            
            if len(execution_details["errors"]) == 0:
                status = TestStatus.COMPLETED
                logger.success("✅ Player registration scenario completed successfully")
            elif len(execution_details["steps_completed"]) >= 2:
                status = TestStatus.COMPLETED  # Partial success is still considered completion
                logger.warning("⚠️ Player registration completed with some issues")
            else:
                status = TestStatus.FAILED
                logger.error("❌ Player registration scenario failed")
            
            # Add summary data
            execution_details.update({
                "invite_link": invite_link,
                "player_id": player_id,
                "total_steps": len(execution_details["steps_completed"]),
                "total_errors": len(execution_details["errors"]),
                "success_rate": (
                    len(execution_details["steps_completed"]) / 4 * 100  # 4 expected steps
                )
            })
            
            return TestResult(
                scenario_name=self.scenario_name,
                status=status,
                start_time=start_time,
                end_time=end_time,
                details=execution_details
            )
            
        except Exception as e:
            logger.error(f"❌ Critical error during player registration execution: {e}")
            execution_details["errors"].append(f"Critical error: {str(e)}")
            
            return TestResult(
                scenario_name=self.scenario_name,
                status=TestStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(timezone.utc),
                details=execution_details,
                error_message=str(e)
            )
    
    async def validate(self, execution_result: TestResult) -> Dict[str, Any]:
        """
        Validate the player registration test results.
        
        Args:
            execution_result: Result from execute() method
            
        Returns:
            Validation results dictionary
        """
        logger.info("✅ Validating player registration results")
        
        try:
            # Get expected outcomes and validation criteria
            expected_outcomes = self.get_expected_outcomes()
            validation_criteria = self.get_validation_criteria()
            
            # Run validation engine
            validation_suite = self.validation_engine.validate_scenario_outcome(
                scenario="player_registration",
                result=execution_result,
                expected_data={
                    "expected_outcomes": expected_outcomes,
                    "validation_criteria": validation_criteria
                }
            )
            
            # Additional specific validations
            execution_details = execution_result.details or {}
            
            # Validate invite link format
            invite_link = execution_details.get("invite_link")
            invite_link_valid = self._validate_invite_link_format(invite_link)
            
            # Validate player ID format
            player_id = execution_details.get("player_id")
            player_id_valid = self._validate_player_id_format(player_id)
            
            # Validate response times
            timings = execution_details.get("timings", {})
            response_times_ok = all(
                timing <= validation_criteria["response_time_max_seconds"]
                for timing in timings.values()
            )
            
            # Validate step completion
            steps_completed = execution_details.get("steps_completed", [])
            expected_steps = [
                "addplayer_command_sent",
                "bot_response_received", 
                "player_join_simulated",
                "welcome_message_received"
            ]
            
            all_steps_completed = all(step in steps_completed for step in expected_steps)
            
            # Compile validation results
            validation_results = {
                "validation_suite": validation_suite.to_dict(),
                "invite_link_valid": invite_link_valid,
                "player_id_valid": player_id_valid,
                "response_times_ok": response_times_ok,
                "all_steps_completed": all_steps_completed,
                "steps_completion_rate": len(steps_completed) / len(expected_steps) * 100,
                "overall_success": (
                    validation_suite.all_passed and
                    invite_link_valid and
                    player_id_valid and
                    response_times_ok and
                    all_steps_completed
                ),
                "validation_summary": {
                    "total_checks": validation_suite.total_count + 4,  # +4 for additional checks
                    "passed_checks": validation_suite.passed_count + sum([
                        invite_link_valid,
                        player_id_valid,
                        response_times_ok,
                        all_steps_completed
                    ]),
                    "success_rate": validation_suite.success_rate
                }
            }
            
            if validation_results["overall_success"]:
                logger.success("✅ Player registration validation passed")
            else:
                logger.warning("⚠️ Player registration validation found issues")
                
                # Log specific failures
                if not invite_link_valid:
                    logger.warning(f"⚠️ Invalid invite link format: {invite_link}")
                if not player_id_valid:
                    logger.warning(f"⚠️ Invalid player ID format: {player_id}")
                if not response_times_ok:
                    logger.warning(f"⚠️ Response times exceeded threshold: {timings}")
                if not all_steps_completed:
                    missing_steps = [s for s in expected_steps if s not in steps_completed]
                    logger.warning(f"⚠️ Missing steps: {missing_steps}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Error during player registration validation: {e}")
            return {
                "validation_error": str(e),
                "overall_success": False,
                "error_type": type(e).__name__
            }
    
    async def cleanup(self, test_context: Dict[str, Any]) -> None:
        """
        Clean up player registration test artifacts.
        
        Args:
            test_context: Test context from setup phase
        """
        logger.info("🧹 Cleaning up player registration test artifacts")
        
        try:
            # Prepare cleanup context
            cleanup_context = {
                "scenario_name": "player_registration",
                "test_users": test_context.get("test_users", []),
                "test_chats": test_context.get("test_chats", []),
                "clear_all_messages": True,  # Clear all test messages
                "fixture_id": test_context.get("fixtures", {}).get("fixture_id"),
                "reset_mock_state": True,
                "clear_cache": True,
                "is_test_data": True,
                "database_artifacts": [
                    {
                        "type": "player_record",
                        "identifier": test_context.get("test_player", {}).get("phone")
                    },
                    {
                        "type": "invite_link",
                        "identifier": "player_registration_test"
                    }
                ]
            }
            
            # Run cleanup through cleanup handler
            cleanup_session = await self.cleanup_handler.cleanup_scenario(
                "player_registration",
                cleanup_context
            )
            
            # Add cleanup results to test context
            self.add_to_test_context("cleanup_session", cleanup_session.to_dict())
            
            if cleanup_session.success_rate >= 90:
                logger.success(f"✅ Player registration cleanup completed successfully")
            else:
                logger.warning(
                    f"⚠️ Player registration cleanup completed with issues: "
                    f"{cleanup_session.success_rate:.1f}% success rate"
                )
            
        except Exception as e:
            logger.error(f"❌ Error during player registration cleanup: {e}")
            # Try emergency cleanup
            try:
                await self.cleanup_handler.emergency_cleanup("player_registration")
                logger.warning("🚨 Emergency cleanup completed for player registration")
            except Exception as emergency_error:
                logger.error(f"❌ Emergency cleanup failed: {emergency_error}")
    
    # Helper validation methods
    
    def _validate_invite_link_format(self, invite_link: Optional[str]) -> bool:
        """Validate invite link format"""
        if not invite_link:
            return False
        
        # Check for valid Telegram or mock invite link format
        import re
        
        telegram_pattern = r'https?://t\.me/[^\s]+'
        mock_pattern = r'http://localhost:8001/\?[^\s]+'
        
        return bool(re.match(telegram_pattern, invite_link) or re.match(mock_pattern, invite_link))
    
    def _validate_player_id_format(self, player_id: Optional[str]) -> bool:
        """Validate player ID format"""
        if not player_id:
            return False
        
        # Player ID should be alphanumeric with underscores, at least 3 characters
        import re
        pattern = r'^[A-Z0-9_]{3,}$'
        
        return bool(re.match(pattern, player_id))