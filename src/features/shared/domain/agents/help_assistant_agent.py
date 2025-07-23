#!/usr/bin/env python3
"""
Help Assistant Agent for KICKAI

This agent specializes in providing help and guidance to users.
"""

import logging
from typing import Any

from crewai import Agent, Crew, Process, Task

from core.enums import AgentRole
from features.shared.domain.tools.help_tools import GenerateHelpResponseTool

logger = logging.getLogger(__name__)


class HelpAssistantAgent:
    """Agent responsible for providing help and command information."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools = [GenerateHelpResponseTool()]

    def create_agent(self) -> Agent:
        """Create the help assistant agent."""
        return Agent(
            role=AgentRole.HELP_ASSISTANT.value,
            goal="Provide comprehensive help and guidance to users by understanding their context and showing relevant commands",
            backstory="""You are an expert help assistant for the KICKAI football team management system. 
            You understand the different chat types (main chat vs leadership chat) and can provide 
            contextually appropriate help and command information. You always use the FINAL_HELP_RESPONSE 
            tool to generate complete, formatted help responses.""",
            verbose=True,  # Enable verbose mode for debugging
            allow_delegation=False,
            tools=self.tools,
            memory=True
        )

    async def process_help_request(self, context: dict[str, Any]) -> str:
        """
        Process a help request using the help assistant agent.
        
        Args:
            context: Dictionary containing:
                - chat_type: Chat type (string or enum)
                - user_id: User ID
                - team_id: Team ID
                - username: Username (optional)
                - message_text: Original message (optional)
        
        Returns:
            Formatted help response string
        """
        try:
            # Create the agent
            agent = self.create_agent()

            # Create the task
            task = Task(
                description=f"""Generate a comprehensive help response for the user.
                
                Context:
                - Chat Type: {context.get('chat_type', 'unknown')}
                - User ID: {context.get('user_id', 'unknown')}
                - Username: {context.get('username', 'unknown')}
                - Message: {context.get('message_text', 'help request')}
                
                Requirements:
                1. Use the FINAL_HELP_RESPONSE tool with the provided context
                2. Ensure the response is tailored to the specific chat type
                3. Include all relevant commands with descriptions
                4. Format the response with proper emojis and structure
                5. Make sure the response is complete and ready for the user
                
                IMPORTANT: The FINAL_HELP_RESPONSE tool's output IS the final answer.
                Do not modify or add to it - return it exactly as provided by the tool.""",
                agent=agent,
                expected_output="A complete, formatted help response ready for the user"
            )

            # Create the crew
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True  # Enable verbose mode for debugging
            )

            # Execute the crew
            result = await crew.kickoff()

            self.logger.info(f"✅ Help response generated successfully for user {context.get('user_id')}")
            return result

        except Exception as e:
            self.logger.error(f"❌ Error processing help request: {e}", exc_info=True)
            return "❌ I'm having trouble accessing the help system right now. Please try again in a moment."

    def get_supported_commands(self) -> list[str]:
        """Get list of commands this agent can help with."""
        return ["/help", "/start", "/info"]

    def can_handle_message(self, message: str) -> bool:
        """Check if this agent can handle the given message."""
        message_lower = message.lower().strip()
        help_keywords = [
            "help", "commands", "what can you do", "show commands",
            "how to", "guide", "assistance", "support"
        ]
        return any(keyword in message_lower for keyword in help_keywords)
