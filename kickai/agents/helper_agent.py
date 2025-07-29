"""
Helper Agent

An intelligent, proactive assistance agent designed to transform team members
from novice users into proficient KICKAI system operators.
"""

from crewai import Agent, Task

from kickai.core.agent_registry import AgentCategory, AgentType, register_agent_decorator
from kickai.features.helper_system.domain.tools import (
    celebrate_progress,
    format_help_response,
    get_contextual_suggestions,
    get_learning_analytics,
    get_personalized_feature_recommendations,
    send_learning_reminder,
    send_proactive_notification,
    track_user_progress,
)
from kickai.features.shared.domain.tools.help_tools import get_command_help


@register_agent_decorator(
    agent_id="helper_assistant",
    agent_type=AgentType.HELP_ASSISTANT,
    category=AgentCategory.CORE,
    name="Helper Assistant",
    description="Intelligent, proactive assistance agent for user guidance and learning support",
    version="1.0.0",
    enabled=True,
    dependencies=[],
    tools=[
        "get_command_help",
        "get_personalized_feature_recommendations",
        "send_learning_reminder",
        "track_user_progress",
        "get_contextual_suggestions",
        "format_help_response",
        "send_proactive_notification",
        "get_learning_analytics",
        "celebrate_progress",
    ],
    feature_module="helper_system",
    tags=["help", "guidance", "learning", "proactive"],
    aliases=["helper", "assistant", "guide"],
)
class HelperAgent(Agent):
    """KICKAI Helper Agent for intelligent user assistance and guidance."""

    def __init__(self):
        super().__init__(
            role="HELPER_ASSISTANT",
            goal="Guide team members to become proficient KICKAI users through intelligent assistance and proactive guidance",
            backstory=self._get_backstory(),
            tools=[
                get_command_help,  # Use existing shared tool
                get_personalized_feature_recommendations,
                send_learning_reminder,
                track_user_progress,
                get_contextual_suggestions,
                format_help_response,
                send_proactive_notification,
                get_learning_analytics,
                celebrate_progress,
            ],
            verbose=True,
            allow_delegation=False,
        )

    def _get_backstory(self) -> str:
        """Get the agent's backstory and personality."""
        return """
        You are the KICKAI Helper, a friendly and knowledgeable assistant dedicated to helping team members master the KICKAI platform.
        
        Your approach:
        - Be encouraging and supportive, never condescending
        - Provide step-by-step guidance with clear examples
        - Suggest relevant features based on user context
        - Celebrate user progress and achievements
        - Adapt your teaching style to each user's learning pace
        - Use emojis and clear formatting to make responses engaging
        
        Core capabilities:
        - Command guidance and examples
        - Feature discovery and recommendations
        - Task reminders and suggestions
        - Learning progress tracking
        - Contextual help and troubleshooting
        - Achievement celebrations
        - Proactive assistance
        
        Communication style:
        - Friendly and approachable
        - Clear and concise explanations
        - Use emojis for visual appeal
        - Provide actionable next steps
        - Encourage exploration and learning
        
        Remember: Your goal is to make every user feel confident and capable while using KICKAI!
        """

    def create_help_task(
        self, user_query: str, user_id: str, team_id: str, context: dict = None
    ) -> Task:
        """
        Create a task for providing help to a user.

        Args:
            user_query: The user's question or request
            user_id: The user's ID
            team_id: The team's ID
            context: Additional context about the user's situation

        Returns:
            CrewAI Task for providing help
        """
        task_description = f"""
        Help the user with their request: "{user_query}"
        
        User ID: {user_id}
        Team ID: {team_id}
        Context: {context or "No additional context provided"}
        
        Provide a helpful, encouraging response that:
        1. Addresses their specific question or need
        2. Offers relevant examples and tips
        3. Suggests related features they might find useful
        4. Celebrates their progress if appropriate
        5. Encourages continued learning
        
        Use the available tools to get personalized information and provide the best possible assistance.
        """

        return Task(
            description=task_description,
            agent=self,
            expected_output="A comprehensive, helpful response that addresses the user's needs and encourages learning",
        )

    def create_suggestion_task(self, user_id: str, team_id: str, context: str) -> Task:
        """
        Create a task for sending proactive suggestions.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            context: Context about the user's current activity

        Returns:
            CrewAI Task for sending suggestions
        """
        task_description = f"""
        Send a proactive suggestion to user {user_id} based on their current activity.
        
        Context: {context}
        
        Create a helpful, non-intrusive suggestion that:
        1. Relates to their current activity
        2. Introduces useful features they might not know about
        3. Provides clear next steps
        4. Encourages exploration and learning
        
        Use the available tools to get personalized recommendations and create the best suggestion.
        """

        return Task(
            description=task_description,
            agent=self,
            expected_output="A helpful, contextual suggestion that encourages feature exploration",
        )

    def create_celebration_task(self, user_id: str, team_id: str, achievement: str) -> Task:
        """
        Create a task for celebrating user achievements.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            achievement: Description of the achievement

        Returns:
            CrewAI Task for celebrating achievements
        """
        task_description = f"""
        Celebrate an achievement for user {user_id}.
        
        Achievement: {achievement}
        
        Create an encouraging celebration message that:
        1. Congratulates them on their achievement
        2. Explains why it's significant
        3. Encourages continued learning
        4. Suggests next steps or goals
        5. Uses positive, motivating language
        
        Make it feel personal and meaningful!
        """

        return Task(
            description=task_description,
            agent=self,
            expected_output="An encouraging celebration message that motivates continued learning",
        )

    def create_learning_guidance_task(self, user_id: str, team_id: str, learning_goal: str) -> Task:
        """
        Create a task for providing learning guidance.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            learning_goal: The user's learning goal

        Returns:
            CrewAI Task for learning guidance
        """
        task_description = f"""
        Provide learning guidance for user {user_id} with goal: {learning_goal}
        
        Create a personalized learning roadmap that:
        1. Breaks down the goal into manageable steps
        2. Suggests relevant commands and features to learn
        3. Provides practice exercises and examples
        4. Sets realistic milestones and timelines
        5. Encourages consistent practice
        
        Use the available tools to get personalized recommendations and create the best learning plan.
        """

        return Task(
            description=task_description,
            agent=self,
            expected_output="A comprehensive learning roadmap with actionable steps and milestones",
        )

    def create_troubleshooting_task(
        self, user_id: str, team_id: str, issue_description: str
    ) -> Task:
        """
        Create a task for troubleshooting user issues.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            issue_description: Description of the issue

        Returns:
            CrewAI Task for troubleshooting
        """
        task_description = f"""
        Help user {user_id} troubleshoot an issue: {issue_description}
        
        Provide troubleshooting assistance that:
        1. Identifies the root cause of the issue
        2. Provides step-by-step solutions
        3. Suggests alternative approaches if needed
        4. Prevents similar issues in the future
        5. Maintains a supportive, encouraging tone
        
        Use the available tools to get relevant information and provide the best troubleshooting guidance.
        """

        return Task(
            description=task_description,
            agent=self,
            expected_output="A comprehensive troubleshooting guide with clear solutions and prevention tips",
        )

    def create_feature_overview_task(self, user_id: str, team_id: str, feature_name: str) -> Task:
        """
        Create a task for providing feature overviews.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            feature_name: Name of the feature to overview

        Returns:
            CrewAI Task for feature overview
        """
        task_description = f"""
        Provide a comprehensive overview of the {feature_name} feature for user {user_id}.
        
        Create an engaging feature overview that:
        1. Explains what the feature does and why it's useful
        2. Shows practical examples and use cases
        3. Highlights key benefits and advantages
        4. Provides step-by-step usage instructions
        5. Suggests related features and next steps
        
        Use the available tools to get detailed information and create the best feature overview.
        """

        return Task(
            description=task_description,
            agent=self,
            expected_output="An engaging, comprehensive feature overview with practical examples and usage instructions",
        )
