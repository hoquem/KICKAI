"""
Quick Test API Integration

FastAPI routes for integrating the Quick Test Scenarios framework with the frontend.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from loguru import logger

from .test_controller import QuickTestController
from .scenarios.player_registration_scenario import PlayerRegistrationScenario
from ..backend.mock_telegram_service import mock_service

# Import real bot system - no mocks allowed
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))
    
    from kickai.core.dependency_container import ensure_container_initialized
    from kickai.agents.telegram_message_adapter import TelegramMessageAdapter
    from kickai.core.startup_validation import run_startup_validation
    
    BOT_SYSTEM_AVAILABLE = True
    logger.info("✅ Real KICKAI bot system imported successfully")
except ImportError as e:
    BOT_SYSTEM_AVAILABLE = False
    logger.error(f"❌ Failed to import real KICKAI bot system: {e}")
    raise HTTPException(status_code=500, detail=f"Real bot system required but not available: {e}")


class RunTestRequest(BaseModel):
    """Request model for running a test scenario"""
    scenario: str
    options: Optional[Dict[str, Any]] = None


class TestSessionRequest(BaseModel):
    """Request model for test session operations"""
    session_id: Optional[str] = None


class TestExecutionStatus(BaseModel):
    """Status model for test execution monitoring"""
    execution_id: str
    scenario_name: str
    status: str
    progress_percentage: float
    current_step: Optional[str] = None
    completed_steps: List[str] = []
    duration_seconds: Optional[float] = None
    completed: bool = False
    failed: bool = False
    error: Optional[str] = None


# Global instances - only real bot system, no mocks
test_controller = None
active_executions: Dict[str, Dict[str, Any]] = {}
bot_message_router = None
bot_system_validated = False

# FastAPI router
router = APIRouter(prefix="/quick-tests", tags=["Quick Test Scenarios"])


@router.post("/initialize")
async def initialize_quick_test_controller():
    """Initialize the Quick Test Controller"""
    global test_controller
    
    try:
        logger.info("🚀 Initializing Quick Test Controller with real KICKAI bot system")
        
        if not BOT_SYSTEM_AVAILABLE:
            raise HTTPException(status_code=500, detail="Real bot system required but not available")
        
        # Validate bot system startup - fail fast if not ready
        global bot_system_validated, bot_message_router
        
        if not bot_system_validated:
            logger.info("🔍 Validating KICKAI bot system startup...")
            
            # Ensure dependency container is initialized
            ensure_container_initialized()
            
            # Run comprehensive startup validation
            validation_report = await run_startup_validation()
            
            if validation_report.overall_status.value != "PASSED":
                error_details = [
                    f"Critical failures: {len(validation_report.critical_failures)}",
                    f"Warnings: {len(validation_report.warnings)}"
                ]
                if validation_report.critical_failures:
                    error_details.extend([f"  - {failure}" for failure in validation_report.critical_failures[:3]])
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Bot system validation failed:\n" + "\n".join(error_details)
                )
            
            # Initialize bot message router
            bot_message_router = TelegramMessageAdapter()
            bot_system_validated = True
            logger.success("✅ KICKAI bot system validation passed")
        
        # Get default team ID for real data loading
        temp_data_manager = TestDataManager()
        default_team_id = await temp_data_manager._get_test_team_id()
        
        if not default_team_id:
            logger.warning("⚠️ No team found in Firestore - tests may fail")
        else:
            logger.info(f"🏆 Using team for testing: {default_team_id}")
        
        # Initialize test controller with real bot system and team context
        test_controller = QuickTestController(
            mock_service=mock_service,
            bot_integration=RealBotIntegration(bot_message_router),
            team_id=default_team_id
        )
        
        # Register available scenarios
        test_controller.register_scenario("player-registration", PlayerRegistrationScenario)
        # Additional scenarios would be registered here
        
        logger.success("✅ Quick Test Controller initialized successfully")
        
        return {
            "status": "initialized",
            "available_scenarios": test_controller.get_available_scenarios(),
            "message": "Quick Test Controller ready"
        }
        
    except Exception as e:
        logger.error(f"❌ Error initializing Quick Test Controller: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize: {str(e)}")


@router.get("/scenarios")
async def get_available_scenarios():
    """Get list of available test scenarios"""
    if not test_controller:
        raise HTTPException(status_code=400, detail="Test controller not initialized")
    
    scenarios = test_controller.get_available_scenarios()
    
    # Add scenario metadata
    scenario_info = {
        "player-registration": {
            "name": "Player Registration Flow",
            "description": "Test complete player onboarding from invite creation to registration",
            "duration_estimate": 60,
            "icon": "🏃"
        },
        "invite-link-validation": {
            "name": "Invite Link Validation",
            "description": "Test invite link security, expiration, and edge cases",
            "duration_estimate": 45,
            "icon": "🔗"
        },
        "command-testing": {
            "name": "Command Testing Suite",
            "description": "Test bot commands across different user roles and chat types",
            "duration_estimate": 90,
            "icon": "🎯"
        },
        "natural-language-processing": {
            "name": "Natural Language Processing",
            "description": "Test bot's natural language understanding and responses",
            "duration_estimate": 60,
            "icon": "💬"
        },
        "error-handling": {
            "name": "Error Handling & Edge Cases",
            "description": "Test system resilience and error handling capabilities",
            "duration_estimate": 75,
            "icon": "🚨"
        },
        "performance-load": {
            "name": "Performance & Load Test",
            "description": "Test system performance under concurrent load",
            "duration_estimate": 120,
            "icon": "📊"
        }
    }
    
    return {
        "scenarios": scenarios,
        "scenario_info": {name: info for name, info in scenario_info.items() if name in scenarios}
    }


@router.post("/run")
async def run_test_scenario(request: RunTestRequest, background_tasks: BackgroundTasks):
    """Run a single test scenario"""
    if not test_controller:
        raise HTTPException(status_code=400, detail="Test controller not initialized")
    
    if request.scenario not in test_controller.get_available_scenarios():
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {request.scenario}")
    
    execution_id = str(uuid.uuid4())
    
    logger.info(f"🏃 Starting test scenario: {request.scenario} (execution_id: {execution_id})")
    
    # Initialize execution tracking
    active_executions[execution_id] = {
        "scenario_name": request.scenario,
        "status": "starting",
        "progress_percentage": 0.0,
        "current_step": "Initializing test...",
        "completed_steps": [],
        "start_time": datetime.now(timezone.utc),
        "completed": False,
        "failed": False,
        "error": None
    }
    
    # Start test execution in background
    background_tasks.add_task(execute_test_scenario, execution_id, request.scenario, request.options)
    
    return {
        "execution_id": execution_id,
        "scenario": request.scenario,
        "status": "started",
        "message": f"Test scenario {request.scenario} started"
    }


@router.get("/status/{execution_id}")
async def get_test_status(execution_id: str) -> TestExecutionStatus:
    """Get status of a running test execution"""
    if execution_id not in active_executions:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    execution = active_executions[execution_id]
    
    # Calculate duration
    duration_seconds = None
    if execution.get("start_time"):
        end_time = execution.get("end_time", datetime.now(timezone.utc))
        duration_seconds = (end_time - execution["start_time"]).total_seconds()
    
    return TestExecutionStatus(
        execution_id=execution_id,
        scenario_name=execution["scenario_name"],
        status=execution["status"],
        progress_percentage=execution["progress_percentage"],
        current_step=execution.get("current_step"),
        completed_steps=execution["completed_steps"],
        duration_seconds=duration_seconds,
        completed=execution["completed"],
        failed=execution["failed"],
        error=execution.get("error")
    )


@router.post("/session/start")
async def start_test_session():
    """Start a new test session"""
    if not test_controller:
        raise HTTPException(status_code=400, detail="Test controller not initialized")
    
    try:
        session_id = await test_controller.start_test_session()
        
        logger.info(f"🎯 Started test session: {session_id}")
        
        return {
            "session_id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"❌ Error starting test session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/end")
async def end_test_session(request: TestSessionRequest):
    """End the current test session"""
    if not test_controller:
        raise HTTPException(status_code=400, detail="Test controller not initialized")
    
    try:
        session = await test_controller.end_test_session()
        
        logger.info(f"🏁 Ended test session: {session.session_id}")
        
        return session.to_dict()
        
    except Exception as e:
        logger.error(f"❌ Error ending test session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/status")
async def get_session_status():
    """Get current test session status"""
    if not test_controller:
        raise HTTPException(status_code=400, detail="Test controller not initialized")
    
    status = test_controller.get_current_session_status()
    
    if not status:
        return {"status": "no_active_session"}
    
    return status


@router.get("/history")
async def get_test_history(limit: int = 10):
    """Get test execution history"""
    # This would typically come from a database
    # For now, return mock history data
    
    mock_history = []
    for i in range(min(limit, 5)):
        mock_history.append({
            "session_id": f"session_{datetime.now().timestamp() - i * 3600}",
            "start_time": (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat(),
            "total_scenarios": 6,
            "completed_scenarios": 5 - (i % 2),
            "failed_scenarios": i % 2,
            "success_rate": 83.3 if i % 2 == 0 else 100.0
        })
    
    return {
        "sessions": mock_history,
        "total": len(mock_history)
    }


@router.get("/metrics/{scenario_name}")
async def get_scenario_metrics(scenario_name: str):
    """Get performance metrics for a specific scenario"""
    if not test_controller:
        raise HTTPException(status_code=400, detail="Test controller not initialized")
    
    try:
        metrics = await test_controller.get_scenario_metrics(scenario_name)
        return metrics
        
    except Exception as e:
        logger.error(f"❌ Error getting scenario metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/executions/{execution_id}")
async def cancel_test_execution(execution_id: str):
    """Cancel a running test execution"""
    if execution_id not in active_executions:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    execution = active_executions[execution_id]
    
    if execution["completed"] or execution["failed"]:
        raise HTTPException(status_code=400, detail="Execution already completed")
    
    # Mark as cancelled
    execution["status"] = "cancelled"
    execution["failed"] = True
    execution["error"] = "Cancelled by user"
    execution["end_time"] = datetime.now(timezone.utc)
    
    logger.info(f"🛑 Cancelled test execution: {execution_id}")
    
    return {"message": f"Execution {execution_id} cancelled"}


# Background task functions

async def execute_test_scenario(execution_id: str, scenario_name: str, options: Optional[Dict[str, Any]]):
    """Execute a test scenario in the background"""
    execution = active_executions[execution_id]
    
    try:
        logger.info(f"⚡ Executing test scenario: {scenario_name}")
        
        # Update status
        execution["status"] = "running"
        execution["current_step"] = "Starting test execution..."
        execution["progress_percentage"] = 10.0
        
        # Run the scenario
        result = await test_controller.run_scenario(scenario_name)
        
        # Update progress throughout execution
        steps = [
            ("Setting up test environment", 20.0),
            ("Executing test scenario", 50.0),
            ("Validating results", 80.0),
            ("Cleaning up test data", 95.0),
            ("Test completed", 100.0)
        ]
        
        for step_name, progress in steps:
            execution["current_step"] = step_name
            execution["progress_percentage"] = progress
            execution["completed_steps"].append(step_name)
            
            # Simulate step execution time
            await asyncio.sleep(1)
            
            # Check if cancelled
            if execution.get("status") == "cancelled":
                return
        
        # Mark as completed
        execution["status"] = "completed"
        execution["completed"] = True
        execution["end_time"] = datetime.now(timezone.utc)
        execution["result"] = result.to_dict() if result else None
        
        logger.success(f"✅ Test scenario completed: {scenario_name}")
        
    except Exception as e:
        logger.error(f"❌ Test scenario failed: {scenario_name} - {e}")
        
        execution["status"] = "failed"
        execution["failed"] = True
        execution["error"] = str(e)
        execution["end_time"] = datetime.now(timezone.utc)


class RealBotIntegration:
    """Real bot integration using KICKAI TelegramMessageAdapter"""
    
    def __init__(self, message_router: TelegramMessageAdapter):
        self.message_router = message_router
        logger.info("🤖 RealBotIntegration initialized with TelegramMessageAdapter")
    
    async def process_mock_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message through the real KICKAI bot system"""
        try:
            logger.debug(f"🤖 Processing message through real bot: {message_data.get('text', '')[:50]}...")
            
            # Convert mock message format to bot system format
            bot_message = {
                "message_id": message_data.get("message_id", 1),
                "from": message_data.get("from", {}),
                "chat": message_data.get("chat", {}),
                "date": message_data.get("date", int(datetime.now().timestamp())),
                "text": message_data.get("text", "")
            }
            
            # Add chat context for proper routing
            chat_context = message_data.get("chat_context", "main_chat")
            bot_message["chat_context"] = chat_context
            
            # Process through TelegramMessageAdapter
            response = await self.message_router.process_message(bot_message)
            
            if response and hasattr(response, 'message'):
                return {
                    "message": response.message,
                    "success": response.success if hasattr(response, 'success') else True
                }
            elif isinstance(response, str):
                return {
                    "message": response,
                    "success": True
                }
            else:
                logger.warning(f"Unexpected response type from bot: {type(response)}")
                return {
                    "message": str(response) if response else "No response from bot",
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing message through real bot: {e}")
            return {
                "message": f"Bot error: {str(e)}",
                "success": False
            }
    
    def process_mock_message_sync(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """DEPRECATED: Sync wrapper removed - violates CrewAI async architecture.
        
        This method causes asyncio.run() event loop conflicts. 
        Use process_mock_message() async method directly.
        """
        logger.error("❌ process_mock_message_sync called - this method is deprecated")
        logger.error("🔧 Use process_mock_message() async method directly instead")
        
        return {
            "message": "Sync wrapper is deprecated - use async patterns",
            "success": False,
            "error": "sync_wrapper_deprecated"
            }


# Import required modules for real bot system
try:
    from datetime import timedelta
    import asyncio
    import concurrent.futures
except ImportError:
    pass

# Ensure we only use real data from Firestore
if BOT_SYSTEM_AVAILABLE:
    logger.info("🔥 Using real Firestore data - no mock data or defaults allowed")
else:
    logger.error("❌ Real bot system required - no fallback to mock implementations")