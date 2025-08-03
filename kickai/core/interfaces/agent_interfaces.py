"""
Agent interfaces for dependency inversion.

These interfaces define contracts for agent components, enabling loose coupling
and testability across the agent system.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from kickai.core.enums import AgentRole
from kickai.core.value_objects import EntityContext


class IAgentResponse(ABC):
    """Interface for agent responses."""
    
    @property
    @abstractmethod
    def content(self) -> str:
        """Get the response content."""
        pass
    
    @property 
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Get response metadata."""
        pass


class IAgentOrchestrator(ABC):
    """Interface for agent orchestration systems."""
    
    @abstractmethod
    async def process_message(
        self, 
        message: str, 
        context: EntityContext
    ) -> IAgentResponse:
        """
        Process a message using appropriate agents.
        
        Args:
            message: The user message to process
            context: The entity context for the request
            
        Returns:
            Agent response with content and metadata
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the agent system.
        
        Returns:
            Health status information
        """
        pass


class IAgentRouter(ABC):
    """Interface for routing messages to appropriate agents."""
    
    @abstractmethod
    async def route_message(
        self,
        message: str,
        context: EntityContext
    ) -> IAgentResponse:
        """
        Route message to the most appropriate agent.
        
        Args:
            message: The user message
            context: Entity context for routing decisions
            
        Returns:
            Response from the selected agent
        """
        pass
    
    @abstractmethod
    def select_agent(
        self,
        message: str,
        context: EntityContext
    ) -> Optional[AgentRole]:
        """
        Select the most appropriate agent for a message.
        
        Args:
            message: The user message
            context: Entity context for selection
            
        Returns:
            Selected agent role or None if no suitable agent
        """
        pass


class IAgentSystem(ABC):
    """Interface for individual agent systems."""
    
    @abstractmethod
    async def execute_task(
        self,
        task_description: str,
        context: EntityContext
    ) -> IAgentResponse:
        """
        Execute a task using this agent.
        
        Args:
            task_description: Description of the task to execute
            context: Entity context for the task
            
        Returns:
            Agent response
        """
        pass
    
    @property
    @abstractmethod
    def role(self) -> AgentRole:
        """Get the agent role."""
        pass
    
    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if agent is enabled."""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[str]:
        """Get list of available tools for this agent."""
        pass


class ICrewSystem(ABC):
    """Interface for CrewAI system management."""
    
    @abstractmethod
    async def execute_with_crew(
        self,
        task_description: str,
        context: EntityContext,
        selected_agents: Optional[List[AgentRole]] = None
    ) -> IAgentResponse:
        """
        Execute task using CrewAI with selected agents.
        
        Args:
            task_description: Task to execute
            context: Entity context
            selected_agents: Specific agents to use (optional)
            
        Returns:
            Crew execution response
        """
        pass
    
    @abstractmethod
    def get_available_agents(self) -> List[AgentRole]:
        """Get list of available agent roles."""
        pass
    
    @abstractmethod
    def get_agent_by_role(self, role: AgentRole) -> Optional[IAgentSystem]:
        """Get agent instance by role."""
        pass


class ILifecycleManager(ABC):
    """Interface for managing agent lifecycle."""
    
    @abstractmethod
    async def initialize_agents(self, team_id: str) -> None:
        """
        Initialize all agents for a team.
        
        Args:
            team_id: Team identifier
        """
        pass
    
    @abstractmethod
    async def shutdown_agents(self, team_id: str) -> None:
        """
        Shutdown agents for a team.
        
        Args:
            team_id: Team identifier
        """
        pass
    
    @abstractmethod
    def get_agent_system(self, team_id: str) -> Optional[ICrewSystem]:
        """
        Get the agent system for a team.
        
        Args:
            team_id: Team identifier
            
        Returns:
            Agent system or None if not found
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of all managed agent systems.
        
        Returns:
            Health status for all systems
        """
        pass


class IUserFlowHandler(ABC):
    """Interface for handling user flow determination."""
    
    @abstractmethod
    async def determine_user_flow(
        self,
        message: str,
        context: EntityContext
    ) -> str:
        """
        Determine the appropriate user flow for a message.
        
        Args:
            message: User message
            context: Entity context
            
        Returns:
            User flow identifier
        """
        pass
    
    @abstractmethod
    async def handle_unregistered_user(
        self,
        message: str,
        context: EntityContext
    ) -> IAgentResponse:
        """
        Handle messages from unregistered users.
        
        Args:
            message: User message
            context: Entity context
            
        Returns:
            Response for unregistered user
        """
        pass


class IContactHandler(ABC):
    """Interface for handling contact sharing operations."""
    
    @abstractmethod
    async def handle_contact_share(
        self,
        contact_data: Dict[str, Any],
        context: EntityContext
    ) -> IAgentResponse:
        """
        Handle contact sharing from Telegram.
        
        Args:
            contact_data: Contact information from Telegram
            context: Entity context
            
        Returns:
            Response to contact sharing
        """
        pass
    
    @abstractmethod
    def validate_contact_data(
        self,
        contact_data: Dict[str, Any]
    ) -> bool:
        """
        Validate contact data structure.
        
        Args:
            contact_data: Contact data to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass


class ICommandValidator(ABC):
    """Interface for command validation."""
    
    @abstractmethod
    def validate_command_for_chat(
        self,
        command: str,
        context: EntityContext
    ) -> bool:
        """
        Validate if command is allowed in the given context.
        
        Args:
            command: Command to validate
            context: Entity context for validation
            
        Returns:
            True if command is valid for context
        """
        pass
    
    @abstractmethod
    def is_helper_command(self, command: str) -> bool:
        """
        Check if command is a helper command.
        
        Args:
            command: Command to check
            
        Returns:
            True if helper command
        """
        pass
    
    @abstractmethod
    def get_validation_error_message(
        self,
        command: str,
        context: EntityContext
    ) -> str:
        """
        Get error message for invalid command.
        
        Args:
            command: Invalid command
            context: Entity context
            
        Returns:
            Error message for user
        """
        pass