"""
Pluggable Service Health Checkers

Specialized health checkers for different service types, providing
comprehensive health monitoring and validation capabilities.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
import logging

from .interfaces import IServiceHealthChecker, ServiceHealth, ServiceStatus

logger = logging.getLogger(__name__)


class DatabaseServiceHealthChecker(IServiceHealthChecker):
    """Health checker for database-related services."""
    
    def __init__(self):
        self.supported_services = {
            'DataStoreInterface', 'FirestoreRepository', 'DatabaseConnection',
            'data_store', 'database', 'db_connection'
        }
    
    async def check_health(self, service_name: str, service_instance: Any) -> ServiceHealth:
        """Check database service health."""
        try:
            start_time = time.time()
            
            # Check if service has database-specific health methods
            if hasattr(service_instance, 'ping') or hasattr(service_instance, 'test_connection'):
                try:
                    if hasattr(service_instance, 'ping'):
                        result = await service_instance.ping()
                    else:
                        result = await service_instance.test_connection()
                    
                    response_time = time.time() - start_time
                    
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.HEALTHY if result else ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        metadata={
                            "checker_type": "database",
                            "connection_test": True,
                            "ping_successful": bool(result)
                        }
                    )
                except Exception as e:
                    response_time = time.time() - start_time
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        error_message=str(e),
                        metadata={
                            "checker_type": "database",
                            "connection_test_failed": True
                        }
                    )
            
            # Basic database interface validation
            required_methods = ['create_document', 'get_document', 'update_document']
            missing_methods = [method for method in required_methods 
                             if not hasattr(service_instance, method)]
            
            if missing_methods:
                return ServiceHealth(
                    service_name=service_name,
                    status=ServiceStatus.UNHEALTHY,
                    last_check=time.time(),
                    error_message=f"Missing required methods: {missing_methods}",
                    metadata={
                        "checker_type": "database",
                        "interface_validation": False,
                        "missing_methods": missing_methods
                    }
                )
            
            response_time = time.time() - start_time
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.HEALTHY,
                last_check=time.time(),
                response_time=response_time,
                metadata={
                    "checker_type": "database",
                    "interface_validation": True
                }
            )
            
        except Exception as e:
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                last_check=time.time(),
                error_message=str(e),
                metadata={"checker_type": "database", "validation_failed": True}
            )
    
    def supports_service(self, service_name: str) -> bool:
        """Check if this checker supports the service."""
        return (service_name in self.supported_services or 
                any(keyword in service_name.lower() for keyword in 
                    ['database', 'db', 'store', 'repository', 'firestore']))


class PlayerServiceHealthChecker(IServiceHealthChecker):
    """Health checker for player-related services."""
    
    def __init__(self):
        self.supported_services = {
            'PlayerService', 'IPlayerService', 'player_service'
        }
    
    async def check_health(self, service_name: str, service_instance: Any) -> ServiceHealth:
        """Check player service health."""
        try:
            start_time = time.time()
            
            # Check core player service methods
            required_methods = ['get_player', 'create_player', 'update_player']
            missing_methods = [method for method in required_methods 
                             if not hasattr(service_instance, method)]
            
            if missing_methods:
                return ServiceHealth(
                    service_name=service_name,
                    status=ServiceStatus.UNHEALTHY,
                    last_check=time.time(),
                    error_message=f"Missing required methods: {missing_methods}",
                    metadata={
                        "checker_type": "player_service",
                        "interface_validation": False,
                        "missing_methods": missing_methods
                    }
                )
            
            # Test basic functionality if available
            if hasattr(service_instance, 'health_check'):
                try:
                    health_result = await service_instance.health_check()
                    response_time = time.time() - start_time
                    
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.HEALTHY if health_result else ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        metadata={
                            "checker_type": "player_service",
                            "has_health_check": True,
                            "interface_validation": True
                        }
                    )
                except Exception as e:
                    response_time = time.time() - start_time
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        error_message=str(e),
                        metadata={
                            "checker_type": "player_service",
                            "health_check_failed": True
                        }
                    )
            
            response_time = time.time() - start_time
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.HEALTHY,
                last_check=time.time(),
                response_time=response_time,
                metadata={
                    "checker_type": "player_service",
                    "interface_validation": True
                }
            )
            
        except Exception as e:
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                last_check=time.time(),
                error_message=str(e),
                metadata={"checker_type": "player_service", "validation_failed": True}
            )
    
    def supports_service(self, service_name: str) -> bool:
        """Check if this checker supports the service."""
        return (service_name in self.supported_services or 
                'player' in service_name.lower())


class TeamServiceHealthChecker(IServiceHealthChecker):
    """Health checker for team-related services."""
    
    def __init__(self):
        self.supported_services = {
            'TeamService', 'ITeamService', 'team_service'
        }
    
    async def check_health(self, service_name: str, service_instance: Any) -> ServiceHealth:
        """Check team service health."""
        try:
            start_time = time.time()
            
            # Check core team service methods
            required_methods = ['get_team', 'create_team', 'update_team']
            missing_methods = [method for method in required_methods 
                             if not hasattr(service_instance, method)]
            
            if missing_methods:
                return ServiceHealth(
                    service_name=service_name,
                    status=ServiceStatus.UNHEALTHY,
                    last_check=time.time(),
                    error_message=f"Missing required methods: {missing_methods}",
                    metadata={
                        "checker_type": "team_service",
                        "interface_validation": False,
                        "missing_methods": missing_methods
                    }
                )
            
            # Test basic functionality if available
            if hasattr(service_instance, 'health_check'):
                try:
                    health_result = await service_instance.health_check()
                    response_time = time.time() - start_time
                    
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.HEALTHY if health_result else ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        metadata={
                            "checker_type": "team_service",
                            "has_health_check": True,
                            "interface_validation": True
                        }
                    )
                except Exception as e:
                    response_time = time.time() - start_time
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        error_message=str(e),
                        metadata={
                            "checker_type": "team_service",
                            "health_check_failed": True
                        }
                    )
            
            response_time = time.time() - start_time
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.HEALTHY,
                last_check=time.time(),
                response_time=response_time,
                metadata={
                    "checker_type": "team_service",
                    "interface_validation": True
                }
            )
            
        except Exception as e:
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                last_check=time.time(),
                error_message=str(e),
                metadata={"checker_type": "team_service", "validation_failed": True}
            )
    
    def supports_service(self, service_name: str) -> bool:
        """Check if this checker supports the service."""
        return (service_name in self.supported_services or 
                'team' in service_name.lower())


class AgentServiceHealthChecker(IServiceHealthChecker):
    """Health checker for CrewAI agent-related services."""
    
    def __init__(self):
        self.supported_services = {
            'AgentFactory', 'CrewAISystem', 'MessageRouter', 'agent_factory',
            'crew_system', 'message_router'
        }
    
    async def check_health(self, service_name: str, service_instance: Any) -> ServiceHealth:
        """Check agent service health."""
        try:
            start_time = time.time()
            
            # Check agent-specific functionality
            if 'agent' in service_name.lower() or 'crew' in service_name.lower():
                # Check for agent creation capabilities
                if hasattr(service_instance, 'create_agent'):
                    try:
                        # Test agent creation with a simple agent
                        test_agent = service_instance.create_agent('help_assistant')
                        response_time = time.time() - start_time
                        
                        return ServiceHealth(
                            service_name=service_name,
                            status=ServiceStatus.HEALTHY if test_agent else ServiceStatus.UNHEALTHY,
                            last_check=time.time(),
                            response_time=response_time,
                            metadata={
                                "checker_type": "agent_service",
                                "agent_creation_test": True,
                                "test_agent_created": bool(test_agent)
                            }
                        )
                    except Exception as e:
                        response_time = time.time() - start_time
                        return ServiceHealth(
                            service_name=service_name,
                            status=ServiceStatus.UNHEALTHY,
                            last_check=time.time(),
                            response_time=response_time,
                            error_message=str(e),
                            metadata={
                                "checker_type": "agent_service",
                                "agent_creation_failed": True
                            }
                        )
                
                # Check for router capabilities
                if hasattr(service_instance, 'route_message') or hasattr(service_instance, 'process_message'):
                    response_time = time.time() - start_time
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.HEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        metadata={
                            "checker_type": "agent_service",
                            "routing_capabilities": True
                        }
                    )
            
            # Generic service validation
            response_time = time.time() - start_time
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.HEALTHY,
                last_check=time.time(),
                response_time=response_time,
                metadata={
                    "checker_type": "agent_service",
                    "basic_validation": True
                }
            )
            
        except Exception as e:
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                last_check=time.time(),
                error_message=str(e),
                metadata={"checker_type": "agent_service", "validation_failed": True}
            )
    
    def supports_service(self, service_name: str) -> bool:
        """Check if this checker supports the service."""
        return (service_name in self.supported_services or 
                any(keyword in service_name.lower() for keyword in 
                    ['agent', 'crew', 'router', 'message']))


class ExternalServiceHealthChecker(IServiceHealthChecker):
    """Health checker for external service integrations."""
    
    def __init__(self):
        self.supported_services = {
            'LLMProvider', 'TelegramBot', 'FirebaseClient', 
            'llm_provider', 'telegram_bot', 'firebase_client'
        }
    
    async def check_health(self, service_name: str, service_instance: Any) -> ServiceHealth:
        """Check external service health."""
        try:
            start_time = time.time()
            
            # Check for connection-based services
            if hasattr(service_instance, 'test_connection'):
                try:
                    connection_result = await service_instance.test_connection()
                    response_time = time.time() - start_time
                    
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.HEALTHY if connection_result else ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        metadata={
                            "checker_type": "external_service",
                            "connection_test": True,
                            "connection_successful": bool(connection_result)
                        }
                    )
                except Exception as e:
                    response_time = time.time() - start_time
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        error_message=str(e),
                        metadata={
                            "checker_type": "external_service",
                            "connection_test_failed": True
                        }
                    )
            
            # Check for API-based services
            if hasattr(service_instance, 'ping') or hasattr(service_instance, 'status'):
                try:
                    if hasattr(service_instance, 'ping'):
                        status_result = await service_instance.ping()
                    else:
                        status_result = await service_instance.status()
                    
                    response_time = time.time() - start_time
                    
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.HEALTHY if status_result else ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        metadata={
                            "checker_type": "external_service",
                            "api_test": True,
                            "api_responsive": bool(status_result)
                        }
                    )
                except Exception as e:
                    response_time = time.time() - start_time
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.UNHEALTHY,
                        last_check=time.time(),
                        response_time=response_time,
                        error_message=str(e),
                        metadata={
                            "checker_type": "external_service",
                            "api_test_failed": True
                        }
                    )
            
            # Basic existence check for external services
            response_time = time.time() - start_time
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.HEALTHY,
                last_check=time.time(),
                response_time=response_time,
                metadata={
                    "checker_type": "external_service",
                    "basic_validation": True
                }
            )
            
        except Exception as e:
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                last_check=time.time(),
                error_message=str(e),
                metadata={"checker_type": "external_service", "validation_failed": True}
            )
    
    def supports_service(self, service_name: str) -> bool:
        """Check if this checker supports the service."""
        return (service_name in self.supported_services or 
                any(keyword in service_name.lower() for keyword in 
                    ['llm', 'telegram', 'firebase', 'client', 'provider', 'bot']))


def get_default_health_checkers() -> List[IServiceHealthChecker]:
    """Get list of default health checkers."""
    return [
        DatabaseServiceHealthChecker(),
        PlayerServiceHealthChecker(),
        TeamServiceHealthChecker(),
        AgentServiceHealthChecker(),
        ExternalServiceHealthChecker(),
    ]


def register_default_health_checkers(registry) -> None:
    """Register all default health checkers with a service registry."""
    for checker in get_default_health_checkers():
        registry.add_health_checker(checker)
    
    logger.info("✅ Registered all default health checkers")