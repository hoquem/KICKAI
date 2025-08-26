#!/usr/bin/env python3
"""
Functional Test Runner

Orchestrates comprehensive functional testing of KICKAI commands using:
- Real Firestore with KTI team data
- Mock Telegram UI for user simulation  
- Puppeteer MCP for UI automation
- Real-time data validation and reporting

Focuses on command specification compliance and data integrity.
"""

import asyncio
import sys
import time
import json
import subprocess
import signal
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.functional.kti_test_data_manager import KTITestDataManager
from tests.functional.mock_ui_controller import MockUIController
from tests.functional.firestore_validator import FirestoreValidator
from loguru import logger

@dataclass
class TestEnvironment:
    """Test environment configuration"""
    mock_ui_url: str = "http://localhost:8001"
    team_id: str = "KTI"
    test_timeout: int = 300  # 5 minutes
    screenshot_on_failure: bool = True
    
@dataclass
class TestSession:
    """Test session metadata"""
    session_id: str
    start_time: datetime
    environment: TestEnvironment
    processes: Dict[str, Any]
    status: str = "initializing"

class FunctionalTestRunner:
    """Orchestrates comprehensive KICKAI functional testing"""
    
    def __init__(self, environment: Optional[TestEnvironment] = None):
        self.environment = environment or TestEnvironment()
        self.session: Optional[TestSession] = None
        
        # Component managers
        self.data_manager: Optional[KTITestDataManager] = None
        self.ui_controller: Optional[MockUIController] = None
        self.validator: Optional[FirestoreValidator] = None
        
        # Test results
        self.test_results: Dict[str, Any] = {}
        self.overall_success: bool = False
        
    async def initialize(self) -> bool:
        """Initialize all test components and environment"""
        try:
            session_id = f"functional_test_{int(datetime.now().timestamp())}"
            self.session = TestSession(
                session_id=session_id,
                start_time=datetime.now(timezone.utc),
                environment=self.environment,
                processes={}
            )
            
            logger.info(f"🚀 Initializing Functional Test Session: {session_id}")
            logger.info("=" * 80)
            
            # 1. Initialize data manager
            logger.info("📊 Initializing test data manager...")
            self.data_manager = KTITestDataManager(self.environment.team_id)
            await self.data_manager.initialize()
            
            # 2. Initialize Firestore validator
            logger.info("🔍 Initializing Firestore validator...")  
            self.validator = FirestoreValidator(self.environment.team_id)
            await self.validator.initialize()
            
            # 3. Initialize Mock UI controller
            logger.info("🎮 Initializing Mock UI controller...")
            self.ui_controller = MockUIController(self.environment.mock_ui_url)
            await self.ui_controller.initialize()
            
            # 4. Verify environment connectivity
            await self._verify_environment_connectivity()
            
            self.session.status = "ready"
            logger.info("✅ Functional test environment initialized successfully")
            logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize functional test environment: {e}")
            self.session.status = "failed" if self.session else "error"
            return False

    async def _verify_environment_connectivity(self):
        """Verify all components can communicate properly"""
        try:
            logger.info("🔌 Verifying environment connectivity...")
            
            # Check Firestore connection
            validation_result = await self.validator.validate_data_integrity()
            if "error" in validation_result:
                raise Exception(f"Firestore connection failed: {validation_result['error']}")
            
            # Check if KTI team data exists
            data_validation = await self.data_manager.validate_test_data()
            if not data_validation.get("team_exists", False):
                logger.warning("⚠️ KTI team not found - will be created during data setup")
            
            logger.info("✅ Environment connectivity verified")
            
        except Exception as e:
            logger.error(f"❌ Environment connectivity check failed: {e}")
            raise

    async def setup_test_data(self) -> bool:
        """Set up comprehensive test data for functional testing"""
        try:
            logger.info("📝 Setting up KTI test data...")
            
            # Create test data
            success = await self.data_manager.setup_test_data()
            
            if not success:
                logger.error("❌ Test data setup failed")
                return False
                
            # Validate created data
            validation_results = await self.data_manager.validate_test_data()
            
            if not validation_results.get("data_integrity", False):
                logger.error(f"❌ Test data validation failed: {validation_results}")
                await self.data_manager.cleanup_test_data()  # Clean up invalid data
                return False
                
            # Get data summary
            summary = await self.data_manager.get_test_summary()
            logger.info("✅ Test data setup completed successfully")
            logger.info(f"   • Players: {summary['counts']['players']}")
            logger.info(f"   • Members: {summary['counts']['members']}")
            logger.info(f"   • Markers: {summary['counts']['markers']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test data setup failed: {e}")
            return False

    async def run_help_command_tests(self) -> Dict[str, Any]:
        """Execute comprehensive /help command tests"""
        try:
            logger.info("🔍 Running /help command tests...")
            
            start_time = time.time()
            test_results = await self.ui_controller.run_help_command_tests()
            execution_time = time.time() - start_time
            
            # Validate data integrity after tests (help shouldn't change data)
            pre_validation = await self.validator.validate_data_integrity()
            
            results = {
                "command": "/help",
                "execution_time": execution_time,
                "test_count": len(test_results),
                "passed_tests": sum(1 for r in test_results if r.get("validation_passed", False)),
                "failed_tests": sum(1 for r in test_results if not r.get("validation_passed", False)),
                "test_details": test_results,
                "data_integrity": pre_validation.get("results", {}).get("overall_valid", False),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            results["success_rate"] = (results["passed_tests"] / results["test_count"] * 100) if results["test_count"] > 0 else 0
            
            logger.info(f"✅ /help tests completed: {results['passed_tests']}/{results['test_count']} passed")
            return results
            
        except Exception as e:
            logger.error(f"❌ /help command tests failed: {e}")
            return {"command": "/help", "error": str(e), "success": False}

    async def run_list_command_tests(self) -> Dict[str, Any]:
        """Execute comprehensive /list command tests"""
        try:
            logger.info("📋 Running /list command tests...")
            
            start_time = time.time()
            test_results = await self.ui_controller.run_list_command_tests()
            execution_time = time.time() - start_time
            
            # Validate data integrity (list shouldn't change data)
            validation = await self.validator.validate_data_integrity()
            
            results = {
                "command": "/list",
                "execution_time": execution_time,
                "test_count": len(test_results),
                "passed_tests": sum(1 for r in test_results if r.get("validation_passed", False)),
                "failed_tests": sum(1 for r in test_results if not r.get("validation_passed", False)),
                "test_details": test_results,
                "data_integrity": validation.get("results", {}).get("overall_valid", False),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            results["success_rate"] = (results["passed_tests"] / results["test_count"] * 100) if results["test_count"] > 0 else 0
            
            logger.info(f"✅ /list tests completed: {results['passed_tests']}/{results['test_count']} passed")
            return results
            
        except Exception as e:
            logger.error(f"❌ /list command tests failed: {e}")
            return {"command": "/list", "error": str(e), "success": False}

    async def run_info_command_tests(self) -> Dict[str, Any]:
        """Execute comprehensive /info command tests"""
        try:
            logger.info("ℹ️ Running /info command tests...")
            
            start_time = time.time()
            test_results = await self.ui_controller.run_info_command_tests()
            execution_time = time.time() - start_time
            
            # Validate data integrity (info shouldn't change data)
            validation = await self.validator.validate_data_integrity()
            
            results = {
                "command": "/info",
                "execution_time": execution_time,
                "test_count": len(test_results),
                "passed_tests": sum(1 for r in test_results if r.get("validation_passed", False)),
                "failed_tests": sum(1 for r in test_results if not r.get("validation_passed", False)),
                "test_details": test_results,
                "data_integrity": validation.get("results", {}).get("overall_valid", False),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            results["success_rate"] = (results["passed_tests"] / results["test_count"] * 100) if results["test_count"] > 0 else 0
            
            logger.info(f"✅ /info tests completed: {results['passed_tests']}/{results['test_count']} passed")
            return results
            
        except Exception as e:
            logger.error(f"❌ /info command tests failed: {e}")
            return {"command": "/info", "error": str(e), "success": False}

    async def run_addplayer_command_tests(self) -> Dict[str, Any]:
        """Execute comprehensive /addplayer command tests"""
        try:
            logger.info("🏃‍♂️ Running /addplayer command tests...")
            
            # Take baseline snapshot
            baseline_validation = await self.validator.validate_data_integrity()
            baseline_counts = baseline_validation.get("counts", {})
            
            start_time = time.time()
            test_results = await self.ui_controller.run_addplayer_command_tests()
            execution_time = time.time() - start_time
            
            # Validate data changes
            post_validation = await self.validator.validate_data_integrity()
            post_counts = post_validation.get("counts", {})
            
            # Calculate data changes
            players_added = post_counts.get("players", 0) - baseline_counts.get("players", 0)
            
            results = {
                "command": "/addplayer",
                "execution_time": execution_time,
                "test_count": len(test_results),
                "passed_tests": sum(1 for r in test_results if r.get("validation_passed", False)),
                "failed_tests": sum(1 for r in test_results if not r.get("validation_passed", False)),
                "test_details": test_results,
                "data_changes": {
                    "players_added": players_added,
                    "baseline_players": baseline_counts.get("players", 0),
                    "current_players": post_counts.get("players", 0)
                },
                "data_integrity": post_validation.get("results", {}).get("overall_valid", False),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            results["success_rate"] = (results["passed_tests"] / results["test_count"] * 100) if results["test_count"] > 0 else 0
            
            logger.info(f"✅ /addplayer tests completed: {results['passed_tests']}/{results['test_count']} passed")
            logger.info(f"   • Players added: {players_added}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ /addplayer command tests failed: {e}")
            return {"command": "/addplayer", "error": str(e), "success": False}

    async def run_addmember_command_tests(self) -> Dict[str, Any]:
        """Execute comprehensive /addmember command tests"""
        try:
            logger.info("👔 Running /addmember command tests...")
            
            # Take baseline snapshot
            baseline_validation = await self.validator.validate_data_integrity()
            baseline_counts = baseline_validation.get("counts", {})
            
            start_time = time.time()
            test_results = await self.ui_controller.run_addmember_command_tests()
            execution_time = time.time() - start_time
            
            # Validate data changes
            post_validation = await self.validator.validate_data_integrity()
            post_counts = post_validation.get("counts", {})
            
            # Calculate data changes
            members_added = post_counts.get("members", 0) - baseline_counts.get("members", 0)
            
            results = {
                "command": "/addmember",
                "execution_time": execution_time,
                "test_count": len(test_results),
                "passed_tests": sum(1 for r in test_results if r.get("validation_passed", False)),
                "failed_tests": sum(1 for r in test_results if not r.get("validation_passed", False)),
                "test_details": test_results,
                "data_changes": {
                    "members_added": members_added,
                    "baseline_members": baseline_counts.get("members", 0),
                    "current_members": post_counts.get("members", 0)
                },
                "data_integrity": post_validation.get("results", {}).get("overall_valid", False),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            results["success_rate"] = (results["passed_tests"] / results["test_count"] * 100) if results["test_count"] > 0 else 0
            
            logger.info(f"✅ /addmember tests completed: {results['passed_tests']}/{results['test_count']} passed")
            logger.info(f"   • Members added: {members_added}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ /addmember command tests failed: {e}")
            return {"command": "/addmember", "error": str(e), "success": False}

    async def run_all_command_tests(self) -> Dict[str, Any]:
        """Execute all command tests in sequence"""
        try:
            logger.info("🎯 Starting comprehensive command testing...")
            logger.info("=" * 80)
            
            overall_start_time = time.time()
            
            # Execute all command tests
            command_results = {}
            
            # 1. Help command tests (read-only)
            command_results["help"] = await self.run_help_command_tests()
            await asyncio.sleep(1)  # Brief pause between test suites
            
            # 2. List command tests (read-only) 
            command_results["list"] = await self.run_list_command_tests()
            await asyncio.sleep(1)
            
            # 3. Info command tests (read-only)
            command_results["info"] = await self.run_info_command_tests()
            await asyncio.sleep(1)
            
            # 4. Add player command tests (writes data)
            command_results["addplayer"] = await self.run_addplayer_command_tests()
            await asyncio.sleep(2)  # Longer pause after data modification
            
            # 5. Add member command tests (writes data)
            command_results["addmember"] = await self.run_addmember_command_tests()
            
            overall_execution_time = time.time() - overall_start_time
            
            # Calculate overall statistics
            total_tests = sum(r.get("test_count", 0) for r in command_results.values())
            total_passed = sum(r.get("passed_tests", 0) for r in command_results.values()) 
            total_failed = sum(r.get("failed_tests", 0) for r in command_results.values())
            
            overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            
            results = {
                "session_id": self.session.session_id,
                "team_id": self.environment.team_id,
                "execution_time": overall_execution_time,
                "command_results": command_results,
                "overall_statistics": {
                    "total_tests": total_tests,
                    "passed_tests": total_passed,
                    "failed_tests": total_failed,
                    "success_rate": overall_success_rate,
                    "commands_tested": len(command_results)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Determine overall success
            self.overall_success = (
                overall_success_rate >= 90 and  # 90% test success rate
                all(r.get("data_integrity", False) for r in command_results.values() if "data_integrity" in r)
            )
            
            results["overall_success"] = self.overall_success
            
            logger.info("=" * 80)
            logger.info(f"🏁 Command testing completed: {total_passed}/{total_tests} tests passed ({overall_success_rate:.1f}%)")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Command testing failed: {e}")
            return {"error": str(e), "success": False}

    async def cleanup_test_data(self) -> bool:
        """Clean up all test data after testing"""
        try:
            logger.info("🧹 Cleaning up test data...")
            
            if not self.data_manager:
                logger.warning("⚠️ No data manager available for cleanup")
                return True
                
            success = await self.data_manager.cleanup_test_data()
            
            if success:
                logger.info("✅ Test data cleanup completed successfully")
            else:
                logger.warning("⚠️ Test data cleanup completed with some errors")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Test data cleanup failed: {e}")
            return False

    async def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        try:
            logger.info("📊 Generating comprehensive test report...")
            
            # Get final Firestore validation
            final_validation = await self.validator.generate_validation_report()
            
            # Generate test summary
            ui_summary = await self.ui_controller.get_test_summary() if self.ui_controller else {}
            data_summary = await self.data_manager.get_test_summary() if self.data_manager else {}
            
            report = {
                "report_id": f"functional_test_report_{self.session.session_id}",
                "session": {
                    "session_id": self.session.session_id,
                    "start_time": self.session.start_time.isoformat(),
                    "end_time": datetime.now(timezone.utc).isoformat(),
                    "duration": (datetime.now(timezone.utc) - self.session.start_time).total_seconds(),
                    "status": "completed"
                },
                "environment": {
                    "team_id": self.environment.team_id,
                    "mock_ui_url": self.environment.mock_ui_url,
                    "test_timeout": self.environment.test_timeout
                },
                "test_results": self.test_results,
                "ui_testing": ui_summary,
                "data_management": data_summary,
                "firestore_validation": final_validation,
                "overall_success": self.overall_success,
                "recommendations": self._generate_recommendations()
            }
            
            logger.info("✅ Test report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate test report: {e}")
            return {"error": str(e)}

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        try:
            if not self.overall_success:
                recommendations.append("⚠️ Overall test success rate below 90% - investigate failed tests")
            
            if self.test_results:
                # Check response times
                avg_response_times = {}
                for command, result in self.test_results.get("command_results", {}).items():
                    if "execution_time" in result:
                        avg_response_times[command] = result["execution_time"]
                
                slow_commands = [cmd for cmd, time in avg_response_times.items() if time > 5.0]
                if slow_commands:
                    recommendations.append(f"🐌 Slow response times detected: {', '.join(slow_commands)}")
            
            recommendations.append("✅ Continue monitoring data integrity during production usage")
            recommendations.append("📊 Consider adding performance benchmarks for response time tracking")
            
        except Exception as e:
            recommendations.append(f"❌ Error generating recommendations: {e}")
            
        return recommendations

    async def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run the complete functional test suite"""
        try:
            logger.info("🎬 Starting Complete KICKAI Functional Test Suite")
            logger.info("=" * 90)
            
            # Phase 1: Environment Setup
            logger.info("Phase 1: Environment Setup")
            if not await self.initialize():
                return {"success": False, "phase": "initialization", "error": "Environment setup failed"}
            
            # Phase 2: Test Data Setup  
            logger.info("\nPhase 2: Test Data Setup")
            if not await self.setup_test_data():
                return {"success": False, "phase": "data_setup", "error": "Test data setup failed"}
            
            # Phase 3: Command Testing
            logger.info("\nPhase 3: Command Testing")
            self.test_results = await self.run_all_command_tests()
            
            # Phase 4: Report Generation
            logger.info("\nPhase 4: Report Generation")
            test_report = await self.generate_test_report()
            
            # Phase 5: Cleanup
            logger.info("\nPhase 5: Cleanup")
            cleanup_success = await self.cleanup_test_data()
            
            # Final results
            final_results = {
                "success": self.overall_success and cleanup_success,
                "session_id": self.session.session_id,
                "test_report": test_report,
                "cleanup_success": cleanup_success,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info("=" * 90)
            if final_results["success"]:
                logger.info("🎉 FUNCTIONAL TEST SUITE COMPLETED SUCCESSFULLY!")
            else:
                logger.info("⚠️ FUNCTIONAL TEST SUITE COMPLETED WITH ISSUES")
            logger.info("=" * 90)
            
            return final_results
            
        except Exception as e:
            logger.error(f"💥 Complete test suite failed: {e}")
            
            # Attempt cleanup on failure
            try:
                if self.data_manager:
                    await self.cleanup_test_data()
            except:
                logger.error("❌ Emergency cleanup also failed")
            
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": "execution"
            }

async def main():
    """Main execution function"""
    print("🚀 KICKAI Functional Test Runner")
    print("=" * 50)
    
    # Create environment
    environment = TestEnvironment(
        team_id="KTI",
        mock_ui_url="http://localhost:8001", 
        test_timeout=300,
        screenshot_on_failure=True
    )
    
    # Run tests
    runner = FunctionalTestRunner(environment)
    results = await runner.run_complete_test_suite()
    
    # Save results
    results_file = Path(f"functional_test_results_{int(datetime.now().timestamp())}.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Exit with appropriate code
    exit_code = 0 if results.get("success", False) else 1
    print(f"\n{'✅ SUCCESS' if exit_code == 0 else '❌ FAILURE'}")
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)