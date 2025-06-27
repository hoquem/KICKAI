#!/usr/bin/env python3
"""
Telegram Tools for KICKAI
Provides tools for sending and receiving Telegram messages via Bot API.
"""

import os
import logging
import requests
from typing import List, Dict, Optional, Any
from crewai.tools import BaseTool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_telegram_bot_token() -> str:
    """Get Telegram bot token from environment."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN environment variable")
    return token


def get_telegram_chat_id() -> str:
    """Get Telegram chat/group ID from environment."""
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not chat_id:
        raise ValueError("Missing TELEGRAM_CHAT_ID environment variable")
    return chat_id


class SendTelegramMessageTool(BaseTool):
    """Tool for sending Telegram messages to the team group."""
    
    name: str = "send_telegram_message"
    description: str = "Send a Telegram message to the team group"
    
    def _run(self, message: str) -> str:
        """
        Send a Telegram message to the team group.
        
        Args:
            message (str): The message to send
            
        Returns:
            str: Success or error message
        """
        try:
            token = get_telegram_bot_token()
            chat_id = get_telegram_chat_id()
            
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
                logger.info(f"Telegram message sent successfully: {result['result']['message_id']}")
                return f"Telegram message sent successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending Telegram message: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendTelegramPollTool(BaseTool):
    """Tool for sending Telegram polls to the team group."""
    
    name: str = "send_telegram_poll"
    description: str = "Send a Telegram poll to the team group"
    
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
            token = get_telegram_bot_token()
            chat_id = get_telegram_chat_id()
            
            url = f"https://api.telegram.org/bot{token}/sendPoll"
            data = {
                'chat_id': chat_id,
                'question': question,
                'options': options,
                'is_anonymous': False,  # Show who voted for what
                'allows_multiple_answers': False
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Telegram poll sent successfully: {result['result']['message_id']}")
                return f"Telegram poll sent successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending Telegram poll: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendAvailabilityPollTool(BaseTool):
    """Tool for sending availability polls for upcoming fixtures."""
    
    name: str = "send_availability_poll"
    description: str = "Send an availability poll for an upcoming fixture"
    
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
            token = get_telegram_bot_token()
            chat_id = get_telegram_chat_id()
            
            # Create availability poll
            question = f"⚽ Availability: {fixture_details}"
            options = [
                "✅ Yes, I'm in!",
                "❌ No, can't make it", 
                "🤔 Maybe, will confirm later"
            ]
            
            url = f"https://api.telegram.org/bot{token}/sendPoll"
            data = {
                'chat_id': chat_id,
                'question': question,
                'options': options,
                'is_anonymous': False,
                'allows_multiple_answers': False
            }
            
            # Add match details as caption
            caption = f"📅 Date: {match_date}\n🕐 Time: {match_time}\n📍 Location: {location}\n\nPlease vote for your availability!"
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                # Send additional details as a separate message
                message_url = f"https://api.telegram.org/bot{token}/sendMessage"
                message_data = {
                    'chat_id': chat_id,
                    'text': caption,
                    'parse_mode': 'HTML'
                }
                requests.post(message_url, data=message_data)
                
                logger.info(f"Telegram availability poll sent successfully: {result['result']['message_id']}")
                return f"Telegram availability poll sent successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending Telegram availability poll: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendSquadAnnouncementTool(BaseTool):
    """Tool for announcing the selected squad for a match."""
    
    name: str = "send_squad_announcement"
    description: str = "Announce the selected squad for an upcoming match"
    
    def _run(self, fixture_details: str, match_date: str, match_time: str, 
             starters: List[str], substitutes: List[str]) -> str:
        """
        Announce the selected squad for an upcoming match.
        
        Args:
            fixture_details (str): Fixture information
            match_date (str): Match date
            match_time (str): Match time
            starters (List[str]): List of starting players
            substitutes (List[str]): List of substitute players
            
        Returns:
            str: Success or error message
        """
        try:
            token = get_telegram_bot_token()
            chat_id = get_telegram_chat_id()
            
            # Format squad announcement
            announcement = f"🏆 <b>SQUAD ANNOUNCEMENT</b>\n\n"
            announcement += f"Fixture: {fixture_details}\n"
            announcement += f"Date: {match_date}\n"
            announcement += f"Time: {match_time}\n\n"
            
            announcement += "📋 <b>STARTING XI:</b>\n"
            for i, player in enumerate(starters, 1):
                announcement += f"{i}. {player}\n"
            
            announcement += "\n🔄 <b>SUBSTITUTES:</b>\n"
            for i, player in enumerate(substitutes, 1):
                announcement += f"{i}. {player}\n"
            
            announcement += "\n🎯 Good luck, team! Let's get the win! 💪"
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': announcement,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Telegram squad announcement sent successfully: {result['result']['message_id']}")
                return f"Telegram squad announcement sent successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending Telegram squad announcement: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendPaymentReminderTool(BaseTool):
    """Tool for sending payment reminders to players."""
    
    name: str = "send_payment_reminder"
    description: str = "Send payment reminders to players who haven't paid match fees"
    
    def _run(self, unpaid_players: List[str], amount: float, fixture_details: str) -> str:
        """
        Send payment reminders to players who haven't paid match fees.
        
        Args:
            unpaid_players (List[str]): List of players who haven't paid
            amount (float): Amount to be paid
            fixture_details (str): Fixture information
            
        Returns:
            str: Success or error message
        """
        try:
            token = get_telegram_bot_token()
            chat_id = get_telegram_chat_id()
            
            # Format payment reminder
            reminder = f"💰 <b>PAYMENT REMINDER</b>\n\n"
            reminder += f"Fixture: {fixture_details}\n"
            reminder += f"Amount: £{amount:.2f}\n\n"
            
            if len(unpaid_players) == 1:
                reminder += f"The following player still needs to pay:\n"
            else:
                reminder += f"The following players still need to pay:\n"
            
            for player in unpaid_players:
                reminder += f"• {player}\n"
            
            reminder += "\nPlease arrange payment as soon as possible. Thanks!"
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': reminder,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Telegram payment reminder sent successfully: {result['result']['message_id']}")
                return f"Telegram payment reminder sent successfully! Message ID: {result['result']['message_id']}"
            else:
                return f"Telegram API error: {result.get('description', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error sending Telegram payment reminder: {str(e)}"
            logger.error(error_msg)
            return error_msg


def get_telegram_tools() -> List[BaseTool]:
    """Get all Telegram tools."""
    return [
        SendTelegramMessageTool(),
        SendTelegramPollTool(),
        SendAvailabilityPollTool(),
        SendSquadAnnouncementTool(),
        SendPaymentReminderTool()
    ] 