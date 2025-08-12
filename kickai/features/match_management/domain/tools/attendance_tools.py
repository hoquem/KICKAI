import logging
from datetime import time

from crewai.tools import tool

from kickai.features.match_management.domain.entities.attendance import AttendanceStatus
from kickai.features.match_management.domain.services.attendance_service import AttendanceService
from kickai.utils.json_helper import json_error, json_response

logger = logging.getLogger(__name__)

@tool("record_attendance")
def record_attendance(
    match_id: str,
    player_id: str,
    status: str,  # attended, absent, late
    reason: str | None = None,
    recorded_by: str = "",
    arrival_time: str | None = None,  # HH:MM format
) -> str:
    """
    Record actual attendance for a player at a match.


        match_id: Match ID to record attendance for
        player_id: Player ID to record attendance for
        status: Attendance status (attended, absent, late)
        reason: Optional reason for attendance status
        recorded_by: Person recording the attendance
        arrival_time: Optional arrival time in HH:MM format


    :return: JSON response with attendance record and match summary
    :rtype: str  # TODO: Fix type
    """
    try:
        from kickai.core.dependency_container import get_container
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        if not attendance_service:
            return json_error("Attendance service not available", "Service unavailable")
        # Convert status string to enum
        try:
            attendance_status = AttendanceStatus(status.lower())
        except ValueError:
            return json_error(f"Invalid status: {status}. Valid options: attended, absent, late", "Validation failed")

        # Parse arrival time if provided
        arrival_time_obj = None
        if arrival_time:
            try:
                arrival_time_obj = time.fromisoformat(arrival_time)
            except ValueError:
                return json_error(f"Invalid arrival time format: {arrival_time}. Use HH:MM format", "Validation failed")

        # Record attendance
        attendance = attendance_service.record_attendance(
            match_id=match_id,
            player_id=player_id,
            status=attendance_status,
            reason=reason,
            recorded_by=recorded_by,
            arrival_time=arrival_time_obj,
        )

        # Get attendance summary for the match
        summary = attendance_service.get_attendance_summary(match_id)

        data = {
            'match_id': match_id,
            'player_id': player_id,
            'status': attendance_status.value,
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

        ui_format = "✅ Match Attendance Recorded\n\n"
        ui_format += f"Match: {match_id}\n"
        ui_format += f"Player: {player_id}\n"
        ui_format += f"Status: {attendance.status_emoji} {attendance_status.value.title()}\n"

        if reason:
            ui_format += f"Reason: {reason}\n"

        if arrival_time_obj:
            ui_format += f"Arrival Time: {attendance.formatted_arrival_time}\n"

        ui_format += f"Recorded by: {recorded_by or 'System'}\n"
        ui_format += f"Time: {attendance.recorded_at.strftime('%H:%M')}\n\n"
        ui_format += "📊 Match Summary\n"
        ui_format += f"• Attended: {summary['attended']} players\n"
        ui_format += f"• Absent: {summary['absent']} players\n"
        ui_format += f"• Late: {summary['late']} players\n"
        ui_format += f"• Pending: {summary['not_recorded']} players"

        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"Failed to record attendance: {e}")
        return json_error(f"Error recording attendance: {e!s}", "Operation failed")

@tool("get_match_attendance")
def get_match_attendance(match_id: str) -> str:
    """
    Get attendance information for a match.


        match_id: Match ID to get attendance for


    :return: JSON response with attendance information and player lists
    :rtype: str  # TODO: Fix type
    """
    try:
        from kickai.core.dependency_container import get_container
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        if not attendance_service:
            return json_error("Attendance service not available", "Service unavailable")
        # Get attendance summary
        summary = attendance_service.get_attendance_summary(match_id)

        # Get attendance records by status
        attended_players = attendance_service.get_attended_players(match_id)
        absent_players = attendance_service.get_absent_players(match_id)
        late_players = attendance_service.get_late_players(match_id)

        data = {
            'match_id': match_id,
            'summary': {
                'total_players': summary['total_players'],
                'attended': summary['attended'],
                'absent': summary['absent'],
                'late': summary['late'],
                'pending': summary['not_recorded']
            },
            'players': {
                'attended': [{
                    'player_id': a.player_id,
                    'arrival_time': a.formatted_arrival_time if a.arrival_time else None
                } for a in attended_players],
                'absent': [{
                    'player_id': a.player_id,
                    'reason': a.reason
                } for a in absent_players],
                'late': [{
                    'player_id': a.player_id,
                    'arrival_time': a.formatted_arrival_time if a.arrival_time else None,
                    'reason': a.reason
                } for a in late_players]
            }
        }

        ui_format = f"📊 Match Attendance: {match_id}\n\n"
        ui_format += f"Total Players: {summary['total_players']}\n\n"

        # Attended players
        if attended_players:
            ui_format += f"✅ Attended ({len(attended_players)}):\n"
            for attendance in attended_players:
                ui_format += f"• {attendance.player_id}\n"
                if attendance.arrival_time:
                    ui_format += f"  - Arrived: {attendance.formatted_arrival_time}\n"
            ui_format += "\n"

        # Absent players
        if absent_players:
            ui_format += f"❌ Absent ({len(absent_players)}):\n"
            for attendance in absent_players:
                ui_format += f"• {attendance.player_id}\n"
                if attendance.reason:
                    ui_format += f"  - Reason: {attendance.reason}\n"
            ui_format += "\n"

        # Late players
        if late_players:
            ui_format += f"⏰ Late ({len(late_players)}):\n"
            for attendance in late_players:
                ui_format += f"• {attendance.player_id}\n"
                if attendance.arrival_time:
                    ui_format += f"  - Arrived: {attendance.formatted_arrival_time}\n"
                if attendance.reason:
                    ui_format += f"  - Reason: {attendance.reason}\n"
            ui_format += "\n"

        ui_format += "📋 Actions\n"
        ui_format += "• /markmatchattendance [match_id] [player_id] [status] - Record attendance"

        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"Failed to get match attendance: {e}")
        return json_error(f"Error getting match attendance: {e!s}", "Operation failed")

@tool("get_player_attendance_history")
def get_player_attendance_history(
    player_id: str,
    limit: int = 10,
) -> str:
    """
    Get attendance history for a player.


        player_id: Player ID to get history for
        limit: Maximum number of records to return (default: 10)


    :return: JSON response with player attendance history
    :rtype: str  # TODO: Fix type
    """
    try:
        from kickai.core.dependency_container import get_container
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        if not attendance_service:
            return json_error("Attendance service not available", "Service unavailable")
        history = attendance_service.get_player_attendance_history(player_id, limit)

        if not history:
            data = {
                'player_id': player_id,
                'history': [],
                'statistics': {
                    'attendance_rate': 0,
                    'attended': 0,
                    'total_matches': 0,
                    'absent': 0,
                    'late': 0,
                    'reliability_rating': 'No data'
                }
            }
            return json_response(data, ui_format=f"📈 Attendance History\n\nNo attendance records found for player {player_id}.")

        # Calculate statistics
        stats = attendance_service.calculate_attendance_stats(player_id)

        data = {
            'player_id': player_id,
            'history': [{
                'match_id': a.match_id,
                'status': a.status.value,
                'status_emoji': a.status_emoji,
                'arrival_time': a.formatted_arrival_time if a.arrival_time else None,
                'reason': a.reason
            } for a in history],
            'statistics': {
                'attendance_rate': stats['attendance_rate'],
                'attended': stats['attended'],
                'total_matches': stats['total_matches'],
                'absent': stats['absent'],
                'late': stats['late'],
                'reliability_rating': stats['reliability_rating']
            }
        }

        ui_format = f"📈 Attendance History for {player_id}\n\n"
        ui_format += f"Last {len(history)} matches:\n\n"

        for attendance in history:
            ui_format += f"{attendance.status_emoji} Match {attendance.match_id} - {attendance.status.value.title()}\n"
            if attendance.arrival_time:
                ui_format += f"  - Arrived: {attendance.formatted_arrival_time}\n"
            if attendance.reason:
                ui_format += f"  - Reason: {attendance.reason}\n"

        ui_format += "\n📊 Statistics\n"
        ui_format += f"• Attendance Rate: {stats['attendance_rate']}% ({stats['attended']}/{stats['total_matches']} matches)\n"
        ui_format += f"• Attended: {stats['attended']} matches\n"
        ui_format += f"• Absent: {stats['absent']} matches\n"
        ui_format += f"• Late: {stats['late']} matches\n"
        ui_format += f"• Reliability Rating: {stats['reliability_rating']}"

        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"Failed to get player attendance history: {e}")
        return json_error(f"Error getting attendance history: {e!s}", "Operation failed")

@tool("bulk_record_attendance")
def bulk_record_attendance(
    match_id: str,
    attendance_records: list[dict],
    recorded_by: str = "",
) -> str:
    """
    Record attendance for multiple players at once.


        match_id: Match ID to record attendance for
        attendance_records: List of attendance records with player_id and status
        recorded_by: Person recording the attendance


    :return: JSON response with bulk attendance recording status
    :rtype: str  # TODO: Fix type
    """
    try:
        from kickai.core.dependency_container import get_container
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        if not attendance_service:
            return json_error("Attendance service not available", "Service unavailable")
        # Validate attendance records format
        for record in attendance_records:
            required_fields = ["player_id", "status"]
            missing_fields = [field for field in required_fields if field not in record]
            if missing_fields:
                return json_error(f"Invalid record format: Missing fields {missing_fields}", "Validation failed")

        # Record attendance for all players
        recorded_attendances = attendance_service.bulk_record_attendance(
            match_id=match_id,
            attendance_records=attendance_records,
            recorded_by=recorded_by,
        )

        # Get attendance summary
        summary = attendance_service.get_attendance_summary(match_id)

        data = {
            'match_id': match_id,
            'players_recorded': len(recorded_attendances),
            'recorded_by': recorded_by or 'System',
            'attendance_records': attendance_records,
            'match_summary': {
                'attended': summary['attended'],
                'absent': summary['absent'],
                'late': summary['late'],
                'pending': summary['not_recorded']
            }
        }

        ui_format = "✅ Bulk Attendance Recorded\n\n"
        ui_format += f"Match: {match_id}\n"
        ui_format += f"Players Recorded: {len(recorded_attendances)}\n"
        ui_format += f"Recorded by: {recorded_by or 'System'}\n\n"
        ui_format += "📊 Match Summary\n"
        ui_format += f"• Attended: {summary['attended']} players\n"
        ui_format += f"• Absent: {summary['absent']} players\n"
        ui_format += f"• Late: {summary['late']} players\n"
        ui_format += f"• Pending: {summary['not_recorded']} players"

        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"Failed to bulk record attendance: {e}")
        return json_error(f"Error bulk recording attendance: {e!s}", "Operation failed")
