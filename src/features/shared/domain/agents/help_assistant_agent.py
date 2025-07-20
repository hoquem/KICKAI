#!/usr/bin/env python3
"""
Help Assistant Agent for KICKAI

This agent processes help requests with proper user validation and context-aware responses.
It follows the feature-based architecture and uses specific tools for operations.
"""

from typing import Dict, Any, Optional
from loguru import logger
from crewai import Agent, Task, Crew
# Tool is not needed for this agent

from core.enums import ChatType
from core.agent_registry import (
    AgentType, AgentCategory, register_agent_decorator, get_agent_registry
)
from features.shared.domain.tools.help_tools import (
    get_user_status_tool,
    get_available_commands_tool,
    format_help_message_tool,
    process_user_registration_flow_tool,
    get_user_display_info_tool
)


@register_agent_decorator(
    agent_id="help_assistant",
    agent_type=AgentType.HELP_ASSISTANT,
    category=AgentCategory.CORE,
    description="Provides context-aware help information to KICKAI users with proper user validation and registration flows",
    version="1.0.0",
    enabled=True,
    dependencies=["permission_service", "player_service", "team_service"],
    tools=[
        "get_user_status",
        "get_available_commands", 
        "format_help_message",
        "process_user_registration_flow",
        "get_user_display_info"
    ],
    feature_module="shared",
    tags=["help", "assistance", "user-validation", "registration"]
)
class HelpAssistantAgent:
    """
    Help Assistant Agent for processing help requests.
    
    This agent follows the feature-based architecture and provides:
    - User status validation
    - Context-aware help responses
    - Proper registration flow handling
    - Message formatting with user context
    """
    
    def __init__(self):
        """Initialize the help assistant agent."""
        self.tools = [
            get_user_status_tool,
            get_available_commands_tool,
            format_help_message_tool,
            process_user_registration_flow_tool,
            get_user_display_info_tool
        ]
        
        logger.info("✅ HelpAssistantAgent initialized")
    
    def create_agent(self) -> Agent:
        """Create the help assistant agent with proper configuration."""
        return Agent(
            role="Help Assistant",
            goal="Provide context-aware help information to KICKAI users",
            backstory="""You are a helpful assistant for the KICKAI football team management system. 
            You provide accurate, context-aware help information based on the user's status and chat type.
            You always validate user status before providing help and guide users through proper registration flows.
            
            CRITICAL RULES:
            1. ALWAYS use the get_user_status tool first to validate user status
            2. ALWAYS use the format_help_message tool to format responses
            3. NEVER fabricate user information or command lists
            4. ALWAYS provide proper registration guidance for unregistered users
            5. Use the exact message formats specified in the documentation
            6. Address users by their telegram name in responses
            7. Provide clear, actionable guidance for all user states""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools
        )
    
    async def process_help_request(self,
                                 user_id: str,
                                 team_id: str,
                                 chat_type: str,
                                 telegram_username: str = "",
                                 telegram_name: str = "") -> str:
        """
        Process a help request with full validation and context.
        
        Args:
            user_id: Telegram user ID
            team_id: Team ID
            chat_type: Type of chat (main_chat|leadership_chat)
            telegram_username: Telegram username (optional)
            telegram_name: Telegram display name (optional)
            
        Returns:
            Formatted help response string
        """
        try:
            # Create the agent
            agent = self.create_agent()
            
            # Create the help processing task
            task = Task(
                description=self._create_help_task_description(
                    user_id, team_id, chat_type, telegram_username, telegram_name
                ),
                agent=agent,
                expected_output="A complete, context-aware help response for the user following the exact message formats from the specification"
            )
            
            # Create and run the crew
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=True
            )
            
            # Execute the task
            result = await crew.kickoff()
            
            logger.info(f"✅ Help request processed for user {user_id} in {chat_type}")
            return str(result)
            
        except Exception as e:
            logger.error(f"❌ Error processing help request: {e}")
            return f"❌ Error processing help request: {str(e)}"
    
    def _create_help_task_description(self,
                                    user_id: str,
                                    team_id: str,
                                    chat_type: str,
                                    telegram_username: str,
                                    telegram_name: str) -> str:
        """
        Create a detailed task description for the help assistant.
        
        This follows the ground rules for clearly defining tasks.
        """
        return f"""
You are a help assistant for the KICKAI football team management system.

CONTEXT:
- Chat Type: {chat_type}
- User ID: {user_id}
- Team ID: {team_id}
- Telegram Username: {telegram_username}
- Telegram Name: {telegram_name}

AVAILABLE TOOLS:
- get_user_status: Get current user's player/team member status
- get_available_commands: Get list of commands available to this user
- format_help_message: Format help message based on context and user status
- process_user_registration_flow: Handle user registration flows
- get_user_display_info: Get user display information for message formatting

TASK:
1. Use get_user_status to determine the user's current status
2. Use format_help_message to generate the appropriate help response
3. The format_help_message tool will automatically:
   - Check if user is registered
   - Format the appropriate message based on chat type and user status

CHAT CONTEXT RULES:
- MAIN CHAT: Treat everyone as players (even if they're also team members)
- LEADERSHIP CHAT: Treat everyone as team members (even if they're also players)
- This ensures clean separation and avoids confusion between contexts

MANDATORY PROCESS:
1. Call get_user_status with user_id={user_id}, team_id={team_id}, chat_type="{chat_type}"
2. Call format_help_message with the user_status result and telegram_name="{telegram_name}"
3. Return the exact output from format_help_message

MESSAGE FORMATS (from specification):
- Main Chat - Unregistered: Welcome message asking to contact leadership
- Main Chat - Registered: Player commands list (treat as player regardless of other registrations)
- Leadership Chat - First User: Admin setup message
- Leadership Chat - Unregistered: Team member registration message
- Leadership Chat - Registered: Team member commands list (treat as team member regardless of other registrations)

IMPORTANT RULES:
- Internally refer to users by their telegram ID and player/member ID
- In messages to users, always refer to them using their telegram name
- When displaying user's actual name, use their actual name, not telegram name
- Always validate user status before providing help
- Provide clear, actionable guidance for unregistered users
- Format messages with proper Markdown for Telegram
- Use the exact message formats specified in the documentation
- Main chat context = player context, Leadership chat context = team member context

EXPECTED OUTPUT:
A complete, context-aware help response that:
- Addresses the user by their telegram name
- Provides appropriate registration guidance if needed
- Shows available commands if user is registered
- Uses proper formatting and emojis
- Follows the established message formatting guidelines
- Respects the chat context (player vs team member)
"""

    async def process_specific_command_help(self,
                                          command_name: str,
                                          user_id: str,
                                          team_id: str,
                                          chat_type: str) -> str:
        """
        Process help for a specific command.
        
        Args:
            command_name: Name of the command (e.g., "/register", "/list")
            user_id: Telegram user ID
            team_id: Team ID
            chat_type: Type of chat (main_chat|leadership_chat)
            
        Returns:
            Specific command help response
        """
        try:
            # Create the agent
            agent = self.create_agent()
            
            # Create specific command help task
            task = Task(
                description=self._create_specific_command_task_description(
                    command_name, user_id, team_id, chat_type
                ),
                agent=agent,
                expected_output=f"Detailed help information for the {command_name} command"
            )
            
            # Create and run the crew
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=True
            )
            
            # Execute the task
            result = await crew.kickoff()
            
            logger.info(f"✅ Specific command help processed for {command_name} - user {user_id}")
            return str(result)
            
        except Exception as e:
            logger.error(f"❌ Error processing specific command help: {e}")
            return f"❌ Error processing help for {command_name}: {str(e)}"
    
    def _create_specific_command_task_description(self,
                                                command_name: str,
                                                user_id: str,
                                                team_id: str,
                                                chat_type: str) -> str:
        """Create task description for specific command help."""
        return f"""
You are a help assistant for the KICKAI football team management system.

CONTEXT:
- Command: {command_name}
- Chat Type: {chat_type}
- User ID: {user_id}
- Team ID: {team_id}

AVAILABLE TOOLS:
- get_user_status: Get current user's player/team member status
- get_available_commands: Get list of commands available to this user
- get_user_display_info: Get user display information

TASK:
1. Use get_user_status to check if the user has permission to use this command
2. Use get_available_commands to get detailed command information
3. Provide specific help for the {command_name} command including:
   - Command description and purpose
   - Usage syntax and examples
   - Permission requirements
   - Available in which chat types
   - Related commands

MANDATORY PROCESS:
1. Call get_user_status with user_id={user_id}, team_id={team_id}, chat_type="{chat_type}"
2. Call get_available_commands with chat_type="{chat_type}", user_id={user_id}, team_id={team_id}
3. Find the {command_name} command in the available commands
4. Provide detailed help information for that specific command

EXPECTED OUTPUT:
Detailed help information for {command_name} including:
- Command description
- Usage syntax
- Examples
- Permission requirements
- Chat type availability
- Related commands
"""


# Factory function to get help assistant agent instance
def get_help_assistant_agent() -> HelpAssistantAgent:
    """Get the help assistant agent instance."""
    return HelpAssistantAgent() 