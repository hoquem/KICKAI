#!/usr/bin/env python3
"""
Training Management Tools

This module provides tools for training session management that can be used by agents.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from crewai import tool
from kickai.core.exceptions import TrainingError
from kickai.database.firebase_client import get_firebase_client
from kickai.features.training_management.domain.entities.training_session import (
    TrainingSession, TrainingSessionStatus, TrainingSessionType
)
from kickai.features.training_management.domain.entities.training_attendance import (
    TrainingAttendance, TrainingAttendanceStatus, TrainingAttendanceResponseMethod
)
from kickai.features.training_management.domain.services.training_session_service import TrainingSessionService
from kickai.features.training_management.domain.services.training_attendance_service import TrainingAttendanceService
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.utils.json_utils import extract_single_value, validate_required_input

logger = logging.getLogger(__name__)


@tool("schedule_training_session")
async def schedule_training_session(
    team_id: str,
    session_type: str,
    date: str,
    start_time: str,
    duration_minutes: int,
    location: str,
    focus_areas: str,
    max_participants: Optional[int] = None,
    coach_notes: Optional[str] = None,
) -> str:
    """
    Schedule a new training session for the team.

    Args:
        team_id: Team ID
        session_type: Training session type (technical_skills, tactical_awareness, fitness_conditioning, match_practice, recovery_session)
        date: Training date (YYYY-MM-DD)
        start_time: Training start time (HH:MM)
        duration_minutes: Session duration in minutes
        location: Training location
        focus_areas: Comma-separated focus areas (e.g., "Passing, Shooting, Fitness")
        max_participants: Maximum number of participants (optional)
        coach_notes: Additional notes from coach (optional)

    Returns:
        Confirmation message with training session details
    """
    try:
        # Handle JSON string input
        team_id = extract_single_value(team_id, "team_id")
        session_type = extract_single_value(session_type, "session_type")
        date = extract_single_value(date, "date")
        start_time = extract_single_value(start_time, "start_time")
        duration_minutes = int(extract_single_value(str(duration_minutes), "duration_minutes"))
        location = extract_single_value(location, "location")
        focus_areas = extract_single_value(focus_areas, "focus_areas")
        
        if max_participants:
            max_participants = int(extract_single_value(str(max_participants), "max_participants"))
        if coach_notes:
            coach_notes = extract_single_value(coach_notes, "coach_notes")

        # Validate required inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(session_type, "Session Type")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(date, "Date")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(start_time, "Start Time")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(location, "Location")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(focus_areas, "Focus Areas")
        if validation_error:
            return validation_error

        # Parse session type
        try:
            session_type_enum = TrainingSessionType(session_type.lower())
        except ValueError:
            valid_types = [t.value for t in TrainingSessionType]
            return f"❌ Invalid session type. Valid types: {', '.join(valid_types)}"

        # Parse date
        try:
            training_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "❌ Invalid date format. Use YYYY-MM-DD"

        # Parse focus areas
        focus_areas_list = [area.strip() for area in focus_areas.split(",") if area.strip()]

        # Create training session
        service = TrainingSessionService()
        training_session = await service.create_training_session(
            team_id=team_id,
            session_type=session_type_enum,
            date=training_date,
            start_time=start_time,
            duration_minutes=duration_minutes,
            location=location,
            focus_areas=focus_areas_list,
            max_participants=max_participants,
            coach_notes=coach_notes,
        )

        # Format response
        response = f"""✅ Training Session Scheduled!

📅 **Session Details:**
• **Type:** {training_session.get_session_type_display()}
• **Date:** {training_date.strftime('%A, %B %d, %Y')}
• **Time:** {start_time} ({duration_minutes} minutes)
• **Location:** {location}
• **Focus Areas:** {', '.join(focus_areas_list)}
• **Session ID:** {training_session.id}

🎯 **Next Steps:**
• Players will be notified of the new training session
• Attendance tracking is now enabled
• Players can mark their availability using /marktraining

💡 **Session Types Available:**
• Technical Skills - Passing, shooting, dribbling
• Tactical Awareness - Positioning, game understanding
• Fitness Conditioning - Strength, endurance training
• Match Practice - Small-sided games
• Recovery Session - Light training and recovery"""

        if max_participants:
            response += f"\n• **Max Participants:** {max_participants}"
        
        if coach_notes:
            response += f"\n• **Coach Notes:** {coach_notes}"

        return response

    except Exception as e:
        logger.error(f"Error scheduling training session: {e}", exc_info=True)
        return f"❌ Error scheduling training session: {e!s}"


@tool("list_training_sessions")
async def list_training_sessions(
    team_id: str,
    period: str = "upcoming"
) -> str:
    """
    List training sessions for a team.

    Args:
        team_id: Team ID
        period: Time period filter (today, this_week, next_week, upcoming, all)

    Returns:
        Formatted list of training sessions
    """
    try:
        # Handle JSON string input
        team_id = extract_single_value(team_id, "team_id")
        period = extract_single_value(period, "period")

        # Validate required inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Get training sessions
        service = TrainingSessionService()
        
        if period == "today":
            training_sessions = await service.get_todays_training_sessions(team_id)
        elif period == "this_week":
            week_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            training_sessions = await service.get_weekly_schedule(team_id, week_start)
        elif period == "next_week":
            week_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=7)
            training_sessions = await service.get_weekly_schedule(team_id, week_start)
        elif period == "all":
            training_sessions = await service.list_training_sessions(team_id, upcoming_only=False)
        else:  # upcoming (default)
            training_sessions = await service.list_training_sessions(team_id, upcoming_only=True)

        if not training_sessions:
            period_display = {
                "today": "today",
                "this_week": "this week",
                "next_week": "next week",
                "upcoming": "upcoming",
                "all": "all"
            }.get(period, period)
            
            return f"📅 No training sessions found for {period_display}."

        # Format response
        response = f"📅 Training Sessions ({period.replace('_', ' ').title()}):\n\n"
        
        for i, session in enumerate(training_sessions, 1):
            session_date = datetime.fromisoformat(session.date)
            response += f"{i}. **{session.get_session_type_display()}** {session.get_status_emoji()}\n"
            response += f"   📅 {session_date.strftime('%A, %B %d')} at {session.start_time}\n"
            response += f"   ⏱️ {session.duration_minutes} minutes\n"
            response += f"   📍 {session.location}\n"
            response += f"   🎯 {', '.join(session.focus_areas)}\n"
            response += f"   🆔 {session.id}\n\n"

        return response

    except Exception as e:
        logger.error(f"Error listing training sessions: {e}", exc_info=True)
        return f"❌ Error listing training sessions: {e!s}"


@tool("mark_training_attendance")
async def mark_training_attendance(
    player_id: str,
    team_id: str,
    status: str,
    training_session_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Mark attendance for a training session.

    Args:
        player_id: Player ID
        team_id: Team ID
        status: Attendance status (confirmed, declined, tentative)
        training_session_id: Optional specific training session ID
        notes: Optional notes about attendance

    Returns:
        Confirmation message
    """
    try:
        # Handle JSON string input
        player_id = extract_single_value(player_id, "player_id")
        team_id = extract_single_value(team_id, "team_id")
        status = extract_single_value(status, "status")
        
        if training_session_id:
            training_session_id = extract_single_value(training_session_id, "training_session_id")
        if notes:
            notes = extract_single_value(notes, "notes")

        # Validate required inputs
        validation_error = validate_required_input(player_id, "Player ID")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(status, "Status")
        if validation_error:
            return validation_error

        # Parse status
        try:
            attendance_status = TrainingAttendanceStatus(status.lower())
        except ValueError:
            valid_statuses = [s.value for s in TrainingAttendanceStatus]
            return f"❌ Invalid status. Valid statuses: {', '.join(valid_statuses)}"

        # If no specific training session, get the next upcoming one
        if not training_session_id:
            service = TrainingSessionService()
            upcoming_sessions = await service.list_training_sessions(team_id, upcoming_only=True)
            if not upcoming_sessions:
                return "❌ No upcoming training sessions found."
            training_session_id = upcoming_sessions[0].id

        # Get player name for caching
        player_service = PlayerService()
        player = await player_service.get_player(player_id)
        player_name = player.name if player else None

        # Get training session details for caching
        training_service = TrainingSessionService()
        training_session = await training_service.get_training_session(training_session_id)
        if not training_session:
            return f"❌ Training session {training_session_id} not found."

        # Mark attendance
        attendance_service = TrainingAttendanceService()
        attendance = await attendance_service.mark_training_attendance(
            player_id=player_id,
            training_session_id=training_session_id,
            team_id=team_id,
            status=attendance_status,
            player_name=player_name,
            training_session_type=training_session.session_type,
            training_date=training_session.date,
            notes=notes,
        )

        # Format response
        session_date = datetime.fromisoformat(training_session.date)
        status_emoji = attendance.get_status_emoji()
        status_display = attendance.get_status_display()
        
        response = f"""✅ Training Attendance Marked!

{status_emoji} **Status:** {status_display}
📅 **Session:** {training_session.get_session_type_display()}
🗓️ **Date:** {session_date.strftime('%A, %B %d, %Y')}
⏰ **Time:** {training_session.start_time}
📍 **Location:** {training_session.location}
🎯 **Focus:** {', '.join(training_session.focus_areas)}"""

        if notes:
            response += f"\n📝 **Notes:** {notes}"

        response += f"\n\n💡 **Next Steps:**"
        if attendance_status == TrainingAttendanceStatus.CONFIRMED:
            response += "\n• You're confirmed for this training session"
            response += "\n• Please arrive 10 minutes early"
            response += "\n• Bring appropriate training gear"
        elif attendance_status == TrainingAttendanceStatus.DECLINED:
            response += "\n• You've declined this training session"
            response += "\n• Please let the coach know if anything changes"
        elif attendance_status == TrainingAttendanceStatus.TENTATIVE:
            response += "\n• You're tentative for this training session"
            response += "\n• Please confirm as soon as possible"

        return response

    except Exception as e:
        logger.error(f"Error marking training attendance: {e}", exc_info=True)
        return f"❌ Error marking training attendance: {e!s}"


@tool("get_training_attendance_summary")
async def get_training_attendance_summary(
    training_session_id: str,
    team_id: str,
) -> str:
    """
    Get attendance summary for a training session.

    Args:
        training_session_id: Training session ID
        team_id: Team ID

    Returns:
        Formatted attendance summary
    """
    try:
        # Handle JSON string input
        training_session_id = extract_single_value(training_session_id, "training_session_id")
        team_id = extract_single_value(team_id, "team_id")

        # Validate required inputs
        validation_error = validate_required_input(training_session_id, "Training Session ID")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Get attendance summary
        attendance_service = TrainingAttendanceService()
        summary = await attendance_service.get_training_attendance_summary(training_session_id, team_id)
        
        # Get training session details
        training_service = TrainingSessionService()
        training_session = await training_service.get_training_session(training_session_id)
        
        if not training_session:
            return f"❌ Training session {training_session_id} not found."

        # Get detailed attendance list
        attendance_list = await attendance_service.get_training_session_attendance(training_session_id, team_id)

        # Format response
        session_date = datetime.fromisoformat(training_session.date)
        
        response = f"""📊 Training Attendance Summary

📅 **Session:** {training_session.get_session_type_display()}
🗓️ **Date:** {session_date.strftime('%A, %B %d, %Y')}
⏰ **Time:** {training_session.start_time}
📍 **Location:** {training_session.location}

📈 **Attendance Overview:**
• ✅ Confirmed: {summary.confirmed_count}
• ❌ Declined: {summary.declined_count}
• ❔ Tentative: {summary.tentative_count}
• ⏳ No Response: {summary.no_response_count}
• ⚠️ Late Cancellation: {summary.late_cancellation_count}
• 📊 Response Rate: {summary.response_rate}%

👥 **Total Players:** {summary.total_players}"""

        if attendance_list:
            response += "\n\n📋 **Detailed Attendance:**\n"
            for attendance in attendance_list:
                status_emoji = attendance.get_status_emoji()
                player_name = attendance.player_name or attendance.player_id
                response += f"• {status_emoji} {player_name}\n"

        return response

    except Exception as e:
        logger.error(f"Error getting training attendance summary: {e}", exc_info=True)
        return f"❌ Error getting training attendance summary: {e!s}"


@tool("cancel_training_session")
async def cancel_training_session(
    training_session_id: str,
    team_id: str,
    reason: Optional[str] = None,
) -> str:
    """
    Cancel a training session.

    Args:
        training_session_id: Training session ID to cancel
        team_id: Team ID
        reason: Optional reason for cancellation

    Returns:
        Confirmation message
    """
    try:
        # Handle JSON string input
        training_session_id = extract_single_value(training_session_id, "training_session_id")
        team_id = extract_single_value(team_id, "team_id")
        
        if reason:
            reason = extract_single_value(reason, "reason")

        # Validate required inputs
        validation_error = validate_required_input(training_session_id, "Training Session ID")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Cancel training session
        service = TrainingSessionService()
        cancelled_session = await service.cancel_training_session(training_session_id, reason)

        # Format response
        session_date = datetime.fromisoformat(cancelled_session.date)
        
        response = f"""❌ Training Session Cancelled!

📅 **Session:** {cancelled_session.get_session_type_display()}
🗓️ **Date:** {session_date.strftime('%A, %B %d, %Y')}
⏰ **Time:** {cancelled_session.start_time}
📍 **Location:** {cancelled_session.location}"""

        if reason:
            response += f"\n📝 **Reason:** {reason}"

        response += f"""

🔔 **Next Steps:**
• All players will be notified of the cancellation
• Attendance tracking has been disabled
• Players can check for rescheduled sessions using /listtrainings

💡 **Note:** Players who had confirmed attendance will be notified automatically."""

        return response

    except Exception as e:
        logger.error(f"Error cancelling training session: {e}", exc_info=True)
        return f"❌ Error cancelling training session: {e!s}" 