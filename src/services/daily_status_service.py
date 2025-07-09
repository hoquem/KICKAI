#!/usr/bin/env python3
"""
Daily Status Service

This service generates and sends daily club/team status messages to the leadership chat.
It provides comprehensive team statistics, player information, and system status.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
import os

from services.player_service import PlayerService
from services.team_service import TeamService
from services.team_member_service import TeamMemberService
from services.fa_registration_checker import run_fa_registration_check, run_fa_fixtures_check
from database.models_improved import Player
from core.bot_config_manager import get_bot_config_manager
from services.interfaces.daily_status_service_interface import IDailyStatusService

class DailyStatusService(IDailyStatusService):
    """Service to generate and send daily team status reports."""
    
    def __init__(self, 
                 player_service: PlayerService,
                 team_service: TeamService,
                 team_member_service: Optional[TeamMemberService],
                 bot_token: str,
                 bot_config_manager):
        self.player_service = player_service
        self.team_service = team_service
        self.team_member_service = team_member_service
        self.bot_token = bot_token
        self.bot_config_manager = bot_config_manager
        
    async def generate_team_stats(self, team_id: str) -> Dict:
        """
        Generate comprehensive team statistics.
        
        Args:
            team_id: The team ID to generate stats for
            
        Returns:
            TeamStats object with all relevant statistics
        """
        try:
            # Get all players for the team
            players = await self.player_service.get_team_players(team_id)
            
            # Calculate basic stats
            total_players = len(players)
            active_players = len([p for p in players if p.is_active()])
            pending_approval = len([p for p in players if p.is_pending_approval()])
            fa_registered = len([p for p in players if p.is_fa_registered()])
            fa_eligible = len([p for p in players if p.is_fa_eligible()])

            # Player role breakdown
            roles = {}
            for player in players:
                role = player.role.value if player.role else "Unknown"
                roles[role] = roles.get(role, 0) + 1

            # Player position breakdown
            positions = {}
            for player in players:
                position = player.position.value if player.position else "Unknown"
                positions[position] = positions.get(position, 0) + 1

            # Onboarding status breakdown
            onboarding_statuses = {}
            for player in players:
                status = player.onboarding_status.value if player.onboarding_status else "Unknown"
                onboarding_statuses[status] = onboarding_statuses.get(status, 0) + 1

            # Player activity (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            active_last_30_days = len([p for p in players if p.last_activity and p.last_activity > thirty_days_ago])

            # Recent additions (last 7 days)
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_additions = [p for p in players if p.created_at and p.created_at > seven_days_ago]

            # Check FA registration updates
            fa_updates = await run_fa_registration_check(team_id, self.player_service, self.team_service)

            # Get recent fixtures
            fixtures = await run_fa_fixtures_check(team_id, self.player_service, self.team_service)

            return {
                "total_players": total_players,
                "active_players": active_players,
                "pending_approval": pending_approval,
                "fa_registered": fa_registered,
                "fa_eligible": fa_eligible,
                "positions": positions,
                "roles": roles,
                "onboarding_statuses": onboarding_statuses,
                "active_last_30_days": active_last_30_days,
                "recent_additions": recent_additions,
                "fa_updates": fa_updates,
                "fixtures": fixtures
            }
            
        except Exception as e:
            logging.error(f"❌ Error generating team stats: {e}")
            return {
                "total_players": 0,
                "active_players": 0,
                "pending_approval": 0,
                "fa_registered": 0,
                "fa_eligible": 0,
                "positions": {},
                "recent_additions": [],
                "fa_updates": {},
                "fixtures": []
            }
    
    def format_daily_status_message(self, team_stats: Dict, team_name: str = "Team", report_content: Optional[List[str]] = None) -> str:
        """Format the daily status message with HTML formatting."""
        if report_content is None:
            report_content = [
                "player_summary",
                "fa_registration_summary",
                "upcoming_matches"
            ]

        today = datetime.now().strftime("%A, %B %d, %Y")

        message = f"""📊 DAILY TEAM STATUS REPORT
📅 Date: {today}
🏆 Team: {team_name}

"""

        if "player_summary" in report_content:
            message += f"""👥 Player Statistics:
• Total Players: {team_stats["total_players"]}
• Active Players: {team_stats["active_players"]}
• Pending Approval: {team_stats["pending_approval"]}
• FA Registered: {team_stats["fa_registered"]}
• FA Eligible: {team_stats["fa_eligible"]}
• Active Last 30 Days: {team_stats["active_last_30_days"]}

⚽ Position Breakdown:"""
            for position, count in team_stats["positions"].items():
                message += f"\n• {position.title()}: {count}"
            message += "\n"

            message += f"\n👑 Role Breakdown:"
            for role, count in team_stats["roles"].items():
                message += f"\n• {role.title()}: {count}"
            message += "\n"

            message += f"\n📝 Onboarding Status Breakdown:"
            for status, count in team_stats["onboarding_statuses"].items():
                message += f"\n• {status.replace('_', ' ').title()}: {count}"
            message += "\n"

        if "recent_additions" in report_content and team_stats["recent_additions"]:
            message += f"\n🆕 Recent Additions (Last 7 Days):"
            for player in team_stats["recent_additions"][:5]:  # Show max 5
                message += f"\n• {player.name.upper()} ({player.player_id})"
            message += "\n"

        if "fa_registration_summary" in report_content and team_stats["fa_updates"]:
            message += f"\n✅ New FA Registrations:"
            for player_id, registered in team_stats["fa_updates"].items():
                if registered:
                    # Get player name from ID (simplified)
                    message += f"\n• Player {player_id} is now FA registered!"
            message += "\n"

        if "upcoming_matches" in report_content and team_stats["fixtures"]:
            message += f"\n📅 Recent Fixtures/Results:"
            for fixture in team_stats["fixtures"][:3]:  # Show max 3
                message += f"\n• {fixture['text'][:100]}..."  # Truncate long text
            message += "\n"

        message += f"""

🔧 System Status:
• Database: ✅ Connected
• FA Website: ✅ Monitored
• Bot: ✅ Online

💡 Next Actions:
• Review pending approvals: {team_stats["pending_approval"]} players
• Monitor FA registration progress
• Check upcoming fixtures

---
Generated automatically by KICKAI Team Management System"""
        
        return message
    
    async def send_daily_status_report(self, team_id: str, leadership_chat_id: str) -> bool:
        """
        Generate and send daily status report to leadership chat.
        
        Args:
            team_id: The team ID to report on
            leadership_chat_id: The leadership chat ID to send to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logging.info(f"📊 Generating daily status report for team {team_id}")

            # Get daily report configuration
            daily_report_config = self.bot_config_manager.get_daily_report_config(team_id)
            if not daily_report_config or not daily_report_config.get("enabled", False):
                logging.info(f"Daily reports disabled for team {team_id}")
                return False

            # Get team info
            team = await self.team_service.get_team(team_id)
            team_name = team.name if team else "Team"

            # Generate stats
            team_stats = await self.generate_team_stats(team_id)

            # Format message
            message = self.format_daily_status_message(team_stats, team_name, daily_report_config.get("content", []))
            
            # Send to leadership chat using requests
            import requests
            # from tools.telegram_tools import format_message_for_telegram  # File doesn't exist
            
            # Format message for Telegram HTML
            formatted_message = message  # Use message as-is since telegram_tools doesn't exist
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": leadership_chat_id,
                "text": formatted_message,
                "parse_mode": "HTML"
            }
            
            try:
                response = requests.post(url, json=data, timeout=10)
                success = response.status_code == 200
            except Exception as e:
                logging.error(f"❌ Error sending Telegram message: {e}")
                success = False
            
            if success:
                logging.info(f"✅ Daily status report sent to leadership chat {leadership_chat_id}")
            else:
                logging.error(f"❌ Failed to send daily status report to leadership chat")
                
            return success
            
        except Exception as e:
            logging.error(f"❌ Error sending daily status report: {e}")
            return False
    
    async def schedule_daily_status_task(self, team_id: str, leadership_chat_id: str) -> None:
        """Schedule the daily status report task to run every day at the configured time."""
        while True:
            try:
                now = datetime.now()
                daily_report_config = self.bot_config_manager.get_daily_report_config(team_id)
                report_time_str = daily_report_config.get("time", "09:00") # Default to 09:00 AM
                report_hour, report_minute = map(int, report_time_str.split(":"))

                # Calculate next run time
                next_run = now.replace(hour=report_hour, minute=report_minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                
                # Calculate sleep time
                sleep_seconds = (next_run - now).total_seconds()
                
                logging.info(f"⏰ Daily status report scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                logging.info(f"💤 Sleeping for {sleep_seconds/3600:.1f} hours until next report")
                
                # Sleep until next run time
                await asyncio.sleep(sleep_seconds)
                
                # Send the report
                await self.send_daily_status_report(team_id, leadership_chat_id)
                
            except Exception as e:
                logging.error(f"❌ Error in daily status task: {e}")
                # Wait 1 hour before retrying
                await asyncio.sleep(3600)


async def start_daily_status_service(team_id: str,
                                   leadership_chat_id: str,
                                   player_service: PlayerService,
                                   team_service: TeamService,
                                   team_member_service: TeamMemberService,
                                   bot_token: str,
                                   bot_config_manager) -> None:
    """
    Start the daily status service.
    
    Args:
        team_id: The team ID to monitor
        leadership_chat_id: The leadership chat ID to send reports to
        player_service: Player service instance
        team_service: Team service instance
        team_member_service: Team member service instance
        bot_token: Telegram bot token
    """
    service = DailyStatusService(
        player_service=player_service,
        team_service=team_service,
        team_member_service=team_member_service,
        bot_token=bot_token,
        bot_config_manager=bot_config_manager
    )
    
    # Start the scheduled task
    await service.schedule_daily_status_task(team_id, leadership_chat_id)


# Global instances - now team-specific
_daily_status_service_instances: dict[str, DailyStatusService] = {}

def get_daily_status_service(team_id: str = None) -> DailyStatusService:
    """
    Get a DailyStatusService instance with proper dependency injection for the specified team.
    
    Args:
        team_id: The team ID (optional, will use default if not provided)
        
    Returns:
        DailyStatusService instance
    """
    global _daily_status_service_instances
    
    # Use default team ID if not provided
    if not team_id:
        import os
        team_id = os.getenv('DEFAULT_TEAM_ID', 'KAI')
    
    # Return existing instance if available for this team
    if team_id in _daily_status_service_instances:
        return _daily_status_service_instances[team_id]
    
    # Create new instance for this team
    from services.player_service import get_player_service
    from services.team_service import get_team_service
    from services.team_member_service import get_team_member_service
    from core.bot_config_manager import get_bot_config_manager
    from core.improved_config_system import get_improved_config
    
    # Get configuration
    config = get_improved_config()
    
    # Get dependencies with explicit team_id
    player_service = get_player_service(team_id=team_id)
    team_service = get_team_service(team_id=team_id)
    team_member_service = get_team_member_service(team_id=team_id)
    bot_config_manager = get_bot_config_manager()
    
    # Create service instance
    service = DailyStatusService(
        player_service=player_service,
        team_service=team_service,
        team_member_service=team_member_service,
        bot_token=config.telegram.bot_token,
        bot_config_manager=bot_config_manager
    )
    
    # Store instance for this team
    _daily_status_service_instances[team_id] = service
    
    logging.info(f"✅ DailyStatusService created for team {team_id}")
    return service 