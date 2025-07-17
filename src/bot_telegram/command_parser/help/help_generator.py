"""
Help Generator

This module generates help text for commands.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..validators.command_validators import CommandType

logger = logging.getLogger(__name__)


@dataclass
class HelpEntry:
    """A help entry for a command."""
    command: str
    description: str
    usage: str
    examples: List[str]
    aliases: List[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class HelpGenerator:
    """Generates help text for commands."""
    
    def __init__(self):
        self.help_entries = self._build_help_entries()
    
    def _build_help_entries(self) -> Dict[str, HelpEntry]:
        """Build help entries for all commands."""
        return {
            # Player commands
            "/add": HelpEntry(
                command="/add",
                description="Add a new player to the team",
                usage="/add <name> <phone> [position]",
                examples=[
                    "/add John Smith +447123456789 midfielder",
                    "/add Jane Doe 07123456789 striker"
                ]
            ),
            "/register": HelpEntry(
                command="/register",
                description="Register yourself or another player",
                usage="/register <player_id> or /register <name> <phone> [position]",
                examples=[
                    "/register MH",
                    "/register John Smith +447123456789 midfielder"
                ]
            ),
            "/status": HelpEntry(
                command="/status",
                description="Check player registration status",
                usage="/status <phone_or_name>",
                examples=[
                    "/status +447123456789",
                    "/status John Smith"
                ]
            ),
            "/list": HelpEntry(
                command="/list",
                description="List all players",
                usage="/list [filter]",
                examples=[
                    "/list",
                    "/list pending",
                    "/list active"
                ]
            ),
            "/approve": HelpEntry(
                command="/approve",
                description="Approve a player for team participation",
                usage="/approve <player_id>",
                examples=[
                    "/approve MH",
                    "/approve John Smith"
                ]
            ),
            "/reject": HelpEntry(
                command="/reject",
                description="Reject a player from team participation",
                usage="/reject <player_id> [reason]",
                examples=[
                    "/reject MH",
                    "/reject John Smith Not available for matches"
                ]
            ),
            "/invitelink": HelpEntry(
                command="/invitelink",
                description="Generate invitation link for a player",
                usage="/invitelink <phone_or_name>",
                examples=[
                    "/invitelink +447123456789",
                    "/invitelink John Smith"
                ]
            ),
            
            # Team commands
            "/addteam": HelpEntry(
                command="/addteam",
                description="Add a new team",
                usage="/addteam <team_name> [description]",
                examples=[
                    "/addteam KickAI Testing",
                    "/addteam KickAI Testing 'Team playing in Test League'"
                ]
            ),
            "/listteams": HelpEntry(
                command="/listteams",
                description="List all teams",
                usage="/listteams [filter]",
                examples=[
                    "/listteams",
                    "/listteams active"
                ]
            ),
            
            # Match commands
            "/creatematch": HelpEntry(
                command="/creatematch",
                description="Create a new match",
                usage="/creatematch <date> <time> <location> [opponent]",
                examples=[
                    "/creatematch 2024-01-15 14:00 'Test Stadium'",
                    "/creatematch 2024-01-15 14:00 'Test Stadium' 'Opponent Team'"
                ]
            ),
            "/listmatches": HelpEntry(
                command="/listmatches",
                description="List all matches",
                usage="/listmatches [filter]",
                examples=[
                    "/listmatches",
                    "/listmatches upcoming",
                    "/listmatches past"
                ]
            ),
            "/attend": HelpEntry(
                command="/attend",
                description="Mark attendance for a match",
                usage="/attend <match_id> [availability]",
                examples=[
                    "/attend match_123",
                    "/attend match_123 yes"
                ]
            ),
            "/unattend": HelpEntry(
                command="/unattend",
                description="Remove attendance for a match",
                usage="/unattend <match_id>",
                examples=[
                    "/unattend match_123"
                ]
            ),
            
            # Payment commands
            "/createpayment": HelpEntry(
                command="/createpayment",
                description="Create a new payment",
                usage="/createpayment <amount> <description> [player_id]",
                examples=[
                    "/createpayment 25.00 'Match fee'",
                    "/createpayment 50.00 'Membership fee' MH"
                ]
            ),
            "/paymentstatus": HelpEntry(
                command="/paymentstatus",
                description="Check payment status",
                usage="/paymentstatus [payment_id] [player_id]",
                examples=[
                    "/paymentstatus",
                    "/paymentstatus payment_123",
                    "/paymentstatus player_id MH"
                ]
            ),
            "/pendingpayments": HelpEntry(
                command="/pendingpayments",
                description="List pending payments",
                usage="/pendingpayments [filter]",
                examples=[
                    "/pendingpayments",
                    "/pendingpayments overdue"
                ]
            ),
            
            # Admin commands
            "/broadcast": HelpEntry(
                command="/broadcast",
                description="Send a broadcast message",
                usage="/broadcast <message> [target]",
                examples=[
                    "/broadcast 'Match tomorrow at 2pm'",
                    "/broadcast 'Team meeting tonight' all"
                ]
            ),
            "/promoteuser": HelpEntry(
                command="/promoteuser",
                description="Promote a user to admin",
                usage="/promoteuser <user_id> <role>",
                examples=[
                    "/promoteuser 123456789 admin",
                    "/promoteuser 123456789 moderator"
                ]
            ),
            
            # System commands
            "/help": HelpEntry(
                command="/help",
                description="Show help information",
                usage="/help [command]",
                examples=[
                    "/help",
                    "/help /add",
                    "/help /status"
                ]
            ),
        }
    
    def get_help_text(self, command_name: Optional[str] = None) -> str:
        """Get help text for a specific command or general help."""
        if command_name:
            return self._get_command_help(command_name)
        else:
            return self._get_general_help()
    
    def _get_command_help(self, command_name: str) -> str:
        """Get help text for a specific command."""
        if command_name not in self.help_entries:
            return f"❌ Unknown command: {command_name}\n\nUse /help to see available commands."
        
        entry = self.help_entries[command_name]
        
        help_text = f"📖 **{entry.command}**\n\n"
        help_text += f"**Description:** {entry.description}\n\n"
        help_text += f"**Usage:** `{entry.usage}`\n\n"
        
        if entry.examples:
            help_text += "**Examples:**\n"
            for example in entry.examples:
                help_text += f"• `{example}`\n"
            help_text += "\n"
        
        if entry.aliases:
            help_text += f"**Aliases:** {', '.join(entry.aliases)}\n"
        
        return help_text
    
    def _get_general_help(self) -> str:
        """Get general help text with all available commands."""
        help_text = "🤖 **KICKAI Bot Commands**\n\n"
        help_text += "**Player Management:**\n"
        help_text += "• `/add` - Add a new player\n"
        help_text += "• `/register` - Register yourself or another player\n"
        help_text += "• `/status` - Check player status\n"
        help_text += "• `/list` - List all players\n"
        help_text += "• `/approve` - Approve a player\n"
        help_text += "• `/reject` - Reject a player\n"
        help_text += "• `/invitelink` - Generate invitation link\n\n"
        
        help_text += "**Match Management:**\n"
        help_text += "• `/creatematch` - Create a new match\n"
        help_text += "• `/listmatches` - List all matches\n"
        help_text += "• `/attend` - Mark attendance\n"
        help_text += "• `/unattend` - Remove attendance\n\n"
        
        help_text += "**Payment Management:**\n"
        help_text += "• `/createpayment` - Create a payment\n"
        help_text += "• `/paymentstatus` - Check payment status\n"
        help_text += "• `/pendingpayments` - List pending payments\n\n"
        
        help_text += "**Admin Commands:**\n"
        help_text += "• `/broadcast` - Send broadcast message\n"
        help_text += "• `/promoteuser` - Promote a user\n\n"
        
        help_text += "**System:**\n"
        help_text += "• `/help [command]` - Show help\n\n"
        
        help_text += "💡 **Tip:** Use `/help <command>` for detailed help on any command."
        
        return help_text
    
    def get_feature_help(self, feature: str) -> str:
        """Get help text for a specific feature."""
        feature_commands = {
            "player": ["/add", "/register", "/status", "/list", "/approve", "/reject", "/invitelink"],
            "match": ["/creatematch", "/listmatches", "/attend", "/unattend"],
            "payment": ["/createpayment", "/paymentstatus", "/pendingpayments"],
            "admin": ["/broadcast", "/promoteuser", "/demoteuser"],
            "team": ["/addteam", "/listteams", "/updateteaminfo"]
        }
        
        if feature not in feature_commands:
            return f"❌ Unknown feature: {feature}"
        
        commands = feature_commands[feature]
        help_text = f"📚 **{feature.title()} Commands**\n\n"
        
        for command in commands:
            if command in self.help_entries:
                entry = self.help_entries[command]
                help_text += f"• `{entry.command}` - {entry.description}\n"
        
        help_text += f"\n💡 Use `/help <command>` for detailed help on any command."
        
        return help_text 