#!/usr/bin/env python3
"""
Telegram Tools for KICKAI
Provides tools for sending and receiving Telegram messages via Bot API.
Supports multi-team isolation with team_id parameter.
"""

import os
import logging
import requests
from typing import List, Dict, Optional, Any, Tuple
from crewai.tools import BaseTool
from supabase import create_client, Client
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """Get Supabase client with proper error handling."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("Missing Supabase environment variables")
    
    return create_client(url, key)


def get_team_bot_credentials(team_id: str) -> Tuple[str, str]:
    """Fetch the Telegram bot token and chat ID for a specific team from the database."""
    try:
        supabase = get_supabase_client()
        
        # Find the bot mapping for the specific team
        bot_resp = supabase.table('team_bots').select('bot_token, chat_id').eq('team_id', team_id).eq('is_active', True).execute()
        if not bot_resp.data:
            raise ValueError(f"No bot mapping found for team ID: {team_id}")
        
        return bot_resp.data[0]['bot_token'], bot_resp.data[0]['chat_id']
        
    except Exception as e:
        logger.error(f"Error getting bot credentials for team {team_id}: {e}")
        raise


def get_team_bot_credentials_dual(team_id: str, chat_type: str = 'main') -> Tuple[str, str]:
    """Fetch the Telegram bot token and chat ID for a specific team from the database.
    
    Args:
        team_id (str): The team ID
        chat_type (str): Either 'main' or 'leadership'
        
    Returns:
        Tuple[str, str]: (bot_token, chat_id)
    """
    try:
        supabase = get_supabase_client()
        
        # Find the bot mapping for the specific team
        if chat_type == 'main':
            bot_resp = supabase.table('team_bots').select('bot_token, chat_id').eq('team_id', team_id).eq('is_active', True).execute()
        elif chat_type == 'leadership':
            bot_resp = supabase.table('team_bots').select('bot_token, leadership_chat_id').eq('team_id', team_id).eq('is_active', True).execute()
            if bot_resp.data and bot_resp.data[0].get('leadership_chat_id'):
                return bot_resp.data[0]['bot_token'], bot_resp.data[0]['leadership_chat_id']
            else:
                raise ValueError(f"No leadership chat configured for team ID: {team_id}")
        else:
            raise ValueError(f"Invalid chat_type: {chat_type}. Must be 'main' or 'leadership'")
        
        if not bot_resp.data:
            raise ValueError(f"No bot mapping found for team ID: {team_id}")
        
        return bot_resp.data[0]['bot_token'], bot_resp.data[0]['chat_id']
        
    except Exception as e:
        logger.error(f"Error getting bot credentials for team {team_id} ({chat_type}): {e}")
        raise


def get_team_name_by_id(team_id: str) -> str:
    """Get the team name from the database by team ID."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('teams').select('name').eq('id', team_id).eq('is_active', True).execute()
        if response.data:
            return response.data[0]['name']
        else:
            raise ValueError(f"Team with ID {team_id} not found or inactive")
    except Exception as e:
        logger.warning(f"Could not get team name for ID {team_id}: {e}")
        return f"Team {team_id}"


def get_user_role_in_team(team_id: str, telegram_user_id: str) -> str:
    """Get the role of a user in a specific team."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('team_members').select('role').eq('team_id', team_id).eq('telegram_user_id', telegram_user_id).eq('is_active', True).execute()
        if response.data:
            return response.data[0]['role']
        else:
            return 'player'  # Default role
    except Exception as e:
        logger.warning(f"Could not get user role for {telegram_user_id} in team {team_id}: {e}")
        return 'player'  # Default role


def is_leadership_member(team_id: str, telegram_user_id: str) -> bool:
    """Check if a user is a leadership member (admin, secretary, manager, treasurer)."""
    role = get_user_role_in_team(team_id, telegram_user_id)
    return role in ['admin', 'secretary', 'manager', 'treasurer']


class SendTelegramMessageTool(BaseTool):
    """Tool for sending Telegram messages to a specific team's group."""
    
    name: str = "send_telegram_message"
    description: str = "Send a Telegram message to the team group"
    team_id: Optional[str] = None
    
    def __init__(self, team_id: str):
        super().__init__(name="send_telegram_message", description="Send a Telegram message to the team group")
        self.team_id = team_id
    
    def _run(self, message: str) -> str:
        """
        Send a Telegram message to the team group.
        
        Args:
            message (str): The message to send
            
        Returns:
            str: Success or error message
        """
        try:
            assert self.team_id is not None, "team_id must be set"
            token, chat_id = get_team_bot_credentials(self.team_id)
            team_name = get_team_name_by_id(self.team_id)
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'  # Support basic HTML formatting
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Telegram message sent to {team_name} successfully: {result['result']['message_id']}")
                return f"Telegram message sent to {team_name} successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending Telegram message to team {self.team_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendTelegramPollTool(BaseTool):
    """Tool for sending Telegram polls to a specific team's group."""
    
    name: str = "send_telegram_poll"
    description: str = "Send a Telegram poll to the team group"
    team_id: Optional[str] = None
    
    def __init__(self, team_id: str):
        super().__init__(name="send_telegram_poll", description="Send a Telegram poll to the team group")
        self.team_id = team_id
    
    def _run(self, question: str, options: List[str]) -> str:
        """
        Send a Telegram poll to the team group.
        
        Args:
            question (str): The poll question
            options (List[str]): List of poll options
            
        Returns:
            str: Success or error message
        """
        try:
            assert self.team_id is not None, "team_id must be set"
            token, chat_id = get_team_bot_credentials(self.team_id)
            team_name = get_team_name_by_id(self.team_id)
            
            url = f"https://api.telegram.org/bot{token}/sendPoll"
            data = {
                'chat_id': chat_id,
                'question': question,
                'options': json.dumps(options),
                'is_anonymous': False,  # Show who voted for what
                'allows_multiple_answers': False
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Telegram poll sent to {team_name} successfully: {result['result']['message_id']}")
                return f"Telegram poll sent to {team_name} successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending Telegram poll to team {self.team_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendAvailabilityPollTool(BaseTool):
    """Tool for sending availability polls for upcoming fixtures to a specific team."""
    
    name: str = "send_availability_poll"
    description: str = "Send an availability poll for an upcoming fixture"
    team_id: Optional[str] = None
    
    def __init__(self, team_id: str):
        super().__init__(name="send_availability_poll", description="Send an availability poll for an upcoming fixture")
        self.team_id = team_id
    
    def _run(self, fixture_details: str, match_date: str, match_time: str, location: str) -> str:
        """
        Send an availability poll for an upcoming fixture.
        
        Args:
            fixture_details (str): Fixture information (opponent, etc.)
            match_date (str): Match date
            match_time (str): Match time
            location (str): Match location
            
        Returns:
            str: Success or error message
        """
        try:
            assert self.team_id is not None, "team_id must be set"
            token, chat_id = get_team_bot_credentials(self.team_id)
            team_name = get_team_name_by_id(self.team_id)
            
            # Create availability poll
            question = f"⚽ {team_name} - Availability: {fixture_details}"
            options = [
                "✅ Yes, I'm in!",
                "❌ No, can't make it", 
                "🤔 Maybe, will confirm later"
            ]
            
            url = f"https://api.telegram.org/bot{token}/sendPoll"
            data = {
                'chat_id': chat_id,
                'question': question,
                'options': json.dumps(options),
                'is_anonymous': False,
                'allows_multiple_answers': False
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Availability poll sent to {team_name} successfully: {result['result']['message_id']}")
                return f"Availability poll sent to {team_name} successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending availability poll to team {self.team_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendSquadAnnouncementTool(BaseTool):
    """Tool for announcing the selected squad for a match to a specific team."""
    
    name: str = "send_squad_announcement"
    description: str = "Announce the selected squad for an upcoming match"
    team_id: Optional[str] = None
    
    def __init__(self, team_id: str):
        super().__init__(name="send_squad_announcement", description="Announce the selected squad for an upcoming match")
        self.team_id = team_id
    
    def _run(self, fixture_details: str, match_date: str, match_time: str, 
             starters: List[str], substitutes: List[str]) -> str:
        """
        Send a squad announcement to the team group.
        
        Args:
            fixture_details (str): Fixture information (opponent, etc.)
            match_date (str): Match date
            match_time (str): Match time
            starters (List[str]): List of starting XI players
            substitutes (List[str]): List of substitute players
            
        Returns:
            str: Success or error message
        """
        try:
            assert self.team_id is not None, "team_id must be set"
            token, chat_id = get_team_bot_credentials(self.team_id)
            team_name = get_team_name_by_id(self.team_id)
            
            # Create squad announcement message
            message = f"""🏆 <b>{team_name} - Squad Announcement</b>

📅 <b>Fixture:</b> {fixture_details}
📅 <b>Date:</b> {match_date}
⏰ <b>Time:</b> {match_time}

<b>Starting XI:</b>
"""
            
            for i, player in enumerate(starters, 1):
                message += f"{i}. {player}\n"
            
            message += f"\n<b>Substitutes:</b>\n"
            for i, player in enumerate(substitutes, 1):
                message += f"{i}. {player}\n"
            
            message += f"\nGood luck, {team_name}! 💪"
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Squad announcement sent to {team_name} successfully: {result['result']['message_id']}")
                return f"Squad announcement sent to {team_name} successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending squad announcement to team {self.team_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendPaymentReminderTool(BaseTool):
    """Tool for sending payment reminders to players of a specific team."""
    
    name: str = "send_payment_reminder"
    description: str = "Send payment reminders to players who haven't paid match fees"
    team_id: Optional[str] = None
    
    def __init__(self, team_id: str):
        super().__init__(name="send_payment_reminder", description="Send payment reminders to players who haven't paid match fees")
        self.team_id = team_id
    
    def _run(self, unpaid_players: List[str], amount: float, fixture_details: str) -> str:
        """
        Send payment reminders to players who haven't paid.
        
        Args:
            unpaid_players (List[str]): List of players who haven't paid
            amount (float): Amount owed per player
            fixture_details (str): Fixture information
            
        Returns:
            str: Success or error message
        """
        try:
            assert self.team_id is not None, "team_id must be set"
            token, chat_id = get_team_bot_credentials(self.team_id)
            team_name = get_team_name_by_id(self.team_id)
            
            # Create payment reminder message
            message = f"""💰 <b>{team_name} - Payment Reminder</b>

📅 <b>Fixture:</b> {fixture_details}
💷 <b>Amount Due:</b> £{amount:.2f} per player

<b>Players who still need to pay:</b>
"""
            
            for player in unpaid_players:
                message += f"• {player}\n"
            
            message += f"\nPlease pay your match fees as soon as possible. Contact the team admin for payment details."
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Payment reminder sent to {team_name} successfully: {result['result']['message_id']}")
                return f"Payment reminder sent to {team_name} successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending payment reminder to team {self.team_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg


def get_telegram_tools(team_id: str) -> List[BaseTool]:
    """Get all Telegram tools configured for a specific team."""
    return [
        SendTelegramMessageTool(team_id),
        SendTelegramPollTool(team_id),
        SendAvailabilityPollTool(team_id),
        SendSquadAnnouncementTool(team_id),
        SendPaymentReminderTool(team_id)
    ]


class SendLeadershipMessageTool(BaseTool):
    """Tool for sending Telegram messages to a team's leadership group."""
    
    name: str = "send_leadership_message"
    description: str = "Send a Telegram message to the team's leadership group"
    team_id: Optional[str] = None
    
    def __init__(self, team_id: str):
        super().__init__(name="send_leadership_message", description="Send a Telegram message to the team's leadership group")
        self.team_id = team_id
    
    def _run(self, message: str) -> str:
        """
        Send a Telegram message to the team's leadership group.
        
        Args:
            message (str): The message to send
            
        Returns:
            str: Success or error message
        """
        try:
            assert self.team_id is not None, "team_id must be set"
            token, chat_id = get_team_bot_credentials_dual(self.team_id, 'leadership')
            team_name = get_team_name_by_id(self.team_id)
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'  # Support basic HTML formatting
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Leadership message sent to {team_name} successfully: {result['result']['message_id']}")
                return f"Leadership message sent to {team_name} successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending leadership message to team {self.team_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg


def get_telegram_tools_dual(team_id: str) -> List[BaseTool]:
    """Get all Telegram tools configured for a specific team with dual-channel support."""
    return [
        SendTelegramMessageTool(team_id),
        SendLeadershipMessageTool(team_id),
        SendTelegramPollTool(team_id),
        SendAvailabilityPollTool(team_id),
        SendSquadAnnouncementTool(team_id),
        SendPaymentReminderTool(team_id)
    ] 