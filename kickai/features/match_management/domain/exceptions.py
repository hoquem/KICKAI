#!/usr/bin/env python3
"""
Match Management Domain Exceptions

Custom exception hierarchy for match management operations to provide
specific error types instead of generic Exception handling.
"""

from kickai.core.exceptions import KickAIError


class MatchManagementError(KickAIError):
    """Base exception for match management errors."""
    pass


class MatchServiceError(MatchManagementError):
    """Base exception for match service errors."""
    pass


class MatchNotFoundError(MatchServiceError):
    """Match not found in system."""
    
    def __init__(self, match_id: str):
        self.match_id = match_id
        super().__init__(
            f"Match not found: {match_id}",
            context={"match_id": match_id}
        )


class MatchAlreadyExistsError(MatchServiceError):
    """Match already exists for the specified time."""
    
    def __init__(self, team_id: str, match_datetime: str):
        self.team_id = team_id
        self.match_datetime = match_datetime
        super().__init__(
            f"Match already exists for team {team_id} at {match_datetime}",
            context={"team_id": team_id, "match_datetime": match_datetime}
        )


class MatchServiceUnavailableError(MatchServiceError):
    """Match service is not available."""
    
    def __init__(self, message: str = "Match service unavailable"):
        super().__init__(message)


class MatchValidationError(MatchManagementError):
    """Base exception for match validation errors."""
    pass


class InvalidMatchDateError(MatchValidationError):
    """Invalid match date or time."""
    
    def __init__(self, match_datetime: str, reason: str):
        self.match_datetime = match_datetime
        self.reason = reason
        super().__init__(
            f"Invalid match date/time '{match_datetime}': {reason}",
            context={"match_datetime": match_datetime, "reason": reason}
        )


class InvalidOpponentError(MatchValidationError):
    """Invalid opponent name."""
    
    def __init__(self, opponent: str):
        self.opponent = opponent
        super().__init__(
            f"Invalid opponent name: {opponent}",
            context={"opponent": opponent}
        )


class InvalidVenueError(MatchValidationError):
    """Invalid venue."""
    
    def __init__(self, venue: str):
        self.venue = venue
        super().__init__(
            f"Invalid venue: {venue}",
            context={"venue": venue}
        )


class AvailabilityError(MatchManagementError):
    """Base exception for availability errors."""
    pass


class AvailabilityServiceUnavailableError(AvailabilityError):
    """Availability service is not available."""
    
    def __init__(self, message: str = "Availability service unavailable"):
        super().__init__(message)


class AvailabilityNotFoundError(AvailabilityError):
    """Availability record not found."""
    
    def __init__(self, player_id: str, match_id: str):
        self.player_id = player_id
        self.match_id = match_id
        super().__init__(
            f"Availability not found for player {player_id} in match {match_id}",
            context={"player_id": player_id, "match_id": match_id}
        )


class AvailabilityAlreadyExistsError(AvailabilityError):
    """Availability already recorded for this player and match."""
    
    def __init__(self, player_id: str, match_id: str):
        self.player_id = player_id
        self.match_id = match_id
        super().__init__(
            f"Availability already recorded for player {player_id} in match {match_id}",
            context={"player_id": player_id, "match_id": match_id}
        )


class InvalidAvailabilityStatusError(AvailabilityError):
    """Invalid availability status."""
    
    def __init__(self, status: str, valid_statuses: list[str]):
        self.status = status
        self.valid_statuses = valid_statuses
        super().__init__(
            f"Invalid availability status '{status}'. Valid statuses: {', '.join(valid_statuses)}",
            context={"status": status, "valid_statuses": valid_statuses}
        )


class AttendanceError(MatchManagementError):
    """Base exception for attendance errors."""
    pass


class AttendanceServiceUnavailableError(AttendanceError):
    """Attendance service is not available."""
    
    def __init__(self, message: str = "Attendance service unavailable"):
        super().__init__(message)


class AttendanceNotFoundError(AttendanceError):
    """Attendance record not found."""
    
    def __init__(self, player_id: str, match_id: str):
        self.player_id = player_id
        self.match_id = match_id
        super().__init__(
            f"Attendance not found for player {player_id} in match {match_id}",
            context={"player_id": player_id, "match_id": match_id}
        )


class AttendanceAlreadyRecordedError(AttendanceError):
    """Attendance already recorded for this player and match."""
    
    def __init__(self, player_id: str, match_id: str):
        self.player_id = player_id
        self.match_id = match_id
        super().__init__(
            f"Attendance already recorded for player {player_id} in match {match_id}",
            context={"player_id": player_id, "match_id": match_id}
        )


class InvalidAttendanceStatusError(AttendanceError):
    """Invalid attendance status."""
    
    def __init__(self, status: str, valid_statuses: list[str]):
        self.status = status
        self.valid_statuses = valid_statuses
        super().__init__(
            f"Invalid attendance status '{status}'. Valid statuses: {', '.join(valid_statuses)}",
            context={"status": status, "valid_statuses": valid_statuses}
        )


class SquadSelectionError(MatchManagementError):
    """Base exception for squad selection errors."""
    pass


class InsufficientPlayersError(SquadSelectionError):
    """Not enough players available for squad selection."""
    
    def __init__(self, available_count: int, required_count: int, match_id: str):
        self.available_count = available_count
        self.required_count = required_count
        self.match_id = match_id
        super().__init__(
            f"Insufficient players for match {match_id}: {available_count} available, {required_count} required",
            context={"available_count": available_count, "required_count": required_count, "match_id": match_id}
        )


class PlayerNotAvailableError(SquadSelectionError):
    """Player is not available for selection."""
    
    def __init__(self, player_id: str, match_id: str, availability_status: str):
        self.player_id = player_id
        self.match_id = match_id
        self.availability_status = availability_status
        super().__init__(
            f"Player {player_id} is not available for match {match_id} (status: {availability_status})",
            context={"player_id": player_id, "match_id": match_id, "availability_status": availability_status}
        )


class MatchStatusError(MatchManagementError):
    """Invalid match status for the requested operation."""
    
    def __init__(self, match_id: str, current_status: str, required_status: str):
        self.match_id = match_id
        self.current_status = current_status
        self.required_status = required_status
        super().__init__(
            f"Invalid match status for operation on {match_id}: current={current_status}, required={required_status}",
            context={"match_id": match_id, "current_status": current_status, "required_status": required_status}
        )


class MatchRepositoryError(MatchManagementError):
    """Base exception for match repository errors."""
    pass


class MatchRepositoryUnavailableError(MatchRepositoryError):
    """Match repository is not available."""
    
    def __init__(self, message: str = "Match repository service not available"):
        super().__init__(message)


class AvailabilityRepositoryError(MatchManagementError):
    """Base exception for availability repository errors."""
    pass


class AvailabilityRepositoryUnavailableError(AvailabilityRepositoryError):
    """Availability repository is not available."""
    
    def __init__(self, message: str = "Availability repository service not available"):
        super().__init__(message)


class AttendanceRepositoryError(MatchManagementError):
    """Base exception for attendance repository errors."""
    pass


class AttendanceRepositoryUnavailableError(AttendanceRepositoryError):
    """Attendance repository is not available."""
    
    def __init__(self, message: str = "Attendance repository service not available"):
        super().__init__(message)