"""
Agent system factory for creating complete agent systems with dependency injection.

This factory is the main entry point for creating fully configured agent systems
with all dependencies properly wired together.
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from loguru import logger

from kickai.core.interfaces import (
    IAgentRouter, IAgentOrchestrator, ILifecycleManager,
    IUserFlowHandler, IContactHandler, ICommandValidator, IUserService
)
from kickai.core.value_objects import TeamId
from .repository_factory import RepositoryFactory
from .service_factory import ServiceFactory


class AgentSystemFactory:
    """
    Factory for creating complete agent systems.

    This factory creates and wires together all components needed for the agent system:
    - Repositories
    - Services  
    - Handlers
    - Agent system components

    It serves as the main composition root for the dependency injection container.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize agent system factory.

        Args:
            config: Optional configuration for the entire system
        """
        self.config = config or {}
        self._system_cache: Dict[str, Any] = {}

        # Create base factories
        self.repository_factory = self._create_repository_factory()
        self.service_factory = self._create_service_factory()

    def create_agent_router(self, team_id: str) -> IAgentRouter:
        """
        Create complete agent router with all dependencies.

        This is the main entry point for creating a fully configured
        agent system for a team.

        Args:
            team_id: Team identifier

        Returns:
            Fully configured agent router
        """
        team_id_obj = TeamId(team_id)
        cache_key = f"agent_router_{team_id}"

        if cache_key not in self._system_cache:
            logger.info(f"Creating agent system for team {team_id}")

            # Create core services
            user_service = self.service_factory.create_user_service(team_id_obj)
            player_service = self.service_factory.create_player_service(team_id_obj)
            team_service = self.service_factory.create_team_service(team_id_obj)

            # Create handlers
            user_flow_handler = self._create_user_flow_handler(user_service, team_id)
            contact_handler = self._create_contact_handler(
                player_service, team_service, team_id
            )
            command_validator = self._create_command_validator()

            # Create agent system components
            agent_orchestrator = self._create_agent_orchestrator(team_id)
            lifecycle_manager = self._create_lifecycle_manager(team_id)

            # Create the main router with all dependencies
            from kickai.agents.refactored_agentic_message_router import (
                RefactoredAgenticMessageRouter
            )

            router = RefactoredAgenticMessageRouter(
                team_id=team_id,
                agent_orchestrator=agent_orchestrator,
                lifecycle_manager=lifecycle_manager,
                user_flow_handler=user_flow_handler,
                contact_handler=contact_handler,
                command_validator=command_validator,
                user_service=user_service,
            )

            self._system_cache[cache_key] = router
            logger.info(f"✅ Agent system created for team {team_id}")

        return self._system_cache[cache_key]

    def create_agent_orchestrator(self, team_id: str) -> IAgentOrchestrator:
        """
        Create agent orchestrator for a team.

        Args:
            team_id: Team identifier

        Returns:
            Agent orchestrator implementation
        """
        return self._create_agent_orchestrator(team_id)

    def create_lifecycle_manager(self, team_id: str) -> ILifecycleManager:
        """
        Create lifecycle manager for a team.

        Args:
            team_id: Team identifier

        Returns:
            Lifecycle manager implementation
        """
        return self._create_lifecycle_manager(team_id)

    def _create_repository_factory(self) -> RepositoryFactory:
        """Create repository factory based on configuration."""
        repo_config = self.config.get("repositories", {})
        
        if self.config.get("environment") == "testing":
            return RepositoryFactory.create_for_testing()
        else:
            return RepositoryFactory.create_for_production()
    
    def _create_service_factory(self) -> ServiceFactory:
        """Create service factory with repository factory."""
        if self.config.get("environment") == "testing":
            return ServiceFactory.create_for_testing(self.repository_factory)
        else:
            return ServiceFactory.create_for_production(self.repository_factory)
    
    def _create_user_flow_handler(self, user_service: IUserService, team_id: str) -> IUserFlowHandler:
        """Create user flow handler."""
        from kickai.agents.handlers.user_flow_handler import UserFlowHandler
        return UserFlowHandler(user_service, team_id)
    
    def _create_contact_handler(
        self, 
        player_service, 
        team_service, 
        team_id: str
    ) -> IContactHandler:
        """Create contact handler."""
        from kickai.agents.handlers.contact_handler import ContactHandler
        return ContactHandler(player_service, team_service, team_id)
    
    def _create_command_validator(self) -> ICommandValidator:
        """Create command validator."""
        from kickai.agents.handlers.command_validator import CommandValidator
        return CommandValidator()
    
    def _create_agent_orchestrator(self, team_id: str) -> IAgentOrchestrator:
        """Create agent orchestrator."""
        # This would create the main CrewAI system or agent orchestrator
        # For now, we'll create a simple implementation
        from kickai.agents.simple_agent_orchestrator import SimpleAgentOrchestrator
        return SimpleAgentOrchestrator(team_id)
    
    def _create_lifecycle_manager(self, team_id: str) -> ILifecycleManager:
        """Create lifecycle manager."""
        from kickai.agents.simple_lifecycle_manager import SimpleLifecycleManager
        return SimpleLifecycleManager(team_id)
    
    def health_check(self, team_id: str) -> Dict[str, Any]:
        """
        Perform health check on agent system.
        
        Args:
            team_id: Team identifier
            
        Returns:
            Health check results
        """
        try:
            router = self.create_agent_router(team_id)
            
            # Check all major components
            health_status = {
                "status": "healthy",
                "team_id": team_id,
                "components": {
                    "agent_router": "healthy",
                    "repository_factory": "healthy",
                    "service_factory": "healthy",
                }
            }
            
            logger.info(f"Health check passed for team {team_id}")
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed for team {team_id}: {e}")
            return {
                "status": "unhealthy",
                "team_id": team_id,
                "error": str(e)
            }
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._system_cache.clear()
        self.repository_factory.clear_cache()
        self.service_factory.clear_cache()
        logger.info("All factory caches cleared")
    
    @classmethod
    def create_for_testing(cls) -> AgentSystemFactory:
        """Create factory configured for testing."""
        return cls(config={
            "environment": "testing",
            "repositories": {"type": "mock"},
            "services": {"type": "mock"},
            "agents": {"type": "mock"}
        })
    
    @classmethod
    def create_for_development(cls) -> AgentSystemFactory:
        """Create factory configured for development."""
        return cls(config={
            "environment": "development",
            "repositories": {"type": "firebase"},
            "services": {"type": "real"},
            "agents": {"type": "crewai"}
        })
    
    @classmethod
    def create_for_production(cls) -> AgentSystemFactory:
        """Create factory configured for production."""
        return cls(config={
            "environment": "production",
            "repositories": {"type": "firebase"},
            "services": {"type": "real"},
            "agents": {"type": "crewai"},
            "caching": {"enabled": True},
            "monitoring": {"enabled": True}
        })
