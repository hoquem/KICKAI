#!/usr/bin/env python3
"""
Help Command Handlers

This module provides command handlers for /help and related commands.
These commands are context-aware and provide different information based on chat type.
"""

from typing import Dict, Any, List
from loguru import logger
from core.command_registry import command, get_command_registry, PermissionLevel, CommandType
from core.enums import ChatType
from features.system_infrastructure.domain.services.permission_service import (
    get_permission_service, PermissionContext
)
from crewai.tools import tool


def get_available_commands(chat_type: ChatType = None, user_id: str = None, team_id: str = None) -> Dict[str, Any]:
    """
    Get available commands for the current context.
    
    This function can be used by agents to provide accurate command information.
    
    Args:
        chat_type: The type of chat (main or leadership)
        user_id: The user ID for permission checking
        team_id: The team ID for context
        
    Returns:
        Dictionary containing command information organized by feature
    """
    try:
        registry = get_command_registry()
        commands = registry.list_all_commands()
        
        # Determine chat type if not provided
        if chat_type is None:
            # Default to main chat if we can't determine
            chat_type = ChatType.MAIN
        
        # Filter commands based on chat type and permissions
        available_commands = []
        for cmd in commands:
            # For leadership chat, show all commands
            if chat_type == ChatType.LEADERSHIP:
                available_commands.append(cmd)
            # For main chat, only show public commands
            elif cmd.permission_level == PermissionLevel.PUBLIC:
                available_commands.append(cmd)
        
        # Group commands by feature
        feature_commands = {}
        for cmd in available_commands:
            if cmd.feature not in feature_commands:
                feature_commands[cmd.feature] = []
            feature_commands[cmd.feature].append({
                'name': cmd.name,
                'description': cmd.description,
                'help_text': cmd.help_text,
                'examples': cmd.examples,
                'permission_level': cmd.permission_level.value if hasattr(cmd.permission_level, 'value') else str(cmd.permission_level)
            })
        
        return {
            'chat_type': chat_type.value if hasattr(chat_type, 'value') else str(chat_type),
            'total_commands': len(available_commands),
            'features': feature_commands,
            'commands_by_feature': feature_commands
        }
        
    except Exception as e:
        logger.error(f"Error getting available commands: {e}")
        return {
            'error': f"Failed to get commands: {str(e)}",
            'chat_type': str(chat_type) if chat_type else 'unknown',
            'total_commands': 0,
            'features': {},
            'commands_by_feature': {}
        }


def format_help_response(chat_type: ChatType, commands_info: Dict[str, Any]) -> str:
    """
    Format a help response based on chat type and command information.
    
    Args:
        chat_type: The type of chat (main or leadership)
        commands_info: Command information from get_available_commands
        
    Returns:
        Formatted help text
    """
    try:
        if chat_type == ChatType.LEADERSHIP:
            return _format_leadership_help_from_info(commands_info)
        else:
            return _format_main_chat_help_from_info(commands_info)
    except Exception as e:
        logger.error(f"Error formatting help response: {e}")
        return f"❌ Error formatting help: {str(e)}"


def _format_leadership_help_from_info(commands_info: Dict[str, Any]) -> str:
    """Format help for leadership chat from command info."""
    help_text = ["👔 *KICKAI Leadership Commands*\n"]
    
    features = commands_info.get('features', {})
    
    # Organize commands by logical categories for better UX
    player_commands = []
    team_commands = []
    general_commands = []
    
    # Command description improvements for better UX
    command_descriptions = {
        "/register": "Register new player with name, phone, position",
        "/add": "Add new player to team roster",
        "/list": "List all players with their status",
        "/status": "Check player status by phone number",
        "/myinfo": "Check your admin information",
        "/help": "Show this help message",
        "/start": "Start the bot"
    }
    
    for feature, cmds in features.items():
        for cmd in cmds:
            cmd_name = cmd['name']
            # Use improved description if available, otherwise use original
            cmd_desc = command_descriptions.get(cmd_name, cmd['description'])
            
            # Categorize commands logically
            if any(keyword in cmd_name.lower() for keyword in ['register', 'add', 'list', 'status', 'player']):
                player_commands.append(f"• {cmd_name} - {cmd_desc}")
            elif any(keyword in cmd_name.lower() for keyword in ['team', 'myinfo', 'admin']):
                team_commands.append(f"• {cmd_name} - {cmd_desc}")
            else:
                general_commands.append(f"• {cmd_name} - {cmd_desc}")
    
    # Add sections in logical order
    if player_commands:
        help_text.append("*Player Management:*")
        help_text.extend(sorted(player_commands))
        help_text.append("")
    
    if team_commands:
        help_text.append("*Team Management:*")
        help_text.extend(sorted(team_commands))
        help_text.append("")
    
    if general_commands:
        help_text.append("*General Commands:*")
        help_text.extend(sorted(general_commands))
        help_text.append("")
    
    help_text.append("*Natural Language:*")
    help_text.append("You can also ask me questions in natural language!")
    
    return "\n".join(help_text)


def _format_main_chat_help_from_info(commands_info: Dict[str, Any]) -> str:
    """Format help for main chat from command info."""
    help_text = ["🤖 *KICKAI Commands*\n"]
    
    features = commands_info.get('features', {})
    
    # Organize commands by logical categories for better UX
    player_commands = []
    general_commands = []
    
    # Command description improvements for better UX
    command_descriptions = {
        "/register": "Register as a new player",
        "/list": "List all team players",
        "/status": "Check player status by phone number",
        "/myinfo": "Show your player information",
        "/help": "Show this help message",
        "/start": "Start the bot"
    }
    
    for feature, cmds in features.items():
        for cmd in cmds:
            cmd_name = cmd['name']
            # Use improved description if available, otherwise use original
            cmd_desc = command_descriptions.get(cmd_name, cmd['description'])
            
            # Categorize commands logically
            if any(keyword in cmd_name.lower() for keyword in ['register', 'add', 'list', 'status', 'player']):
                player_commands.append(f"• {cmd_name} - {cmd_desc}")
            else:
                general_commands.append(f"• {cmd_name} - {cmd_desc}")
    
    # Add sections in logical order
    if player_commands:
        help_text.append("*Player Management:*")
        help_text.extend(sorted(player_commands))
        help_text.append("")
    
    if general_commands:
        help_text.append("*General Commands:*")
        help_text.extend(sorted(general_commands))
        help_text.append("")
    
    help_text.append("*Natural Language:*")
    help_text.append("You can also ask me questions in natural language!")
    
    return "\n".join(help_text)


@command("/help", "Show available commands and help information", 
         permission_level=PermissionLevel.PUBLIC,
         feature="shared",
         examples=["/help", "/help register", "/help add"],
         help_text="Show available commands. Use /help [command] for detailed help on a specific command.")
async def handle_help_command(update, context, **kwargs):
    """Handle /help command with context-aware help information using the new framework."""
    try:
        # Get chat type and user info
        chat_id = str(update.effective_chat.id)
        user_id = str(update.effective_user.id)
        telegram_username = update.effective_user.username or ""
        telegram_name = update.effective_user.first_name or "User"
        
        # Determine chat type
        chat_type = _determine_chat_type(chat_id)
        chat_type_str = "main_chat" if chat_type == ChatType.MAIN else "leadership_chat"
        
        # Get team ID (you'll need to implement team mapping logic)
        team_id = "KTI"  # This should come from team mapping service
        
        # Get command arguments
        args = context.args if context.args else []
        
        # Use the new help assistant agent
        from features.shared.domain.agents.help_assistant_agent import get_help_assistant_agent
        
        help_agent = get_help_assistant_agent()
        
        if args:
            # Show help for specific command
            command_name = args[0]
            if not command_name.startswith('/'):
                command_name = f"/{command_name}"
            
            help_text = await help_agent.process_specific_command_help(
                command_name, user_id, team_id, chat_type_str
            )
        else:
            # Show general help
            help_text = await help_agent.process_help_request(
                user_id, team_id, chat_type_str, telegram_username, telegram_name
            )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Error handling help command: {e}")
        await update.message.reply_text(
            "❌ Error processing help request. Please try again.",
            parse_mode='Markdown'
        )
            
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await update.message.reply_text("❌ Error generating help. Please try again.")


@command("/list", "List players and team members", 
         permission_level=PermissionLevel.PUBLIC,
         feature="shared",
         examples=["/list"],
         help_text="List players and team members. Shows active players in main chat, all players in leadership chat.")
async def handle_list_command(update, context, **kwargs):
    """Handle /list command - delegates to CrewAI for processing."""
    # This command is handled by CrewAI agents, so we just acknowledge it
    await update.message.reply_text("📋 Fetching player list... Please wait.")


@command("/status", "Check player or team member status", 
         permission_level=PermissionLevel.PUBLIC,
         feature="shared",
         examples=["/status", "/status +1234567890"],
         help_text="Check status of a player or team member. Use with phone number to check specific player.")
async def handle_status_command(update, context, **kwargs):
    """Handle /status command - delegates to CrewAI for processing."""
    # This command is handled by CrewAI agents, so we just acknowledge it
    await update.message.reply_text("🔍 Checking status... Please wait.")


@command("/myinfo", "Show your player or team member information", 
         permission_level=PermissionLevel.PUBLIC,
         feature="shared",
         examples=["/myinfo"],
         help_text="Show your personal player or team member information.")
async def handle_myinfo_command(update, context, **kwargs):
    """Handle /myinfo command - delegates to CrewAI for processing."""
    # This command is handled by CrewAI agents, so we just acknowledge it
    await update.message.reply_text("👤 Fetching your information... Please wait.")


@tool("get_available_commands")
def get_available_commands_tool(chat_type: str = None, user_id: str = None, team_id: str = None) -> str:
    """
    Get available commands for the current chat context.
    
    This tool returns a formatted list of all available commands based on the chat type
    (main chat vs leadership chat) and user permissions.
    
    Args:
        chat_type: The type of chat - "main" or "leadership"
        user_id: The user ID for permission checking
        team_id: The team ID for context
        
    Returns:
        Formatted string with available commands organized by feature
    """
    try:
        # Convert string to ChatType enum
        if chat_type == "leadership":
            chat_type_enum = ChatType.LEADERSHIP
        else:
            chat_type_enum = ChatType.MAIN
            
        # Get command information
        commands_info = get_available_commands(chat_type_enum, user_id, team_id)
        
        # Format the response
        if chat_type_enum == ChatType.LEADERSHIP:
            return format_help_response(ChatType.LEADERSHIP, commands_info)
        else:
            return format_help_response(ChatType.MAIN, commands_info)
            
    except Exception as e:
        logger.error(f"Error in get_available_commands_tool: {e}")
        return f"❌ Error getting available commands: {str(e)}"


def _determine_chat_type(chat_id: str) -> ChatType:
    """Determine the chat type based on chat ID."""
    # This would need to be injected or determined from context
    # For now, we'll use a simple approach
    if chat_id.endswith('_leadership'):
        return ChatType.LEADERSHIP
    else:
        return ChatType.MAIN


def _format_general_help(registry, chat_type: ChatType) -> str:
    """Format general help information based on chat type."""
    if chat_type == ChatType.LEADERSHIP:
        return _format_leadership_help(registry)
    else:
        return _format_main_chat_help(registry)


def _format_leadership_help(registry) -> str:
    """Format help for leadership chat."""
    commands = registry.list_all_commands()
    
    # Group commands by feature
    feature_commands = {}
    for cmd in commands:
        if cmd.feature not in feature_commands:
            feature_commands[cmd.feature] = []
        feature_commands[cmd.feature].append(cmd)
    
    help_text = ["👔 *KICKAI Leadership Commands*\n"]
    
    # Add feature sections
    for feature, cmds in feature_commands.items():
        if feature == "shared":
            help_text.append("*General Commands:*")
        else:
            feature_name = feature.replace('_', ' ').title()
            help_text.append(f"*{feature_name}:*")
        
        for cmd in sorted(cmds, key=lambda x: x.name):
            help_text.append(f"• {cmd.name} - {cmd.description}")
        
        help_text.append("")
    
    help_text.append("*Natural Language:*")
    help_text.append("You can also ask me questions in natural language!")
    
    return "\n".join(help_text)


def _format_main_chat_help(registry) -> str:
    """Format help for main chat."""
    commands = registry.list_all_commands()
    
    # Filter for public commands
    public_commands = [cmd for cmd in commands if cmd.permission_level == PermissionLevel.PUBLIC]
    
    help_text = ["🤖 *KICKAI Commands*\n"]
    
    # Group by feature
    feature_commands = {}
    for cmd in public_commands:
        if cmd.feature not in feature_commands:
            feature_commands[cmd.feature] = []
        feature_commands[cmd.feature].append(cmd)
    
    for feature, cmds in feature_commands.items():
        if feature == "shared":
            help_text.append("*General Commands:*")
        else:
            feature_name = feature.replace('_', ' ').title()
            help_text.append(f"*{feature_name}:*")
        
        for cmd in sorted(cmds, key=lambda x: x.name):
            help_text.append(f"• {cmd.name} - {cmd.description}")
        
        help_text.append("")
    
    help_text.append("*Natural Language:*")
    help_text.append("You can also ask me questions in natural language!")
    
    return "\n".join(help_text)


def _format_command_help(cmd_metadata, chat_type: ChatType) -> str:
    """Format detailed help for a specific command."""
    help_text = [f"📖 *Help for {cmd_metadata.name}*\n"]
    help_text.append(f"**Description:** {cmd_metadata.description}")
    
    if cmd_metadata.help_text:
        help_text.append(f"**Details:** {cmd_metadata.help_text}")
    
    if cmd_metadata.examples:
        help_text.append("\n**Examples:**")
        for example in cmd_metadata.examples:
            help_text.append(f"• `{example}`")
    
    if cmd_metadata.parameters:
        help_text.append("\n**Parameters:**")
        for param, desc in cmd_metadata.parameters.items():
            help_text.append(f"• `{param}` - {desc}")
    
    if cmd_metadata.aliases:
        help_text.append(f"\n**Aliases:** {', '.join(cmd_metadata.aliases)}")
    
    help_text.append(f"\n**Feature:** {cmd_metadata.feature}")
    help_text.append(f"**Permission Level:** {cmd_metadata.permission_level.value}")
    
    return "\n".join(help_text) 