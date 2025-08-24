#!/usr/bin/env python3
"""
Attendance Management Tools - Clean Architecture Application Layer

This module provides CrewAI tools for attendance management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Optional
from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.features.attendance_management.domain.services.attendance_service import AttendanceService
from kickai.features.attendance_management.domain.entities.attendance import AttendanceStatus, AttendanceResponseMethod
from kickai.utils.tool_helpers import create_json_response


@tool("mark_availability", result_as_answer=True)
async def mark_availability(
    telegram_id: int, 
    team_id: str, 
    username: str, 
    chat_type: str,
    match_id: str,
    status: str,  # "available", "unavailable", "maybe"
    notes: Optional[str] = None
) -> str:
    """
    Mark player availability for a match.

    This tool serves as the application boundary for availability marking functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Player's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        match_id: The unique match identifier
        status: Availability status (available, unavailable, maybe)
        notes: Optional notes about availability

    Returns:
        JSON formatted availability confirmation
    """
    try:
        logger.info(f"📊 Availability marking for {match_id} from {username} ({telegram_id})")

        if not all([match_id, status]):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Match ID and status are required"
            )

        # Map string status to enum
        status_mapping = {
            "available": AttendanceStatus.AVAILABLE,
            "unavailable": AttendanceStatus.UNAVAILABLE,
            "maybe": AttendanceStatus.MAYBE,
            "tentative": AttendanceStatus.MAYBE
        }
        
        attendance_status = status_mapping.get(status.lower())
        if not attendance_status:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Invalid status. Use: {', '.join(status_mapping.keys())}"
            )

        # Get required services from container (application boundary)
        container = get_container()
        attendance_service = AttendanceService()
        
        if not attendance_service:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="AttendanceService is not available"
            )

        # Execute domain operation
        attendance = await attendance_service.mark_attendance(
            player_id=str(telegram_id),
            match_id=match_id,
            status=attendance_status,
            team_id=team_id,
            response_method=AttendanceResponseMethod.COMMAND,
            notes=notes,
            marked_by=str(telegram_id)
        )

        # Format response at application boundary
        status_emoji = {
            AttendanceStatus.AVAILABLE: "✅",
            AttendanceStatus.UNAVAILABLE: "❌", 
            AttendanceStatus.MAYBE: "❓"
        }

        message = f"""📊 **Availability Marked**

{status_emoji.get(attendance_status, "📊")} **Status**: {attendance_status.value.title()}
🏆 **Match ID**: {match_id}
👤 **Player**: {username}
📅 **Marked**: {attendance.created_at.strftime('%Y-%m-%d %H:%M')}"""

        if notes:
            message += f"\n💬 **Notes**: {notes}"

        message += "\n\n✅ Your availability has been recorded successfully!"

        logger.info(f"✅ Availability marked for {username}: {match_id} - {attendance_status.value}")
        return create_json_response(ResponseStatus.SUCCESS, data=message)

    except Exception as e:
        logger.error(f"❌ Error marking availability for {match_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to mark availability: {e}")


@tool("get_availability", result_as_answer=True)
async def get_availability(telegram_id: int, team_id: str, username: str, chat_type: str, match_id: str) -> str:
    """
    Get player availability for a match.

    This tool serves as the application boundary for availability retrieval functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        match_id: The unique match identifier

    Returns:
        JSON formatted availability information
    """
    try:
        logger.info(f"📊 Availability query for {match_id} from {username} ({telegram_id})")

        if not match_id:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Match ID is required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        attendance_service = AttendanceService()
        
        if not attendance_service:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="AttendanceService is not available"
            )

        # Execute domain operation
        attendance_summary = await attendance_service.get_match_attendance_summary(match_id)
        
        if not attendance_summary:
            return create_json_response(
                ResponseStatus.SUCCESS,
                data=f"📊 **Match Availability: {match_id}**\n\nNo availability responses recorded yet."
            )

        # Format response at application boundary
        result = [
            f"📊 **Match Availability: {match_id}**",
            "",
            f"✅ **Available**: {attendance_summary.available_count} players",
            f"❌ **Unavailable**: {attendance_summary.unavailable_count} players", 
            f"❓ **Maybe/Tentative**: {attendance_summary.maybe_count} players",
            f"⏳ **No Response**: {attendance_summary.no_response_count} players",
            "",
            f"📊 **Total Responses**: {attendance_summary.total_responses}/{attendance_summary.total_players}",
        ]

        if attendance_summary.available_players:
            result.append("")
            result.append("✅ **Available Players**:")
            for player in attendance_summary.available_players:
                result.append(f"• {player}")

        if attendance_summary.unavailable_players:
            result.append("")
            result.append("❌ **Unavailable Players**:")
            for player in attendance_summary.unavailable_players:
                result.append(f"• {player}")

        result.append("")
        result.append("📋 **Actions**")
        result.append("• /markattendance [match_id] [status] - Update your availability")
        result.append("• /selectsquad [match_id] - Select squad (Leadership only)")

        logger.info(f"✅ Availability summary retrieved for {match_id}")
        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))

    except Exception as e:
        logger.error(f"❌ Error getting availability for {match_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get availability: {e}")


@tool("get_player_availability_history", result_as_answer=True)
async def get_player_availability_history(telegram_id: int, team_id: str, username: str, chat_type: str, player_id: Optional[str] = None) -> str:
    """
    Get player availability history.

    This tool serves as the application boundary for availability history functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        player_id: Optional specific player ID (defaults to requesting user)

    Returns:
        JSON formatted availability history
    """
    try:
        # Default to requesting user if no specific player_id provided
        target_player_id = player_id or str(telegram_id)
        
        logger.info(f"📊 Availability history request for player {target_player_id} from {username} ({telegram_id})")

        # Get required services from container (application boundary)
        container = get_container()
        attendance_service = AttendanceService()
        
        if not attendance_service:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="AttendanceService is not available"
            )

        # Execute domain operation
        history = await attendance_service.get_player_attendance_history(target_player_id, team_id)
        
        if not history:
            return create_json_response(
                ResponseStatus.SUCCESS,
                data=f"📊 **Availability History**\n\nNo availability history found for player {target_player_id}."
            )

        # Format response at application boundary
        result = [
            f"📊 **Availability History: {target_player_id}**",
            "",
            f"📅 **Recent Responses** (Last {len(history)} matches):",
            "",
        ]

        for attendance in history:
            status_emoji = {
                AttendanceStatus.AVAILABLE: "✅",
                AttendanceStatus.UNAVAILABLE: "❌",
                AttendanceStatus.MAYBE: "❓"
            }
            
            result.append(f"{status_emoji.get(attendance.status, '📊')} **{attendance.match_id}**")
            result.append(f"   📅 {attendance.created_at.strftime('%Y-%m-%d %H:%M')}")
            result.append(f"   📊 Status: {attendance.status.value.title()}")
            if attendance.notes:
                result.append(f"   💬 Notes: {attendance.notes}")
            result.append("")

        result.append("📋 **Actions**")
        result.append("• /markattendance [match_id] [status] - Mark new availability")
        result.append("• /availability [match_id] - View match availability")

        logger.info(f"✅ Availability history retrieved for player {target_player_id}")
        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))

    except Exception as e:
        logger.error(f"❌ Error getting availability history for {target_player_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get availability history: {e}")


@tool("record_attendance", result_as_answer=True)
async def record_attendance(
    telegram_id: int, 
    team_id: str, 
    username: str, 
    chat_type: str,
    match_id: str,
    player_id: str,
    status: str,
    notes: Optional[str] = None
) -> str:
    """
    Record actual match attendance (for completed matches).

    This tool serves as the application boundary for attendance recording functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Recorder's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        match_id: The unique match identifier
        player_id: Player whose attendance is being recorded
        status: Actual attendance status (present, absent)
        notes: Optional notes about attendance

    Returns:
        JSON formatted attendance confirmation
    """
    try:
        logger.info(f"📊 Attendance recording for {match_id}, player {player_id} from {username} ({telegram_id})")

        if not all([match_id, player_id, status]):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Match ID, player ID, and status are required"
            )

        # Map string status to enum for actual attendance
        status_mapping = {
            "present": AttendanceStatus.AVAILABLE,  # Present at match
            "absent": AttendanceStatus.UNAVAILABLE,   # Absent from match
        }
        
        attendance_status = status_mapping.get(status.lower())
        if not attendance_status:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Invalid attendance status. Use: {', '.join(status_mapping.keys())}"
            )

        # Get required services from container (application boundary)
        container = get_container()
        attendance_service = AttendanceService()
        
        if not attendance_service:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="AttendanceService is not available"
            )

        # Execute domain operation
        attendance = await attendance_service.mark_attendance(
            player_id=player_id,
            match_id=match_id,
            status=attendance_status,
            team_id=team_id,
            response_method=AttendanceResponseMethod.ADMIN,
            notes=notes,
            marked_by=str(telegram_id)
        )

        # Format response at application boundary
        status_text = "Present" if attendance_status == AttendanceStatus.AVAILABLE else "Absent"
        status_emoji = "✅" if attendance_status == AttendanceStatus.AVAILABLE else "❌"

        message = f"""📊 **Attendance Recorded**

{status_emoji} **Status**: {status_text}
🏆 **Match ID**: {match_id}
👤 **Player**: {player_id}
🔧 **Recorded by**: {username}
📅 **Recorded**: {attendance.created_at.strftime('%Y-%m-%d %H:%M')}"""

        if notes:
            message += f"\n💬 **Notes**: {notes}"

        message += "\n\n✅ Attendance has been recorded successfully!"

        logger.info(f"✅ Attendance recorded: {player_id} - {match_id} - {status_text}")
        return create_json_response(ResponseStatus.SUCCESS, data=message)

    except Exception as e:
        logger.error(f"❌ Error recording attendance for {match_id}, player {player_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to record attendance: {e}")


@tool("get_match_attendance", result_as_answer=True)
async def get_match_attendance(telegram_id: int, team_id: str, username: str, chat_type: str, match_id: str) -> str:
    """
    Get complete match attendance information.

    This tool serves as the application boundary for match attendance functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        match_id: The unique match identifier

    Returns:
        JSON formatted match attendance information
    """
    try:
        logger.info(f"📊 Match attendance query for {match_id} from {username} ({telegram_id})")

        if not match_id:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Match ID is required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        attendance_service = AttendanceService()
        
        if not attendance_service:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="AttendanceService is not available"
            )

        # Execute domain operation
        attendance_records = await attendance_service.get_match_attendance(match_id)
        
        if not attendance_records:
            return create_json_response(
                ResponseStatus.SUCCESS,
                data=f"📊 **Match Attendance: {match_id}**\n\nNo attendance records found."
            )

        # Format response at application boundary
        result = [
            f"📊 **Match Attendance: {match_id}**",
            "",
        ]

        # Group by status
        available = [r for r in attendance_records if r.status == AttendanceStatus.AVAILABLE]
        unavailable = [r for r in attendance_records if r.status == AttendanceStatus.UNAVAILABLE]
        maybe = [r for r in attendance_records if r.status == AttendanceStatus.MAYBE]

        if available:
            result.append("✅ **Available/Present**:")
            for record in available:
                result.append(f"• {record.player_id}")
                if record.notes:
                    result.append(f"  💬 {record.notes}")
            result.append("")

        if unavailable:
            result.append("❌ **Unavailable/Absent**:")
            for record in unavailable:
                result.append(f"• {record.player_id}")
                if record.notes:
                    result.append(f"  💬 {record.notes}")
            result.append("")

        if maybe:
            result.append("❓ **Maybe/Tentative**:")
            for record in maybe:
                result.append(f"• {record.player_id}")
                if record.notes:
                    result.append(f"  💬 {record.notes}")
            result.append("")

        result.append(f"📊 **Summary**: {len(available)} available, {len(unavailable)} unavailable, {len(maybe)} maybe")
        
        result.append("")
        result.append("📋 **Actions**")
        result.append("• /recordattendance [match_id] [player_id] [status] - Record actual attendance")
        result.append("• /markattendance [match_id] [status] - Update your availability")

        logger.info(f"✅ Match attendance retrieved for {match_id}: {len(attendance_records)} records")
        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))

    except Exception as e:
        logger.error(f"❌ Error getting match attendance for {match_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get match attendance: {e}")


@tool("get_player_attendance_history", result_as_answer=True) 
async def get_player_attendance_history(telegram_id: int, team_id: str, username: str, chat_type: str, player_id: Optional[str] = None) -> str:
    """
    Get comprehensive player attendance history.

    This tool serves as the application boundary for player attendance history functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        player_id: Optional specific player ID (defaults to requesting user)

    Returns:
        JSON formatted player attendance history
    """
    try:
        # Default to requesting user if no specific player_id provided
        target_player_id = player_id or str(telegram_id)
        
        logger.info(f"📊 Attendance history request for player {target_player_id} from {username} ({telegram_id})")

        # Get required services from container (application boundary)
        container = get_container()
        attendance_service = AttendanceService()
        
        if not attendance_service:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="AttendanceService is not available"
            )

        # Execute domain operation
        history = await attendance_service.get_player_attendance_history(target_player_id, team_id)
        
        if not history:
            return create_json_response(
                ResponseStatus.SUCCESS,
                data=f"📊 **Attendance History**\n\nNo attendance history found for player {target_player_id}."
            )

        # Format response at application boundary
        result = [
            f"📊 **Attendance History: {target_player_id}**",
            "",
            f"📅 **Match Records** (Last {len(history)} matches):",
            "",
        ]

        # Calculate statistics
        total_matches = len(history)
        available_count = len([h for h in history if h.status == AttendanceStatus.AVAILABLE])
        unavailable_count = len([h for h in history if h.status == AttendanceStatus.UNAVAILABLE])
        maybe_count = len([h for h in history if h.status == AttendanceStatus.MAYBE])
        
        availability_rate = (available_count / total_matches * 100) if total_matches > 0 else 0

        for attendance in history:
            status_emoji = {
                AttendanceStatus.AVAILABLE: "✅",
                AttendanceStatus.UNAVAILABLE: "❌",
                AttendanceStatus.MAYBE: "❓"
            }
            
            result.append(f"{status_emoji.get(attendance.status, '📊')} **{attendance.match_id}**")
            result.append(f"   📅 {attendance.created_at.strftime('%Y-%m-%d %H:%M')}")
            result.append(f"   📊 Status: {attendance.status.value.title()}")
            if attendance.notes:
                result.append(f"   💬 Notes: {attendance.notes}")
            result.append("")

        result.append("📊 **Statistics**")
        result.append(f"• **Total Matches**: {total_matches}")
        result.append(f"• **Available**: {available_count} ({availability_rate:.1f}%)")
        result.append(f"• **Unavailable**: {unavailable_count}")
        result.append(f"• **Maybe**: {maybe_count}")

        result.append("")
        result.append("📋 **Actions**")
        result.append("• /markattendance [match_id] [status] - Mark availability")
        result.append("• /attendance [match_id] - View match attendance")

        logger.info(f"✅ Attendance history retrieved for player {target_player_id}: {total_matches} matches")
        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))

    except Exception as e:
        logger.error(f"❌ Error getting attendance history for {target_player_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get attendance history: {e}")