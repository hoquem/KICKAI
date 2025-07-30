#!/usr/bin/env python3
"""
Help Assistant Agent for KICKAI

This agent specializes in providing help and guidance to users.
"""

import logging
from typing import Any

from crewai import Agent, Crew, Process, Task

from kickai.core.enums import AgentRole
from kickai.features.shared.domain.tools.help_tools import final_help_response
from kickai.utils.llm_factory import LLMFactory

logger = logging.getLogger(__name__)


def get_help_assistant_agent() -> "HelpAssistantAgent":
    """Get a help assistant agent instance with proper LLM configuration."""
    return HelpAssistantAgent()


class HelpAssistantAgent:
    """Agent responsible for providing help and command information."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools = [final_help_response]
        self.llm = LLMFactory.create_from_environment()  # Get the LLM instance

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
            llm=self.llm,  # Add the LLM
            memory=False,  # Temporarily disabled - CrewAI + Gemini memory compatibility issue
        )

    def process_help_request(self, context: dict[str, Any]) -> str:
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

            # Create the task with robust context enhancement
            base_task = """Generate a comprehensive help response for the user.

Requirements:
1. Use the FINAL_HELP_RESPONSE tool with the provided context
2. Ensure the response is tailored to the specific chat type
3. Include all relevant commands with descriptions
4. Format the response with proper emojis and structure
5. Make sure the response is complete and ready for the user

IMPORTANT: The FINAL_HELP_RESPONSE tool's output IS the final answer.
Do not modify or add to it - return it exactly as provided by the tool.

CRITICAL: You MUST use the context parameters provided to you when calling the FINAL_HELP_RESPONSE tool.
The context contains: chat_type, user_id, team_id, and username. Use these exact values."""

            # Enhance task with context parameters (robust approach)
            enhanced_task = base_task
            if context:
                # Build context info with robust handling
                context_info = []
                for key, value in context.items():
                    # Handle different value types robustly
                    if value is None:
                        context_info.append(f"{key}: null")
                    elif isinstance(value, str):
                        if value.strip():
                            context_info.append(f"{key}: {value}")
                        else:
                            context_info.append(f"{key}: empty")
                    else:
                        context_info.append(f"{key}: {value!s}")

                if context_info:
                    enhanced_task = f"{base_task}\n\nAvailable context parameters: {', '.join(context_info)}\n\nPlease use these context parameters when calling tools that require them."
                    self.logger.info(
                        f"🔧 [HELP ASSISTANT] Enhanced task with context: {', '.join(context_info)}"
                    )
                else:
                    self.logger.warning("🔧 [HELP ASSISTANT] No context parameters found!")

            # Create the task
            task = Task(
                description=enhanced_task,
                agent=agent,
                expected_output="A complete, formatted help response ready for the user",
                config=context or {},  # Pass context data through config for reference
            )

            # Temporarily disable memory to resolve CrewAI + Gemini compatibility issues
            memory_enabled = (
                False  # Temporarily disabled - CrewAI + Gemini memory compatibility issue
            )

            memory_config = None
            if memory_enabled:
                # Configure memory to use Google Gemini embeddings
                from kickai.core.settings import get_settings

                settings = get_settings()
                memory_config = {
                    "provider": "google",
                    "config": {
                        "api_key": settings.google_api_key,
                        "model": "text-embedding-004",  # Google's latest embedding model
                    },
                }

            # Create the crew
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True,  # Enable verbose mode for debugging
                memory=memory_enabled,  # Enable memory with Google Gemini configuration
                memory_config=memory_config,  # Use Google Gemini for embeddings
            )

            # Execute the crew
            result = crew.kickoff()

            self.logger.info(
                f"✅ Help response generated successfully for user {context.get('user_id')}"
            )
            return result

        except Exception as e:
            self.logger.error(f"❌ Error processing help request: {e}", exc_info=True)
            return "❌ I'm having trouble accessing the help system right now. Please try again in a moment."

    def get_supported_commands(self) -> list[str]:
        """Get list of commands this agent can help with."""
        return ["/help", "/info"]

    def can_handle_message(self, message: str) -> bool:
        """Check if this agent can handle the given message."""
        message_lower = message.lower().strip()
        help_keywords = [
            "help",
            "commands",
            "what can you do",
            "show commands",
            "how to",
            "guide",
            "assistance",
            "support",
        ]
        return any(keyword in message_lower for keyword in help_keywords)
