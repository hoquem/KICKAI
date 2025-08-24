#!/usr/bin/env python3
"""
Attendance Service Interface

Defines the contract for attendance management services.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from kickai.features.attendance_management.domain.entities.attendance import Attendance


class IAttendanceService(ABC):
    """Interface for attendance service operations."""

    @abstractmethod
    async def record_attendance(
        self,
        player_id: str,
        match_id: str,
        attendance_status: str,
        arrival_time: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> Attendance:
        """
        Record player attendance for a match.
        
        Args:
            player_id: Player identifier
            match_id: Match identifier  
            attendance_status: Present/absent/late/injured
            arrival_time: When player arrived (if present)
            notes: Additional notes
            
        Returns:
            Created attendance record
        """
        pass

    @abstractmethod
    async def update_attendance(
        self,
        attendance_id: str,
        attendance_status: str,
        notes: Optional[str] = None
    ) -> Optional[Attendance]:
        """
        Update an existing attendance record.
        
        Args:
            attendance_id: Attendance record identifier
            attendance_status: New attendance status
            notes: Updated notes
            
        Returns:
            Updated attendance record if found
        """
        pass

    @abstractmethod
    async def get_player_attendance(
        self,
        player_id: str,
        match_id: str
    ) -> Optional[Attendance]:
        """
        Get player's attendance for a specific match.
        
        Args:
            player_id: Player identifier
            match_id: Match identifier
            
        Returns:
            Attendance record if found
        """
        pass

    @abstractmethod
    async def get_match_attendance(
        self,
        match_id: str
    ) -> List[Attendance]:
        """
        Get all attendance records for a match.
        
        Args:
            match_id: Match identifier
            
        Returns:
            List of attendance records
        """
        pass

    @abstractmethod
    async def get_player_attendance_history(
        self,
        player_id: str,
        limit: int = 50
    ) -> List[Attendance]:
        """
        Get attendance history for a player.
        
        Args:
            player_id: Player identifier
            limit: Maximum records to return
            
        Returns:
            List of attendance records
        """
        pass

    @abstractmethod
    async def get_attendance_statistics(
        self,
        team_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get attendance statistics for a team.
        
        Args:
            team_id: Team identifier
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Dictionary with attendance statistics
        """
        pass

    @abstractmethod
    async def mark_bulk_attendance(
        self,
        match_id: str,
        attendance_records: List[Dict[str, Any]]
    ) -> List[Attendance]:
        """
        Record attendance for multiple players at once.
        
        Args:
            match_id: Match identifier
            attendance_records: List of attendance data
            
        Returns:
            List of created attendance records
        """
        pass