#!/usr/bin/env python3
"""
Firestore Training Repository

This module provides Firestore-based data access for training management.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from kickai.database.firebase_client import get_firebase_client
from kickai.features.training_management.domain.entities.training_session import TrainingSession
from kickai.features.training_management.domain.entities.training_attendance import TrainingAttendance
from kickai.core.exceptions import TrainingError, TrainingNotFoundError, create_error_context

logger = logging.getLogger(__name__)


class FirestoreTrainingRepository:
    """Firestore repository for training session and attendance data."""

    def __init__(self):
        self.firebase_client = get_firebase_client()

    def _get_training_sessions_collection(self, team_id: str) -> str:
        """Get training sessions collection name for team."""
        return f"kickai_{team_id}_training_sessions"

    def _get_training_attendance_collection(self, team_id: str) -> str:
        """Get training attendance collection name for team."""
        return f"kickai_{team_id}_training_attendance"

    async def create_training_session(self, training_session: TrainingSession) -> str:
        """Create a new training session."""
        try:
            collection_name = self._get_training_sessions_collection(training_session.team_id)
            
            # Convert to dict for storage
            session_data = training_session.to_dict()
            
            # Create document with training session ID
            await self.firebase_client.create_document(
                collection_name=collection_name,
                document_id=training_session.id,
                data=session_data
            )
            
            logger.info(f"Created training session {training_session.id} for team {training_session.team_id}")
            return training_session.id
            
        except Exception as e:
            logger.error(f"Failed to create training session: {e}")
            raise TrainingError(
                f"Failed to create training session: {e}",
                create_error_context("create_training_session", training_id=training_session.id)
            )

    async def get_training_session(self, training_id: str, team_id: str) -> Optional[TrainingSession]:
        """Get a training session by ID."""
        try:
            collection_name = self._get_training_sessions_collection(team_id)
            
            session_data = await self.firebase_client.get_document(
                collection_name=collection_name,
                document_id=training_id
            )
            
            if not session_data:
                return None
                
            return TrainingSession.from_dict(session_data)
            
        except Exception as e:
            logger.error(f"Failed to get training session {training_id}: {e}")
            raise TrainingError(
                f"Failed to get training session: {e}",
                create_error_context("get_training_session", training_id=training_id)
            )

    async def update_training_session(self, training_session: TrainingSession) -> None:
        """Update a training session."""
        try:
            collection_name = self._get_training_sessions_collection(training_session.team_id)
            
            # Update timestamp
            training_session.update(updated_at=datetime.utcnow().isoformat())
            session_data = training_session.to_dict()
            
            await self.firebase_client.update_document(
                collection_name=collection_name,
                document_id=training_session.id,
                data=session_data
            )
            
            logger.info(f"Updated training session {training_session.id}")
            
        except Exception as e:
            logger.error(f"Failed to update training session {training_session.id}: {e}")
            raise TrainingError(
                f"Failed to update training session: {e}",
                create_error_context("update_training_session", training_id=training_session.id)
            )

    async def delete_training_session(self, training_id: str, team_id: str) -> None:
        """Delete a training session."""
        try:
            collection_name = self._get_training_sessions_collection(team_id)
            
            await self.firebase_client.delete_document(
                collection_name=collection_name,
                document_id=training_id
            )
            
            logger.info(f"Deleted training session {training_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete training session {training_id}: {e}")
            raise TrainingError(
                f"Failed to delete training session: {e}",
                create_error_context("delete_training_session", training_id=training_id)
            )

    async def list_training_sessions(
        self, 
        team_id: str, 
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[TrainingSession]:
        """List training sessions with optional filtering."""
        try:
            collection_name = self._get_training_sessions_collection(team_id)
            
            # Build query filters
            filters = []
            if status:
                filters.append(("status", "==", status))
            if date_from:
                filters.append(("date", ">=", date_from))
            if date_to:
                filters.append(("date", "<=", date_to))
            
            # Get documents
            if filters:
                documents = await self.firebase_client.query_documents(
                    collection_name=collection_name,
                    filters=filters
                )
            else:
                documents = await self.firebase_client.get_all_documents(collection_name)
            
            # Convert to TrainingSession objects
            training_sessions = []
            for doc_data in documents:
                training_sessions.append(TrainingSession.from_dict(doc_data))
            
            # Sort by date
            training_sessions.sort(key=lambda x: x.date)
            
            logger.info(f"Retrieved {len(training_sessions)} training sessions for team {team_id}")
            return training_sessions
            
        except Exception as e:
            logger.error(f"Failed to list training sessions for team {team_id}: {e}")
            raise TrainingError(
                f"Failed to list training sessions: {e}",
                create_error_context("list_training_sessions", team_id=team_id)
            )

    async def create_training_attendance(self, attendance: TrainingAttendance) -> str:
        """Create a new training attendance record."""
        try:
            collection_name = self._get_training_attendance_collection(attendance.team_id)
            
            # Convert to dict for storage
            attendance_data = attendance.to_dict()
            
            # Create document with attendance ID
            await self.firebase_client.create_document(
                collection_name=collection_name,
                document_id=attendance.id,
                data=attendance_data
            )
            
            logger.info(f"Created training attendance {attendance.id} for player {attendance.player_id}")
            return attendance.id
            
        except Exception as e:
            logger.error(f"Failed to create training attendance: {e}")
            raise TrainingError(
                f"Failed to create training attendance: {e}",
                create_error_context("create_training_attendance", attendance_id=attendance.id)
            )

    async def get_training_attendance(self, attendance_id: str, team_id: str) -> Optional[TrainingAttendance]:
        """Get a training attendance record by ID."""
        try:
            collection_name = self._get_training_attendance_collection(team_id)
            
            attendance_data = await self.firebase_client.get_document(
                collection_name=collection_name,
                document_id=attendance_id
            )
            
            if not attendance_data:
                return None
                
            return TrainingAttendance.from_dict(attendance_data)
            
        except Exception as e:
            logger.error(f"Failed to get training attendance {attendance_id}: {e}")
            raise TrainingError(
                f"Failed to get training attendance: {e}",
                create_error_context("get_training_attendance", attendance_id=attendance_id)
            )

    async def update_training_attendance(self, attendance: TrainingAttendance) -> None:
        """Update a training attendance record."""
        try:
            collection_name = self._get_training_attendance_collection(attendance.team_id)
            
            # Update timestamp
            attendance.update_status(
                status=attendance.status,
                response_method=attendance.response_method,
                notes=attendance.notes
            )
            attendance_data = attendance.to_dict()
            
            await self.firebase_client.update_document(
                collection_name=collection_name,
                document_id=attendance.id,
                data=attendance_data
            )
            
            logger.info(f"Updated training attendance {attendance.id}")
            
        except Exception as e:
            logger.error(f"Failed to update training attendance {attendance.id}: {e}")
            raise TrainingError(
                f"Failed to update training attendance: {e}",
                create_error_context("update_training_attendance", attendance_id=attendance.id)
            )

    async def delete_training_attendance(self, attendance_id: str, team_id: str) -> None:
        """Delete a training attendance record."""
        try:
            collection_name = self._get_training_attendance_collection(team_id)
            
            await self.firebase_client.delete_document(
                collection_name=collection_name,
                document_id=attendance_id
            )
            
            logger.info(f"Deleted training attendance {attendance_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete training attendance {attendance_id}: {e}")
            raise TrainingError(
                f"Failed to delete training attendance: {e}",
                create_error_context("delete_training_attendance", attendance_id=attendance_id)
            )

    async def get_training_session_attendance(
        self, 
        training_session_id: str, 
        team_id: str
    ) -> List[TrainingAttendance]:
        """Get all attendance records for a training session."""
        try:
            collection_name = self._get_training_attendance_collection(team_id)
            
            # Query by training session ID
            documents = await self.firebase_client.query_documents(
                collection_name=collection_name,
                filters=[("training_session_id", "==", training_session_id)]
            )
            
            # Convert to TrainingAttendance objects
            attendance_records = []
            for doc_data in documents:
                attendance_records.append(TrainingAttendance.from_dict(doc_data))
            
            logger.info(f"Retrieved {len(attendance_records)} attendance records for training session {training_session_id}")
            return attendance_records
            
        except Exception as e:
            logger.error(f"Failed to get training session attendance {training_session_id}: {e}")
            raise TrainingError(
                f"Failed to get training session attendance: {e}",
                create_error_context("get_training_session_attendance", training_session_id=training_session_id)
            )

    async def get_player_training_attendance(
        self, 
        player_id: str, 
        team_id: str,
        training_session_id: Optional[str] = None
    ) -> List[TrainingAttendance]:
        """Get training attendance records for a player."""
        try:
            collection_name = self._get_training_attendance_collection(team_id)
            
            # Build query filters
            filters = [("player_id", "==", player_id)]
            if training_session_id:
                filters.append(("training_session_id", "==", training_session_id))
            
            # Query documents
            documents = await self.firebase_client.query_documents(
                collection_name=collection_name,
                filters=filters
            )
            
            # Convert to TrainingAttendance objects
            attendance_records = []
            for doc_data in documents:
                attendance_records.append(TrainingAttendance.from_dict(doc_data))
            
            # Sort by response timestamp
            attendance_records.sort(key=lambda x: x.response_timestamp, reverse=True)
            
            logger.info(f"Retrieved {len(attendance_records)} attendance records for player {player_id}")
            return attendance_records
            
        except Exception as e:
            logger.error(f"Failed to get player training attendance {player_id}: {e}")
            raise TrainingError(
                f"Failed to get player training attendance: {e}",
                create_error_context("get_player_training_attendance", player_id=player_id)
            ) 