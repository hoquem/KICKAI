#!/usr/bin/env python3
"""
Telegram Tools for KICKAI

This module provides utilities for Telegram bot operations including
credential management, message formatting, and user role checking.
"""

import os
import logging
import requests
from typing import List, Dict, Optional, Any, Tuple
from langchain.tools import BaseTool
import json
from datetime import datetime
import re

from ..core.bot_config_manager import get_bot_config_manager, ChatType
from ..database.firebase_client import get_firebase_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_team_bot_credentials(team_id: str) -> Tuple[str, str]:
    """Fetch the Telegram bot token and main chat ID for a specific team.
    
    This function uses the new bot configuration manager which supports
    both local files (testing/staging) and Firestore (production).
    
    Args:
        team_id (str): The team ID
        
    Returns:
        Tuple[str, str]: (bot_token, main_chat_id)
        
    Raises:
        ValueError: If no bot mapping is found for the team
    """
    try:
        manager = get_bot_config_manager()
        bot_config = manager.get_bot_config(team_id)
        
        if not bot_config:
            raise ValueError(f"No bot found for team ID: {team_id}")
        
        return bot_config.token, bot_config.main_chat_id
        
    except Exception as e:
        logger.error(f"Error getting bot credentials for team {team_id}: {e}")
        raise


def get_team_bot_credentials_dual(team_id: str, chat_type: str = 'main') -> Tuple[str, str]:
    """Fetch the Telegram bot token and chat ID for a specific team from the database.
    
    This function uses the new bot configuration manager which supports
    both local files (testing/staging) and Firestore (production).
    
    Args:
        team_id (str): The team ID
        chat_type (str): Either 'main' or 'leadership'
        
    Returns:
        Tuple[str, str]: (bot_token, chat_id)
        
    Raises:
        ValueError: If no bot mapping is found for the team or invalid chat type
    """
    try:
        manager = get_bot_config_manager()
        bot_config = manager.get_bot_config(team_id)
        
        if not bot_config:
            raise ValueError(f"No bot found for team ID: {team_id}")
        
        if chat_type == 'main':
            return bot_config.token, bot_config.main_chat_id
        elif chat_type == 'leadership':
            return bot_config.token, bot_config.leadership_chat_id
        else:
            raise ValueError(f"Invalid chat_type: {chat_type}. Must be 'main' or 'leadership'")
        
    except Exception as e:
        logger.error(f"Error getting bot credentials for team {team_id} ({chat_type}): {e}")
        raise


def get_team_bot_username(team_id: str, chat_type: str = 'main') -> str:
    """Get the bot username for a team.
    
    Args:
        team_id (str): The team ID
        chat_type (str): Either 'main' or 'leadership' (not used in single bot design)
        
    Returns:
        str: Bot username
        
    Raises:
        ValueError: If no bot is found for the team
    """
    try:
        manager = get_bot_config_manager()
        bot_config = manager.get_bot_config(team_id)
        
        if not bot_config:
            raise ValueError(f"No bot found for team ID: {team_id}")
        
        return bot_config.username
        
    except Exception as e:
        logger.error(f"Error getting bot username for team {team_id}: {e}")
        raise


def get_all_team_bots(team_id: str) -> Dict[str, Dict[str, str]]:
    """Get all bot configurations for a team.
    
    Args:
        team_id (str): The team ID
        
    Returns:
        Dict[str, Dict[str, str]]: Dictionary with bot configurations
        Format: {
            'main': {'token': '...', 'chat_id': '...', 'username': '...'},
            'leadership': {'token': '...', 'chat_id': '...', 'username': '...'}
        }
    """
    try:
        manager = get_bot_config_manager()
        bot_config = manager.get_bot_config(team_id)
        
        if not bot_config:
            return {}
        
        return {
            'main': {
                'token': bot_config.token,
                'chat_id': bot_config.main_chat_id,
                'username': bot_config.username
            },
            'leadership': {
                'token': bot_config.token,
                'chat_id': bot_config.leadership_chat_id,
                'username': bot_config.username
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting all bots for team {team_id}: {e}")
        return {}


def get_user_role_in_team(team_id: str, user_id: str) -> str:
    """Get the role of a user in a specific team.
    
    Args:
        team_id (str): The team ID
        user_id (str): The user ID
        
    Returns:
        str: User role ('admin', 'member', 'guest', etc.) or 'unknown' if not found
    """
    try:
        db = get_firebase_client()
        
        # Query team members collection
        members_ref = db.collection('team_members')
        query = members_ref.where('team_id', '==', team_id).where('user_id', '==', user_id).where('is_active', '==', True)
        docs = list(query.stream())
        
        if docs:
            member_data = docs[0].to_dict()
            return member_data.get('role', 'member')
        else:
            return 'unknown'
            
    except Exception as e:
        logger.error(f"Error getting user role for user {user_id} in team {team_id}: {e}")
        return 'unknown'


def is_user_admin(team_id: str, user_id: str) -> bool:
    """Check if a user is an admin in a specific team.
    
    Args:
        team_id (str): The team ID
        user_id (str): The user ID
        
    Returns:
        bool: True if user is admin, False otherwise
    """
    role = get_user_role_in_team(team_id, user_id)
    return role in ['admin', 'owner', 'manager']


def is_user_member(team_id: str, user_id: str) -> bool:
    """Check if a user is a member in a specific team.
    
    Args:
        team_id (str): The team ID
        user_id (str): The user ID
        
    Returns:
        bool: True if user is a member, False otherwise
    """
    role = get_user_role_in_team(team_id, user_id)
    return role in ['admin', 'owner', 'manager', 'member']


def format_message_for_telegram(message: str) -> str:
    """Format a message for Telegram with proper HTML escaping (only supported tags)."""
    # Define supported HTML tags
    supported_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 
                     'span', 'tg-spoiler', 'a', 'code', 'pre']
    
    # Create a pattern to match supported HTML tags
    tag_pattern = r'</?(?:' + '|'.join(supported_tags) + r')(?:\s+[^>]*)?>'
    
    # Find all HTML tags in the message
    tags = re.findall(tag_pattern, message, re.IGNORECASE)
    
    # Temporarily replace HTML tags with placeholders
    tag_placeholders = {}
    for i, tag in enumerate(tags):
        placeholder = f"__HTML_TAG_{i}__"
        tag_placeholders[placeholder] = tag
        message = message.replace(tag, placeholder, 1)
    
    # Escape remaining angle brackets (not part of HTML tags)
    message = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Restore HTML tags
    for placeholder, tag in tag_placeholders.items():
        message = message.replace(placeholder, tag)
    
    return message


def get_team_info(team_id: str) -> Optional[Dict[str, Any]]:
    """Get team information including bot configurations.
    
    Args:
        team_id (str): The team ID
        
    Returns:
        Optional[Dict[str, Any]]: Team information or None if not found
    """
    try:
        manager = get_bot_config_manager()
        team_config = manager.get_team_config(team_id)
        
        if not team_config:
            return None
        
        # Get team info from Firebase
        db = get_firebase_client()
        team_ref = db.collection('teams').document(team_id)
        team_doc = team_ref.get()
        
        team_info = {
            'id': team_id,
            'name': team_config.name,
            'description': team_config.description,
            'settings': team_config.settings,
            'bots': {}
        }
        
        if team_doc.exists:
            firebase_data = team_doc.to_dict()
            team_info.update(firebase_data)
        
        # Add bot information
        for bot_type, bot_config in team_config.bots.items():
            team_info['bots'][bot_type.value] = {
                'username': bot_config.username,
                'chat_id': bot_config.chat_id,
                'is_active': bot_config.is_active
            }
        
        return team_info
        
    except Exception as e:
        logger.error(f"Error getting team info for team {team_id}: {e}")
        return None


def validate_bot_configuration(team_id: str) -> Dict[str, Any]:
    """Validate bot configuration for a team.
    
    Args:
        team_id (str): The team ID
        
    Returns:
        Dict[str, Any]: Validation results
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'bots': {}
    }
    
    try:
        manager = get_bot_config_manager()
        team_config = manager.get_team_config(team_id)
        
        if not team_config:
            results['valid'] = False
            results['errors'].append(f"Team '{team_id}' not found")
            return results
        
        # Check each bot
        for bot_type, bot_config in team_config.bots.items():
            bot_results = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check token
            if not bot_config.token:
                bot_results['valid'] = False
                bot_results['errors'].append("Bot token is missing")
            elif len(bot_config.token) < 10:
                bot_results['warnings'].append("Bot token seems too short")
            
            # Check username
            if not bot_config.username:
                bot_results['valid'] = False
                bot_results['errors'].append("Bot username is missing")
            
            # Check chat ID
            if not bot_config.chat_id:
                bot_results['valid'] = False
                bot_results['errors'].append("Chat ID is missing")
            elif not bot_config.chat_id.startswith('-'):
                bot_results['warnings'].append("Chat ID should start with '-' for groups")
            
            # Check if bot is active
            if not bot_config.is_active:
                bot_results['warnings'].append("Bot is marked as inactive")
            
            results['bots'][bot_type.value] = bot_results
            
            # Update overall validity
            if not bot_results['valid']:
                results['valid'] = False
                results['errors'].extend([f"{bot_type.value} bot: {error}" for error in bot_results['errors']])
            
            results['warnings'].extend([f"{bot_type.value} bot: {warning}" for warning in bot_results['warnings']])
        
        # Check if team has any bots
        if not team_config.bots:
            results['valid'] = False
            results['errors'].append("No bots configured for team")
        
    except Exception as e:
        results['valid'] = False
        results['errors'].append(f"Validation error: {str(e)}")
    
    return results


def get_team_name_by_id(team_id: str) -> str:
    """Get the team name from the database by team ID."""
    try:
        db = get_firebase_client()
        doc = db.collection('teams').document(team_id).get()
        if doc.exists:
            data = doc.to_dict()
            return data.get('name', f"Team {team_id}")
        else:
            raise ValueError(f"Team with ID {team_id} not found")
    except Exception as e:
        logger.warning(f"Could not get team name for ID {team_id}: {e}")
        return f"Team {team_id}"


def get_user_role_in_team(team_id: str, telegram_user_id: str) -> str:
    """Get the role of a user in a specific team."""
    try:
        db = get_firebase_client()
        members_ref = db.collection('team_members')
        query = members_ref.where('team_id', '==', team_id).where('telegram_user_id', '==', telegram_user_id).where('is_active', '==', True)
        docs = query.stream()
        docs_list = list(docs)
        
        if docs_list:
            data = docs_list[0].to_dict()
            return data.get('role', 'player')
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
                'parse_mode': 'HTML'
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
            fixture_details (str): Details about the fixture (e.g., "vs Thunder FC")
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
            
            # Create availability poll message
            poll_question = f"Availability for {fixture_details}"
            poll_options = [
                "✅ Available",
                "❌ Not Available",
                "🤔 Maybe (will confirm later)"
            ]
            
            # Add match details to the poll
            match_info = f"📅 {match_date} at {match_time}\n📍 {location}"
            
            url = f"https://api.telegram.org/bot{token}/sendPoll"
            data = {
                'chat_id': chat_id,
                'question': poll_question,
                'options': json.dumps(poll_options),
                'is_anonymous': False,
                'allows_multiple_answers': False,
                'explanation': match_info
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
        Announce the selected squad for an upcoming match.
        
        Args:
            fixture_details (str): Details about the fixture (e.g., "vs Thunder FC")
            match_date (str): Match date
            match_time (str): Match time
            starters (List[str]): List of starting players
            substitutes (List[str]): List of substitute players
            
        Returns:
            str: Success or error message
        """
        try:
            assert self.team_id is not None, "team_id must be set"
            token, chat_id = get_team_bot_credentials(self.team_id)
            team_name = get_team_name_by_id(self.team_id)
            
            # Create squad announcement message
            message = f"⚽ **SQUAD ANNOUNCEMENT** ⚽\n\n"
            message += f"**Match:** {fixture_details}\n"
            message += f"**Date:** {match_date}\n"
            message += f"**Time:** {match_time}\n\n"
            
            message += "🟢 **STARTING XI:**\n"
            for i, player in enumerate(starters, 1):
                message += f"{i}. {player}\n"
            
            if substitutes:
                message += "\n🟡 **SUBSTITUTES:**\n"
                for i, player in enumerate(substitutes, 1):
                    message += f"{i}. {player}\n"
            
            message += "\n💪 Let's get the win! 💪"
            
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
        Send payment reminders to players who haven't paid match fees.
        
        Args:
            unpaid_players (List[str]): List of players who haven't paid
            amount (float): Amount owed per player
            fixture_details (str): Details about the fixture
            
        Returns:
            str: Success or error message
        """
        try:
            assert self.team_id is not None, "team_id must be set"
            token, chat_id = get_team_bot_credentials(self.team_id)
            team_name = get_team_name_by_id(self.team_id)
            
            # Create payment reminder message
            message = f"💰 **PAYMENT REMINDER** 💰\n\n"
            message += f"**Match:** {fixture_details}\n"
            message += f"**Amount Due:** £{amount:.2f}\n\n"
            
            message += "The following players still need to pay:\n"
            for i, player in enumerate(unpaid_players, 1):
                message += f"{i}. {player}\n"
            
            message += f"\nPlease pay £{amount:.2f} to the team treasurer before the match.\n"
            message += "Thank you! 🙏"
            
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
    """Get all Telegram tools for a specific team."""
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
                'parse_mode': 'HTML'
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
    """Get all Telegram tools for a specific team including leadership messaging."""
    return [
        SendTelegramMessageTool(team_id),
        SendTelegramPollTool(team_id),
        SendAvailabilityPollTool(team_id),
        SendSquadAnnouncementTool(team_id),
        SendPaymentReminderTool(team_id),
        SendLeadershipMessageTool(team_id)
    ] 