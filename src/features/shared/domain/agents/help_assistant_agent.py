#!/usr/bin/env python3
"""
Help Assistant Agent for KICKAI

This agent processes help requests with proper user validation and context-aware responses.
It follows the feature-based architecture and uses specific tools for operations.
"""

from typing import Dict, Any, Optional
from loguru import logger
from crewai import Agent, Task, Crew
from crewai.tools import Tool

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
            You always validate user status before providing help and guide users through proper registration flows.""",
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
                expected_output="A complete, context-aware help response for the user"
            )
            
            # Create and run the crew
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=True
            )
            
            # Execute the task
            result = crew.kickoff()
            
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
- format_help_message: Format help message based on context
- process_user_registration_flow: Handle user registration flows
- get_user_display_info: Get user display information for message formatting

TASK:
1. Determine user's current status using get_user_status
2. If user is not registered:
   - For main_chat: Ask them to contact leadership team to add them as a player
   - For leadership_chat: 
     - If first user: Welcome them and ask for admin registration
     - If not first user: Ask them to provide details for team member registration
3. If user is registered:
   - Get available commands using get_available_commands
   - Get user display info using get_user_display_info
   - Format appropriate help message using format_help_message
4. Return contextually appropriate help information

IMPORTANT RULES:
- Internally refer to users by their telegram ID and player/member ID
- In messages to users, always refer to them using their telegram name and player/member ID
- When displaying user's actual name, use their actual name, not telegram name
- Always validate user status before providing help
- Provide clear, actionable guidance for unregistered users
- Format messages with proper Markdown for Telegram

EXPECTED OUTPUT:
A complete, context-aware help response that:
- Addresses the user by their telegram name
- Provides appropriate registration guidance if needed
- Shows available commands if user is registered
- Uses proper formatting and emojis
- Follows the established message formatting guidelines
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
            result = crew.kickoff()
            
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
- format_help_message: Format help message based on context
- process_user_registration_flow: Handle user registration flows
- get_user_display_info: Get user display information for message formatting

TASK:
1. Determine user's current status using get_user_status
2. Check if user has access to the {command_name} command
3. If user is not registered or doesn't have access:
   - Provide appropriate registration guidance
   - Explain why they can't use this command
4. If user has access:
   - Provide detailed help for the {command_name} command
   - Include usage examples and syntax
   - Explain what the command does
   - Mention any permissions or requirements
5. Return comprehensive help for the specific command

IMPORTANT RULES:
- Always validate user permissions before providing command help
- Provide clear examples and syntax
- Explain any prerequisites or requirements
- Use proper Markdown formatting
- Include relevant emojis for better readability

EXPECTED OUTPUT:
Detailed help information for the {command_name} command that includes:
- Command description and purpose
- Usage syntax and examples
- Permission requirements
- Any prerequisites or setup needed
- Common use cases
- Troubleshooting tips if applicable
"""


def get_help_assistant_agent() -> HelpAssistantAgent:
    """Get the help assistant agent instance."""
    return HelpAssistantAgent() 