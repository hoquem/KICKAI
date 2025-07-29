"""
Helper Task Manager

Manages CrewAI task execution for the helper system.
"""

from crewai import Crew
from loguru import logger

from kickai.agents.helper_agent import HelperAgent


class HelperTaskManager:
    """Manages task execution for the helper system using CrewAI."""

    def __init__(self):
        self.helper_agent = HelperAgent()

    async def execute_help_task(
        self, user_query: str, user_id: str, team_id: str, context: dict = None
    ) -> str:
        """
        Execute a help task for a user.

        Args:
            user_query: The user's question or request
            user_id: The user's ID
            team_id: The team's ID
            context: Additional context about the user's situation

        Returns:
            Helpful response with guidance
        """
        try:
            # Create the help task
            help_task = self.helper_agent.create_help_task(user_query, user_id, team_id, context)

            # Create a crew with the helper agent
            crew = Crew(agents=[self.helper_agent], tasks=[help_task], verbose=True)

            # Execute the task
            result = await crew.kickoff()

            return result

        except Exception as e:
            logger.error(f"Error executing help task for user {user_id}: {e}")
            return "❌ Sorry, I encountered an error while helping you. Please try again."

    async def execute_suggestion_task(self, user_id: str, team_id: str, context: str) -> str | None:
        """
        Execute a suggestion task for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            context: Context about the user's current activity

        Returns:
            Proactive suggestion message
        """
        try:
            # Create the suggestion task
            suggestion_task = self.helper_agent.create_suggestion_task(user_id, team_id, context)

            # Create a crew with the helper agent
            crew = Crew(agents=[self.helper_agent], tasks=[suggestion_task], verbose=True)

            # Execute the task
            result = await crew.kickoff()

            return result

        except Exception as e:
            logger.error(f"Error executing suggestion task for user {user_id}: {e}")
            return None

    async def execute_celebration_task(self, user_id: str, team_id: str, achievement: str) -> str:
        """
        Execute a celebration task for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            achievement: Description of the achievement

        Returns:
            Celebration message
        """
        try:
            # Create the celebration task
            celebration_task = self.helper_agent.create_celebration_task(
                user_id, team_id, achievement
            )

            # Create a crew with the helper agent
            crew = Crew(agents=[self.helper_agent], tasks=[celebration_task], verbose=True)

            # Execute the task
            result = await crew.kickoff()

            return result

        except Exception as e:
            logger.error(f"Error executing celebration task for user {user_id}: {e}")
            return f"🎉 Congratulations on your achievement: {achievement}!"

    async def execute_learning_guidance_task(
        self, user_id: str, team_id: str, learning_goal: str
    ) -> str:
        """
        Execute a learning guidance task for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            learning_goal: The user's learning goal

        Returns:
            Learning guidance and roadmap
        """
        try:
            # Create the learning guidance task
            guidance_task = self.helper_agent.create_learning_guidance_task(
                user_id, team_id, learning_goal
            )

            # Create a crew with the helper agent
            crew = Crew(agents=[self.helper_agent], tasks=[guidance_task], verbose=True)

            # Execute the task
            result = await crew.kickoff()

            return result

        except Exception as e:
            logger.error(f"Error executing learning guidance task for user {user_id}: {e}")
            return "❌ Sorry, I encountered an error while creating your learning plan. Please try again."

    async def execute_troubleshooting_task(
        self, user_id: str, team_id: str, issue_description: str
    ) -> str:
        """
        Execute a troubleshooting task for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            issue_description: Description of the issue

        Returns:
            Troubleshooting guidance
        """
        try:
            # Create the troubleshooting task
            troubleshooting_task = self.helper_agent.create_troubleshooting_task(
                user_id, team_id, issue_description
            )

            # Create a crew with the helper agent
            crew = Crew(agents=[self.helper_agent], tasks=[troubleshooting_task], verbose=True)

            # Execute the task
            result = await crew.kickoff()

            return result

        except Exception as e:
            logger.error(f"Error executing troubleshooting task for user {user_id}: {e}")
            return (
                "❌ Sorry, I encountered an error while helping you troubleshoot. Please try again."
            )

    async def execute_feature_overview_task(
        self, user_id: str, team_id: str, feature_name: str
    ) -> str:
        """
        Execute a feature overview task for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            feature_name: Name of the feature to overview

        Returns:
            Feature overview and guidance
        """
        try:
            # Create the feature overview task
            overview_task = self.helper_agent.create_feature_overview_task(
                user_id, team_id, feature_name
            )

            # Create a crew with the helper agent
            crew = Crew(agents=[self.helper_agent], tasks=[overview_task], verbose=True)

            # Execute the task
            result = await crew.kickoff()

            return result

        except Exception as e:
            logger.error(f"Error executing feature overview task for user {user_id}: {e}")
            return f"❌ Sorry, I encountered an error while explaining the {feature_name} feature. Please try again."
