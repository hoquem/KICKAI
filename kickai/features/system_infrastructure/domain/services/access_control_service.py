"""
Minimal AccessControlService for unit tests.
"""


class AccessControlService:
    """Simple access control checks used in tests."""

    def is_admin_command(self, command: str) -> bool:
        command = (command or "").lower().strip()
        return command.startswith("add") or command.startswith("remove")

    def is_read_only_command(self, command: str) -> bool:
        command = (command or "").lower().strip()
        return command.startswith("list") or command == "help"
