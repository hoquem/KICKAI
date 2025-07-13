"""
Monitoring Service for KICKAI

This service handles system monitoring and health checks.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from database.interfaces import DataStoreInterface
from services.interfaces.bot_status_service_interface import IBotStatusService

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for system monitoring and health checks."""
    
    def __init__(self, data_store: DataStoreInterface, bot_status_service: IBotStatusService):
        self.data_store = data_store
        self.bot_status_service = bot_status_service
        self.start_time = datetime.now()
        self.health_checks = {}
        logger.info("✅ MonitoringService initialized")
    
    async def perform_system_health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive system health check."""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {},
                "uptime": str(datetime.now() - self.start_time).split('.')[0]
            }
            
            # Database health check
            try:
                db_health = await self.data_store.health_check()
                health_status["checks"]["database"] = {
                    "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
                    "response_time_ms": db_health.get("response_time_ms", 0)
                }
            except Exception as e:
                health_status["checks"]["database"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            
            # Bot status check
            try:
                bot_status = self.bot_status_service.get_bot_status()
                health_status["checks"]["bot"] = {
                    "status": "healthy" if bot_status["status"] == "running" else "unhealthy",
                    "uptime": bot_status.get("uptime_formatted", "unknown")
                }
            except Exception as e:
                health_status["checks"]["bot"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            
            # Overall status determination
            all_checks = health_status["checks"].values()
            if any(check.get("status") == "unhealthy" for check in all_checks):
                health_status["status"] = "unhealthy"
            elif any(check.get("status") == "warning" for check in all_checks):
                health_status["status"] = "warning"
            
            logger.info(f"✅ System health check completed: {health_status['status']}")
            return health_status
            
        except Exception as e:
            logger.error(f"❌ System health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics and statistics."""
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "uptime": str(datetime.now() - self.start_time).split('.')[0],
                "services": {}
            }
            
            # Get metrics from various services
            try:
                # Add player service metrics here
                metrics["services"]["player_service"] = "healthy"
            except Exception as e:
                metrics["services"]["player_service"] = f"unhealthy: {str(e)}"
            
            try:
                # Add team service metrics here
                metrics["services"]["team_service"] = "healthy"
            except Exception as e:
                metrics["services"]["team_service"] = f"unhealthy: {str(e)}"
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error getting system metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def log_system_event(self, event_type: str, message: str, level: str = "info") -> None:
        """Log a system event."""
        log_message = f"[{event_type.upper()}] {message}"
        
        if level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    async def check_service_dependencies(self) -> Dict[str, bool]:
        """Check if all service dependencies are available."""
        dependencies = {}
        
        try:
            await self.data_store.health_check()
            dependencies["database"] = True
        except Exception:
            dependencies["database"] = False
        
        try:
            self.bot_status_service.get_bot_status()
            dependencies["bot_status_service"] = True
        except Exception:
            dependencies["bot_status_service"] = False
        
        return dependencies 