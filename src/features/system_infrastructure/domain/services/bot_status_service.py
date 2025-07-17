import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BotStatusService:
    def __init__(self):
        self.start_time = datetime.now()
        self.last_health_check = None
        self.status = "running"
        logger.info("✅ BotStatusService initialized")
    def get_bot_status(self) -> Dict[str, Any]:
        try:
            uptime = datetime.now() - self.start_time
            return {
                "status": self.status,
                "uptime_seconds": int(uptime.total_seconds()),
                "uptime_formatted": str(uptime).split('.')[0],
                "start_time": self.start_time.isoformat(),
                "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error getting bot status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    async def perform_health_check(self) -> Dict[str, Any]:
        try:
            self.last_health_check = datetime.now()
            health_status = {
                "status": "healthy",
                "timestamp": self.last_health_check.isoformat(),
                "checks": {}
            }
            uptime = datetime.now() - self.start_time
            if uptime.total_seconds() > 86400:
                health_status["checks"]["uptime"] = "warning"
            else:
                health_status["checks"]["uptime"] = "healthy"
            all_checks = health_status["checks"].values()
            if "error" in all_checks:
                health_status["status"] = "unhealthy"
            elif "warning" in all_checks:
                health_status["status"] = "warning"
            else:
                health_status["status"] = "healthy"
            logger.info(f"✅ Health check completed: {health_status['status']}")
            return health_status
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    def update_status(self, status: str) -> None:
        self.status = status
        logger.info(f"🔄 Bot status updated to: {status}")
    def is_healthy(self) -> bool:
        if not self.last_health_check:
            return True
        time_since_check = datetime.now() - self.last_health_check
        return time_since_check.total_seconds() < 300
    def get_uptime(self) -> str:
        uptime = datetime.now() - self.start_time
        return str(uptime).split('.')[0]
    def get_main_chat_features(self) -> Dict[str, Any]:
        try:
            return {
                "features": {
                    "player_registration": {
                        "enabled": True,
                        "commands": ["/register", "/myinfo", "/list"],
                        "description": "Player registration and management"
                    },
                    "match_management": {
                        "enabled": True,
                        "commands": ["/match", "/attendance", "/status"],
                        "description": "Match scheduling and attendance tracking"
                    },
                    "team_administration": {
                        "enabled": True,
                        "commands": ["/approve", "/reject", "/admin"],
                        "description": "Team administration and player approval"
                    },
                    "payment_tracking": {
                        "enabled": False,
                        "commands": [],
                        "description": "Payment tracking and management"
                    }
                },
                "natural_language": {
                    "enabled": True,
                    "description": "Natural language processing for queries"
                },
                "ai_assistance": {
                    "enabled": True,
                    "description": "AI-powered assistance and recommendations"
                },
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error getting main chat features: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    def get_leadership_chat_features(self) -> Dict[str, Any]:
        try:
            return {
                "Commands": {
                    "admin_commands": ["/add", "/remove", "/approve", "/reject", "/admin"],
                    "management_commands": ["/team", "/match", "/stats", "/report"],
                    "description": "Leadership and administrative commands"
                },
                "Permissions": {
                    "admin_only": ["/add", "/remove", "/admin"],
                    "leadership": ["/approve", "/reject", "/team", "/match"],
                    "description": "Permission levels for different commands"
                },
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error getting leadership chat features: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    def get_version_info(self) -> Dict[str, Any]:
        try:
            return {
                "version": "1.0.0",
                "name": "KICKAI Bot",
                "description": "AI-powered football team management bot",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error getting version info: {e}")
            return {
                "version": "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 