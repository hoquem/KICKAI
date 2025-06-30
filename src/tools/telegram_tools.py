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
from langchain.tools import BaseTool
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_firebase_client():
    """Get Firebase client with proper error handling."""
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Check if Firebase app is already initialized
        try:
            app = firebase_admin.get_app()
            logger.info("✅ Using existing Firebase app")
        except ValueError:
            # Initialize Firebase app
            logger.info("🔧 Initializing Firebase app...")
            
            # Check for service account key file
            service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
            if service_account_path and os.path.exists(service_account_path):
                # Use service account file
                cred = credentials.Certificate(service_account_path)
                app = firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase app initialized with service account file")
            else:
                # Use environment variables for Railway deployment
                service_account_info = {
                    "type": "service_account",
                    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
                }
                
                # Validate required fields
                required_fields = ['project_id', 'private_key', 'client_email']
                missing_fields = [field for field in required_fields if not service_account_info.get(field)]
                if missing_fields:
                    raise ValueError(f"Missing Firebase environment variables: {missing_fields}")
                
                cred = credentials.Certificate(service_account_info)
                app = firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase app initialized with environment variables")
        
        # Get Firestore client
        db = firestore.client()
        logger.info("✅ Firebase Firestore client created successfully")
        return db
        
    except ImportError as e:
        logger.error(f"Firebase client not available: {e}")
        raise ImportError("Firebase client not available. Install with: pip install firebase-admin")
    except Exception as e:
        logger.error(f"Error in get_firebase_client: {e}")
        raise e


def get_team_bot_credentials(team_id: str) -> Tuple[str, str]:
    """Fetch the Telegram bot token and chat ID for a specific team from the database."""
    try:
        db = get_firebase_client()
        
        # Find the bot mapping for the specific team
        bots_ref = db.collection('team_bots')
        query = bots_ref.where('team_id', '==', team_id).where('is_active', '==', True)
        docs = query.stream()
        docs_list = list(docs)
        
        if not docs_list:
            raise ValueError(f"No bot mapping found for team ID: {team_id}")
        
        bot_data = docs_list[0].to_dict()
        return bot_data['bot_token'], bot_data['chat_id']
        
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
        db = get_firebase_client()
        
        # Find the bot mapping for the specific team
        bots_ref = db.collection('team_bots')
        query = bots_ref.where('team_id', '==', team_id).where('is_active', '==', True)
        docs = query.stream()
        docs_list = list(docs)
        
        if not docs_list:
            raise ValueError(f"No bot mapping found for team ID: {team_id}")
        
        bot_data = docs_list[0].to_dict()
        
        if chat_type == 'main':
            return bot_data['bot_token'], bot_data['chat_id']
        elif chat_type == 'leadership':
            if bot_data.get('leadership_chat_id'):
                return bot_data['bot_token'], bot_data['leadership_chat_id']
            else:
                raise ValueError(f"No leadership chat configured for team ID: {team_id}")
        else:
            raise ValueError(f"Invalid chat_type: {chat_type}. Must be 'main' or 'leadership'")
        
    except Exception as e:
        logger.error(f"Error getting bot credentials for team {team_id} ({chat_type}): {e}")
        raise


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
                'parse_mode': 'Markdown'  # Support markdown formatting
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
                'parse_mode': 'Markdown'
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
                'parse_mode': 'Markdown'
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
                'parse_mode': 'Markdown'  # Support markdown formatting
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