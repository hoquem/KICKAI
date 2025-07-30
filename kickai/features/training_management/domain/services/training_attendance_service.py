#!/usr/bin/env python3
"""
Training Attendance Service

This module provides the service layer for training attendance management.
"""

import logging
from datetime import datetime
from typing import List, Optional

from kickai.core.exceptions import TrainingError, TrainingNotFoundError, create_error_context
from kickai.database.firebase_client import get_firebase_client
from kickai.features.training_management.domain.entities.training_attendance import (
    TrainingAttendance, TrainingAttendanceStatus, TrainingAttendanceResponseMethod, TrainingAttendanceSummary
)
from kickai.features.training_management.infrastructure.firestore_training_repository import FirestoreTrainingRepository

logger = logging.getLogger(__name__)


class TrainingAttendanceService:
    """Service for managing training attendance."""

    def __init__(self, data_store=None):
        if data_store is None:
            self._data_store = FirestoreTrainingRepository()
        else:
            self._data_store = data_store

    async def mark_training_attendance(
        self,
        player_id: str,
        training_session_id: str,
        team_id: str,
        status: TrainingAttendanceStatus,
        response_method: TrainingAttendanceResponseMethod = TrainingAttendanceResponseMethod.COMMAND,
        player_name: Optional[str] = None,
        training_session_type: Optional[str] = None,
        training_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> TrainingAttendance:
        """Marks attendance for a training session."""
        try:
            # Check if attendance record already exists
            existing_attendance = await self.get_training_attendance(
                player_id, training_session_id, team_id
            )
            
            if existing_attendance:
                # Update existing attendance
                existing_attendance.update_status(status, response_method, notes)
                await self._data_store.update_training_attendance(existing_attendance)
                logger.info(f"Training attendance updated: {existing_attendance.id}")
                return existing_attendance
            else:
                # Create new attendance record
                attendance = TrainingAttendance.create(
                    player_id=player_id,
                    training_session_id=training_session_id,
                    team_id=team_id,
                    status=status,
                    response_method=response_method,
                    player_name=player_name,
                    training_session_type=training_session_type,
                    training_date=training_date,
                    notes=notes,
                )
                
                await self._data_store.create_training_attendance(attendance)
                logger.info(f"Training attendance created: {attendance.id}")
                return attendance
        except Exception as e:
            logger.error(f"Failed to mark training attendance: {e}")
            raise TrainingError(f"Failed to mark training attendance: {e!s}", create_error_context("mark_training_attendance"))

    async def get_training_attendance(
        self, 
        player_id: str, 
        training_session_id: str, 
        team_id: str
    ) -> Optional[TrainingAttendance]:
        """Gets attendance for a specific player and training session."""
        try:
            attendance_id = f"{team_id}_{training_session_id}_{player_id}"
            attendance = await self._data_store.get_training_attendance(attendance_id)
            return attendance
        except Exception as e:
            logger.error(f"Failed to get training attendance {attendance_id}: {e}")
            raise TrainingError(f"Failed to get training attendance: {e!s}", create_error_context("get_training_attendance"))

    async def get_training_session_attendance(
        self, 
        training_session_id: str, 
        team_id: str
    ) -> List[TrainingAttendance]:
        """Gets all attendance records for a training session."""
        try:
            filters = [
                {"field": "training_session_id", "operator": "==", "value": training_session_id},
                {"field": "team_id", "operator": "==", "value": team_id}
            ]
            
            data_list = await self._data_store.query_documents("training_attendance", filters)
            attendance_list = [TrainingAttendance.from_dict(data) for data in data_list]
            
            # Sort by player name
            attendance_list.sort(key=lambda x: x.player_name or x.player_id)
            
            return attendance_list
        except Exception as e:
            logger.error(f"Failed to get training session attendance {training_session_id}: {e}")
            raise TrainingError(f"Failed to get training session attendance: {e!s}", create_error_context("get_training_session_attendance"))

    async def get_player_training_attendance(
        self, 
        player_id: str, 
        team_id: str,
        limit: Optional[int] = None
    ) -> List[TrainingAttendance]:
        """Gets training attendance history for a player."""
        try:
            filters = [
                {"field": "player_id", "operator": "==", "value": player_id},
                {"field": "team_id", "operator": "==", "value": team_id}
            ]
            
            data_list = await self._data_store.query_documents("training_attendance", filters)
            attendance_list = [TrainingAttendance.from_dict(data) for data in data_list]
            
            # Sort by date (most recent first)
            attendance_list.sort(key=lambda x: x.training_date or "", reverse=True)
            
            if limit:
                attendance_list = attendance_list[:limit]
            
            return attendance_list
        except Exception as e:
            logger.error(f"Failed to get player training attendance {player_id}: {e}")
            raise TrainingError(f"Failed to get player training attendance: {e!s}", create_error_context("get_player_training_attendance"))

    async def get_training_attendance_summary(
        self, 
        training_session_id: str, 
        team_id: str
    ) -> TrainingAttendanceSummary:
        """Gets attendance summary for a training session."""
        try:
            attendance_list = await self.get_training_session_attendance(training_session_id, team_id)
            return TrainingAttendanceSummary.from_attendance_list(training_session_id, team_id, attendance_list)
        except Exception as e:
            logger.error(f"Failed to get training attendance summary {training_session_id}: {e}")
            raise TrainingError(f"Failed to get training attendance summary: {e!s}", create_error_context("get_training_attendance_summary"))

    async def update_training_attendance(
        self, 
        attendance_id: str, 
        **updates
    ) -> TrainingAttendance:
        """Updates an existing training attendance record."""
        try:
            attendance = await self._data_store.get_training_attendance(attendance_id)
            if not attendance:
                raise TrainingNotFoundError(
                    f"Training attendance not found: {attendance_id}", create_error_context("update_training_attendance")
                )

            attendance.update_status(**updates)
            await self._data_store.update_training_attendance(attendance)
            logger.info(f"Training attendance {attendance.id} updated.")
            return attendance
        except TrainingNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update training attendance {attendance_id}: {e}")
            raise TrainingError(f"Failed to update training attendance: {e!s}", create_error_context("update_training_attendance"))

    async def delete_training_attendance(self, attendance_id: str) -> bool:
        """Deletes a training attendance record."""
        try:
            success = await self._data_store.delete_training_attendance(attendance_id)
            if not success:
                raise TrainingNotFoundError(
                    f"Training attendance not found: {attendance_id}", create_error_context("delete_training_attendance")
                )
            logger.info(f"Training attendance {attendance_id} deleted.")
            return True
        except TrainingNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete training attendance {attendance_id}: {e}")
            raise TrainingError(f"Failed to delete training attendance: {e!s}", create_error_context("delete_training_attendance"))

    async def get_players_without_response(
        self, 
        training_session_id: str, 
        team_id: str,
        active_players: List[str]
    ) -> List[str]:
        """Gets list of players who haven't responded to training session."""
        try:
            attendance_list = await self.get_training_session_attendance(training_session_id, team_id)
            responded_players = {att.player_id for att in attendance_list if att.has_responded()}
            
            return [player_id for player_id in active_players if player_id not in responded_players]
        except Exception as e:
            logger.error(f"Failed to get players without response {training_session_id}: {e}")
            raise TrainingError(f"Failed to get players without response: {e!s}", create_error_context("get_players_without_response"))

    async def get_confirmed_players(
        self, 
        training_session_id: str, 
        team_id: str
    ) -> List[TrainingAttendance]:
        """Gets list of players confirmed for training session."""
        try:
            attendance_list = await self.get_training_session_attendance(training_session_id, team_id)
            return [att for att in attendance_list if att.is_confirmed()]
        except Exception as e:
            logger.error(f"Failed to get confirmed players {training_session_id}: {e}")
            raise TrainingError(f"Failed to get confirmed players: {e!s}", create_error_context("get_confirmed_players")) 