#!/usr/bin/env python3
"""
JSON Tool Example

This example demonstrates how to convert an existing tool from formatted string output
to JSON output while maintaining human-friendly UI display.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kickai.utils.json_response import JSONResponseBuilder, create_data_response
from kickai.utils.ui_formatter import UIFormatBuilder, DynamicUIFormatter


# BEFORE: Original tool with formatted string output
def list_team_members_and_players_old(team_id: str) -> str:
    """Original tool that returns formatted string (problematic for LLM parsing)."""
    try:
        # Simulate getting data from services
        team_members = [
            {"name": "Coach Wilson", "role": "Coach"},
            {"name": "Manager Smith", "role": "Manager"}
        ]
        
        players = [
            {"name": "John Doe", "position": "Forward", "status": "Active", "player_id": "JD001"},
            {"name": "Jane Smith", "position": "Midfielder", "status": "Active", "player_id": "JS002"}
        ]
        
        # Return formatted string (this causes LLM parsing issues)
        result = f"📋 Team Overview for {team_id}\n\n"
        
        if team_members:
            result += "👔 Team Members:\n"
            for member in team_members:
                result += f"• {member['name']} - {member['role'].title()}\n"
            result += "\n"
        
        if players:
            result += "👥 Players:\n"
            for player in players:
                status_emoji = "✅" if player['status'].lower() == "active" else "⏳"
                result += f"• {player['name']} - {player['position']} {status_emoji} {player['status'].title()}"
                if player.get('player_id'):
                    result += f" (ID: {player['player_id']})"
                result += "\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


# AFTER: New tool with JSON output
def list_team_members_and_players_new(team_id: str) -> str:
    """New tool that returns JSON (better for LLM parsing)."""
    try:
        # Simulate getting data from services
        team_members = [
            {"name": "Coach Wilson", "role": "Coach"},
            {"name": "Manager Smith", "role": "Manager"}
        ]
        
        players = [
            {"name": "John Doe", "position": "Forward", "status": "Active", "player_id": "JD001"},
            {"name": "Jane Smith", "position": "Midfielder", "status": "Active", "player_id": "JS002"}
        ]
        
        # Create structured data
        data = {
            "team_id": team_id,
            "team_members": team_members,
            "players": players
        }
        
        # Generate UI format for human display
        ui_format = UIFormatBuilder.build_team_overview(team_id, players, team_members)
        
        # Return JSON response with UI format
        return create_data_response(data, ui_format)
        
    except Exception as e:
        return JSONResponseBuilder.to_json(
            JSONResponseBuilder.error(str(e), "Failed to retrieve team data")
        )


# Example of how the agent would process the response
def process_tool_response_for_ui(tool_response: str) -> str:
    """Process tool response and extract human-friendly display."""
    try:
        # Parse JSON response
        response = JSONResponseBuilder.from_json(tool_response)
        if response:
            # Return UI format for human display
            return DynamicUIFormatter.format_response(response)
        else:
            return "❌ Error: Invalid response format"
    except Exception as e:
        return f"❌ Error: Failed to process response ({str(e)})"


def demonstrate_migration():
    """Demonstrate the migration from old to new format."""
    print("🔄 JSON Tool Migration Demonstration")
    print("=" * 50)
    
    team_id = "KTI"
    
    print("\n📋 BEFORE: Original tool output (formatted string)")
    print("-" * 40)
    old_result = list_team_members_and_players_old(team_id)
    print(old_result)
    
    print("\n🔧 PROBLEM: This formatted string causes LLM parsing issues")
    print("- Contains emojis and special characters")
    print("- Multi-line formatted text")
    print("- Complex structure that confuses open-source LLMs")
    
    print("\n📋 AFTER: New tool output (JSON)")
    print("-" * 40)
    new_result = list_team_members_and_players_new(team_id)
    print(new_result)
    
    print("\n✅ BENEFITS: JSON output is better for LLM parsing")
    print("- Structured, parseable data")
    print("- Consistent format across all tools")
    print("- Works with all LLM providers")
    print("- Contains both data and UI format")
    
    print("\n👥 USER DISPLAY: Human-friendly format extracted from JSON")
    print("-" * 40)
    user_display = process_tool_response_for_ui(new_result)
    print(user_display)
    
    print("\n🎯 RESULT: Users see the same friendly format, but LLMs get structured data!")
    print("=" * 50)


def demonstrate_error_handling():
    """Demonstrate error handling in JSON format."""
    print("\n🚨 Error Handling Demonstration")
    print("=" * 30)
    
    # Simulate an error
    def failing_tool() -> str:
        """Tool that fails."""
        raise Exception("Service temporarily unavailable")
    
    try:
        result = failing_tool()
    except Exception as e:
        # Return JSON error response
        error_response = JSONResponseBuilder.to_json(
            JSONResponseBuilder.error(str(e), "Failed to retrieve data")
        )
        print("JSON Error Response:")
        print(error_response)
        
        print("\nUser Display:")
        user_display = process_tool_response_for_ui(error_response)
        print(user_display)


def demonstrate_different_data_types():
    """Demonstrate different data type formatting."""
    print("\n📊 Different Data Type Examples")
    print("=" * 30)
    
    # Player list example
    players_data = {
        "players": [
            {"name": "John Doe", "position": "Forward", "status": "Active", "player_id": "JD001"},
            {"name": "Jane Smith", "position": "Midfielder", "status": "Pending", "player_id": "JS002"}
        ]
    }
    
    ui_format = UIFormatBuilder.build_player_list(players_data["players"])
    player_response = create_data_response(players_data, ui_format)
    
    print("Player List Response:")
    print(player_response)
    
    print("\nUser Display:")
    user_display = process_tool_response_for_ui(player_response)
    print(user_display)
    
    # Match details example
    match_data = {
        "match": {
            "match_id": "MATCH001",
            "date": "2025-01-15",
            "time": "14:00",
            "location": "Home Ground",
            "opponent": "Team B",
            "status": "Scheduled"
        }
    }
    
    ui_format = UIFormatBuilder.build_match_details(match_data["match"])
    match_response = create_data_response(match_data, ui_format)
    
    print("\nMatch Details Response:")
    print(match_response)
    
    print("\nUser Display:")
    user_display = process_tool_response_for_ui(match_response)
    print(user_display)


if __name__ == "__main__":
    demonstrate_migration()
    demonstrate_error_handling()
    demonstrate_different_data_types()
    
    print("\n🎉 Migration demonstration complete!")
    print("\nKey Benefits:")
    print("✅ Eliminates LLM parsing errors")
    print("✅ Maintains human-friendly UI")
    print("✅ Provides structured data for processing")
    print("✅ Works with all LLM providers")
    print("✅ Consistent error handling")
    print("✅ Easy to test and debug")
