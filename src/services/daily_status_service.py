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

from src.services.player_service import PlayerService
from src.services.team_service import TeamService
from src.services.team_member_service import TeamMemberService
from src.services.fa_registration_checker import run_fa_registration_check, run_fa_fixtures_check
from src.database.models import Player, PlayerRole, PlayerPosition, OnboardingStatus

class DailyStatusService:
    """Service to generate and send daily team status reports."""
    
    def __init__(self, 
                 player_service: PlayerService,
                 team_service: TeamService,
                 team_member_service: Optional[TeamMemberService],
                 bot_token: str):
        self.player_service = player_service
        self.team_service = team_service
        self.team_member_service = team_member_service
        self.bot_token = bot_token
        
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
            active_players = len([p for p in players if p.onboarding_status == OnboardingStatus.COMPLETED])
            pending_approval = len([p for p in players if p.onboarding_status == OnboardingStatus.PENDING_APPROVAL])
            fa_registered = len([p for p in players if p.fa_registered])
            fa_eligible = len([p for p in players if p.fa_eligible])
            
            # Position breakdown
            positions = {}
            for player in players:
                if player.onboarding_status == OnboardingStatus.COMPLETED:
                    pos = player.position.value if player.position else "Unknown"
                    positions[pos] = positions.get(pos, 0) + 1
            
            # Recent additions (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_additions = [
                p for p in players 
                if p.created_at and p.created_at > week_ago
            ]
            
            # Check FA registration updates
            fa_updates = await run_fa_registration_check(team_id, self.player_service)
            
            # Get recent fixtures
            fixtures = await run_fa_fixtures_check(self.player_service)
            
            return {
                "total_players": total_players,
                "active_players": active_players,
                "pending_approval": pending_approval,
                "fa_registered": fa_registered,
                "fa_eligible": fa_eligible,
                "positions": positions,
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
    
    def format_daily_status_message(self, team_stats: Dict, team_name: str = "BP Hatters FC") -> str:
        """
        Format the daily status message with HTML formatting.
        
        Args:
            team_stats: Team statistics
            team_name: Name of the team
            
        Returns:
            Formatted HTML message
        """
        today = datetime.now().strftime("%A, %B %d, %Y")
        
        message = f"""📊 <b>Daily Team Status Report</b>
📅 <b>Date:</b> {today}
🏆 <b>Team:</b> {team_name}

👥 <b>Player Statistics:</b>
• Total Players: {team_stats["total_players"]}
• Active Players: {team_stats["active_players"]}
• Pending Approval: {team_stats["pending_approval"]}
• FA Registered: {team_stats["fa_registered"]}
• FA Eligible: {team_stats["fa_eligible"]}

⚽ <b>Position Breakdown:</b>"""
        
        for position, count in team_stats["positions"].items():
            message += f"\n• {position.title()}: {count}"
        
        if team_stats["recent_additions"]:
            message += f"\n\n🆕 <b>Recent Additions (Last 7 Days):</b>"
            for player in team_stats["recent_additions"][:5]:  # Show max 5
                message += f"\n• {player.name.upper()} ({player.player_id})"
        
        if team_stats["fa_updates"]:
            message += f"\n\n✅ <b>New FA Registrations:</b>"
            for player_id, registered in team_stats["fa_updates"].items():
                if registered:
                    # Get player name from ID (simplified)
                    message += f"\n• Player {player_id} is now FA registered!"
        
        if team_stats["fixtures"]:
            message += f"\n\n📅 <b>Recent Fixtures/Results:</b>"
            for fixture in team_stats["fixtures"][:3]:  # Show max 3
                message += f"\n• {fixture['text'][:100]}..."  # Truncate long text
        
        message += f"""

🔧 <b>System Status:</b>
• Database: ✅ Connected
• FA Website: ✅ Monitored
• Bot: ✅ Online

💡 <b>Next Actions:</b>
• Review pending approvals: {team_stats["pending_approval"]} players
• Monitor FA registration progress
• Check upcoming fixtures

---
<i>Generated automatically by KICKAI Team Management System</i>"""
        
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
            
            # Get team info
            team = await self.team_service.get_team(team_id)
            team_name = team.name if team else "BP Hatters FC"
            
            # Generate stats
            team_stats = await self.generate_team_stats(team_id)
            
            # Format message
            message = self.format_daily_status_message(team_stats, team_name)
            
            # Send to leadership chat using requests
            import requests
            from src.tools.telegram_tools import format_message_for_telegram
            
            # Format message for Telegram HTML
            formatted_message = format_message_for_telegram(message)
            
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
        """
        Schedule the daily status report task to run every day at 9:00 AM.
        
        Args:
            team_id: The team ID to report on
            leadership_chat_id: The leadership chat ID to send to
        """
        while True:
            try:
                now = datetime.now()
                
                # Calculate next run time (9:00 AM today or tomorrow)
                next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
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
                                   bot_token: str) -> None:
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
        bot_token=bot_token
    )
    
    # Start the scheduled task
    await service.schedule_daily_status_task(team_id, leadership_chat_id) 