#!/usr/bin/env python3
"""
Welcome Message Templates for KICKAI System

This module provides configurable welcome message templates for new members
joining different chat types. Templates can be customized per team or context.
"""

from dataclasses import dataclass

from kickai.core.enums import ChatType


@dataclass
class WelcomeMessageTemplate:
    """Template structure for welcome messages."""

    title: str
    body: str
    features: str
    getting_started: str
    help_section: str
    footer: str

    def format(self, username: str, **kwargs) -> str:
        """Format the template with the given username and optional parameters."""
        try:
            return f"""{self.title.format(username=username.upper())}

{self.body}

{self.features}

{self.getting_started}

{self.help_section}

{self.footer}"""
        except Exception:
            # Fallback to safe formatting
            return f"""🎉 WELCOME TO THE TEAM, {username.upper()}!

👋 Welcome to KICKAI! We're excited to have you join our football community!

📋 Getting Started:
• Use /help to see available commands
• Contact team leadership for assistance

Welcome aboard! ⚽"""


# Default welcome message templates
DEFAULT_WELCOME_TEMPLATES = {
    ChatType.MAIN: WelcomeMessageTemplate(
        title="🎉 WELCOME TO THE TEAM, {username}!",
        body="👋 Welcome to KICKAI! We're excited to have you join our football community!",
        features="""⚽ WHAT YOU CAN DO HERE:
• Link your phone number to connect your account
• Check your status with `/myinfo`
• See available commands with `/help`
• View active players with `/list`
• Update your details with `/update`""",
        getting_started="""🔗 GETTING STARTED:
1. Link your account - Share your phone number to connect to your player record
2. Check your status - Use `/myinfo` to see your current registration
3. Update details - Use `/update` to modify your position and contact info
4. Explore commands - Use `/help` to see all available options""",
        help_section="""📱 NEED HELP?
• Type `/help` for command information
• Contact team leadership for assistance
• Check pinned messages for important updates""",
        footer="Welcome aboard! Let's make this team amazing! ⚽🔥",
    ),
    ChatType.LEADERSHIP: WelcomeMessageTemplate(
        title="🎉 WELCOME TO LEADERSHIP, {username}!",
        body="👥 Welcome to the KICKAI Leadership Team! You're now part of our administrative team.",
        features="""🛠️ ADMINISTRATIVE FEATURES:
• Manage players with `/add`, `/approve`, `/listmembers`
• View pending players with `/pending`
• Schedule training with `/scheduletraining`
• Manage matches with `/creatematch`, `/squadselect`
• Send announcements with `/announce`""",
        getting_started="""📋 QUICK START:
1. View pending players - Use `/pending` to see who needs approval
2. Add new players - Use `/add [name] [phone] [position]`
3. Approve players - Use `/approve [player_id]`
4. Explore admin commands - Use `/help` for full list""",
        help_section="""🎯 TEAM MANAGEMENT:
• Player registration and approval
• Training session management
• Match scheduling and squad selection
• Team communication and announcements""",
        footer="Welcome to the leadership team! Let's build something great together! 👥🌟",
    ),
    ChatType.PRIVATE: WelcomeMessageTemplate(
        title="🎉 WELCOME, {username}!",
        body="👋 Welcome to KICKAI! You're now connected to our football management system.",
        features="""⚽ AVAILABLE COMMANDS:
• Get help with `/help`
• Check your status with `/myinfo`
• Contact leadership to be added as a player""",
        getting_started="""🔗 NEXT STEPS:
1. Join the main team chat for full access
2. Register as a player or team member
3. Start participating in team activities""",
        help_section="""📱 NEED HELP?
• Use `/help` for command information
• Contact team leadership for assistance""",
        footer="Welcome! We're glad to have you on board! ⚽",
    ),
}


class WelcomeMessageManager:
    """Manager for welcome message templates and customization."""

    def __init__(self, team_id: str = None):
        self.team_id = team_id
        self.templates = DEFAULT_WELCOME_TEMPLATES.copy()
        self.custom_templates = {}

    def get_template(self, chat_type: ChatType) -> WelcomeMessageTemplate:
        """Get the welcome message template for a specific chat type."""
        # Check for custom template first
        if self.team_id and self.team_id in self.custom_templates:
            team_templates = self.custom_templates[self.team_id]
            if chat_type in team_templates:
                return team_templates[chat_type]

        # Return default template
        return self.templates.get(chat_type, self.templates[ChatType.MAIN])

    def set_custom_template(
        self, chat_type: ChatType, template: WelcomeMessageTemplate, team_id: str = None
    ):
        """Set a custom template for a specific chat type and team."""
        target_team = team_id or self.team_id
        if not target_team:
            raise ValueError("Team ID is required for custom templates")

        if target_team not in self.custom_templates:
            self.custom_templates[target_team] = {}

        self.custom_templates[target_team][chat_type] = template

    def generate_welcome_message(self, username: str, chat_type: ChatType, **kwargs) -> str:
        """Generate a welcome message using the appropriate template."""
        try:
            template = self.get_template(chat_type)
            return template.format(username=username, **kwargs)
        except Exception:
            # Fallback to basic welcome
            return f"👋 Welcome to the team, {username}! Use /help to see available commands."

    def reset_to_defaults(self, team_id: str = None):
        """Reset templates to defaults for a team."""
        target_team = team_id or self.team_id
        if target_team and target_team in self.custom_templates:
            del self.custom_templates[target_team]


# Global instance for easy access
_welcome_message_manager = WelcomeMessageManager()


def get_welcome_message_manager(team_id: str = None) -> WelcomeMessageManager:
    """Get the global welcome message manager instance."""
    if team_id:
        _welcome_message_manager.team_id = team_id
    return _welcome_message_manager


def generate_welcome_message(
    username: str, chat_type: ChatType, team_id: str = None, **kwargs
) -> str:
    """Generate a welcome message using the global manager."""
    manager = get_welcome_message_manager(team_id)
    return manager.generate_welcome_message(username, chat_type, **kwargs)
