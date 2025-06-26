#!/usr/bin/env python3
"""
WhatsApp Tools for KICKAI
Provides tools for sending and receiving WhatsApp messages via Twilio API.
"""

import os
import logging
from typing import List, Dict, Optional, Any
from crewai.tools import BaseTool
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppTools:
    """Base class for WhatsApp tools with Twilio client initialization."""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.team_group = os.getenv('TEAM_WHATSAPP_GROUP')
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            raise ValueError("Missing required Twilio environment variables")
        
        self.client = Client(self.account_sid, self.auth_token)
        logger.info("WhatsApp tools initialized successfully")


class SendWhatsAppMessageTool(BaseTool):
    """Tool for sending WhatsApp messages to the team group."""
    
    name: str = "send_whatsapp_message"
    description: str = "Send a WhatsApp message to the team group"
    
    def __init__(self):
        super().__init__(name=self.name, description=self.description)
        self.whatsapp = WhatsAppTools()
    
    def _run(self, message: str) -> str:
        """
        Send a WhatsApp message to the team group.
        
        Args:
            message (str): The message to send
            
        Returns:
            str: Success or error message
        """
        try:
            if not self.whatsapp.team_group:
                return "Error: Team WhatsApp group not configured"
            
            # Send message to team group
            message_obj = self.whatsapp.client.messages.create(
                from_=self.whatsapp.phone_number,
                body=message,
                to=self.whatsapp.team_group
            )
            
            logger.info(f"Message sent successfully: {message_obj.sid}")
            return f"Message sent successfully! SID: {message_obj.sid}"
            
        except TwilioException as e:
            error_msg = f"Twilio error: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendWhatsAppPollTool(BaseTool):
    """Tool for sending WhatsApp polls to the team group."""
    
    name: str = "send_whatsapp_poll"
    description: str = "Send a WhatsApp poll to the team group"
    
    def __init__(self):
        super().__init__(name=self.name, description=self.description)
        self.whatsapp = WhatsAppTools()
    
    def _run(self, question: str, options: List[str]) -> str:
        """
        Send a WhatsApp poll to the team group.
        
        Args:
            question (str): The poll question
            options (List[str]): List of poll options
            
        Returns:
            str: Success or error message
        """
        try:
            if not self.whatsapp.team_group:
                return "Error: Team WhatsApp group not configured"
            
            if len(options) < 2:
                return "Error: Poll must have at least 2 options"
            
            # Format poll message
            poll_message = f"📊 {question}\n\n"
            for i, option in enumerate(options, 1):
                poll_message += f"{i}. {option}\n"
            poll_message += "\nReply with the number of your choice."
            
            # Send poll message
            message_obj = self.whatsapp.client.messages.create(
                from_=self.whatsapp.phone_number,
                body=poll_message,
                to=self.whatsapp.team_group
            )
            
            logger.info(f"Poll sent successfully: {message_obj.sid}")
            return f"Poll sent successfully! SID: {message_obj.sid}"
            
        except TwilioException as e:
            error_msg = f"Twilio error: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendAvailabilityPollTool(BaseTool):
    """Tool for sending availability polls for upcoming fixtures."""
    
    name: str = "send_availability_poll"
    description: str = "Send an availability poll for an upcoming fixture"
    
    def __init__(self):
        super().__init__(name=self.name, description=self.description)
        self.whatsapp = WhatsAppTools()
    
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
            if not self.whatsapp.team_group:
                return "Error: Team WhatsApp group not configured"
            
            # Format availability poll message
            poll_message = f"⚽ MATCH AVAILABILITY POLL\n\n"
            poll_message += f"Fixture: {fixture_details}\n"
            poll_message += f"Date: {match_date}\n"
            poll_message += f"Time: {match_time}\n"
            poll_message += f"Location: {location}\n\n"
            poll_message += "Are you available for this match?\n\n"
            poll_message += "1. ✅ Yes, I'm in!\n"
            poll_message += "2. ❌ No, can't make it\n"
            poll_message += "3. 🤔 Maybe, will confirm later\n\n"
            poll_message += "Reply with 1, 2, or 3."
            
            # Send availability poll
            message_obj = self.whatsapp.client.messages.create(
                from_=self.whatsapp.phone_number,
                body=poll_message,
                to=self.whatsapp.team_group
            )
            
            logger.info(f"Availability poll sent successfully: {message_obj.sid}")
            return f"Availability poll sent successfully! SID: {message_obj.sid}"
            
        except TwilioException as e:
            error_msg = f"Twilio error: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendSquadAnnouncementTool(BaseTool):
    """Tool for announcing the selected squad for a match."""
    
    name: str = "send_squad_announcement"
    description: str = "Announce the selected squad for an upcoming match"
    
    def __init__(self):
        super().__init__(name=self.name, description=self.description)
        self.whatsapp = WhatsAppTools()
    
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
            if not self.whatsapp.team_group:
                return "Error: Team WhatsApp group not configured"
            
            # Format squad announcement message
            announcement = f"🏆 SQUAD ANNOUNCEMENT\n\n"
            announcement += f"Fixture: {fixture_details}\n"
            announcement += f"Date: {match_date}\n"
            announcement += f"Time: {match_time}\n\n"
            
            announcement += "📋 STARTING XI:\n"
            for i, player in enumerate(starters, 1):
                announcement += f"{i}. {player}\n"
            
            announcement += "\n🔄 SUBSTITUTES:\n"
            for i, player in enumerate(substitutes, 1):
                announcement += f"{i}. {player}\n"
            
            announcement += "\n🎯 Good luck, team! Let's get the win! 💪"
            
            # Send squad announcement
            message_obj = self.whatsapp.client.messages.create(
                from_=self.whatsapp.phone_number,
                body=announcement,
                to=self.whatsapp.team_group
            )
            
            logger.info(f"Squad announcement sent successfully: {message_obj.sid}")
            return f"Squad announcement sent successfully! SID: {message_obj.sid}"
            
        except TwilioException as e:
            error_msg = f"Twilio error: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return error_msg


class SendPaymentReminderTool(BaseTool):
    """Tool for sending payment reminders to players."""
    
    name: str = "send_payment_reminder"
    description: str = "Send payment reminders to players who haven't paid match fees"
    
    def __init__(self):
        super().__init__(name=self.name, description=self.description)
        self.whatsapp = WhatsAppTools()
    
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
            if not self.whatsapp.team_group:
                return "Error: Team WhatsApp group not configured"
            
            # Format payment reminder message
            reminder = f"💰 PAYMENT REMINDER\n\n"
            reminder += f"Fixture: {fixture_details}\n"
            reminder += f"Amount: £{amount:.2f}\n\n"
            
            if len(unpaid_players) == 1:
                reminder += f"The following player still needs to pay:\n"
            else:
                reminder += f"The following players still need to pay:\n"
            
            for player in unpaid_players:
                reminder += f"• {player}\n"
            
            reminder += "\nPlease arrange payment as soon as possible. Thanks!"
            
            # Send payment reminder
            message_obj = self.whatsapp.client.messages.create(
                from_=self.whatsapp.phone_number,
                body=reminder,
                to=self.whatsapp.team_group
            )
            
            logger.info(f"Payment reminder sent successfully: {message_obj.sid}")
            return f"Payment reminder sent successfully! SID: {message_obj.sid}"
            
        except TwilioException as e:
            error_msg = f"Twilio error: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return error_msg


def get_whatsapp_tools() -> List[BaseTool]:
    """Get all WhatsApp tools for use with CrewAI agents."""
    return [
        SendWhatsAppMessageTool(),
        SendWhatsAppPollTool(),
        SendAvailabilityPollTool(),
        SendSquadAnnouncementTool(),
        SendPaymentReminderTool()
    ] 