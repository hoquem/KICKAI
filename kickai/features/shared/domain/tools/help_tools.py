#!/usr/bin/env python3
"""
Help Tools

This module provides tools for help and command information.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import PermissionLevel
from kickai.features.shared.domain.services.help_service import HelpService


@tool("FINAL_HELP_RESPONSE")
def final_help_response(telegram_id: int, team_id: str, chat_type: str) -> str:
    """
    Generate dynamic help response based on available commands for the user's context.

    This tool dynamically discovers and presents commands available to the user
    based on their chat type, role permissions, and team context.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private) - determines command visibility


    :return: str: Dynamically generated help content with available commands, descriptions, and usage examples
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get help information."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get help information."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get help information."

    try:
        # Get service using simple container access
        container = get_container()
        help_service = container.get_service(HelpService)

        if not help_service:
            return "❌ Help service is temporarily unavailable. Please try again later."

        # Get available commands for this context
        commands = help_service.get_available_commands_sync(team_id.strip(), chat_type.strip())

        if not commands:
            return f"📋 HELP INFORMATION (Team: {team_id})\n\nNo commands available for {chat_type} chat. Please check with your team administrator."

        # Filter commands based on chat type and appropriate permissions
        filtered_commands = []
        for cmd in commands:
            permission = cmd.get('permission_level', PermissionLevel.PUBLIC.value)
            
            if chat_type.lower() == 'main':
                # Main chat: Show PUBLIC and PLAYER commands, but not LEADERSHIP/ADMIN commands
                if permission in [PermissionLevel.PUBLIC.value, PermissionLevel.PLAYER.value]:
                    filtered_commands.append(cmd)
            elif chat_type.lower() == 'leadership':
                # Leadership chat: Show all commands (PUBLIC, PLAYER, LEADERSHIP, ADMIN)
                filtered_commands.append(cmd)
            else:
                # Private chat: Show PUBLIC and basic PLAYER commands
                if permission in [PermissionLevel.PUBLIC.value, PermissionLevel.PLAYER.value]:
                    filtered_commands.append(cmd)
        
        commands = filtered_commands

        # Generate dynamic help content
        chat_title = {
            'main': 'Main Chat Commands',
            'leadership': 'Leadership Commands',
            'private': 'Private Chat Commands'
        }.get(chat_type.lower(), f'{chat_type.title()} Commands')

        result = f"📋 {chat_title.upper()} (Team: {team_id})\n\n"

        # Group commands by feature for better organization
        features = {}
        for cmd in commands:
            feature = cmd.get('feature', 'general').replace('_', ' ').title()
            if feature not in features:
                features[feature] = []
            features[feature].append(cmd)

        # Display commands grouped by feature
        for feature, feature_commands in sorted(features.items()):
            if len(features) > 1:  # Only show feature headers if multiple features
                result += f"{feature.upper()}:\n"

            for cmd in sorted(feature_commands, key=lambda x: x['name']):
                name = cmd['name']
                desc = cmd['description']
                permission = cmd.get('permission_level', PermissionLevel.PUBLIC.value)

                # Add permission indicator for restricted commands
                permission_icon = ""
                if permission in [PermissionLevel.LEADERSHIP.value, PermissionLevel.ADMIN.value]:
                    permission_icon = " 👑"
                elif permission == PermissionLevel.PLAYER.value:
                    permission_icon = " ⚽"

                result += f"• {name}{permission_icon} - {desc}\n"

            result += "\n"

        # Add helpful footer
        result += "💡 USAGE TIPS:\n"
        result += "• Use /help [command] for detailed information about specific commands\n"
        result += "• Commands marked with 👑 require leadership privileges\n"
        result += "• Commands marked with ⚽ are for registered players\n\n"
        result += "🤖 KICKAI - Your AI-powered team management assistant"

        return result

    except Exception as e:
        logger.error(f"Error generating dynamic help response: {e}")
        return f"📋 HELP INFORMATION (Team: {team_id})\n\nHelp system encountered an error. Please try again later or contact support."

@tool("get_available_commands")
def get_available_commands(telegram_id: int, team_id: str, chat_type: str) -> str:
    """
    Get available commands for the current context with detailed information.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private) - determines command visibility


    :return: Comprehensive list of available commands with descriptions, permissions, and examples
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get available commands."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get available commands."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get available commands."

    try:
        # Get service using simple container access
        container = get_container()
        help_service = container.get_service(HelpService)

        if not help_service:
            return "❌ Help service is temporarily unavailable. Please try again later."

        # Get available commands with full details
        commands = help_service.get_available_commands_sync(team_id.strip(), chat_type.strip())

        if not commands:
            return f"📋 AVAILABLE COMMANDS (Team: {team_id})\n\nNo commands available for {chat_type} chat context."

        # Filter commands based on chat type and appropriate permissions
        filtered_commands = []
        for cmd in commands:
            permission = cmd.get('permission_level', PermissionLevel.PUBLIC.value)
            
            if chat_type.lower() == 'main':
                # Main chat: Show PUBLIC and PLAYER commands, but not LEADERSHIP/ADMIN commands
                if permission in [PermissionLevel.PUBLIC.value, PermissionLevel.PLAYER.value]:
                    filtered_commands.append(cmd)
            elif chat_type.lower() == 'leadership':
                # Leadership chat: Show all commands (PUBLIC, PLAYER, LEADERSHIP, ADMIN)
                filtered_commands.append(cmd)
            else:
                # Private chat: Show PUBLIC and basic PLAYER commands
                if permission in [PermissionLevel.PUBLIC.value, PermissionLevel.PLAYER.value]:
                    filtered_commands.append(cmd)
        
        commands = filtered_commands

        # Format comprehensive command list
        result = f"📋 AVAILABLE COMMANDS FOR {chat_type.upper()} CHAT (Team: {team_id})\n\n"

        # Group by permission level for clarity
        permission_groups = {
            PermissionLevel.PUBLIC.value: {'title': '🌍 PUBLIC COMMANDS', 'commands': []},
            PermissionLevel.PLAYER.value: {'title': '⚽ PLAYER COMMANDS', 'commands': []},
            PermissionLevel.LEADERSHIP.value: {'title': '👑 LEADERSHIP COMMANDS', 'commands': []},
            PermissionLevel.ADMIN.value: {'title': '🔧 ADMIN COMMANDS', 'commands': []},
            PermissionLevel.SYSTEM.value: {'title': '⚙️ SYSTEM COMMANDS', 'commands': []}
        }

        # Categorize commands by permission
        for cmd in commands:
            perm = cmd.get('permission_level', PermissionLevel.PUBLIC.value)
            if perm in permission_groups:
                permission_groups[perm]['commands'].append(cmd)

        # Display each permission group
        for _perm_level, group_info in permission_groups.items():
            if group_info['commands']:
                result += f"{group_info['title']}\n"
                for cmd in sorted(group_info['commands'], key=lambda x: x['name']):
                    name = cmd['name']
                    desc = cmd['description']
                    feature = cmd.get('feature', 'general').replace('_', ' ').title()

                    result += f"• {name} - {desc}\n"
                    result += f"  📁 Feature: {feature}\n"

                    # Add examples if available
                    if cmd.get('examples'):
                        examples = cmd['examples'][:2]  # Show max 2 examples
                        result += f"  💡 Examples: {', '.join(examples)}\n"

                    result += "\n"

                result += "\n"

        # Add usage instructions
        result += "📖 USAGE INSTRUCTIONS:\n"
        result += "• Type any command directly (e.g., /help)\n"
        result += "• Use /help [command] for detailed help on specific commands\n"
        result += "• Commands are filtered based on your role and current chat type\n\n"
        result += f"📊 TOTAL AVAILABLE: {len(commands)} commands for your current context"

        return result

    except Exception as e:
        logger.error(f"Failed to get available commands: {e}")
        return f"❌ Failed to get available commands: {e!s}"

@tool("get_command_help")
def get_command_help(telegram_id: int, team_id: str, chat_type: str, command_name: str) -> str:
    """
    Get comprehensive help for a specific command with usage examples and parameter details.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private) - used for permission checking
        command_name (str): Name of the command to get help for (with or without slash)


    :return: Detailed help information including usage, examples, parameters, and permission requirements
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get command help."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get command help."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get command help."

    if not command_name or command_name.strip() == "":
        return "❌ Command name is required to get help."

    try:
        # Clean up command name (handle with/without slash)
        clean_command = command_name.strip()
        if not clean_command.startswith('/'):
            clean_command = f'/{clean_command}'

        # Get service using simple container access
        container = get_container()
        help_service = container.get_service(HelpService)

        if not help_service:
            return "❌ Help service is temporarily unavailable. Please try again later."

        # Get detailed command help from registry
        help_info = help_service.get_command_help_sync(clean_command, team_id.strip())

        if not help_info:
            return f"❌ Command '{clean_command}' not found or not available in your current context.\n\n💡 TIP: Use /help to see all available commands."

        # Build comprehensive help response
        result = f"📖 DETAILED HELP FOR {clean_command}\n\n"

        # Basic info
        result += f"📝 DESCRIPTION: {help_info.get('description', 'No description available')}\n\n"

        # Permission and access info
        permission = help_info.get('permission_level', PermissionLevel.PUBLIC.value)
        feature = help_info.get('feature', 'general').replace('_', ' ').title()

        result += f"🔒 ACCESS LEVEL: {permission}\n"
        result += f"📁 FEATURE CATEGORY: {feature}\n\n"

        # Usage information
        if help_info.get('usage'):
            result += f"⚙️ USAGE: {help_info['usage']}\n\n"

        # Parameters
        if help_info.get('parameters'):
            result += "📊 PARAMETERS:\n"
            for param, desc in help_info['parameters'].items():
                result += f"• {param}: {desc}\n"
            result += "\n"

        # Examples
        if help_info.get('examples'):
            result += "💡 EXAMPLES:\n"
            for example in help_info['examples'][:5]:  # Show max 5 examples
                result += f"• {example}\n"
            result += "\n"

        # Additional notes
        if help_info.get('notes'):
            result += f"📝 ADDITIONAL NOTES:\n{help_info['notes']}\n\n"

        # Context info
        result += "📍 CONTEXT INFORMATION:\n"
        result += f"• Team: {team_id}\n"
        result += f"• Chat Type: {chat_type.title()}\n"
        result += f"• Your Access: Command is {'available' if permission == PermissionLevel.PUBLIC.value or chat_type == 'leadership' else 'restricted'}\n\n"

        # Footer
        result += "🔗 RELATED: Use /help to see all available commands for your role."

        return result

    except Exception as e:
        logger.error(f"Failed to get command help for '{command_name}': {e}")
        return f"❌ Failed to get command help for '{command_name}': {e!s}"

@tool("get_welcome_message")
def get_welcome_message(telegram_id: int, team_id: str, chat_type: str) -> str:
    """
    Generate a personalized welcome message with context-aware command previews.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private) - determines available features


    :return: Personalized welcome message with available commands and quick start guide
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get welcome message."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get welcome message."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get welcome message."

    try:
        # Get service using simple container access
        container = get_container()
        help_service = container.get_service(HelpService)

        if not help_service:
            return "❌ Help service is temporarily unavailable. Please try again later."

        # Get available commands to personalize welcome
        commands = help_service.get_available_commands_sync(team_id.strip(), chat_type.strip())

        # Build context-aware welcome message
        chat_context = {
            'leadership': {
                'title': '👑 WELCOME TO KICKAI LEADERSHIP CHAT!',
                'role': 'team leadership',
                'features': ['Team member management', 'Match creation & squad selection', 'Administrative controls', 'Full system access'],
                'key_commands': ['/addmember', '/creatematch', '/announce', '/listmembers']
            },
            'main': {
                'title': '⚽ WELCOME TO KICKAI TEAM CHAT!',
                'role': 'team player',
                'features': ['Match attendance tracking', 'Team information', 'Player status updates', 'Match schedules'],
                'key_commands': ['/myinfo', '/attendance', '/matches', '/help']
            },
            'private': {
                'title': '💬 WELCOME TO KICKAI PRIVATE CHAT!',
                'role': 'team member',
                'features': ['Personal status checking', 'Individual support', 'Registration assistance', 'Direct communication'],
                'key_commands': ['/myinfo', '/help', '/register']
            }
        }

        context = chat_context.get(chat_type.lower(), chat_context['private'])

        result = f"{context['title']}\n\n"
        result += "👋 Hello! I'm KICKAI, your AI-powered team management assistant.\n\n"

        # Role-specific features
        result += f"🎆 AS {context['role'].upper()}, YOU HAVE ACCESS TO:\n"
        for feature in context['features']:
            result += f"• {feature}\n"
        result += "\n"

        # Show actual available commands (top 4)
        if commands:
            available_key_commands = []
            for cmd_name in context['key_commands']:
                for cmd in commands:
                    if cmd['name'] == cmd_name:
                        available_key_commands.append(cmd)
                        break

            if available_key_commands:
                result += "📅 QUICK START COMMANDS:\n"
                for cmd in available_key_commands[:4]:  # Show max 4
                    result += f"• {cmd['name']} - {cmd['description']}\n"
                result += "\n"

        # Dynamic command count
        cmd_count = len(commands) if commands else 0
        result += f"📊 AVAILABLE FEATURES: {cmd_count} commands accessible to you\n\n"

        # Context-specific tips
        if chat_type.lower() == 'leadership':
            result += "👑 LEADERSHIP PRIVILEGES: You have administrative access in this chat!\n\n"
        elif chat_type.lower() == 'main':
            result += "🏆 TEAM CHAT FEATURES: All team communication happens here!\n\n"
        else:
            result += "🗺️ PRIVATE CHAT: This is your personal space with KICKAI!\n\n"

        # Universal help instructions
        result += "🎓 GETTING STARTED:\n"
        result += "• Type /help to see all your available commands\n"
        result += "• Use /help [command] for detailed command information\n"
        result += "• Commands are personalized based on your role and chat context\n\n"

        # Team context
        result += f"🏠 Team: {team_id} | 💬 Chat: {chat_type.title()}\n\n"
        result += "⚽ Ready to get started? Try /help to explore what you can do!"

        return result

    except Exception as e:
        logger.error(f"Failed to generate welcome message: {e}")
        return "🎉 WELCOME TO KICKAI!\n\n👋 I'm your AI team management assistant!\n\n⚽ Use /help to see what I can do for you.\n\n❌ Note: Welcome customization is temporarily unavailable."
