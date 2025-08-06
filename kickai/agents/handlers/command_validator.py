"""
Command validator for validating commands based on context.

This handler extracts command validation logic from AgenticMessageRouter,
implementing single responsibility principle.
"""

from __future__ import annotations

from loguru import logger

from kickai.core.enums import ChatType, PermissionLevel
from kickai.core.interfaces import ICommandValidator
from kickai.core.value_objects import EntityContext


class CommandValidator(ICommandValidator):
    """
    Validates commands based on context and permissions.

    This class is responsible for:
    - Validating command permissions for chat type
    - Checking user roles and permissions
    - Providing validation error messages
    - Identifying helper commands
    """

    def __init__(self):
        # Helper commands that provide system information
        self.helper_commands: set[str] = {
            "/help", "/commands", "/info", "/status", "/version"
        }

        # Command permissions by chat type
        self.chat_permissions: dict[ChatType, dict[str, PermissionLevel]] = {
            ChatType.MAIN: {
                "/help": PermissionLevel.PUBLIC,
                "/myinfo": PermissionLevel.PLAYER,
                "/list": PermissionLevel.PLAYER,
                "/available": PermissionLevel.PLAYER,
                "/unavailable": PermissionLevel.PLAYER,
                "/status": PermissionLevel.PLAYER,
            },
            ChatType.LEADERSHIP: {
                "/help": PermissionLevel.PUBLIC,
                "/list": PermissionLevel.LEADERSHIP,
                "/approve": PermissionLevel.LEADERSHIP,
                "/addplayer": PermissionLevel.LEADERSHIP,
                "/addmember": PermissionLevel.LEADERSHIP,
                "/update": PermissionLevel.LEADERSHIP,
                "/remove": PermissionLevel.ADMIN,
            },
            ChatType.PRIVATE: {
                "/help": PermissionLevel.PUBLIC,
                "/myinfo": PermissionLevel.PLAYER,
                "/status": PermissionLevel.PLAYER,
            }
        }

        # User permission hierarchy
        self.permission_hierarchy: dict[PermissionLevel, int] = {
            PermissionLevel.PUBLIC: 0,
            PermissionLevel.PLAYER: 1,
            PermissionLevel.LEADERSHIP: 2,
            PermissionLevel.ADMIN: 3,
            PermissionLevel.SYSTEM: 4,
        }

    def validate_command_for_chat(
        self,
        command: str,
        context: EntityContext
    ) -> bool:
        """
        Validate if command is allowed in the given context.

        Args:
            command: Command to validate
            context: Entity context for validation

        Returns:
            True if command is valid for context
        """
        try:
            # Helper commands are always allowed
            if self.is_helper_command(command):
                return True

            # Get required permission for command in this chat type
            chat_perms = self.chat_permissions.get(context.chat_type, {})
            required_permission = chat_perms.get(command)

            if required_permission is None:
                # Command not defined for this chat type
                return False

            # Check if user has required permission
            user_permission = self._get_user_permission_level(context)
            return self._has_permission(user_permission, required_permission)

        except Exception as e:
            logger.error(f"Error validating command {command}: {e}")
            return False

    def is_helper_command(self, command: str) -> bool:
        """
        Check if command is a helper command.

        Args:
            command: Command to check

        Returns:
            True if helper command
        """
        if not command:
            return False
        return command.lower() in self.helper_commands

    def get_validation_error_message(
        self,
        command: str,
        context: EntityContext
    ) -> str:
        """
        Get error message for invalid command.

        Args:
            command: Invalid command
            context: Entity context

        Returns:
            Error message for user
        """
        try:
            # Check if command exists in any chat type
            all_commands = set()
            for chat_commands in self.chat_permissions.values():
                all_commands.update(chat_commands.keys())

            if command not in all_commands:
                return self._create_unknown_command_message(command, context)

            # Command exists but not allowed in this context
            if context.chat_type not in self.chat_permissions:
                return self._create_chat_not_supported_message(context)

            chat_perms = self.chat_permissions[context.chat_type]
            if command not in chat_perms:
                return self._create_command_not_available_message(command, context)

            # Command exists but user lacks permission
            required_permission = chat_perms[command]
            user_permission = self._get_user_permission_level(context)

            if not self._has_permission(user_permission, required_permission):
                return self._create_insufficient_permission_message(
                    command, required_permission, context
                )

            return "❌ Command validation failed for unknown reason."

        except Exception as e:
            logger.error(f"Error creating validation error message: {e}")
            return "❌ Unable to validate command. Please try again."

    def get_available_commands(self, context: EntityContext) -> list[str]:
        """Get list of commands available to user in current context."""
        try:
            chat_perms = self.chat_permissions.get(context.chat_type, {})
            user_permission = self._get_user_permission_level(context)

            available = []
            for command, required_perm in chat_perms.items():
                if self._has_permission(user_permission, required_perm):
                    available.append(command)

            # Add helper commands
            available.extend(self.helper_commands)

            return sorted(list(set(available)))

        except Exception as e:
            logger.error(f"Error getting available commands: {e}")
            return list(self.helper_commands)

    def _get_user_permission_level(self, context: EntityContext) -> PermissionLevel:
        """Get user's permission level based on registration."""
        if context.user_registration.is_admin:
            return PermissionLevel.ADMIN
        elif context.user_registration.is_leadership:
            return PermissionLevel.LEADERSHIP
        elif context.user_registration.has_any_role():
            return PermissionLevel.PLAYER
        else:
            return PermissionLevel.PUBLIC

    def _has_permission(
        self,
        user_permission: PermissionLevel,
        required_permission: PermissionLevel
    ) -> bool:
        """Check if user permission meets required permission."""
        user_level = self.permission_hierarchy.get(user_permission, 0)
        required_level = self.permission_hierarchy.get(required_permission, 0)
        return user_level >= required_level

    def _create_unknown_command_message(
        self,
        command: str,
        context: EntityContext
    ) -> str:
        """Create message for unknown command."""
        available = self.get_available_commands(context)
        available_str = ", ".join(available[:5])  # Show first 5

        return f"""❌ **Unknown Command: {command}**

**Available commands:**
{available_str}

Type /help to see all available commands and their descriptions."""

    def _create_chat_not_supported_message(self, context: EntityContext) -> str:
        """Create message for unsupported chat type."""
        return f"""❌ **Chat Type Not Supported**

Commands are not available in {context.chat_type.value} chat.

Please try in:
- Main team chat for player commands
- Leadership chat for admin commands
- Private chat for personal commands"""

    def _create_command_not_available_message(
        self,
        command: str,
        context: EntityContext
    ) -> str:
        """Create message for command not available in current chat."""
        chat_name = {
            ChatType.MAIN: "main team chat",
            ChatType.LEADERSHIP: "leadership chat",
            ChatType.PRIVATE: "private chat"
        }.get(context.chat_type, "this chat")

        return f"""❌ **Command Not Available**

`{command}` is not available in {chat_name}.

**Try:**
- /help to see available commands
- Moving to the appropriate chat type"""

    def _create_insufficient_permission_message(
        self,
        command: str,
        required_permission: PermissionLevel,
        context: EntityContext
    ) -> str:
        """Create message for insufficient permissions."""
        permission_names = {
            PermissionLevel.PLAYER: "player",
            PermissionLevel.LEADERSHIP: "leadership",
            PermissionLevel.ADMIN: "admin"
        }

        required_name = permission_names.get(required_permission, "special")
        current_role = context.user_registration.primary_role()

        return f"""❌ **Insufficient Permissions**

`{command}` requires {required_name} permissions.

**Your current role:** {current_role}
**Required role:** {required_name}

Contact team leadership if you need access to this command."""
