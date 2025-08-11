#!/usr/bin/env python3
"""
UI Formatter

This module provides formatting utilities to convert JSON tool responses
into human-friendly display text while maintaining the structured data.
"""

import json
from typing import Dict, Any, List, Optional
from .json_response import ToolResponse


class UIFormatter:
    """Format JSON data for human-readable display."""
    
    @staticmethod
    def format_team_overview(data: Dict[str, Any]) -> str:
        """Format team overview data."""
        team_id = data.get("team_id", "Unknown")
        players = data.get("players", [])
        team_members = data.get("team_members", [])
        
        result = f"📋 Team Overview for {team_id}\n\n"
        
        if team_members:
            result += "👔 Team Members:\n"
            for member in team_members:
                result += f"• {member['name']} - {member['role'].title()}\n"
            result += "\n"
        else:
            result += "👔 No team members found\n\n"
        
        if players:
            result += "👥 Players:\n"
            for player in players:
                status_emoji = "✅" if player['status'].lower() == "active" else "⏳"
                result += f"• {player['name']} - {player['position']} {status_emoji} {player['status'].title()}"
                if player.get('player_id'):
                    result += f" (ID: {player['player_id']})"
                result += "\n"
        else:
            result += "👥 No players found"
        
        return result
    
    @staticmethod
    def format_player_list(data: Dict[str, Any]) -> str:
        """Format player list data."""
        players = data.get("players", [])
        if not players:
            return "👥 No players found"
        
        result = "👥 Players:\n"
        for player in players:
            status_emoji = "✅" if player['status'].lower() == "active" else "⏳"
            result += f"• {player['name']} - {player['position']} {status_emoji} {player['status'].title()}"
            if player.get('player_id'):
                result += f" (ID: {player['player_id']})"
            result += "\n"
        
        return result
    
    @staticmethod
    def format_match_details(data: Dict[str, Any]) -> str:
        """Format match details data."""
        match = data.get("match", {})
        if not match:
            return "📋 No match details found"
        
        return f"""📋 Match Details

🏆 Match ID: {match.get('match_id', 'N/A')}
📅 Date: {match.get('date', 'N/A')}
⏰ Time: {match.get('time', 'N/A')}
📍 Location: {match.get('location', 'N/A')}
👥 Opponent: {match.get('opponent', 'N/A')}
📊 Status: {match.get('status', 'N/A')}"""
    
    @staticmethod
    def format_attendance_list(data: Dict[str, Any]) -> str:
        """Format attendance list data."""
        attendance_records = data.get("attendance", [])
        match_info = data.get("match_info", {})
        
        if not attendance_records:
            return "📊 No attendance records found"
        
        result = f"📊 Attendance for {match_info.get('match_id', 'Unknown Match')}\n\n"
        
        for record in attendance_records:
            status_emoji = "✅" if record['status'].lower() == "yes" else "❌"
            result += f"• {record['player_name']} - {status_emoji} {record['status'].title()}\n"
        
        return result
    
    @staticmethod
    def format_help_response(data: Dict[str, Any]) -> str:
        """Format help response data."""
        help_info = data.get("help", {})
        commands = help_info.get("commands", {})
        chat_type = help_info.get("chat_type", "unknown")
        
        result = f"📋 Available Commands ({chat_type.title()} Chat)\n\n"
        
        for category, cmd_list in commands.items():
            result += f"🔹 {category.title()}:\n"
            for cmd in cmd_list:
                result += f"  • {cmd['name']} - {cmd['description']}\n"
            result += "\n"
        
        result += "💡 Use `/help [command]` for detailed help on any command."
        return result
    
    @staticmethod
    def format_system_info(data: Dict[str, Any]) -> str:
        """Format system information data."""
        return f"""📋 System Information

🔧 Version: {data.get('version', 'N/A')}
📅 Build Date: {data.get('build_date', 'N/A')}
🐍 Python: {data.get('python_version', 'N/A')}
🤖 CrewAI: {data.get('crewai_version', 'N/A')}"""
    
    @staticmethod
    def format_announcement(data: Dict[str, Any]) -> str:
        """Format announcement data."""
        announcement = data.get("announcement", {})
        message = announcement.get("message", "")
        chat_type = announcement.get("chat_type", "unknown")
        
        return f"📢 Announcement sent to {chat_type} chat:\n\n{message}"
    
    @staticmethod
    def format_error_response(data: Dict[str, Any]) -> str:
        """Format error response data."""
        error = data.get("error", "Unknown error")
        message = data.get("message", "An error occurred")
        
        return f"❌ Error: {error}\n\n{message}"


class DynamicUIFormatter:
    """Dynamic UI formatting based on data structure."""
    
    @staticmethod
    def format_response(response: ToolResponse) -> str:
        """Format any tool response for UI display."""
        if not response.success:
            return UIFormatter.format_error_response({
                "error": response.error or "Unknown error",
                "message": response.message
            })
        
        # Use provided UI format if available
        if response.ui_format:
            return response.ui_format
        
        # Generate format based on data structure
        return DynamicUIFormatter._generate_format(response.data)
    
    @staticmethod
    def _generate_format(data: Dict[str, Any]) -> str:
        """Generate UI format based on data structure."""
        # Auto-detect format based on data keys
        if "players" in data and "team_members" in data:
            return UIFormatter.format_team_overview(data)
        elif "players" in data:
            return UIFormatter.format_player_list(data)
        elif "match" in data:
            return UIFormatter.format_match_details(data)
        elif "attendance" in data:
            return UIFormatter.format_attendance_list(data)
        elif "help" in data:
            return UIFormatter.format_help_response(data)
        elif "announcement" in data:
            return UIFormatter.format_announcement(data)
        elif "version" in data or "python_version" in data:
            return UIFormatter.format_system_info(data)
        else:
            # Fallback to simple JSON display for unknown structures
            return f"📋 Data:\n{json.dumps(data, indent=2)}"
    
    @staticmethod
    def format_json_response(json_str: str) -> str:
        """Format a JSON response string for UI display."""
        try:
            from .json_response import JSONResponseBuilder
            response = JSONResponseBuilder.from_json(json_str)
            if response:
                return DynamicUIFormatter.format_response(response)
            else:
                return f"❌ Error: Invalid JSON response format"
        except Exception as e:
            return f"❌ Error: Failed to parse response ({str(e)})"


class UIFormatBuilder:
    """Builder for creating UI formats from data."""
    
    @staticmethod
    def build_team_overview(team_id: str, players: List[Dict], team_members: List[Dict]) -> str:
        """Build team overview UI format."""
        data = {
            "team_id": team_id,
            "players": players,
            "team_members": team_members
        }
        return UIFormatter.format_team_overview(data)
    
    @staticmethod
    def build_player_list(players: List[Dict]) -> str:
        """Build player list UI format."""
        data = {"players": players}
        return UIFormatter.format_player_list(data)
    
    @staticmethod
    def build_match_details(match: Dict[str, Any]) -> str:
        """Build match details UI format."""
        data = {"match": match}
        return UIFormatter.format_match_details(data)
    
    @staticmethod
    def build_attendance_list(attendance: List[Dict], match_info: Dict[str, Any]) -> str:
        """Build attendance list UI format."""
        data = {
            "attendance": attendance,
            "match_info": match_info
        }
        return UIFormatter.format_attendance_list(data)
    
    @staticmethod
    def build_help_response(help_data: Dict[str, Any]) -> str:
        """Build help response UI format."""
        data = {"help": help_data}
        return UIFormatter.format_help_response(data)
    
    @staticmethod
    def build_system_info(system_data: Dict[str, Any]) -> str:
        """Build system info UI format."""
        return UIFormatter.format_system_info(system_data)
    
    @staticmethod
    def build_announcement(message: str, chat_type: str) -> str:
        """Build announcement UI format."""
        data = {
            "announcement": {
                "message": message,
                "chat_type": chat_type
            }
        }
        return UIFormatter.format_announcement(data)
