"""
Guidance Service

Provides contextual help, suggestions, and guidance to users based on their
learning profile and current activity.
"""

from typing import Any

from loguru import logger

from kickai.features.helper_system.domain.entities.learning_profile import LearningProfile
from kickai.features.helper_system.domain.interfaces.guidance_service_interface import (
    IGuidanceService,
)
from kickai.features.helper_system.domain.repositories.help_request_repository_interface import (
    HelpRequestRepositoryInterface,
)
from kickai.features.helper_system.domain.repositories.learning_profile_repository_interface import (
    LearningProfileRepositoryInterface,
)


class GuidanceService(IGuidanceService):
    """Service for providing intelligent guidance and help to users."""

    def __init__(
        self,
        profile_repository: LearningProfileRepositoryInterface,
        help_request_repository: HelpRequestRepositoryInterface,
    ):
        self.profile_repository = profile_repository
        self.help_request_repository = help_request_repository

        # Command help content library
        self._command_help_content = self._initialize_command_help_content()

        # Feature help content library
        self._feature_help_content = self._initialize_feature_help_content()

    async def get_command_help(self, command_name: str, user_level: str = "beginner") -> str:
        """
        Get contextual help for a command based on user level.

        Args:
            command_name: The command to get help for
            user_level: The user's experience level

        Returns:
            Formatted help content
        """
        try:
            # Get base help content
            help_content = self._command_help_content.get(command_name, {})
            if not help_content:
                return f"❌ No help content available for command '{command_name}'."

            # Build response based on user level
            response = f"📖 **Help for {command_name}**\n\n"

            # Add description
            description = help_content.get("description", "No description available")
            response += f"**Description**: {description}\n\n"

            # Add usage examples
            examples = help_content.get("examples", [])
            if examples:
                response += "**Examples**:\n"
                for example in examples:
                    response += f"• {example}\n"
                response += "\n"

            # Add level-specific tips
            tips = help_content.get("tips", {}).get(user_level, [])
            if tips:
                response += "**💡 Tips**:\n"
                for tip in tips:
                    response += f"• {tip}\n"
                response += "\n"

            # Add related commands
            related = help_content.get("related", [])
            if related:
                response += "**🔗 Related Commands**:\n"
                for cmd in related:
                    response += f"• {cmd}\n"

            return response

        except Exception as e:
            logger.error(f"Error getting command help for {command_name}: {e}")
            return f"❌ Sorry, I encountered an error while getting help for '{command_name}'."

    async def get_feature_suggestions(self, user_id: str, team_id: str) -> list[str]:
        """
        Get personalized feature suggestions for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            List of feature suggestions
        """
        try:
            # Get user's learning profile
            profile = await self.profile_repository.get_profile(user_id, team_id)
            if not profile:
                return self._get_beginner_suggestions()

            # Get suggestions based on user's level and usage
            suggestions = []

            if profile.experience_level == "beginner":
                suggestions = self._get_beginner_suggestions()
            elif profile.experience_level == "intermediate":
                suggestions = await self._get_intermediate_suggestions(profile)
            elif profile.experience_level == "advanced":
                suggestions = await self._get_advanced_suggestions(profile)
            else:  # expert
                suggestions = await self._get_expert_suggestions(profile)

            return suggestions

        except Exception as e:
            logger.error(f"Error getting feature suggestions for user {user_id}: {e}")
            return self._get_beginner_suggestions()

    async def format_help_response(self, help_data: dict[str, Any]) -> str:
        """
        Format help response with emojis and clear structure.

        Args:
            help_data: Dictionary containing help information

        Returns:
            Formatted help response
        """
        try:
            response_type = help_data.get("type", "general")

            if response_type == "command_help":
                return self._format_command_help(help_data)
            elif response_type == "feature_help":
                return self._format_feature_help(help_data)
            elif response_type == "general_help":
                return self._format_general_help(help_data)
            else:
                return self._format_general_help(help_data)

        except Exception as e:
            logger.error(f"Error formatting help response: {e}")
            return "❌ Sorry, I encountered an error while formatting the help response."

    async def get_contextual_tips(self, current_command: str, user_level: str) -> list[str]:
        """
        Get contextual tips based on current command and user level.

        Args:
            current_command: The command being used
            user_level: The user's experience level

        Returns:
            List of contextual tips
        """
        try:
            tips = []

            # Get workflow tips
            workflow_tips = self._get_workflow_tips(current_command, user_level)
            tips.extend(workflow_tips)

            # Get best practice tips
            best_practice_tips = self._get_best_practice_tips(current_command, user_level)
            tips.extend(best_practice_tips)

            return tips[:5]  # Limit to 5 tips

        except Exception as e:
            logger.error(f"Error getting contextual tips for {current_command}: {e}")
            return ["💡 The system will proactively provide assistance when needed"]

    async def get_workflow_suggestions(
        self, user_id: str, team_id: str, current_task: str
    ) -> list[str]:
        """
        Get workflow suggestions for a specific task.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            current_task: The current task being performed

        Returns:
            List of workflow suggestions
        """
        try:
            # Get user's learning profile
            profile = await self.profile_repository.get_profile(user_id, team_id)
            if not profile:
                return ["💡 The system will proactively provide assistance when needed"]

            suggestions = []

            # Task-based workflow suggestions
            if "add" in current_task.lower():
                suggestions.extend(
                    [
                        "📋 After adding players, use /list to verify",
                        "📊 Use /status to check their availability",
                    ]
                )

            if "match" in current_task.lower():
                suggestions.extend(
                    ["📋 Use /attendance to track responses", "📢 Use /announce to send reminders"]
                )

            if "organize" in current_task.lower():
                suggestions.extend(
                    [
                        "📅 Use /creatematch for game scheduling",
                        "📊 Use /attendance for availability tracking",
                    ]
                )

            # Level-based suggestions
            if profile.experience_level == "beginner":
                suggestions.append("🎯 Start with basic commands like /list and /status")
            elif profile.experience_level == "intermediate":
                suggestions.append("🚀 Explore advanced features like match management")
            elif profile.experience_level == "advanced":
                suggestions.append("🎯 Optimize your workflows and help mentor others")

            return suggestions[:3]  # Limit to 3 workflow suggestions

        except Exception as e:
            logger.error(f"Error getting workflow suggestions for user {user_id}: {e}")
            return ["💡 The system will proactively provide assistance when needed"]

    async def get_best_practices(self, feature: str, user_level: str) -> list[str]:
        """
        Get best practices for a specific feature.

        Args:
            feature: The feature to get best practices for
            user_level: The user's experience level

        Returns:
            List of best practices
        """
        try:
            practices = []

            # Feature-specific best practices
            if "player" in feature.lower():
                practices.extend(
                    [
                        "👥 Always include player positions for better team management",
                        "📱 Use consistent phone number formats",
                        "🏷️ Use player IDs for quick identification",
                    ]
                )

            if "match" in feature.lower():
                practices.extend(
                    [
                        "📅 Schedule matches well in advance",
                        "📋 Track attendance consistently",
                        "📢 Send reminders at appropriate times",
                    ]
                )

            if "communication" in feature.lower():
                practices.extend(
                    [
                        "💬 Use clear, concise messages",
                        "📢 Announce important updates promptly",
                        "📋 Keep communication organized and searchable",
                    ]
                )

            # Level-specific best practices
            if user_level == "beginner":
                practices.append("🎯 Focus on mastering basic commands first")
            elif user_level == "intermediate":
                practices.append("🚀 Explore automation and advanced features")
            elif user_level == "advanced":
                practices.append("🏆 Help mentor other team members")
            elif user_level == "expert":
                practices.append("👑 Lead by example and optimize team workflows")

            return practices[:5]  # Limit to 5 best practices

        except Exception as e:
            logger.error(f"Error getting best practices for {feature}: {e}")
            return ["💡 The system will proactively provide assistance when needed"]

    def _initialize_command_help_content(self) -> dict[str, Any]:
        """Initialize the command help content library."""
        return {
            "/addplayer": {
                "description": "Add a new player to your team",
                "examples": [
                    "/addplayer John Smith +447123456789 Forward",
                    "/addplayer Sarah Johnson +447987654321 Defender",
                ],
                "tips": {
                    "beginner": [
                        "Always include the player's position for better team management",
                        "Use the player's preferred name for easier identification",
                    ],
                    "intermediate": [
                        "Consider adding notes about the player's strengths",
                        "Use consistent naming conventions for your team",
                    ],
                    "advanced": [
                        "Bulk add players using the CSV import feature",
                        "Set up player categories for better organization",
                    ],
                    "expert": [
                        "Integrate with external player databases",
                        "Use advanced filtering and search capabilities",
                    ],
                },
                "related": ["/list", "/update", "/status"],
            },
            "/list": {
                "description": "View all team members and their status",
                "examples": ["/list", "/list --status active", "/list --position Forward"],
                "tips": {
                    "beginner": [
                        "Use filters to find specific players quickly",
                        "Check the status column to see who's active",
                    ],
                    "intermediate": [
                        "Export the list for external use",
                        "Use advanced filtering options",
                    ],
                    "advanced": [
                        "Create custom views for different purposes",
                        "Set up automated list generation",
                    ],
                    "expert": [
                        "Integrate with reporting systems",
                        "Use API endpoints for custom integrations",
                    ],
                },
                "related": ["/status", "/myinfo", "/pending"],
            },
            "/status": {
                "description": "Check a player's availability status",
                "examples": ["/status +447123456789", "/status MH"],
                "tips": {
                    "beginner": [
                        "You can search by phone number or player ID",
                        "Use this to quickly check player availability",
                    ],
                    "intermediate": [
                        "Set up status update reminders",
                        "Use bulk status updates for efficiency",
                    ],
                    "advanced": [
                        "Automate status updates based on schedules",
                        "Integrate with calendar systems",
                    ],
                    "expert": [
                        "Create custom status workflows",
                        "Use advanced analytics for availability patterns",
                    ],
                },
                "related": ["/list", "/myinfo", "/update"],
            },
            "/help": {
                "description": "Get help and see available commands",
                "examples": ["/help", "/help addplayer"],
                "tips": {
                    "beginner": [
                        "Use /help to discover new commands",
                        "Try /help [command] for specific help",
                    ],
                    "intermediate": [
                        "Explore advanced features through help",
                        "Use help to learn best practices",
                    ],
                    "advanced": [
                        "Customize help content for your team",
                        "Create help shortcuts for common tasks",
                    ],
                    "expert": [
                        "Contribute to help documentation",
                        "Create team-specific help guides",
                    ],
                },
                "related": [],
            },
        }

    def _initialize_feature_help_content(self) -> dict[str, Any]:
        """Initialize the feature help content library."""
        return {
            "player_management": {
                "description": "Manage your team's player roster and information",
                "commands": ["/addplayer", "/list", "/update", "/status"],
                "workflow": "Add players → Manage roster → Track status → Update information",
                "tips": [
                    "Keep player information up to date",
                    "Use consistent naming conventions",
                    "Regularly review and clean up inactive players",
                ],
            },
            "match_management": {
                "description": "Create and manage matches, track attendance, and organize events",
                "commands": ["/creatematch", "/attendance", "/announce", "/remind"],
                "workflow": "Create match → Track attendance → Send reminders → Manage logistics",
                "tips": [
                    "Plan matches well in advance",
                    "Use attendance tracking for better planning",
                    "Send timely reminders to players",
                ],
            },
            "communication": {
                "description": "Communicate with your team through announcements and reminders",
                "commands": ["/announce", "/remind", "/message"],
                "workflow": "Create message → Target audience → Send → Track engagement",
                "tips": [
                    "Use clear, concise messaging",
                    "Target messages to specific groups when needed",
                    "Follow up on important announcements",
                ],
            },
        }

    def _get_beginner_suggestions(self) -> list[str]:
        """Get suggestions for beginner users."""
        return [
            "🎯 **Player Management**: Use /addplayer to add new team members",
            "📋 **Team Overview**: Use /list to see all team members with their status",
            "📞 **Status Check**: Use /status to check player availability",
            "❓ **Help System**: The system will proactively provide assistance when needed",
            "📢 **Announcements**: Use /announce to communicate with your team",
        ]

    async def _get_intermediate_suggestions(self, profile: LearningProfile) -> list[str]:
        """Get suggestions for intermediate users."""
        suggestions = []

        # Check what features they haven't used yet
        unused_commands = profile.get_unused_commands(
            ["/creatematch", "/attendance", "/remind", "/pending", "/approve"]
        )

        for command in unused_commands:
            if command == "/creatematch":
                suggestions.append("🏟️ **Match Management**: Try /creatematch to organize games")
            elif command == "/attendance":
                suggestions.append(
                    "📊 **Attendance Tracking**: Use /attendance to track player availability"
                )
            elif command == "/remind":
                suggestions.append("⏰ **Smart Reminders**: Use /remind to send targeted reminders")
            elif command == "/pending":
                suggestions.append(
                    "⏳ **Approval Management**: Use /pending to check players awaiting approval"
                )

        if not suggestions:
            suggestions.append("🚀 **Advanced Features**: Explore match management and analytics")

        return suggestions

    async def _get_advanced_suggestions(self, profile: LearningProfile) -> list[str]:
        """Get suggestions for advanced users."""
        suggestions = []

        # Suggest advanced features
        if profile.get_feature_adoption_rate() < 0.8:
            suggestions.append("📈 **Analytics**: Explore team performance analytics")
            suggestions.append("🔧 **Automation**: Set up automated workflows")
            suggestions.append("📊 **Reporting**: Generate detailed team reports")

        suggestions.append("🎯 **Optimization**: Fine-tune your team management processes")

        return suggestions

    async def _get_expert_suggestions(self, profile: LearningProfile) -> list[str]:
        """Get suggestions for expert users."""
        return [
            "🏆 **Mentorship**: Help other team members learn the system",
            "🔧 **Customization**: Create custom workflows for your team",
            "📊 **Analytics**: Dive deep into team performance data",
            "🚀 **Innovation**: Explore new features and integrations",
        ]

    def _get_workflow_tips(self, command: str, user_level: str) -> list[str]:
        """Get workflow tips for a command."""
        workflow_tips = {
            "/addplayer": [
                "After adding a player, use /list to verify they appear correctly",
                "Consider using /status to check their availability after adding them",
            ],
            "/list": [
                "Use /list before making team decisions to get current information",
                "Combine with /status for a complete team overview",
            ],
            "/status": [
                "Check status before creating matches or sending announcements",
                "Use this to identify available players for upcoming events",
            ],
        }

        return workflow_tips.get(command, [])

    def _get_best_practice_tips(self, command: str, user_level: str) -> list[str]:
        """Get best practice tips for a command."""
        best_practice_tips = {
            "/addplayer": [
                "Always verify contact information before adding players",
                "Use consistent naming conventions across your team",
            ],
            "/list": [
                "Regularly review and update your team roster",
                "Use filters to focus on relevant information",
            ],
            "/status": [
                "Encourage players to keep their status updated",
                "Use status information for better team planning",
            ],
        }

        return best_practice_tips.get(command, [])

    def _format_command_help(self, help_data: dict[str, Any]) -> str:
        """Format command help response."""
        command = help_data.get("command", "")
        description = help_data.get("description", "")
        examples = help_data.get("examples", [])
        tips = help_data.get("tips", [])

        response = f"📖 **Help for {command}**\n\n"
        response += f"{description}\n\n"

        if examples:
            response += "**Examples**:\n"
            for example in examples:
                response += f"• {example}\n"
            response += "\n"

        if tips:
            response += "**💡 Tips**:\n"
            for tip in tips:
                response += f"• {tip}\n"

        return response

    def _format_feature_help(self, help_data: dict[str, Any]) -> str:
        """Format feature help response."""
        feature = help_data.get("feature", "")
        description = help_data.get("description", "")
        commands = help_data.get("commands", [])

        response = f"🔧 **{feature} Feature**\n\n"
        response += f"{description}\n\n"

        if commands:
            response += "**Available Commands**:\n"
            for cmd in commands:
                response += f"• {cmd}\n"

        return response

    def _format_general_help(self, help_data: dict[str, Any]) -> str:
        """Format general help response."""
        title = help_data.get("title", "Help")
        content = help_data.get("content", "")

        response = f"❓ **{title}**\n\n"
        response += content

        return response
