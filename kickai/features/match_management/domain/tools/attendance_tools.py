import logging
from datetime import time

from crewai import Tool

from kickai.features.match_management.domain.entities.attendance import AttendanceStatus
from kickai.features.match_management.domain.services.attendance_service import AttendanceService

logger = logging.getLogger(__name__)


class RecordAttendanceTool(Tool):
    """Tool for recording actual match day attendance."""

    name: str = "record_attendance"
    description: str = "Record actual attendance for a player at a match (attended, absent, late)"

    def __init__(self, attendance_service: AttendanceService):
        super().__init__()
        self.attendance_service = attendance_service

    def _run(
        self,
        match_id: str,
        player_id: str,
        status: str,  # attended, absent, late
        reason: str | None = None,
        recorded_by: str = "",
        arrival_time: str | None = None,  # HH:MM format
    ) -> str:
        """Record actual attendance for a player at a match."""
        try:
            # Convert status string to enum
            try:
                attendance_status = AttendanceStatus(status.lower())
            except ValueError:
                return f"❌ Invalid status: {status}. Valid options: attended, absent, late"

            # Parse arrival time if provided
            arrival_time_obj = None
            if arrival_time:
                try:
                    arrival_time_obj = time.fromisoformat(arrival_time)
                except ValueError:
                    return f"❌ Invalid arrival time format: {arrival_time}. Use HH:MM format"

            # Record attendance
            attendance = self.attendance_service.record_attendance(
                match_id=match_id,
                player_id=player_id,
                status=attendance_status,
                reason=reason,
                recorded_by=recorded_by,
                arrival_time=arrival_time_obj,
            )

            # Get attendance summary for the match
            summary = self.attendance_service.get_attendance_summary(match_id)

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

            result.extend([
                f"Recorded by: {recorded_by or 'System'}",
                f"Time: {attendance.recorded_at.strftime('%H:%M')}",
                "",
                "📊 Match Summary",
                f"• Attended: {summary['attended']} players",
                f"• Absent: {summary['absent']} players",
                f"• Late: {summary['late']} players",
                f"• Pending: {summary['not_recorded']} players",
            ])

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to record attendance: {e}")
            return f"❌ Error recording attendance: {e!s}"


class GetMatchAttendanceTool(Tool):
    """Tool for getting attendance information for a match."""

    name: str = "get_match_attendance"
    description: str = "Get attendance information for a match"

    def __init__(self, attendance_service: AttendanceService):
        super().__init__()
        self.attendance_service = attendance_service

    def _run(self, match_id: str) -> str:
        """Get attendance information for a match."""
        try:
            # Get attendance summary
            summary = self.attendance_service.get_attendance_summary(match_id)

            # Get attendance records by status
            attended_players = self.attendance_service.get_attended_players(match_id)
            absent_players = self.attendance_service.get_absent_players(match_id)
            late_players = self.attendance_service.get_late_players(match_id)

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

            result.append("📋 Actions")
            result.append("• /markmatchattendance [match_id] [player_id] [status] - Record attendance")

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to get match attendance: {e}")
            return f"❌ Error getting match attendance: {e!s}"


class GetPlayerAttendanceHistoryTool(Tool):
    """Tool for getting player attendance history."""

    name: str = "get_player_attendance_history"
    description: str = "Get attendance history for a player"

    def __init__(self, attendance_service: AttendanceService):
        super().__init__()
        self.attendance_service = attendance_service

    def _run(
        self,
        player_id: str,
        limit: int = 10,
    ) -> str:
        """Get attendance history for a player."""
        try:
            history = self.attendance_service.get_player_attendance_history(player_id, limit)

            if not history:
                return f"📈 Attendance History\n\nNo attendance records found for player {player_id}."

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
            stats = self.attendance_service.calculate_attendance_stats(player_id)

            result.extend([
                "",
                "📊 Statistics",
                f"• Attendance Rate: {stats['attendance_rate']}% ({stats['attended']}/{stats['total_matches']} matches)",
                f"• Attended: {stats['attended']} matches",
                f"• Absent: {stats['absent']} matches",
                f"• Late: {stats['late']} matches",
                f"• Reliability Rating: {stats['reliability_rating']}",
            ])

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to get player attendance history: {e}")
            return f"❌ Error getting attendance history: {e!s}"


class BulkRecordAttendanceTool(Tool):
    """Tool for bulk recording attendance for multiple players."""

    name: str = "bulk_record_attendance"
    description: str = "Record attendance for multiple players at once"

    def __init__(self, attendance_service: AttendanceService):
        super().__init__()
        self.attendance_service = attendance_service

    def _run(
        self,
        match_id: str,
        attendance_records: list[dict],
        recorded_by: str = "",
    ) -> str:
        """Record attendance for multiple players at once."""
        try:
            # Validate attendance records format
            for record in attendance_records:
                required_fields = ["player_id", "status"]
                missing_fields = [field for field in required_fields if field not in record]
                if missing_fields:
                    return f"❌ Invalid record format: Missing fields {missing_fields}"

            # Record attendance for all players
            recorded_attendances = self.attendance_service.bulk_record_attendance(
                match_id=match_id,
                attendance_records=attendance_records,
                recorded_by=recorded_by,
            )

            # Get attendance summary
            summary = self.attendance_service.get_attendance_summary(match_id)

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

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to bulk record attendance: {e}")
            return f"❌ Error bulk recording attendance: {e!s}"
