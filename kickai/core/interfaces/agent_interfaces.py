"""
Agent interfaces for dependency inversion.

These interfaces define contracts for agent components, enabling loose coupling
and testability across the agent system.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

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
    def metadata(self) -> dict[str, Any]:
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


            message: The user message to process
            context: The entity context for the request


    :return: Agent response with content and metadata
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check on the agent system.


    :return: Health status information
    :rtype: str  # TODO: Fix type
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


            message: The user message
            context: Entity context for routing decisions


    :return: Response from the selected agent
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    def select_agent(
        self,
        message: str,
        context: EntityContext
    ) -> AgentRole | None:
        """
        Select the most appropriate agent for a message.


            message: The user message
            context: Entity context for selection


    :return: Selected agent role or None if no suitable agent
    :rtype: str  # TODO: Fix type
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


            task_description: Description of the task to execute
            context: Entity context for the task


    :return: Agent response
    :rtype: str  # TODO: Fix type
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
    def get_tools(self) -> list[str]:
        """Get list of available tools for this agent."""
        pass


class ICrewSystem(ABC):
    """Interface for CrewAI system management."""

    @abstractmethod
    async def execute_with_crew(
        self,
        task_description: str,
        context: EntityContext,
        selected_agents: list[AgentRole] | None = None
    ) -> IAgentResponse:
        """
        Execute task using CrewAI with selected agents.


            task_description: Task to execute
            context: Entity context
            selected_agents: Specific agents to use (optional)


    :return: Crew execution response
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    def get_available_agents(self) -> list[AgentRole]:
        """Get list of available agent roles."""
        pass

    @abstractmethod
    def get_agent_by_role(self, role: AgentRole) -> IAgentSystem | None:
        """Get agent instance by role."""
        pass


class ILifecycleManager(ABC):
    """Interface for managing agent lifecycle."""

    @abstractmethod
    async def initialize_agents(self, team_id: str) -> None:
        """
        Initialize all agents for a team.


            team_id: Team identifier
        """
        pass

    @abstractmethod
    async def shutdown_agents(self, team_id: str) -> None:
        """
        Shutdown agents for a team.


            team_id: Team identifier
        """
        pass

    @abstractmethod
    def get_agent_system(self, team_id: str) -> ICrewSystem | None:
        """
        Get the agent system for a team.


            team_id: Team identifier


    :return: Agent system or None if not found
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """
        Check health of all managed agent systems.


    :return: Health status for all systems
    :rtype: str  # TODO: Fix type
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


            message: User message
            context: Entity context


    :return: User flow identifier
    :rtype: str  # TODO: Fix type
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


            message: User message
            context: Entity context


    :return: Response for unregistered user
    :rtype: str  # TODO: Fix type
        """
        pass


class IContactHandler(ABC):
    """Interface for handling contact sharing operations."""

    @abstractmethod
    async def handle_contact_share(
        self,
        contact_data: dict[str, Any],
        context: EntityContext
    ) -> IAgentResponse:
        """
        Handle contact sharing from Telegram.


            contact_data: Contact information from Telegram
            context: Entity context


    :return: Response to contact sharing
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    def validate_contact_data(
        self,
        contact_data: dict[str, Any]
    ) -> bool:
        """
        Validate contact data structure.


            contact_data: Contact data to validate


    :return: True if valid, False otherwise
    :rtype: str  # TODO: Fix type
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


            command: Command to validate
            context: Entity context for validation


    :return: True if command is valid for context
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    def is_helper_command(self, command: str) -> bool:
        """
        Check if command is a helper command.


            command: Command to check


    :return: True if helper command
    :rtype: str  # TODO: Fix type
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


            command: Invalid command
            context: Entity context


    :return: Error message for user
    :rtype: str  # TODO: Fix type
        """
        pass
