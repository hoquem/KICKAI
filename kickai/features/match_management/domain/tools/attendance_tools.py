import logging
from datetime import time
from typing import List, Optional

from crewai.tools import tool

from kickai.features.match_management.domain.entities.attendance import AttendanceStatus
from kickai.utils.tool_validation import create_tool_response
from kickai.features.match_management.domain.services.attendance_service import AttendanceService

logger = logging.getLogger(__name__)


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def record_attendance(
    match_id: str,
    player_id: str,
    status: str,  # attended, absent, late
    reason: Optional[str] = None,
    recorded_by: str = "",
    arrival_time: Optional[str] = None,  # HH:MM format
) -> str:
    """Record actual attendance for a player at a match.
    
    Returns:
        JSON string with attendance record result
    """
    try:
        from kickai.core.dependency_container import get_container
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        if not attendance_service:
            return create_tool_response(False, "Service unavailable: Attendance service not available.")
        # Convert status string to enum
        try:
            attendance_status = AttendanceStatus(status.lower())
        except ValueError:
            return create_tool_response(False, f"Invalid status: {status}. Valid options: attended, absent, late")

        # Parse arrival time if provided
        arrival_time_obj = None
        if arrival_time:
            try:
                arrival_time_obj = time.fromisoformat(arrival_time)
            except ValueError:
                return create_tool_response(False, f"Invalid arrival time format: {arrival_time}. Use HH:MM format")

        # Record attendance
        attendance = await attendance_service.record_attendance(
            match_id=match_id,
            player_id=player_id,
            status=attendance_status,
            reason=reason,
            recorded_by=recorded_by,
            arrival_time=arrival_time_obj,
        )

        # Get attendance summary for the match
        summary = await attendance_service.get_attendance_summary(match_id)

        result = [
            "✅ Match Attendance Recorded",
            "",
            f"Match: {match_id}",
            f"Player: {player_id}",
            f"Status: {attendance.status_emoji} {attendance_status.value.title()}",
        ]

        if reason:
            result.append(f"Reason: {reason}")

        if arrival_time_obj:
            result.append(f"Arrival Time: {attendance.formatted_arrival_time}")

        attendance_data = {
            'message': 'Match Attendance Recorded',
            'match_id': match_id,
            'player_id': player_id,
            'status': attendance_status.value.title(),
            'status_emoji': attendance.status_emoji,
            'reason': reason,
            'arrival_time': attendance.formatted_arrival_time if arrival_time_obj else None,
            'recorded_by': recorded_by or 'System',
            'recorded_at': attendance.recorded_at.strftime('%H:%M'),
            'match_summary': {
                'attended': summary['attended'],
                'absent': summary['absent'],
                'late': summary['late'],
                'pending': summary['not_recorded']
            }
        }
        return create_tool_response(True, "Operation completed successfully", data=attendance_data)

    except Exception as e:
        logger.error(f"Failed to record attendance: {e}")
        return create_tool_response(False, f"Error recording attendance: {e!s}")



# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_match_attendance(match_id: str) -> str:
    """Get attendance information for a match.
    
    Returns:
        JSON string with match attendance information
    """
    try:
        from kickai.core.dependency_container import get_container
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        if not attendance_service:
            return create_tool_response(False, "Service unavailable: Attendance service not available.")
        # Get attendance summary
        summary = await attendance_service.get_attendance_summary(match_id)

        # Get attendance records by status
        attended_players = await attendance_service.get_attended_players(match_id)
        absent_players = await attendance_service.get_absent_players(match_id)
        late_players = await attendance_service.get_late_players(match_id)

        result = [
            f"📊 Match Attendance: {match_id}",
            "",
            f"Total Players: {summary['total_players']}",
            "",
        ]

        # Attended players
        if attended_players:
            result.append(f"✅ Attended ({len(attended_players)}):")
            for attendance in attended_players:
                result.append(f"• {attendance.player_id}")
                if attendance.arrival_time:
                    result.append(f"  - Arrived: {attendance.formatted_arrival_time}")
            result.append("")

        # Absent players
        if absent_players:
            result.append(f"❌ Absent ({len(absent_players)}):")
            for attendance in absent_players:
                result.append(f"• {attendance.player_id}")
                if attendance.reason:
                    result.append(f"  - Reason: {attendance.reason}")
            result.append("")

        # Late players
        if late_players:
            result.append(f"⏰ Late ({len(late_players)}):")
            for attendance in late_players:
                result.append(f"• {attendance.player_id}")
                if attendance.arrival_time:
                    result.append(f"  - Arrived: {attendance.formatted_arrival_time}")
                if attendance.reason:
                    result.append(f"  - Reason: {attendance.reason}")
            result.append("")

        attendance_info = {
            'match_id': match_id,
            'total_players': summary['total_players'],
            'attended_players': [{'player_id': a.player_id, 'arrival_time': a.formatted_arrival_time} for a in attended_players],
            'absent_players': [{'player_id': a.player_id, 'reason': a.reason} for a in absent_players],
            'late_players': [{'player_id': a.player_id, 'arrival_time': a.formatted_arrival_time, 'reason': a.reason} for a in late_players],
            'summary': {
                'attended': len(attended_players),
                'absent': len(absent_players),
                'late': len(late_players)
            }
        }
        return create_tool_response(True, "Operation completed successfully", data=attendance_info)

    except Exception as e:
        logger.error(f"Failed to get match attendance: {e}")
        return create_tool_response(False, f"Error getting match attendance: {e!s}")



# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_player_attendance_history(
    player_id: str,
    limit: int = 10,
) -> str:
    """Get attendance history for a player."""
    try:
        from kickai.core.dependency_container import get_container
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        if not attendance_service:
            return create_tool_response(False, "Service unavailable: Attendance service not available.")
        history = await attendance_service.get_player_attendance_history(player_id, limit)

        if not history:
            return create_tool_response(True, "Operation completed successfully", data={"message": f"No attendance records found for player {player_id}", "player_id": player_id, "history": []})

        result = [
            f"📈 Attendance History for {player_id}",
            "",
            f"Last {len(history)} matches:",
            "",
        ]

        for attendance in history:
            result.append(
                f"{attendance.status_emoji} Match {attendance.match_id} - {attendance.status.value.title()}"
            )
            if attendance.arrival_time:
                result.append(f"  - Arrived: {attendance.formatted_arrival_time}")
            if attendance.reason:
                result.append(f"  - Reason: {attendance.reason}")

        # Calculate statistics
        stats = await attendance_service.calculate_attendance_stats(player_id)

        result.extend([
            "",
            "📊 Statistics",
            f"• Attendance Rate: {stats['attendance_rate']}% ({stats['attended']}/{stats['total_matches']} matches)",
            f"• Attended: {stats['attended']} matches",
            f"• Absent: {stats['absent']} matches",
            f"• Late: {stats['late']} matches",
            f"• Reliability Rating: {stats['reliability_rating']}",
        ])

        attendance_data = {
            "player_id": player_id,
            "history": [
                {
                    "match_id": attendance.match_id,
                    "status": attendance.status.value.title(),
                    "status_emoji": attendance.status_emoji,
                    "arrival_time": attendance.formatted_arrival_time if attendance.arrival_time else None,
                    "reason": attendance.reason
                } for attendance in history
            ],
            "statistics": stats,
            "formatted_message": "\n".join(result)
        }
        return create_tool_response(True, "Operation completed successfully", data=attendance_data)

    except Exception as e:
        logger.error(f"Failed to get player attendance history: {e}")
        return create_tool_response(False, f"Error getting attendance history: {e!s}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def bulk_record_attendance(
    match_id: str,
    attendance_records: List[dict],
    recorded_by: str = "",
) -> str:
    """Record attendance for multiple players at once."""
    try:
        from kickai.core.dependency_container import get_container
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        if not attendance_service:
            return create_tool_response(False, "Service unavailable: Attendance service not available.")
        # Validate attendance records format
        for record in attendance_records:
            required_fields = ["player_id", "status"]
            missing_fields = [field for field in required_fields if field not in record]
            if missing_fields:
                return create_tool_response(False, f"Invalid record format: Missing fields {missing_fields}")

        # Record attendance for all players
        recorded_attendances = await attendance_service.bulk_record_attendance(
            match_id=match_id,
            attendance_records=attendance_records,
            recorded_by=recorded_by,
        )

        # Get attendance summary
        summary = await attendance_service.get_attendance_summary(match_id)

        result = [
            "✅ Bulk Attendance Recorded",
            "",
            f"Match: {match_id}",
            f"Players Recorded: {len(recorded_attendances)}",
            f"Recorded by: {recorded_by or 'System'}",
            "",
            "📊 Match Summary",
            f"• Attended: {summary['attended']} players",
            f"• Absent: {summary['absent']} players",
            f"• Late: {summary['late']} players",
            f"• Pending: {summary['not_recorded']} players",
        ]

        bulk_data = {
            "match_id": match_id,
            "players_recorded": len(recorded_attendances),
            "recorded_by": recorded_by or 'System',
            "match_summary": summary,
            "formatted_message": "\n".join(result)
        }
        return create_tool_response(True, "Operation completed successfully", data=bulk_data)

    except Exception as e:
        logger.error(f"Failed to bulk record attendance: {e}")
        return create_tool_response(False, f"Error bulk recording attendance: {e!s}")
