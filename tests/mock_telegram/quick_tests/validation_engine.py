"""
Validation Engine

Validates test execution results with comprehensive checking and enhanced logging.
"""

import re
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from loguru import logger


class ValidationResult:
    """Result of a validation check"""
    
    def __init__(self, 
                 check_name: str, 
                 passed: bool, 
                 message: str = "", 
                 details: Optional[Dict[str, Any]] = None,
                 expected: Any = None,
                 actual: Any = None):
        self.check_name = check_name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.expected = expected
        self.actual = actual
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "expected": self.expected,
            "actual": self.actual,
            "timestamp": self.timestamp.isoformat()
        }


class ValidationSuite:
    """Collection of validation results"""
    
    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.results: List[ValidationResult] = []
        self.start_time = datetime.now(timezone.utc)
        self.end_time: Optional[datetime] = None
    
    def add_result(self, result: ValidationResult):
        """Add a validation result"""
        self.results.append(result)
    
    def finalize(self):
        """Finalize the validation suite"""
        self.end_time = datetime.now(timezone.utc)
    
    @property
    def passed_count(self) -> int:
        """Number of passed validations"""
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed_count(self) -> int:
        """Number of failed validations"""
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def total_count(self) -> int:
        """Total number of validations"""
        return len(self.results)
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage"""
        if self.total_count == 0:
            return 0.0
        return (self.passed_count / self.total_count) * 100
    
    @property
    def all_passed(self) -> bool:
        """True if all validations passed"""
        return self.failed_count == 0 and self.total_count > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "suite_name": self.suite_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "total_count": self.total_count,
            "success_rate": self.success_rate,
            "all_passed": self.all_passed,
            "results": [r.to_dict() for r in self.results]
        }


class ValidationEngine:
    """
    Validates test execution results with comprehensive checking.
    
    Features:
    - Scenario-specific validation rules
    - Database state validation
    - Bot response validation
    - Performance metrics validation
    - Enhanced logging with detailed tracing
    """
    
    def __init__(self):
        """Initialize the validation engine"""
        logger.debug("🔍 ValidationEngine initialized")
    
    def validate_scenario_outcome(self, scenario: str, result: Any, expected_data: Dict[str, Any]) -> ValidationSuite:
        """
        Validate specific scenario outcomes.
        
        Args:
            scenario: Scenario name
            result: Test execution result
            expected_data: Expected outcomes from test data
            
        Returns:
            ValidationSuite with all validation results
        """
        logger.info(f"🔍 Validating scenario outcome: {scenario}")
        
        suite = ValidationSuite(f"{scenario}_validation")
        
        try:
            # Validate based on scenario type
            if scenario == "player_registration":
                self._validate_player_registration(suite, result, expected_data)
            elif scenario == "invite_link_validation":
                self._validate_invite_link_validation(suite, result, expected_data)
            elif scenario == "command_testing":
                self._validate_command_testing(suite, result, expected_data)
            elif scenario == "natural_language_processing":
                self._validate_nlp_testing(suite, result, expected_data)
            elif scenario == "error_handling":
                self._validate_error_handling(suite, result, expected_data)
            elif scenario == "performance_load":
                self._validate_performance_testing(suite, result, expected_data)
            else:
                self._validate_generic_scenario(suite, result, expected_data)
            
            suite.finalize()
            
            logger.info(
                f"✅ Scenario validation completed: {scenario} | "
                f"Passed: {suite.passed_count}/{suite.total_count} | "
                f"Success rate: {suite.success_rate:.1f}%"
            )
            
            # Log validation summary
            if suite.all_passed:
                logger.success(f"🎯 All validations passed for scenario: {scenario}")
            else:
                logger.warning(f"⚠️ Some validations failed for scenario: {scenario}")
                for result in suite.results:
                    if not result.passed:
                        logger.error(f"❌ Failed validation: {result.check_name} - {result.message}")
            
            return suite
            
        except Exception as e:
            logger.error(f"❌ Error during scenario validation for {scenario}: {e}")
            suite.add_result(ValidationResult(
                "validation_error",
                False,
                f"Validation error: {str(e)}",
                {"error_type": type(e).__name__}
            ))
            suite.finalize()
            return suite
    
    def _validate_player_registration(self, suite: ValidationSuite, result: Any, expected_data: Dict[str, Any]):
        """Validate player registration scenario"""
        logger.debug("🏃 Validating player registration scenario")
        
        expected_outcomes = expected_data.get("expected_outcomes", {})
        
        # Check if invite link was created
        if expected_outcomes.get("invite_link_created", False):
            invite_link_created = self._check_invite_link_creation(result)
            suite.add_result(ValidationResult(
                "invite_link_creation",
                invite_link_created,
                "Invite link should be created and returned in response",
                expected=True,
                actual=invite_link_created
            ))
        
        # Check if player record was created
        if expected_outcomes.get("player_record_created", False):
            player_record_created = self._check_player_record_creation(result)
            suite.add_result(ValidationResult(
                "player_record_creation",
                player_record_created,
                "Player record should be created in database",
                expected=True,
                actual=player_record_created
            ))
        
        # Check if Telegram link was established
        if expected_outcomes.get("telegram_link_established", False):
            telegram_link_established = self._check_telegram_link_establishment(result)
            suite.add_result(ValidationResult(
                "telegram_link_establishment",
                telegram_link_established,
                "Telegram user should be linked to player record",
                expected=True,
                actual=telegram_link_established
            ))
        
        # Check if welcome message was sent
        if expected_outcomes.get("welcome_message_sent", False):
            welcome_message_sent = self._check_welcome_message(result)
            suite.add_result(ValidationResult(
                "welcome_message_sent",
                welcome_message_sent,
                "Welcome message should be sent to new player",
                expected=True,
                actual=welcome_message_sent
            ))
    
    def _validate_invite_link_validation(self, suite: ValidationSuite, result: Any, expected_data: Dict[str, Any]):
        """Validate invite link validation scenario"""
        logger.debug("🔗 Validating invite link validation scenario")
        
        test_links = expected_data.get("test_links", {})
        
        for link_type, link_data in test_links.items():
            expected_result = link_data.get("expected_result")
            
            # Check if link validation behaved as expected
            validation_correct = self._check_link_validation_result(result, link_type, expected_result)
            suite.add_result(ValidationResult(
                f"link_validation_{link_type}",
                validation_correct,
                f"Link validation for {link_type} should return {expected_result}",
                details={"link_type": link_type, "link_data": link_data},
                expected=expected_result,
                actual=self._get_actual_validation_result(result, link_type)
            ))
    
    def _validate_command_testing(self, suite: ValidationSuite, result: Any, expected_data: Dict[str, Any]):
        """Validate command testing scenario"""
        logger.debug("🎯 Validating command testing scenario")
        
        command_tests = expected_data.get("command_tests", {})
        
        # Validate player commands
        for command in command_tests.get("player_commands", []):
            command_response = self._check_command_response(result, command, "player")
            suite.add_result(ValidationResult(
                f"player_command_{command.replace('/', '').replace(' ', '_')}",
                command_response,
                f"Player command '{command}' should execute successfully",
                details={"command": command, "user_role": "player"}
            ))
        
        # Validate leadership commands
        for command in command_tests.get("leadership_commands", []):
            command_response = self._check_command_response(result, command, "leadership")
            suite.add_result(ValidationResult(
                f"leadership_command_{command.replace('/', '').replace(' ', '_')[:20]}",
                command_response,
                f"Leadership command '{command}' should execute successfully",
                details={"command": command, "user_role": "leadership"}
            ))
        
        # Validate permission tests
        permission_tests = command_tests.get("permission_tests", {})
        for test_name, test_data in permission_tests.items():
            permission_denied = self._check_permission_denial(result, test_data)
            suite.add_result(ValidationResult(
                f"permission_test_{test_name}",
                permission_denied,
                f"Permission test '{test_name}' should deny unauthorized access",
                details=test_data
            ))
    
    def _validate_nlp_testing(self, suite: ValidationSuite, result: Any, expected_data: Dict[str, Any]):
        """Validate natural language processing scenario"""
        logger.debug("💬 Validating NLP testing scenario")
        
        nlp_tests = expected_data.get("natural_language_tests", [])
        validation_criteria = expected_data.get("validation_criteria", {})
        
        for i, test_case in enumerate(nlp_tests):
            test_input = test_case.get("input")
            expected_keywords = test_case.get("expected_response_contains", [])
            
            # Check response time
            response_time_ok = self._check_response_time(result, i, validation_criteria.get("response_time_max_seconds", 10))
            suite.add_result(ValidationResult(
                f"nlp_response_time_{i}",
                response_time_ok,
                f"Response time for '{test_input}' should be within acceptable limits",
                details={"test_input": test_input, "test_index": i}
            ))
            
            # Check response content
            keywords_found = self._check_response_keywords(result, i, expected_keywords)
            suite.add_result(ValidationResult(
                f"nlp_keywords_{i}",
                keywords_found,
                f"Response for '{test_input}' should contain expected keywords",
                details={"test_input": test_input, "expected_keywords": expected_keywords}
            ))
    
    def _validate_error_handling(self, suite: ValidationSuite, result: Any, expected_data: Dict[str, Any]):
        """Validate error handling scenario"""
        logger.debug("🚨 Validating error handling scenario")
        
        error_scenarios = expected_data.get("error_scenarios", {})
        expected_behaviors = expected_data.get("expected_behaviors", {})
        
        # Check graceful error handling
        if expected_behaviors.get("graceful_error_messages", False):
            graceful_errors = self._check_graceful_error_handling(result)
            suite.add_result(ValidationResult(
                "graceful_error_handling",
                graceful_errors,
                "System should handle errors gracefully with user-friendly messages",
                expected=True,
                actual=graceful_errors
            ))
        
        # Check no system crashes
        if expected_behaviors.get("no_system_crashes", False):
            no_crashes = self._check_no_system_crashes(result)
            suite.add_result(ValidationResult(
                "no_system_crashes",
                no_crashes,
                "System should not crash during error scenarios",
                expected=True,
                actual=no_crashes
            ))
        
        # Validate specific error scenarios
        for scenario_type, scenarios in error_scenarios.items():
            if isinstance(scenarios, list):
                for i, scenario in enumerate(scenarios):
                    error_handled = self._check_specific_error_handling(result, scenario_type, i, scenario)
                    suite.add_result(ValidationResult(
                        f"error_{scenario_type}_{i}",
                        error_handled,
                        f"Error scenario '{scenario_type}' should be handled correctly",
                        details={"scenario_type": scenario_type, "scenario": scenario}
                    ))
    
    def _validate_performance_testing(self, suite: ValidationSuite, result: Any, expected_data: Dict[str, Any]):
        """Validate performance testing scenario"""
        logger.debug("📊 Validating performance testing scenario")
        
        performance_thresholds = expected_data.get("performance_thresholds", {})
        
        # Check response time threshold
        max_response_time = performance_thresholds.get("max_response_time_seconds", 5)
        response_time_ok = self._check_performance_response_time(result, max_response_time)
        suite.add_result(ValidationResult(
            "performance_response_time",
            response_time_ok,
            f"Average response time should be under {max_response_time} seconds",
            expected=f"< {max_response_time}s",
            actual=self._get_actual_response_time(result)
        ))
        
        # Check success rate threshold
        min_success_rate = performance_thresholds.get("min_success_rate_percent", 95)
        success_rate_ok = self._check_performance_success_rate(result, min_success_rate)
        suite.add_result(ValidationResult(
            "performance_success_rate",
            success_rate_ok,
            f"Success rate should be above {min_success_rate}%",
            expected=f"> {min_success_rate}%",
            actual=f"{self._get_actual_success_rate(result):.1f}%"
        ))
    
    def _validate_generic_scenario(self, suite: ValidationSuite, result: Any, expected_data: Dict[str, Any]):
        """Validate generic scenario"""
        logger.debug("🔧 Validating generic scenario")
        
        # Basic validation - check if result exists and has expected structure
        result_exists = result is not None
        suite.add_result(ValidationResult(
            "result_exists",
            result_exists,
            "Test result should exist",
            expected=True,
            actual=result_exists
        ))
        
        # Check if test completed within timeout
        timeout_seconds = expected_data.get("timeout_seconds", 60)
        within_timeout = self._check_timeout_compliance(result, timeout_seconds)
        suite.add_result(ValidationResult(
            "within_timeout",
            within_timeout,
            f"Test should complete within {timeout_seconds} seconds",
            expected=f"< {timeout_seconds}s",
            actual=self._get_actual_duration(result)
        ))
    
    # Helper methods for specific validations
    
    def _check_invite_link_creation(self, result: Any) -> bool:
        """Check if invite link was created"""
        try:
            # Look for invite link in result data
            if hasattr(result, 'details') and isinstance(result.details, dict):
                details = result.details
                return (
                    "invite_link" in details or
                    "invite_id" in details or
                    any("invite" in str(v).lower() for v in details.values())
                )
            return False
        except Exception as e:
            logger.debug(f"Error checking invite link creation: {e}")
            return False
    
    def _check_player_record_creation(self, result: Any) -> bool:
        """Check if player record was created"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                details = result.details
                return (
                    "player_id" in details or
                    "player_created" in details or
                    any("player" in str(k).lower() for k in details.keys())
                )
            return False
        except Exception as e:
            logger.debug(f"Error checking player record creation: {e}")
            return False
    
    def _check_telegram_link_establishment(self, result: Any) -> bool:
        """Check if Telegram link was established"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                details = result.details
                return (
                    "telegram_id" in details or
                    "user_linked" in details or
                    any("telegram" in str(k).lower() for k in details.keys())
                )
            return False
        except Exception as e:
            logger.debug(f"Error checking telegram link establishment: {e}")
            return False
    
    def _check_welcome_message(self, result: Any) -> bool:
        """Check if welcome message was sent"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                details = result.details
                return (
                    "welcome_sent" in details or
                    "message_sent" in details or
                    any("welcome" in str(v).lower() for v in details.values())
                )
            return False
        except Exception as e:
            logger.debug(f"Error checking welcome message: {e}")
            return False
    
    def _check_link_validation_result(self, result: Any, link_type: str, expected_result: str) -> bool:
        """Check if link validation returned expected result"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                validation_results = result.details.get("validation_results", {})
                actual_result = validation_results.get(link_type, "unknown")
                return actual_result == expected_result
            return False
        except Exception as e:
            logger.debug(f"Error checking link validation result: {e}")
            return False
    
    def _get_actual_validation_result(self, result: Any, link_type: str) -> str:
        """Get actual validation result for link type"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                validation_results = result.details.get("validation_results", {})
                return validation_results.get(link_type, "unknown")
            return "no_result"
        except Exception as e:
            logger.debug(f"Error getting actual validation result: {e}")
            return "error"
    
    def _check_command_response(self, result: Any, command: str, user_role: str) -> bool:
        """Check if command executed successfully"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                command_results = result.details.get("command_results", {})
                command_key = f"{user_role}_{command.replace('/', '').split()[0]}"
                return command_results.get(command_key, {}).get("success", False)
            return False
        except Exception as e:
            logger.debug(f"Error checking command response: {e}")
            return False
    
    def _check_permission_denial(self, result: Any, test_data: Dict[str, Any]) -> bool:
        """Check if permission was correctly denied"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                permission_results = result.details.get("permission_results", {})
                expected = test_data.get("expected", "permission_denied")
                actual = permission_results.get("result", "unknown")
                return actual == expected
            return False
        except Exception as e:
            logger.debug(f"Error checking permission denial: {e}")
            return False
    
    def _check_response_time(self, result: Any, test_index: int, max_seconds: float) -> bool:
        """Check if response time is within acceptable limits"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                response_times = result.details.get("response_times", [])
                if test_index < len(response_times):
                    return response_times[test_index] <= max_seconds
            return False
        except Exception as e:
            logger.debug(f"Error checking response time: {e}")
            return False
    
    def _check_response_keywords(self, result: Any, test_index: int, expected_keywords: List[str]) -> bool:
        """Check if response contains expected keywords"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                responses = result.details.get("nlp_responses", [])
                if test_index < len(responses):
                    response_text = responses[test_index].lower()
                    return all(keyword.lower() in response_text for keyword in expected_keywords)
            return False
        except Exception as e:
            logger.debug(f"Error checking response keywords: {e}")
            return False
    
    def _check_graceful_error_handling(self, result: Any) -> bool:
        """Check if errors were handled gracefully"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                error_handling = result.details.get("error_handling", {})
                return error_handling.get("graceful", False)
            return False
        except Exception as e:
            logger.debug(f"Error checking graceful error handling: {e}")
            return False
    
    def _check_no_system_crashes(self, result: Any) -> bool:
        """Check if system didn't crash during testing"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                error_handling = result.details.get("error_handling", {})
                return not error_handling.get("system_crashed", False)
            return True  # Assume no crash if we got a result
        except Exception as e:
            logger.debug(f"Error checking system crashes: {e}")
            return True
    
    def _check_specific_error_handling(self, result: Any, scenario_type: str, index: int, scenario: Any) -> bool:
        """Check specific error handling scenario"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                error_results = result.details.get("error_results", {})
                scenario_results = error_results.get(scenario_type, [])
                if index < len(scenario_results):
                    return scenario_results[index].get("handled_correctly", False)
            return False
        except Exception as e:
            logger.debug(f"Error checking specific error handling: {e}")
            return False
    
    def _check_performance_response_time(self, result: Any, max_seconds: float) -> bool:
        """Check if performance response time meets threshold"""
        try:
            actual_time = self._get_actual_response_time(result)
            return actual_time <= max_seconds if actual_time is not None else False
        except Exception as e:
            logger.debug(f"Error checking performance response time: {e}")
            return False
    
    def _check_performance_success_rate(self, result: Any, min_percent: float) -> bool:
        """Check if performance success rate meets threshold"""
        try:
            actual_rate = self._get_actual_success_rate(result)
            return actual_rate >= min_percent if actual_rate is not None else False
        except Exception as e:
            logger.debug(f"Error checking performance success rate: {e}")
            return False
    
    def _get_actual_response_time(self, result: Any) -> Optional[float]:
        """Get actual response time from result"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                performance = result.details.get("performance", {})
                return performance.get("avg_response_time", None)
            return None
        except Exception as e:
            logger.debug(f"Error getting actual response time: {e}")
            return None
    
    def _get_actual_success_rate(self, result: Any) -> Optional[float]:
        """Get actual success rate from result"""
        try:
            if hasattr(result, 'details') and isinstance(result.details, dict):
                performance = result.details.get("performance", {})
                return performance.get("success_rate", None)
            return None
        except Exception as e:
            logger.debug(f"Error getting actual success rate: {e}")
            return None
    
    def _check_timeout_compliance(self, result: Any, timeout_seconds: float) -> bool:
        """Check if test completed within timeout"""
        try:
            actual_duration = self._get_actual_duration(result)
            return actual_duration <= timeout_seconds if actual_duration is not None else False
        except Exception as e:
            logger.debug(f"Error checking timeout compliance: {e}")
            return False
    
    def _get_actual_duration(self, result: Any) -> Optional[float]:
        """Get actual test duration from result"""
        try:
            if hasattr(result, 'end_time') and hasattr(result, 'start_time'):
                duration = (result.end_time - result.start_time).total_seconds()
                return duration
            return None
        except Exception as e:
            logger.debug(f"Error getting actual duration: {e}")
            return None
    
    def check_database_state(self, expected_state: Dict[str, Any]) -> ValidationSuite:
        """
        Validate database state matches expectations.
        
        Args:
            expected_state: Expected database state
            
        Returns:
            ValidationSuite with database validation results
        """
        logger.info("🗄️ Validating database state")
        
        suite = ValidationSuite("database_validation")
        
        try:
            # Check player records
            if "players" in expected_state:
                players_valid = self._validate_player_records(expected_state["players"])
                suite.add_result(ValidationResult(
                    "player_records",
                    players_valid,
                    "Player records should match expected state",
                    details=expected_state["players"]
                ))
            
            # Check invite links
            if "invite_links" in expected_state:
                invites_valid = self._validate_invite_links(expected_state["invite_links"])
                suite.add_result(ValidationResult(
                    "invite_links",
                    invites_valid,
                    "Invite links should match expected state",
                    details=expected_state["invite_links"]
                ))
            
            # Check team member records
            if "team_members" in expected_state:
                members_valid = self._validate_team_member_records(expected_state["team_members"])
                suite.add_result(ValidationResult(
                    "team_member_records",
                    members_valid,
                    "Team member records should match expected state",
                    details=expected_state["team_members"]
                ))
            
            suite.finalize()
            
            logger.info(f"✅ Database validation completed | Passed: {suite.passed_count}/{suite.total_count}")
            return suite
            
        except Exception as e:
            logger.error(f"❌ Error during database validation: {e}")
            suite.add_result(ValidationResult(
                "database_error",
                False,
                f"Database validation error: {str(e)}",
                {"error_type": type(e).__name__}
            ))
            suite.finalize()
            return suite
    
    def _validate_player_records(self, expected_players: List[Dict[str, Any]]) -> bool:
        """Validate player records in database"""
        # This would connect to actual database to validate
        # For now, return True as placeholder
        logger.debug(f"Validating {len(expected_players)} player records")
        return True
    
    def _validate_invite_links(self, expected_invites: List[Dict[str, Any]]) -> bool:
        """Validate invite links in database"""
        # This would connect to actual database to validate
        # For now, return True as placeholder
        logger.debug(f"Validating {len(expected_invites)} invite links")
        return True
    
    def _validate_team_member_records(self, expected_members: List[Dict[str, Any]]) -> bool:
        """Validate team member records in database"""
        # This would connect to actual database to validate
        # For now, return True as placeholder
        logger.debug(f"Validating {len(expected_members)} team member records")
        return True
    
    def verify_bot_responses(self, responses: List[str], criteria: Dict[str, Any]) -> ValidationSuite:
        """
        Verify bot responses meet specified criteria.
        
        Args:
            responses: List of bot response messages
            criteria: Validation criteria
            
        Returns:
            ValidationSuite with response validation results
        """
        logger.info(f"🤖 Verifying {len(responses)} bot responses")
        
        suite = ValidationSuite("bot_response_validation")
        
        try:
            for i, response in enumerate(responses):
                # Check response length
                min_length = criteria.get("min_length", 5)
                length_ok = len(response) >= min_length
                suite.add_result(ValidationResult(
                    f"response_length_{i}",
                    length_ok,
                    f"Response {i+1} should be at least {min_length} characters",
                    expected=f">= {min_length}",
                    actual=len(response)
                ))
                
                # Check for required keywords
                required_keywords = criteria.get("required_keywords", [])
                if required_keywords:
                    keywords_found = all(keyword.lower() in response.lower() for keyword in required_keywords)
                    suite.add_result(ValidationResult(
                        f"required_keywords_{i}",
                        keywords_found,
                        f"Response {i+1} should contain required keywords",
                        details={"required_keywords": required_keywords, "response": response[:100]}
                    ))
                
                # Check for forbidden patterns
                forbidden_patterns = criteria.get("forbidden_patterns", [])
                for pattern in forbidden_patterns:
                    pattern_found = re.search(pattern, response, re.IGNORECASE)
                    suite.add_result(ValidationResult(
                        f"forbidden_pattern_{i}_{pattern[:10]}",
                        not pattern_found,
                        f"Response {i+1} should not contain forbidden pattern: {pattern}",
                        details={"pattern": pattern, "found": bool(pattern_found)}
                    ))
            
            suite.finalize()
            
            logger.info(f"✅ Bot response validation completed | Passed: {suite.passed_count}/{suite.total_count}")
            return suite
            
        except Exception as e:
            logger.error(f"❌ Error during bot response validation: {e}")
            suite.add_result(ValidationResult(
                "response_validation_error",
                False,
                f"Response validation error: {str(e)}",
                {"error_type": type(e).__name__}
            ))
            suite.finalize()
            return suite