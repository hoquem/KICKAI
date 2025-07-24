
import re

from crewai.tools import tool


@tool("Parse Registration Command")
def parse_registration_command(command: str) -> dict[str, str] | None:
    """
    Parses the /register command to extract the user's name, phone number, and role.
    This tool is essential for the player registration process and should be used by the Registration Agent.

    Args:
        command: The full command string (e.g., "/register John Smith +1234567890 Team Manager").

    Returns:
        A dictionary containing the user's name, phone, and role, or None if parsing fails.
    """
    # Regex to capture the name, phone number, and role
    match = re.match(r"/register\s+(.+?)\s+((?:\+\d{1,3})?\s?\d{1,4}[-\s]?\d{1,4}[-\s]?\d{1,9})\s+(.+)""", command)
    if match:
        return {
            "name": match.group(1).strip(),
            "phone": match.group(2).strip(),
            "role": match.group(3).strip(),
        }
    return None
