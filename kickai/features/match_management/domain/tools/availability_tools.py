#!/usr/bin/env python3
"""
Availability Management Tools

This module provides tools for managing player availability for matches.
"""

import asyncio
import logging

from crewai.tools import tool

from kickai.core.dependency_container import get_container
from kickai.features.match_management.domain.entities.availability import AvailabilityStatus
from kickai.features.match_management.domain.services.availability_service import (
    AvailabilityService,
)
from kickai.utils.json_helper import json_error, json_response

logger = logging.getLogger(__name__)

@tool("mark_availability")
def mark_availability(
    match_id: str,
    player_id: str,
    status: str,  # available, unavailable, maybe
    reason: str | None = None,
) -> str:
    """
    Mark player availability for a match.


        match_id: Match ID to mark availability for
        player_id: Player ID marking availability
        status: Availability status (available, unavailable, maybe)
        reason: Optional reason for availability status


    :return: JSON response with availability status and team summary
    :rtype: str  # TODO: Fix type
    """
    try:
        container = get_container()
        availability_service: AvailabilityService = container.get_service(AvailabilityService)

        # Convert status string to enum
        try:
            availability_status = AvailabilityStatus(status.lower())
        except ValueError:
            return json_error(f"Invalid status: {status}. Valid options: available, unavailable, maybe", "Validation failed")

        # Mark availability
        availability = asyncio.run(
            availability_service.mark_availability(
                match_id=match_id,
                player_id=player_id,
                status=availability_status,
                reason=reason,
            )
        )

        # Get availability summary for the match
        summary = asyncio.run(availability_service.get_availability_summary(match_id))

        data = {
            'match_id': match_id,
            'player_id': player_id,
            'status': availability_status.value,
            'status_emoji': availability.status_emoji,
            'reason': reason,
            'team_summary': {
                'available': summary['available'],
                'unavailable': summary['unavailable'],
                'maybe': summary['maybe'],
                'pending': summary['pending']
            }
        }

        ui_format = "✅ **Availability Updated**\n\n"
        ui_format += f"**Match**: {match_id}\n"
        ui_format += f"**Your Status**: {availability.status_emoji} {availability_status.value.title()}\n"

        if reason:
            ui_format += f"**Reason**: {reason}\n"

        ui_format += "\n📊 **Team Availability**\n"
        ui_format += f"• Available: {summary['available']} players\n"
        ui_format += f"• Unavailable: {summary['unavailable']} players\n"
        ui_format += f"• Maybe: {summary['maybe']} players\n"
        ui_format += f"• Pending: {summary['pending']} players\n\n"
        ui_format += "💡 **Tip**: You can update your availability anytime before squad selection"

        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"Failed to mark availability: {e}")
        return json_error(f"Error marking availability: {e!s}", "Operation failed")

@tool("get_availability")
def get_availability(match_id: str) -> str:
    """
    Get availability information for a match.


        match_id: Match ID to get availability for


    :return: JSON response with availability information and player lists
    :rtype: str  # TODO: Fix type
    """
    try:
        container = get_container()
        availability_service: AvailabilityService = container.get_service(AvailabilityService)

        # Get availability summary
        summary = asyncio.run(availability_service.get_availability_summary(match_id))

        # Get availability records by status
        available_players = asyncio.run(availability_service.get_available_players(match_id))
        unavailable_players = asyncio.run(availability_service.get_unavailable_players(match_id))
        maybe_players = asyncio.run(availability_service.get_maybe_players(match_id))
        pending_players = asyncio.run(availability_service.get_pending_players(match_id))

        data = {
            'match_id': match_id,
            'summary': {
                'total_players': summary['total_players'],
                'available': summary['available'],
                'unavailable': summary['unavailable'],
                'maybe': summary['maybe'],
                'pending': summary['pending']
            },
            'players': {
                'available': [{'player_id': a.player_id} for a in available_players],
                'unavailable': [{'player_id': a.player_id, 'reason': a.reason} for a in unavailable_players],
                'maybe': [{'player_id': a.player_id, 'reason': a.reason} for a in maybe_players],
                'pending': [{'player_id': a.player_id} for a in pending_players]
            }
        }

        ui_format = f"📊 **Match Availability: {match_id}**\n\n"
        ui_format += f"**Total Players**: {summary['total_players']}\n\n"

        # Available players
        if available_players:
            ui_format += f"✅ **Available** ({len(available_players)}):\n"
            for availability in available_players:
                ui_format += f"• {availability.player_id}\n"
            ui_format += "\n"

        # Unavailable players
        if unavailable_players:
            ui_format += f"❌ **Unavailable** ({len(unavailable_players)}):\n"
            for availability in unavailable_players:
                ui_format += f"• {availability.player_id}\n"
                if availability.reason:
                    ui_format += f"  - Reason: {availability.reason}\n"
            ui_format += "\n"

        # Maybe players
        if maybe_players:
            ui_format += f"❓ **Maybe** ({len(maybe_players)}):\n"
            for availability in maybe_players:
                ui_format += f"• {availability.player_id}\n"
                if availability.reason:
                    ui_format += f"  - Reason: {availability.reason}\n"
            ui_format += "\n"

        # Pending players
        if pending_players:
            ui_format += f"⏳ **Pending** ({len(pending_players)}):\n"
            for availability in pending_players:
                ui_format += f"• {availability.player_id}\n"
            ui_format += "\n"

        ui_format += "📋 **Actions**\n"
        ui_format += "• /markattendance [match_id] [status] - Mark your availability"

        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"Failed to get availability: {e}")
        return json_error(f"Error getting availability: {e!s}", "Operation failed")

@tool("get_player_availability_history")
def get_player_availability_history(
    player_id: str,
    limit: int = 10,
) -> str:
    """
    Get availability history for a player.


        player_id: Player ID to get history for
        limit: Maximum number of records to return (default: 10)


    :return: JSON response with player availability history
    :rtype: str  # TODO: Fix type
    """
    try:
        container = get_container()
        availability_service: AvailabilityService = container.get_service(AvailabilityService)
        history = asyncio.run(availability_service.get_player_history(player_id, limit))

        if not history:
            data = {
                'player_id': player_id,
                'history': [],
                'statistics': {
                    'total_matches': 0,
                    'available_count': 0,
                    'unavailable_count': 0,
                    'maybe_count': 0,
                    'availability_rate': 0.0,
                    'reliability_rating': 'No data'
                }
            }
            return json_response(data, ui_format=f"📈 **Availability History**\n\nNo availability records found for player {player_id}.")

        # Calculate statistics
        total_matches = len(history)
        available_count = len([a for a in history if a.is_available])
        unavailable_count = len([a for a in history if a.is_unavailable])
        maybe_count = len([a for a in history if a.is_maybe])

        availability_rate = (available_count / total_matches) * 100 if total_matches > 0 else 0

        # Reliability rating
        if availability_rate >= 90:
            reliability = "⭐⭐⭐⭐⭐ (Excellent)"
        elif availability_rate >= 80:
            reliability = "⭐⭐⭐⭐ (Good)"
        elif availability_rate >= 70:
            reliability = "⭐⭐⭐ (Fair)"
        elif availability_rate >= 60:
            reliability = "⭐⭐ (Poor)"
        else:
            reliability = "⭐ (Very Poor)"

        data = {
            'player_id': player_id,
            'history': [{
                'match_id': a.match_id,
                'status': a.status.value,
                'status_emoji': a.status_emoji,
                'reason': a.reason
            } for a in history],
            'statistics': {
                'total_matches': total_matches,
                'available_count': available_count,
                'unavailable_count': unavailable_count,
                'maybe_count': maybe_count,
                'availability_rate': availability_rate,
                'reliability_rating': reliability
            }
        }

        ui_format = f"📈 **Availability History for {player_id}**\n\n"
        ui_format += f"**Last {len(history)} matches**:\n\n"

        for availability in history:
            ui_format += f"{availability.status_emoji} Match {availability.match_id} - {availability.status.value.title()}\n"
            if availability.reason:
                ui_format += f"  - Reason: {availability.reason}\n"

        ui_format += "\n📊 **Statistics**\n"
        ui_format += f"• **Availability Rate**: {availability_rate:.1f}% ({available_count}/{total_matches} matches)\n"
        ui_format += f"• **Available**: {available_count} matches\n"
        ui_format += f"• **Unavailable**: {unavailable_count} matches\n"
        ui_format += f"• **Maybe**: {maybe_count} matches\n"
        ui_format += f"• **Reliability Rating**: {reliability}"

        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"Failed to get player availability history: {e}")
        return json_error(f"Error getting availability history: {e!s}", "Operation failed")

@tool("send_availability_reminders")
def send_availability_reminders(match_id: str) -> str:
    """
    Send availability reminders for a match.


        match_id: Match ID to send reminders for


    :return: JSON response with reminder sending status
    :rtype: str  # TODO: Fix type
    """
    try:
        container = get_container()
        availability_service: AvailabilityService = container.get_service(AvailabilityService)
        success = asyncio.run(availability_service.send_availability_reminders(match_id))

        if success:
            pending_players = asyncio.run(availability_service.get_pending_players(match_id))
            data = {
                'match_id': match_id,
                'status': 'reminders_sent',
                'pending_players_count': len(pending_players),
                'success': True
            }
            ui_format = (
                "✅ **Reminders Sent**\n\n"
                f"Reminders sent to {len(pending_players)} players who haven't responded to availability requests for match {match_id}."
            )
            return json_response(data, ui_format=ui_format)
        else:
            data = {
                'match_id': match_id,
                'status': 'reminders_failed',
                'success': False
            }
            ui_format = (
                "❌ **Failed to send reminders**\n\n"
                f"Unable to send availability reminders for match {match_id}."
            )
            return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"Failed to send reminders: {e}")
        return json_error(f"Error sending reminders: {e!s}", "Operation failed")
