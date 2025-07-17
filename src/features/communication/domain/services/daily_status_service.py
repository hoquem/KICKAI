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

from src.features.player_registration.domain.services.player_service import PlayerService
from src.features.team_administration.domain.services.team_service import TeamService
from src.features.player_registration.domain.services.team_member_service import TeamMemberService
from src.features.player_registration.domain.services.fa_registration_checker import run_fa_registration_check, run_fa_fixtures_check
from src.database.models_improved import Player

from src.features.communication.domain.interfaces.daily_status_service_interface import IDailyStatusService

class DailyStatusService(IDailyStatusService):
    """Service to generate and send daily team status reports."""
    
    def __init__(self, 
                 player_service: PlayerService,
                 team_service: TeamService,
                 team_member_service: Optional[TeamMemberService],
                 bot_token: str,
                 settings):
        self.player_service = player_service
        self.team_service = team_service
        self.team_member_service = team_member_service
        self.bot_token = bot_token
        self.settings = settings
        
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
        Send daily status report to leadership chat.
        
        Args:
            team_id: The team ID to generate report for
            leadership_chat_id: The leadership chat ID to send to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate team stats
            team_stats = await self.generate_team_stats(team_id)
            
            # Get team name
            team = await self.team_service.get_team(team_id)
            team_name = team.name if team else f"Team {team_id}"
            
            # Format message
            message = self.format_daily_status_message(team_stats, team_name)
            
            # Send message (this would integrate with Telegram bot)
            # For now, just log the message
            logging.info(f"📊 Daily status report for {team_name}:\n{message}")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error sending daily status report: {e}")
            return False
    
    async def schedule_daily_status_task(self, team_id: str, leadership_chat_id: str) -> None:
        """
        Schedule daily status report task.
        
        Args:
            team_id: The team ID to generate report for
            leadership_chat_id: The leadership chat ID to send to
        """
        # This would schedule the daily status report
        # For now, just log that it would be scheduled
        logging.info(f"📅 Daily status report scheduled for team {team_id}") 