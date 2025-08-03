"""
Refactored Agentic Message Router with Dependency Injection.

This module provides a clean, dependency-injected version of the message router
that follows SOLID principles and enables better testing and maintainability.
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from loguru import logger

from kickai.core.interfaces import (
    IAgentRouter, IAgentResponse, IAgentOrchestrator, ILifecycleManager,
    IUserFlowHandler, IContactHandler, ICommandValidator, IUserService
)
from kickai.core.value_objects import EntityContext
from kickai.core.enums import ChatType


class AgentResponse:
    """Simple agent response implementation."""
    
    def __init__(self, content: str, metadata: dict = None):
        self._content = content
        self._metadata = metadata or {}
    
    @property
    def content(self) -> str:
        return self._content
    
    @property
    def metadata(self) -> dict:
        return self._metadata


class RefactoredAgenticMessageRouter(IAgentRouter):
    """
    Refactored message router using dependency injection.
    
    This router implements the single responsibility principle by delegating
    specific concerns to specialized handlers. It serves as an orchestrator
    that coordinates between handlers and the agent system.
    
    Key improvements:
    - Dependency injection for all components
    - Single responsibility principle
    - No circular dependencies
    - Testable design
    - Clear separation of concerns
    """
    
    def __init__(
        self,
        team_id: str,
        agent_orchestrator: IAgentOrchestrator,
        lifecycle_manager: ILifecycleManager,
        user_flow_handler: IUserFlowHandler,
        contact_handler: IContactHandler,
        command_validator: ICommandValidator,
        user_service: IUserService,
    ):
        """
        Initialize router with injected dependencies.
        
        Args:
            team_id: Team identifier
            agent_orchestrator: Main agent system for message processing
            lifecycle_manager: Manages agent lifecycle
            user_flow_handler: Handles user flow determination
            contact_handler: Handles contact sharing
            command_validator: Validates commands and permissions
            user_service: Provides user-related services
        """
        self.team_id = team_id
        self._agent_orchestrator = agent_orchestrator
        self._lifecycle_manager = lifecycle_manager
        self._user_flow_handler = user_flow_handler
        self._contact_handler = contact_handler
        self._command_validator = command_validator
        self._user_service = user_service
        
        logger.info(f"🤖 RefactoredAgenticMessageRouter initialized for team {team_id}")
    
    async def route_message(
        self,
        message: str,
        context: EntityContext
    ) -> IAgentResponse:
        """
        Route message to the most appropriate handler/agent.
        
        This method implements the main routing logic using injected handlers,
        following a clean chain of responsibility pattern.
        
        Args:
            message: The user message
            context: Entity context for routing decisions
            
        Returns:
            Response from the selected handler/agent
        """
        try:
            logger.info(
                f"🔄 Routing message from user {context.user_id} in {context.chat_type.value}"
            )
            
            # Step 1: Handle contact sharing (highest priority)
            if await self._is_contact_share_message(message, context):
                return await self._handle_contact_sharing(message, context)
            
            # Step 2: Extract and validate commands
            command = self._extract_command(message)
            if command and not self._command_validator.validate_command_for_chat(command, context):
                return self._create_command_validation_error(command, context)
            
            # Step 3: Handle helper commands directly
            if command and self._command_validator.is_helper_command(command):
                return await self._handle_helper_command(command, context)
            
            # Step 4: Determine user flow for unregistered users
            if not context.user_registration.is_registered:
                return await self._handle_unregistered_user(message, context)
            
            # Step 5: Route to main agent system for registered users
            return await self._route_to_agent_system(message, context)
            
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            return self._create_error_response(str(e))
    
    def select_agent(
        self,
        message: str,
        context: EntityContext
    ) -> Optional[str]:
        """
        Select the most appropriate agent for a message.
        
        This is a simpler method that just returns the agent type
        without executing the full routing pipeline.
        
        Args:
            message: The user message
            context: Entity context for selection
            
        Returns:
            Selected agent role or None if no suitable agent
        """
        try:
            # Contact sharing -> Contact handler
            if self._looks_like_contact_share(message):
                return "contact_handler"
            
            # Helper commands -> Help system
            command = self._extract_command(message)
            if command and self._command_validator.is_helper_command(command):
                return "help_assistant"
            
            # Unregistered users -> User flow handler
            if not context.user_registration.is_registered:
                return "user_flow_handler"
            
            # Registered users -> Main agent system
            if context.user_registration.has_any_role():
                return "agent_orchestrator"
            
            return "command_fallback_agent"
            
        except Exception as e:
            logger.error(f"Error selecting agent: {e}")
            return "command_fallback_agent"
    
    async def _is_contact_share_message(
        self, 
        message: str, 
        context: EntityContext
    ) -> bool:
        """Check if message represents contact sharing."""
        # This would typically check message metadata or structure
        # For now, we'll use a simple heuristic
        return (
            "contact" in message.lower() or
            "phone_number" in message.lower() or
            self._looks_like_contact_share(message)
        )
    
    def _looks_like_contact_share(self, message: str) -> bool:
        """Check if message looks like contact data."""
        # Simple heuristic - real implementation would check Telegram message structure
        return (
            ("first_name" in message.lower() and "phone" in message.lower()) or
            ("contact" in message.lower() and "+" in message)
        )
    
    async def _handle_contact_sharing(
        self, 
        message: str, 
        context: EntityContext
    ) -> IAgentResponse:
        """Handle contact sharing through contact handler."""
        # Parse contact data from message (simplified)
        contact_data = self._parse_contact_data(message)
        return await self._contact_handler.handle_contact_share(contact_data, context)
    
    def _parse_contact_data(self, message: str) -> Dict[str, Any]:
        """Parse contact data from message (simplified implementation)."""
        # In real implementation, this would parse Telegram contact structure
        return {
            "first_name": "Contact",
            "last_name": "User",
            "phone_number": "+44123456789"  # Extract from message
        }
    
    def _extract_command(self, message: str) -> Optional[str]:
        """Extract command from message."""
        message = message.strip()
        if message.startswith("/"):
            return message.split()[0].lower()
        return None
    
    def _create_command_validation_error(
        self, 
        command: str, 
        context: EntityContext
    ) -> IAgentResponse:
        """Create validation error response."""
        error_message = self._command_validator.get_validation_error_message(
            command, context
        )
        return AgentResponse(
            content=error_message,
            metadata={"error": "command_validation", "command": command}
        )
    
    async def _handle_helper_command(
        self, 
        command: str, 
        context: EntityContext
    ) -> IAgentResponse:
        """Handle helper commands."""
        if command == "/help":
            return self._create_help_response(context)
        elif command == "/commands":
            return self._create_commands_response(context)
        elif command in ["/status", "/info"]:
            return self._create_status_response(context)
        else:
            return AgentResponse(
                content=f"Helper command {command} not implemented yet.",
                metadata={"command": command, "type": "helper"}
            )
    
    def _create_help_response(self, context: EntityContext) -> IAgentResponse:
        """Create help response."""
        available_commands = self._command_validator.get_available_commands(context)
        commands_str = "\n".join(f"• {cmd}" for cmd in available_commands[:10])
        
        return AgentResponse(
            content=f"""🤖 **KICKAI Help**

**Available Commands:**
{commands_str}

**Chat Types:**
• Main Chat: Player commands
• Leadership Chat: Admin commands  
• Private Chat: Personal commands

**Getting Started:**
• New users: Share contact or type /register
• Players: Use /myinfo, /available, /list
• Leadership: Use /approve, /add, /update

Need specific help? Ask me anything! ⚽""",
            metadata={"type": "help", "commands_count": len(available_commands)}
        )
    
    def _create_commands_response(self, context: EntityContext) -> IAgentResponse:
        """Create commands list response."""
        available_commands = self._command_validator.get_available_commands(context)
        commands_str = "\n".join(f"• {cmd}" for cmd in available_commands)
        
        return AgentResponse(
            content=f"""📋 **Available Commands**

{commands_str}

**Your Role:** {context.user_registration.primary_role()}
**Chat Type:** {context.chat_type.value}

Type /help for detailed guidance.""",
            metadata={"type": "commands", "role": context.user_registration.primary_role()}
        )
    
    def _create_status_response(self, context: EntityContext) -> IAgentResponse:
        """Create status response."""
        return AgentResponse(
            content=f"""📊 **System Status**

**User:** {context.username or 'Unknown'}
**Role:** {context.user_registration.primary_role()}
**Team:** {context.team_id}
**Chat:** {context.chat_type.value}
**Registered:** {'✅' if context.user_registration.is_registered else '❌'}

**Permissions:**
• Player: {'✅' if context.user_registration.is_player else '❌'}
• Team Member: {'✅' if context.user_registration.is_team_member else '❌'}
• Leadership: {'✅' if context.user_registration.is_leadership else '❌'}
• Admin: {'✅' if context.user_registration.is_admin else '❌'}

System is operational! ⚽""",
            metadata={
                "type": "status",
                "user_context": context.to_dict()
            }
        )
    
    async def _handle_unregistered_user(
        self, 
        message: str, 
        context: EntityContext
    ) -> IAgentResponse:
        """Handle unregistered user through user flow handler."""
        return await self._user_flow_handler.handle_unregistered_user(message, context)
    
    async def _route_to_agent_system(
        self, 
        message: str, 
        context: EntityContext
    ) -> IAgentResponse:
        """Route to main agent orchestrator system."""
        return await self._agent_orchestrator.process_message(message, context)
    
    def _create_error_response(self, error: str) -> IAgentResponse:
        """Create error response."""
        return AgentResponse(
            content="❌ Sorry, I encountered an error processing your request. Please try again.",
            metadata={"error": error, "type": "system_error"}
        )