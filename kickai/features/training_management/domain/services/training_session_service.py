#!/usr/bin/env python3
"""
Training Session Service

This module provides the service layer for training session management.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from kickai.core.exceptions import TrainingError, TrainingNotFoundError, create_error_context
from kickai.database.firebase_client import get_firebase_client
from kickai.features.training_management.domain.entities.training_session import (
    TrainingSession, TrainingSessionStatus, TrainingSessionType
)
from kickai.utils.football_id_generator import generate_football_training_id
from kickai.features.training_management.infrastructure.firestore_training_repository import FirestoreTrainingRepository

logger = logging.getLogger(__name__)


class TrainingSessionService:
    """Service for managing training sessions."""

    def __init__(self, data_store=None):
        if data_store is None:
            self._data_store = FirestoreTrainingRepository()
        else:
            self._data_store = data_store

    async def create_training_session(
        self,
        team_id: str,
        session_type: TrainingSessionType,
        date: datetime,
        start_time: str,
        duration_minutes: int,
        location: str,
        focus_areas: List[str],
        max_participants: Optional[int] = None,
        coach_notes: Optional[str] = None,
    ) -> TrainingSession:
        """Creates a new training session."""
        try:
            # Generate football-friendly training session ID
            training_date_str = date.strftime("%Y-%m-%d")
            session_type_str = session_type.value.replace("_", "").upper()
            
            training_id = generate_football_training_id(
                team_id, session_type_str, training_date_str, start_time
            )

            training_session = TrainingSession.create(
                team_id=team_id,
                session_type=session_type,
                date=date,
                start_time=start_time,
                duration_minutes=duration_minutes,
                location=location,
                focus_areas=focus_areas,
                max_participants=max_participants,
                coach_notes=coach_notes,
            )
            training_session.id = training_id
            
            await self._data_store.create_training_session(training_session)
            logger.info(f"Training session created: {training_session.id}")
            return training_session
        except Exception as e:
            logger.error(f"Failed to create training session: {e}")
            raise TrainingError(f"Failed to create training session: {e!s}", create_error_context("create_training_session"))

    async def get_training_session(self, training_session_id: str, team_id: str) -> Optional[TrainingSession]:
        """Retrieves a training session by its ID."""
        try:
            training_session = await self._data_store.get_training_session(training_session_id, team_id)
            return training_session
        except Exception as e:
            logger.error(f"Failed to get training session {training_session_id}: {e}")
            raise TrainingError(f"Failed to get training session: {e!s}", create_error_context("get_training_session"))

    async def update_training_session(self, training_session_id: str, team_id: str, **updates) -> TrainingSession:
        """Updates an existing training session."""
        try:
            training_session = await self.get_training_session(training_session_id, team_id)
            if not training_session:
                raise TrainingNotFoundError(
                    f"Training session not found: {training_session_id}", create_error_context("update_training_session")
                )

            training_session.update(**updates)
            await self._data_store.update_training_session(training_session)
            logger.info(f"Training session {training_session.id} updated.")
            return training_session
        except TrainingNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update training session {training_session_id}: {e}")
            raise TrainingError(f"Failed to update training session: {e!s}", create_error_context("update_training_session"))

    async def delete_training_session(self, training_session_id: str) -> bool:
        """Deletes a training session."""
        try:
            success = await self._data_store.delete_training_session(training_session_id)
            if not success:
                raise TrainingNotFoundError(
                    f"Training session not found: {training_session_id}", create_error_context("delete_training_session")
                )
            logger.info(f"Training session {training_session_id} deleted.")
            return True
        except TrainingNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete training session {training_session_id}: {e}")
            raise TrainingError(f"Failed to delete training session: {e!s}", create_error_context("delete_training_session"))

    async def list_training_sessions(
        self, 
        team_id: str, 
        status: Optional[TrainingSessionStatus] = None,
        upcoming_only: bool = True
    ) -> List[TrainingSession]:
        """Lists training sessions for a team, with optional filters."""
        try:
            filters = [{"field": "team_id", "operator": "==", "value": team_id}]
            if status:
                filters.append({"field": "status", "operator": "==", "value": status.value})

            data_list = await self._data_store.query_documents("training_sessions", filters)
            training_sessions = [TrainingSession.from_dict(data) for data in data_list]
            
            # Filter for upcoming sessions if requested
            if upcoming_only:
                training_sessions = [ts for ts in training_sessions if ts.is_upcoming()]
            
            # Sort by date and time
            training_sessions.sort(key=lambda x: (x.date, x.start_time))
            
            return training_sessions
        except Exception as e:
            logger.error(f"Failed to list training sessions for team {team_id}: {e}")
            raise TrainingError(f"Failed to list training sessions: {e!s}", create_error_context("list_training_sessions"))

    async def get_todays_training_sessions(self, team_id: str) -> List[TrainingSession]:
        """Gets today's training sessions for a team."""
        try:
            all_sessions = await self.list_training_sessions(team_id, upcoming_only=False)
            return [ts for ts in all_sessions if ts.is_today()]
        except Exception as e:
            logger.error(f"Failed to get today's training sessions for team {team_id}: {e}")
            raise TrainingError(f"Failed to get today's training sessions: {e!s}", create_error_context("get_todays_training_sessions"))

    async def get_weekly_schedule(self, team_id: str, week_start: datetime) -> List[TrainingSession]:
        """Gets the weekly training schedule for a team."""
        try:
            week_end = week_start + timedelta(days=7)
            filters = [
                {"field": "team_id", "operator": "==", "value": team_id},
                {"field": "date", "operator": ">=", "value": week_start.isoformat()},
                {"field": "date", "operator": "<", "value": week_end.isoformat()}
            ]
            
            data_list = await self._data_store.query_documents("training_sessions", filters)
            training_sessions = [TrainingSession.from_dict(data) for data in data_list]
            
            # Sort by date and time
            training_sessions.sort(key=lambda x: (x.date, x.start_time))
            
            return training_sessions
        except Exception as e:
            logger.error(f"Failed to get weekly schedule for team {team_id}: {e}")
            raise TrainingError(f"Failed to get weekly schedule: {e!s}", create_error_context("get_weekly_schedule"))

    async def cancel_training_session(self, training_session_id: str, reason: Optional[str] = None) -> TrainingSession:
        """Cancels a training session."""
        try:
            updates = {"status": TrainingSessionStatus.CANCELLED.value}
            if reason:
                updates["coach_notes"] = f"Cancelled: {reason}"
            
            return await self.update_training_session(training_session_id, **updates)
        except Exception as e:
            logger.error(f"Failed to cancel training session {training_session_id}: {e}")
            raise TrainingError(f"Failed to cancel training session: {e!s}", create_error_context("cancel_training_session"))

    async def postpone_training_session(
        self, 
        training_session_id: str, 
        new_date: datetime, 
        new_start_time: str,
        reason: Optional[str] = None
    ) -> TrainingSession:
        """Postpones a training session to a new date and time."""
        try:
            updates = {
                "status": TrainingSessionStatus.POSTPONED.value,
                "date": new_date.isoformat(),
                "start_time": new_start_time
            }
            if reason:
                updates["coach_notes"] = f"Postponed: {reason}"
            
            return await self.update_training_session(training_session_id, **updates)
        except Exception as e:
            logger.error(f"Failed to postpone training session {training_session_id}: {e}")
            raise TrainingError(f"Failed to postpone training session: {e!s}", create_error_context("postpone_training_session")) 