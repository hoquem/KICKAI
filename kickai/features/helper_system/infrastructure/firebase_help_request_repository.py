"""
Firebase Help Request Repository

Firebase implementation of the HelpRequestRepositoryInterface.
"""

from datetime import datetime, timedelta

from loguru import logger

from kickai.database.interfaces import DataStoreInterface
from kickai.features.helper_system.domain.entities.help_request import HelpRequest
from kickai.features.helper_system.domain.repositories.help_request_repository_interface import (
    HelpRequestRepositoryInterface,
)
from kickai.features.helper_system.domain.value_objects.analytics_value_objects import (
    HelpRequestAnalytics,
    HelpRequestStatistics,
    PopularHelpTopic,
)


class FirebaseHelpRequestRepository(HelpRequestRepositoryInterface):
    """Firebase implementation of help request repository."""

    def __init__(self, firebase_client: DataStoreInterface):
        self.firebase_client = firebase_client

    async def create_help_request(self, help_request: HelpRequest) -> HelpRequest:
        """Create a new help request."""
        return await self.save_help_request(help_request)

    async def save_help_request(self, help_request: HelpRequest) -> HelpRequest:
        """Save a help request to Firestore."""
        try:
            collection_name = f"kickai_{help_request.team_id}_help_requests"
            data = help_request.to_dict()

            await self.firebase_client.create_document(
                collection_name, data, help_request.request_id
            )

            return help_request

        except Exception as e:
            logger.error(f"Error saving help request {help_request.request_id}: {e}")
            raise

    async def get_help_request(self, request_id: str, team_id: str) -> HelpRequest | None:
        """Get a help request by ID."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"
            data = await self.firebase_client.get_document(collection_name, request_id)

            if data:
                return HelpRequest.from_dict(data)
            return None

        except Exception as e:
            logger.error(f"Error getting help request {request_id}: {e}")
            return None

    async def update_help_request(
        self, request_id: str, team_id: str, updates: dict
    ) -> HelpRequest | None:
        """Update a help request with specific fields."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            # Get current request
            current_data = await self.firebase_client.get_document(collection_name, request_id)
            if not current_data:
                return None

            # Update with new data
            current_data.update(updates)

            # Save updated request
            await self.firebase_client.update_document(collection_name, request_id, current_data)

            return HelpRequest.from_dict(current_data)

        except Exception as e:
            logger.error(f"Error updating help request {request_id}: {e}")
            return None

    async def get_user_help_requests(
        self, user_id: str, team_id: str, limit: int = 50
    ) -> list[HelpRequest]:
        """Get help requests for a specific user."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            # Query for user's help requests
            query_filters = [("user_id", "==", user_id)]
            data_list = await self.firebase_client.query_documents(
                collection_name,
                query_filters,
                limit=limit,
                order_by="created_at",
                order_direction="desc",
            )

            return [HelpRequest.from_dict(data) for data in data_list]

        except Exception as e:
            logger.error(f"Error getting help requests for user {user_id}: {e}")
            return []

    async def get_team_help_requests(self, team_id: str, limit: int = 100) -> list[HelpRequest]:
        """Get all help requests for a team."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            data_list = await self.firebase_client.get_all_documents(
                collection_name, limit=limit, order_by="created_at", order_direction="desc"
            )

            return [HelpRequest.from_dict(data) for data in data_list]

        except Exception as e:
            logger.error(f"Error getting help requests for team {team_id}: {e}")
            return []

    async def get_recent_help_requests(self, team_id: str, days: int = 7) -> list[HelpRequest]:
        """Get recent help requests for a team."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            # Get requests from the last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            query_filters = [("created_at", ">=", cutoff_date.isoformat())]

            data_list = await self.firebase_client.query_documents(
                collection_name, query_filters, order_by="created_at", order_direction="desc"
            )

            return [HelpRequest.from_dict(data) for data in data_list]

        except Exception as e:
            logger.error(f"Error getting recent help requests for team {team_id}: {e}")
            return []

    async def get_help_requests_by_type(self, team_id: str, request_type: str) -> list[HelpRequest]:
        """Get help requests by type."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            # Query for requests with specific type
            query_filters = [("request_type", "==", request_type)]
            data_list = await self.firebase_client.query_documents(
                collection_name, query_filters, order_by="created_at", order_direction="desc"
            )

            return [HelpRequest.from_dict(data) for data in data_list]

        except Exception as e:
            logger.error(
                f"Error getting help requests by type {request_type} for team {team_id}: {e}"
            )
            return []

    async def get_unresolved_help_requests(self, team_id: str) -> list[HelpRequest]:
        """Get unresolved help requests for a team."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            # Query for unresolved requests
            query_filters = [("status", "==", "pending")]
            data_list = await self.firebase_client.query_documents(
                collection_name, query_filters, order_by="created_at", order_direction="asc"
            )

            return [HelpRequest.from_dict(data) for data in data_list]

        except Exception as e:
            logger.error(f"Error getting unresolved help requests for team {team_id}: {e}")
            return []

    async def mark_help_request_resolved(
        self, request_id: str, team_id: str, response: str, helpful: bool = None, rating: int = None
    ) -> HelpRequest | None:
        """Mark a help request as resolved."""
        try:
            updates = {
                "status": "resolved",
                "response": response,
                "resolved_at": datetime.now().isoformat(),
            }

            if helpful is not None:
                updates["helpful"] = helpful

            if rating is not None:
                updates["rating"] = rating

            return await self.update_help_request(request_id, team_id, updates)

        except Exception as e:
            logger.error(f"Error marking help request {request_id} as resolved: {e}")
            return None

    async def delete_help_request(self, request_id: str, team_id: str) -> bool:
        """Delete a help request."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"
            await self.firebase_client.delete_document(collection_name, request_id)
            return True

        except Exception as e:
            logger.error(f"Error deleting help request {request_id}: {e}")
            return False

    async def get_help_request_statistics(
        self, team_id: str, start_date: datetime = None, end_date: datetime = None
    ) -> HelpRequestStatistics:
        """Get help request statistics for a team."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            # Build query filters
            query_filters = []
            if start_date:
                query_filters.append(("created_at", ">=", start_date.isoformat()))
            if end_date:
                query_filters.append(("created_at", "<=", end_date.isoformat()))

            data_list = await self.firebase_client.query_documents(collection_name, query_filters)

            if not data_list:
                return HelpRequestStatistics(
                    total_requests=0,
                    resolved_requests=0,
                    pending_requests=0,
                    avg_resolution_time=0,
                    popular_topics=[],
                )

            # Calculate statistics
            total_requests = len(data_list)
            resolved_requests = len([r for r in data_list if r.get("status") == "resolved"])
            pending_requests = len([r for r in data_list if r.get("status") == "pending"])

            # Calculate average resolution time
            resolution_times = []
            for request in data_list:
                if request.get("status") == "resolved" and request.get("resolved_at"):
                    created_at = datetime.fromisoformat(request["created_at"])
                    resolved_at = datetime.fromisoformat(request["resolved_at"])
                    resolution_time = (resolved_at - created_at).total_seconds() / 3600  # hours
                    resolution_times.append(resolution_time)

            avg_resolution_time = (
                sum(resolution_times) / len(resolution_times) if resolution_times else 0
            )

            # Get popular topics
            topics = {}
            for request in data_list:
                topic = request.get("topic", "general")
                topics[topic] = topics.get(topic, 0) + 1

            popular_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
            popular_topics = [{"topic": topic[0], "count": topic[1]} for topic in popular_topics]

            return HelpRequestStatistics(
                total_requests=total_requests,
                resolved_requests=resolved_requests,
                pending_requests=pending_requests,
                avg_resolution_time=avg_resolution_time,
                popular_topics=popular_topics,
            )

        except Exception as e:
            logger.error(f"Error getting help request statistics for team {team_id}: {e}")
            return HelpRequestStatistics(
                total_requests=0,
                resolved_requests=0,
                pending_requests=0,
                avg_resolution_time=0,
                popular_topics=[],
            )

    async def get_popular_help_topics(
        self, team_id: str, limit: int = 10
    ) -> list[PopularHelpTopic]:
        """Get popular help topics for a team."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            data_list = await self.firebase_client.get_all_documents(collection_name)

            # Count topics
            topics = {}
            for request in data_list:
                topic = request.get("topic", "general")
                topics[topic] = topics.get(topic, 0) + 1

            # Sort by count and limit
            popular_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:limit]
            return [PopularHelpTopic(topic=topic[0], count=topic[1]) for topic in popular_topics]

        except Exception as e:
            logger.error(f"Error getting popular help topics for team {team_id}: {e}")
            return []

    async def get_pending_help_requests(self, team_id: str) -> list[HelpRequest]:
        """Get pending help requests for a team."""
        return await self.get_unresolved_help_requests(team_id)

    async def update_help_request_status(
        self, request_id: str, team_id: str, status: str, response: str = None
    ) -> HelpRequest | None:
        """Update the status of a help request."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            # Get current request
            current_data = await self.firebase_client.get_document(collection_name, request_id)
            if not current_data:
                return None

            # Update status and response
            current_data["status"] = status
            current_data["resolved_at"] = datetime.now().isoformat()

            if response:
                current_data["response"] = response

            # Save updated request
            await self.firebase_client.update_document(collection_name, request_id, current_data)

            return HelpRequest.from_dict(current_data)

        except Exception as e:
            logger.error(f"Error updating help request {request_id}: {e}")
            return None

    async def get_help_request_analytics(
        self, team_id: str, days: int = 30
    ) -> HelpRequestAnalytics:
        """Get analytics for help requests."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            # Get requests from the last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            query_filters = [("created_at", ">=", cutoff_date.isoformat())]

            data_list = await self.firebase_client.query_documents(collection_name, query_filters)

            if not data_list:
                return HelpRequestAnalytics(
                    total_requests=0,
                    pending_requests=0,
                    resolved_requests=0,
                    avg_resolution_time=0,
                    common_topics=[],
                    user_activity={},
                )

            # Calculate analytics
            total_requests = len(data_list)
            pending_requests = len([r for r in data_list if r.get("status") == "pending"])
            resolved_requests = len([r for r in data_list if r.get("status") == "resolved"])

            # Calculate average resolution time
            resolution_times = []
            for request in data_list:
                if request.get("status") == "resolved" and request.get("resolved_at"):
                    created_at = datetime.fromisoformat(request["created_at"])
                    resolved_at = datetime.fromisoformat(request["resolved_at"])
                    resolution_time = (resolved_at - created_at).total_seconds() / 3600  # hours
                    resolution_times.append(resolution_time)

            avg_resolution_time = (
                sum(resolution_times) / len(resolution_times) if resolution_times else 0
            )

            # Get common topics
            topics = {}
            for request in data_list:
                topic = request.get("topic", "general")
                topics[topic] = topics.get(topic, 0) + 1

            common_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
            common_topics = [topic[0] for topic in common_topics]

            # Get user activity
            user_activity = {}
            for request in data_list:
                user_id = request.get("user_id")
                if user_id:
                    user_activity[user_id] = user_activity.get(user_id, 0) + 1

            return HelpRequestAnalytics(
                total_requests=total_requests,
                pending_requests=pending_requests,
                resolved_requests=resolved_requests,
                avg_resolution_time=avg_resolution_time,
                common_topics=common_topics,
                user_activity=user_activity,
            )

        except Exception as e:
            logger.error(f"Error getting help request analytics for team {team_id}: {e}")
            return HelpRequestAnalytics(
                total_requests=0,
                pending_requests=0,
                resolved_requests=0,
                avg_resolution_time=0,
                common_topics=[],
                user_activity={},
            )

    async def get_recent_help_requests(self, team_id: str, hours: int = 24) -> list[HelpRequest]:
        """Get help requests from the last N hours."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            # Get requests from the last N hours
            cutoff_date = datetime.now() - timedelta(hours=hours)
            query_filters = [("created_at", ">=", cutoff_date.isoformat())]

            data_list = await self.firebase_client.query_documents(
                collection_name, query_filters, order_by="created_at", order_direction="desc"
            )

            return [HelpRequest.from_dict(data) for data in data_list]

        except Exception as e:
            logger.error(f"Error getting recent help requests for team {team_id}: {e}")
            return []

    async def get_help_requests_by_topic(self, team_id: str, topic: str) -> list[HelpRequest]:
        """Get help requests by topic."""
        try:
            collection_name = f"kickai_{team_id}_help_requests"

            # Query for requests with specific topic
            query_filters = [("topic", "==", topic)]
            data_list = await self.firebase_client.query_documents(
                collection_name, query_filters, order_by="created_at", order_direction="desc"
            )

            return [HelpRequest.from_dict(data) for data in data_list]

        except Exception as e:
            logger.error(f"Error getting help requests by topic {topic} for team {team_id}: {e}")
            return []
