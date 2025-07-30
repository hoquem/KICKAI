"""
Firebase Learning Profile Repository

Firebase implementation of the LearningProfileRepositoryInterface.
"""

from datetime import datetime, timedelta
from typing import Any

from loguru import logger

from kickai.database.interfaces import DataStoreInterface
from kickai.features.helper_system.domain.entities.help_request import HelpRequest
from kickai.features.helper_system.domain.entities.learning_profile import LearningProfile
from kickai.features.helper_system.domain.repositories.learning_profile_repository_interface import (
    LearningProfileRepositoryInterface,
)


class FirebaseLearningProfileRepository(LearningProfileRepositoryInterface):
    """Firebase implementation of learning profile repository."""

    def __init__(self, firebase_client: DataStoreInterface):
        self.firebase_client = firebase_client

    async def get_profile(self, user_id: str, team_id: str) -> LearningProfile | None:
        """Get a user's learning profile from Firestore."""
        try:
            collection_name = f"kickai_{team_id}_learning_profiles"
            data = await self.firebase_client.get_document(collection_name, user_id)

            if data:
                return LearningProfile.from_dict(data)
            return None

        except Exception as e:
            logger.error(f"Error getting learning profile for user {user_id}: {e}")
            return None

    async def save_profile(self, profile: LearningProfile) -> LearningProfile:
        """Save a learning profile to Firestore."""
        try:
            collection_name = f"kickai_{profile.team_id}_learning_profiles"
            data = profile.to_dict()

            await self.firebase_client.create_document(collection_name, data, profile.user_id)

            return profile

        except Exception as e:
            logger.error(f"Error saving learning profile for user {profile.user_id}: {e}")
            raise

    async def update_profile(
        self, user_id: str, team_id: str, updates: dict[str, Any]
    ) -> LearningProfile | None:
        """Update a learning profile with specific fields."""
        try:
            collection_name = f"kickai_{team_id}_learning_profiles"

            # Get current profile
            current_data = await self.firebase_client.get_document(collection_name, user_id)
            if not current_data:
                return None

            # Update with new data
            current_data.update(updates)

            # Save updated profile
            await self.firebase_client.update_document(collection_name, user_id, current_data)

            return LearningProfile.from_dict(current_data)

        except Exception as e:
            logger.error(f"Error updating learning profile for user {user_id}: {e}")
            return None

    async def update_command_usage(self, user_id: str, team_id: str, command: str) -> None:
        """Update command usage statistics for a user."""
        try:
            collection_name = f"kickai_{team_id}_learning_profiles"

            # Get current profile
            current_data = await self.firebase_client.get_document(collection_name, user_id)
            if not current_data:
                # Create new profile if it doesn't exist
                profile = LearningProfile(user_id=user_id, team_id=team_id)
                profile.update_command_usage(command)
                await self.save_profile(profile)
                return

            # Update command usage
            commands_used = current_data.get("commands_used", {})
            commands_used[command] = commands_used.get(command, 0) + 1
            current_data["commands_used"] = commands_used

            # Update last active
            current_data["last_active"] = datetime.now().isoformat()

            # Update progress metrics
            progress_metrics = current_data.get("progress_metrics", {})
            progress_metrics["total_commands_used"] = (
                progress_metrics.get("total_commands_used", 0) + 1
            )
            progress_metrics["unique_commands_used"] = len(commands_used)
            progress_metrics["last_command_used"] = command

            # Recalculate learning velocity
            registration_date = datetime.fromisoformat(
                current_data.get("registration_date", datetime.now().isoformat())
            )
            days_since_reg = (datetime.now() - registration_date).days
            if days_since_reg > 0:
                progress_metrics["learning_velocity"] = (
                    progress_metrics["total_commands_used"] / days_since_reg
                )

            current_data["progress_metrics"] = progress_metrics

            # Save updated profile
            await self.firebase_client.update_document(collection_name, user_id, current_data)

        except Exception as e:
            logger.error(f"Error updating command usage for user {user_id}: {e}")

    async def add_help_request(self, user_id: str, team_id: str, help_request: HelpRequest) -> None:
        """Add a help request to a user's profile."""
        try:
            collection_name = f"kickai_{team_id}_learning_profiles"

            # Get current profile
            current_data = await self.firebase_client.get_document(collection_name, user_id)
            if not current_data:
                # Create new profile if it doesn't exist
                profile = LearningProfile(user_id=user_id, team_id=team_id)
                profile.add_help_request(help_request)
                await self.save_profile(profile)
                return

            # Add help request
            help_requests = current_data.get("help_requests", [])
            help_requests.append(help_request.to_dict())
            current_data["help_requests"] = help_requests

            # Update last active
            current_data["last_active"] = datetime.now().isoformat()

            # Update progress metrics
            progress_metrics = current_data.get("progress_metrics", {})
            progress_metrics["help_requests_count"] = len(help_requests)
            progress_metrics["last_help_request"] = help_request.request_type
            current_data["progress_metrics"] = progress_metrics

            # Save updated profile
            await self.firebase_client.update_document(collection_name, user_id, current_data)

        except Exception as e:
            logger.error(f"Error adding help request for user {user_id}: {e}")

    async def get_team_profiles(self, team_id: str) -> list[LearningProfile]:
        """Get all learning profiles for a team."""
        try:
            collection_name = f"kickai_{team_id}_learning_profiles"
            documents = await self.firebase_client.query_documents(collection_name)

            profiles = []
            for doc in documents:
                try:
                    profile = LearningProfile.from_dict(doc)
                    profiles.append(profile)
                except Exception as e:
                    logger.error(f"Error parsing profile document: {e}")
                    continue

            return profiles

        except Exception as e:
            logger.error(f"Error getting team profiles for team {team_id}: {e}")
            return []

    async def get_active_profiles(
        self, team_id: str, days_threshold: int = 7
    ) -> list[LearningProfile]:
        """Get active learning profiles for a team."""
        try:
            all_profiles = await self.get_team_profiles(team_id)
            cutoff_date = datetime.now() - timedelta(days=days_threshold)

            active_profiles = []
            for profile in all_profiles:
                if profile.last_active >= cutoff_date:
                    active_profiles.append(profile)

            return active_profiles

        except Exception as e:
            logger.error(f"Error getting active profiles for team {team_id}: {e}")
            return []

    async def delete_profile(self, user_id: str, team_id: str) -> bool:
        """Delete a learning profile."""
        try:
            collection_name = f"kickai_{team_id}_learning_profiles"
            await self.firebase_client.delete_document(collection_name, user_id)
            return True

        except Exception as e:
            logger.error(f"Error deleting learning profile for user {user_id}: {e}")
            return False

    async def get_profiles_by_experience_level(
        self, team_id: str, level: str
    ) -> list[LearningProfile]:
        """Get profiles by experience level."""
        try:
            all_profiles = await self.get_team_profiles(team_id)

            filtered_profiles = []
            for profile in all_profiles:
                if profile.experience_level == level:
                    filtered_profiles.append(profile)

            return filtered_profiles

        except Exception as e:
            logger.error(f"Error getting profiles by experience level for team {team_id}: {e}")
            return []

    async def get_most_active_users(self, team_id: str, limit: int = 10) -> list[LearningProfile]:
        """Get the most active users in a team."""
        try:
            all_profiles = await self.get_team_profiles(team_id)

            # Sort by total commands used (descending)
            sorted_profiles = sorted(
                all_profiles, key=lambda p: p.progress_metrics.total_commands_used, reverse=True
            )

            return sorted_profiles[:limit]

        except Exception as e:
            logger.error(f"Error getting most active users for team {team_id}: {e}")
            return []
