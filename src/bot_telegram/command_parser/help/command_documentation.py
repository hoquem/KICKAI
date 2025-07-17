"""
Command Documentation

This module provides comprehensive command documentation and examples.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CommandExample:
    """An example of command usage."""
    command: str
    description: str
    expected_output: str


@dataclass
class CommandDocumentation:
    """Complete documentation for a command."""
    name: str
    description: str
    syntax: str
    parameters: Dict[str, str]
    examples: List[CommandExample]
    notes: List[str]
    permissions: List[str]


class CommandDocumentationBuilder:
    """Builds comprehensive command documentation."""
    
    def __init__(self):
        self.documentation = self._build_documentation()
    
    def _build_documentation(self) -> Dict[str, CommandDocumentation]:
        """Build comprehensive documentation for all commands."""
        return {
            "/add": CommandDocumentation(
                name="/add",
                description="Add a new player to the team with their contact information and position",
                syntax="/add <name> <phone> [position]",
                parameters={
                    "name": "Player's full name (required)",
                    "phone": "UK mobile number in 07xxx or +447xxx format (required)",
                    "position": "Player position: goalkeeper, defender, midfielder, forward, striker, utility (optional, default: utility)"
                },
                examples=[
                    CommandExample(
                        command="/add John Smith +447123456789 midfielder",
                        description="Add John Smith as a midfielder",
                        expected_output="✅ Player John Smith added successfully with ID: JS"
                    ),
                    CommandExample(
                        command="/add Jane Doe 07123456789",
                        description="Add Jane Doe with default utility position",
                        expected_output="✅ Player Jane Doe added successfully with ID: JD"
                    )
                ],
                notes=[
                    "Phone number must be a valid UK mobile number",
                    "Player ID is automatically generated from initials",
                    "Position defaults to 'utility' if not specified"
                ],
                permissions=["leadership", "admin"]
            ),
            
            "/register": CommandDocumentation(
                name="/register",
                description="Register yourself or another player in the system",
                syntax="/register <player_id> or /register <name> <phone> [position]",
                parameters={
                    "player_id": "Existing player ID for simple registration (when used alone)",
                    "name": "Your full name (when doing full registration)",
                    "phone": "Your UK mobile number (when doing full registration)",
                    "position": "Your preferred position (when doing full registration)"
                },
                examples=[
                    CommandExample(
                        command="/register MH",
                        description="Register using existing player ID",
                        expected_output="✅ Registration successful! Welcome to the team, MH"
                    ),
                    CommandExample(
                        command="/register John Smith +447123456789 midfielder",
                        description="Full registration with all details",
                        expected_output="✅ Registration successful! Welcome to the team, John Smith (ID: JS)"
                    )
                ],
                notes=[
                    "Can be used for simple registration with existing player ID",
                    "Or for full registration with name, phone, and position",
                    "Phone number must be a valid UK mobile number"
                ],
                permissions=["public"]
            ),
            
            "/status": CommandDocumentation(
                name="/status",
                description="Check the registration status of a player",
                syntax="/status <phone_or_name>",
                parameters={
                    "phone_or_name": "Player's phone number or name to check"
                },
                examples=[
                    CommandExample(
                        command="/status +447123456789",
                        description="Check status by phone number",
                        expected_output="📱 **Player Status**\nName: John Smith\nID: JS\nStatus: Active\nPosition: Midfielder"
                    ),
                    CommandExample(
                        command="/status John Smith",
                        description="Check status by name",
                        expected_output="📱 **Player Status**\nName: John Smith\nID: JS\nStatus: Active\nPosition: Midfielder"
                    )
                ],
                notes=[
                    "Can search by phone number or player name",
                    "Shows current registration status and details",
                    "Works for both registered and pending players"
                ],
                permissions=["public"]
            ),
            
            "/list": CommandDocumentation(
                name="/list",
                description="List all players with optional filtering",
                syntax="/list [filter]",
                parameters={
                    "filter": "Optional filter: pending, active, inactive (default: all players)"
                },
                examples=[
                    CommandExample(
                        command="/list",
                        description="List all players",
                        expected_output="👥 **All Players**\n• John Smith (JS) - Active - Midfielder\n• Jane Doe (JD) - Pending - Utility"
                    ),
                    CommandExample(
                        command="/list pending",
                        description="List only pending players",
                        expected_output="⏳ **Pending Players**\n• Jane Doe (JD) - Pending - Utility"
                    )
                ],
                notes=[
                    "Shows different information based on chat type",
                    "Main chat shows only active players",
                    "Leadership chat shows all players with status"
                ],
                permissions=["player", "leadership", "admin"]
            ),
            
            "/approve": CommandDocumentation(
                name="/approve",
                description="Approve a player for team participation",
                syntax="/approve <player_id>",
                parameters={
                    "player_id": "Player ID or name to approve"
                },
                examples=[
                    CommandExample(
                        command="/approve JD",
                        description="Approve player with ID JD",
                        expected_output="✅ Player Jane Doe (JD) approved successfully!"
                    ),
                    CommandExample(
                        command="/approve Jane Doe",
                        description="Approve player by name",
                        expected_output="✅ Player Jane Doe (JD) approved successfully!"
                    )
                ],
                notes=[
                    "Only works in leadership chat",
                    "Moves player from pending to active status",
                    "Player will receive notification of approval"
                ],
                permissions=["leadership", "admin"]
            ),
            
            "/reject": CommandDocumentation(
                name="/reject",
                description="Reject a player from team participation",
                syntax="/reject <player_id> [reason]",
                parameters={
                    "player_id": "Player ID or name to reject",
                    "reason": "Optional reason for rejection"
                },
                examples=[
                    CommandExample(
                        command="/reject JD",
                        description="Reject player with default reason",
                        expected_output="❌ Player Jane Doe (JD) rejected: No reason provided"
                    ),
                    CommandExample(
                        command="/reject JD Not available for matches",
                        description="Reject player with specific reason",
                        expected_output="❌ Player Jane Doe (JD) rejected: Not available for matches"
                    )
                ],
                notes=[
                    "Only works in leadership chat",
                    "Moves player to rejected status",
                    "Player will receive notification of rejection"
                ],
                permissions=["leadership", "admin"]
            ),
            
            "/help": CommandDocumentation(
                name="/help",
                description="Show help information for commands",
                syntax="/help [command]",
                parameters={
                    "command": "Optional specific command to get help for"
                },
                examples=[
                    CommandExample(
                        command="/help",
                        description="Show general help",
                        expected_output="🤖 **KICKAI Bot Commands**\n\n**Player Management:**\n• /add - Add a new player\n..."
                    ),
                    CommandExample(
                        command="/help /add",
                        description="Show help for specific command",
                        expected_output="📖 **/add**\n\n**Description:** Add a new player to the team\n..."
                    )
                ],
                notes=[
                    "Shows general help if no command specified",
                    "Shows detailed help for specific command if provided",
                    "Available to all users"
                ],
                permissions=["public"]
            )
        }
    
    def get_documentation(self, command_name: str) -> Optional[CommandDocumentation]:
        """Get documentation for a specific command."""
        return self.documentation.get(command_name)
    
    def get_all_commands(self) -> List[str]:
        """Get list of all documented commands."""
        return list(self.documentation.keys())
    
    def get_commands_by_category(self, category: str) -> List[str]:
        """Get commands by category."""
        categories = {
            "player": ["/add", "/register", "/status", "/list", "/approve", "/reject", "/invitelink"],
            "match": ["/creatematch", "/listmatches", "/attend", "/unattend"],
            "payment": ["/createpayment", "/paymentstatus", "/pendingpayments"],
            "admin": ["/broadcast", "/promoteuser", "/demoteuser"],
            "system": ["/help"]
        }
        
        return categories.get(category, [])
    
    def generate_markdown_documentation(self) -> str:
        """Generate complete markdown documentation."""
        markdown = "# KICKAI Bot Command Documentation\n\n"
        markdown += "This document provides comprehensive documentation for all KICKAI bot commands.\n\n"
        
        # Group by category
        categories = {
            "Player Management": ["/add", "/register", "/status", "/list", "/approve", "/reject", "/invitelink"],
            "Match Management": ["/creatematch", "/listmatches", "/attend", "/unattend"],
            "Payment Management": ["/createpayment", "/paymentstatus", "/pendingpayments"],
            "Admin Commands": ["/broadcast", "/promoteuser", "/demoteuser"],
            "System Commands": ["/help"]
        }
        
        for category, commands in categories.items():
            markdown += f"## {category}\n\n"
            
            for command in commands:
                if command in self.documentation:
                    doc = self.documentation[command]
                    markdown += f"### {doc.name}\n\n"
                    markdown += f"{doc.description}\n\n"
                    markdown += f"**Syntax:** `{doc.syntax}`\n\n"
                    
                    if doc.parameters:
                        markdown += "**Parameters:**\n"
                        for param, desc in doc.parameters.items():
                            markdown += f"- `{param}`: {desc}\n"
                        markdown += "\n"
                    
                    if doc.examples:
                        markdown += "**Examples:**\n"
                        for example in doc.examples:
                            markdown += f"- `{example.command}` - {example.description}\n"
                        markdown += "\n"
                    
                    if doc.notes:
                        markdown += "**Notes:**\n"
                        for note in doc.notes:
                            markdown += f"- {note}\n"
                        markdown += "\n"
                    
                    if doc.permissions:
                        markdown += f"**Permissions:** {', '.join(doc.permissions)}\n\n"
                    
                    markdown += "---\n\n"
        
        return markdown 