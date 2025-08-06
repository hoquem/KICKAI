#!/usr/bin/env python3
"""
Simple ConfigurableAgent - Pure CrewAI 2025 Best Practices

This implements the correct CrewAI approach without over-engineering:
1. Task.config contains context
2. Tools receive parameters directly via LLM
3. No custom context management layers
"""

import traceback
from typing import Any

from crewai import Agent, Crew, Process, Task
from loguru import logger

from kickai.agents.tools_manager import AgentToolsManager
from kickai.config.agents import get_agent_config
from kickai.config.llm_config import get_llm_config
from kickai.core.enums import AgentRole


class SimpleConfigurableAgent:
    """
    Simple, clean ConfigurableAgent following pure CrewAI 2025 best practices.

    Key principles:
    - Task.config contains execution context
    - Tools receive parameters directly from LLM
    - No complex context management
    - CrewAI handles everything natively
    """

    def __init__(self, agent_role: AgentRole, team_id: str):
        """Initialize agent with role and team ID."""
        self.agent_role = agent_role
        self.team_id = team_id

        # Initialize components simply
        from kickai.agents.tool_registry import initialize_tool_registry
        tool_registry = initialize_tool_registry("kickai")
        tools_manager = AgentToolsManager(tool_registry)

        # Get LLM and agent config
        llm_config = get_llm_config()
        self.llm = llm_config.main_llm

        # Use default context for agent initialization
        context = {
            "team_name": "KICKAI",
            "team_id": team_id,
            "chat_type": "main",
            "user_role": "public",
            "username": "user"
        }
        self.config = get_agent_config(agent_role, context)

        # Get tools for this agent
        tools = tools_manager.get_tools_for_role(agent_role)

        # Create CrewAI agent
        self.crew_agent = Agent(
            role=self.config.role,
            goal=self.config.goal,
            backstory=self.config.backstory,
            tools=tools,
            llm=self.llm,
            verbose=True,
            max_iter=self.config.max_iterations,
        )

        logger.info(f"✅ SimpleConfigurableAgent created: {agent_role.value}")

    async def execute(self, task_description: str, context: dict[str, Any]) -> str:
        """
        Execute a task using pure CrewAI best practices.

        Args:
            task_description: Description of the task to execute
            context: Execution context (passed via Task.config)

        Returns:
            Result of the task execution
        """
        if not context:
            raise ValueError("Execution context is required")

        logger.info(f"🚀 Executing task for {self.agent_role.value}: {task_description[:50]}...")

        try:
            # Create enhanced task description with context values for LLM visibility
            enhanced_description = self._create_context_aware_prompt(task_description, context)

            # Create task with context in config (CrewAI best practice)
            task = Task(
                description=enhanced_description,
                agent=self.crew_agent,
                expected_output="A clear and helpful response based on the user's request.",
                config=context,  # Available for any custom tool implementations
            )

            # Create and execute crew
            crew = Crew(
                agents=[self.crew_agent],
                tasks=[task],
                process=Process.sequential,
                memory=False,
                verbose=True,
            )

            # Execute and return result
            result = crew.kickoff()

            logger.info(f"✅ Task completed for {self.agent_role.value}")
            return result.raw if hasattr(result, 'raw') else str(result)

        except Exception as e:
            logger.error(f"❌ Task execution failed for {self.agent_role.value}: {e}")
            logger.error(traceback.format_exc())
            return f"❌ Task execution failed: {e!s}"

    def _create_context_aware_prompt(self, task_description: str, context: dict[str, Any]) -> str:
        """
        Create a context-aware prompt that gives the LLM all the information it needs
        to call tools with the correct parameters.

        This is the CrewAI way - make context visible to the LLM so it can extract
        what it needs and pass to tools directly.
        """
        context_info = f"""Task: {task_description}

EXECUTION CONTEXT (use these values when calling tools):
- telegram_id: {context['telegram_id']}
- username: {context['username']}
- team_id: {context['team_id']}
- chat_type: {context['chat_type']}
- user_role: {context['user_role']}
- is_registered: {context['is_registered']}

INSTRUCTIONS:
1. Use the above context values as parameters when calling tools
2. For example, call get_available_commands(chat_type="{context['chat_type']}", user_role="{context['user_role']}", is_registered={context['is_registered']})
3. Always use the actual values from the context, not placeholder values
4. Provide a helpful response based on the user's request and their role/permissions"""

        return context_info
