#!/usr/bin/env python3
"""
Firebase Client Wrapper for KICKAI

This module provides a robust Firebase client wrapper with connection pooling,
error handling, batch operations, and performance optimization.
"""

import json
import os
import time
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import firebase_admin
from firebase_admin import credentials, firestore
from google.api_core import exceptions as google_exceptions
from google.cloud import firestore as firestore_client
from google.cloud.firestore import CollectionReference
from loguru import logger

# Local imports
from kickai.core.config import get_settings
from kickai.core.constants import FIRESTORE_COLLECTION_PREFIX
from kickai.core.exceptions import (
    ConnectionError,
    DatabaseError,
    DuplicateError,
    NotFoundError,
    create_error_context,
)
from kickai.core.firestore_constants import (
    COLLECTION_PLAYERS,
    get_collection_name,
    get_team_members_collection,
)
from kickai.features.team_administration.domain.entities.team_member import TeamMember
# Removed async_utils - using standard Python async patterns
from kickai.utils.enum_utils import serialize_enums_for_firestore


class FirebaseClient:
    """Robust Firebase client wrapper with connection pooling and error handling."""

    def __init__(self, config):
        self.config = config
        self._client: firestore_client.Union[Client, None] = None
        self._connection_pool: dict[str, Any] = {}
        self._batch_operations: List[dict[str, Any]] = []

        # Skip initialization in testing environment
        if config.firebase_project_id == "test_project" or not config.firebase_project_id:
            logger.info(
                "Test environment detected or no project ID, skipping Firebase initialization"
            )
            return

        self._initialize_client()

    def _initialize_client(self):
        """Initialize Firebase client with proper error handling."""
        try:
            # ALL business logic here
            if not firebase_admin._apps:
                import json
                import os

                logger.info("🔍 Starting Firebase client initialization...")

                # Check if Firebase app is already initialized
                try:
                    firebase_admin.get_app()
                    logger.info("✅ Using existing Firebase app")
                except ValueError:
                    logger.info("🔄 Initializing new Firebase app...")

                    # Get credentials from config object
                    creds_dict = None
                    if self.config.firebase_credentials_json:
                        logger.info("🔄 Using firebase_credentials_json from kickai.config...")
                        creds_dict = json.loads(self.config.firebase_credentials_json)
                    elif self.config.firebase_credentials_file:
                        logger.info(
                            f"🔄 Using firebase_credentials_file from config: {self.config.firebase_credentials_file} ..."
                        )
                        with open(self.config.firebase_credentials_file) as f:
                            creds_dict = json.load(f)
                    else:
                        # Fallback to environment variables for backward compatibility
                        firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
                        if firebase_creds_json:
                            logger.info(
                                "🔄 Using FIREBASE_CREDENTIALS_JSON from environment..."
                            )
                            creds_dict = json.loads(firebase_creds_json)
                        else:
                            firebase_creds_file = os.getenv("FIREBASE_CREDENTIALS_FILE")
                            if firebase_creds_file:
                                logger.info(
                                    f"🔄 Using FIREBASE_CREDENTIALS_FILE from environment: {firebase_creds_file} ..."
                                )
                                with open(firebase_creds_file) as f:
                                    creds_dict = json.load(f)
                            else:
                                raise RuntimeError(
                                    "No Firebase credentials found. Please set either firebase_credentials_json, firebase_credentials_path in config, or FIREBASE_CREDENTIALS_JSON/FIREBASE_CREDENTIALS_FILE environment variables."
                                )

                    # Log private key details for debugging
                    private_key = creds_dict.get("private_key", "")
                    logger.info(f"🔍 Private key length: {len(private_key)} characters")

                    # Create credentials
                    cred = credentials.Certificate(creds_dict)
                    logger.info("✅ Credentials created from JSON string")

                    # Initialize Firebase app
                    logger.info("🔄 Initializing Firebase app...")
                    firebase_admin.initialize_app(cred)
                    logger.info("✅ Firebase app initialized successfully")

            # Create Firestore client with error handling
            self._client = firestore.client()
            logger.info("✅ Firebase Firestore client created successfully")

        except Exception as e:
            logger.error(f"❌ Error in _initialize_client: {e}")
            raise ConnectionError(
                f"Failed to initialize Firebase client: {e!s}",
                create_error_context("firebase", error=e),
            )

    @property
    def client(self) -> firestore_client.Client:
        """Get the Firebase client instance."""
        if self._client is None:
            if self.config.firebase_project_id == "test_project":
                raise ConnectionError(
                    "Firebase client not available in test environment",
                    create_error_context("firebase_client_access"),
                )
            raise ConnectionError(
                "Firebase client not initialized", create_error_context("firebase_client_access")
            )
        return self._client

    def _get_collection(self, collection_name: str) -> CollectionReference:
        """Get a collection reference with proper prefixing."""
        # Check if collection name already has the prefix
        if collection_name.startswith(f"{FIRESTORE_COLLECTION_PREFIX}_"):
            # Already prefixed, use as-is
            full_name = collection_name
        else:
            # Not prefixed, add the prefix
            full_name = f"{FIRESTORE_COLLECTION_PREFIX}_{collection_name}"
        return self.client.collection(full_name)

    def _handle_firebase_error(self, error: Exception, operation: str, **context) -> None:
        """Handle Firebase errors and convert to KICKAI exceptions."""
        error_context = create_error_context(operation, **context)

        if isinstance(error, google_exceptions.NotFound):
            raise NotFoundError(f"Resource not found: {error!s}", error_context)
        elif isinstance(error, google_exceptions.AlreadyExists):
            raise DuplicateError(f"Resource already exists: {error!s}", error_context)
        elif isinstance(error, google_exceptions.PermissionDenied):
            raise DatabaseError(f"Permission denied: {error!s}", error_context)
        elif isinstance(error, google_exceptions.DeadlineExceeded):
            raise DatabaseError(f"Operation timeout: {error!s}", error_context)
        elif isinstance(error, google_exceptions.ResourceExhausted):
            raise DatabaseError(f"Resource exhausted: {error!s}", error_context)
        else:
            raise DatabaseError(f"Database operation failed: {error!s}", error_context)

    @asynccontextmanager
    async def transaction(self):
        """Context manager for Firebase transactions."""
        transaction = self.client.transaction()
        try:
            yield transaction
        except Exception as e:
            self._handle_firebase_error(e, "transaction")

    async def execute_batch(self, operations: List[dict[str, Any]]) -> List[Any]:
        """Execute a batch of operations."""
        if not operations:
            return []

        batch = self.client.batch()
        results = []

        try:
            for operation in operations:
                op_type = operation["type"]
                collection = operation["collection"]
                data = operation.get("data", {})

                if op_type == "create":
                    doc_ref = self._get_collection(collection).document()
                    batch.set(doc_ref, data)
                    results.append(doc_ref.id)

                elif op_type == "update":
                    doc_id = operation["document_id"]
                    doc_ref = self._get_collection(collection).document(doc_id)
                    batch.update(doc_ref, data)
                    results.append(doc_id)

                elif op_type == "delete":
                    doc_id = operation["document_id"]
                    doc_ref = self._get_collection(collection).document(doc_id)
                    batch.delete(doc_ref)
                    results.append(doc_id)

            batch.commit()
            logger.info(f"Batch operation completed: {len(operations)} operations")
            return results

        except Exception as e:
            self._handle_firebase_error(
                e, "batch_execution", additional_info={"operation_count": len(operations)}
            )
            return []  # Return empty list on error

    async def create_document(
        self, collection: str, data: dict[str, Any], document_id: Optional[str] = None
    ) -> str:
        """
        Create a new document with optional custom document ID.
        
        Args:
            collection: Collection name
            data: Document data
            document_id: Optional custom document ID
            
        Returns:
            Document ID on success, empty string on failure
        """
        try:
            # ALL business logic here
            data_serialized = serialize_enums_for_firestore(data)
            logger.info(
                f"[Firestore] Creating document in '{collection}' with data: {data_serialized}"
            )
            doc_ref = (
                self._get_collection(collection).document(document_id)
                if document_id
                else self._get_collection(collection).document()
            )
            doc_ref.set(data_serialized)
            logger.info(f"[Firestore] Document created: {doc_ref.id}")
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"❌ Error in create_document: {e}")
            self._handle_firebase_error(
                e, "create_document", additional_info={"collection": collection}
            )
            return ""

    async def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            collection: Collection name
            document_id: Document ID
            
        Returns:
            Document data or None if not found/error
        """
        try:
            # ALL business logic here
            doc_ref = self._get_collection(collection).document(document_id)
            doc = doc_ref.get()

            if doc is not None and doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            else:
                return None

        except Exception as e:
            logger.error(f"❌ Error in get_document: {e}")
            self._handle_firebase_error(
                e,
                "get_document",
                entity_id=document_id,
                additional_info={"collection": collection},
            )
            return None

    async def update_document(
        self, collection: str, document_id: str, data: dict[str, Any]
    ) -> bool:
        """
        Update an existing document.
        
        Args:
            collection: Collection name
            document_id: Document ID
            data: Update data
            
        Returns:
            True on success, False on failure
        """
        try:
            # ALL business logic here
            data_serialized = serialize_enums_for_firestore(data)
            logger.info(
                f"[Firestore] Updating document in '{collection}' with ID: {document_id}, data: {data_serialized}"
            )
            doc_ref = self._get_collection(collection).document(document_id)
            doc_ref.update(data_serialized)
            logger.info(f"[Firestore] Document updated: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in update_document: {e}")
            self._handle_firebase_error(
                e,
                "update_document",
                entity_id=document_id,
                additional_info={"collection": collection},
            )
            return False

    async def delete_document(self, collection: str, document_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            collection: Collection name
            document_id: Document ID
            
        Returns:
            True on success, False on failure
        """
        try:
            # ALL business logic here
            logger.info(f"[Firestore] Deleting document in '{collection}' with ID: {document_id}")
            doc_ref = self._get_collection(collection).document(document_id)
            doc_ref.delete()
            logger.info(f"[Firestore] Document deleted: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in delete_document: {e}")
            self._handle_firebase_error(
                e,
                "delete_document",
                entity_id=document_id,
                additional_info={"collection": collection},
            )
            return False

    async def query_documents(
        self,
        collection: str,
        filters: Optional[List[Dict[str, Any]]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query documents with filters and ordering.
        
        Args:
            collection: Collection name
            filters: List of filter dictionaries
            order_by: Field to order by
            limit: Maximum number of results
            
        Returns:
            List of document data or empty list on error
        """
        logger.debug(
            f"Query documents called with collection={collection}, filters={filters}, limit={limit}"
        )
        try:
            # ALL business logic here
            query = self._get_collection(collection)
            logger.debug(f"Got collection: {collection}")

            # Apply filters
            if filters:
                for filter_item in filters:
                    field = filter_item["field"]
                    operator = filter_item["operator"]
                    value = filter_item["value"]
                    logger.debug(f"Applying filter: {field} {operator} {value}")
                    # Use where method with keyword arguments to avoid deprecation warning
                    query = query.where(field_path=field, op_string=operator, value=value)

            # Apply ordering
            if order_by:
                logger.debug(f"Applying order_by: {order_by}")
                query = query.order_by(order_by)

            # Apply limit
            if limit:
                logger.debug(f"Applying limit: {limit}")
                query = query.limit(limit)

            # Execute query
            logger.debug("Executing query.stream()")
            docs = query.stream()
            results = []

            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                results.append(data)

            logger.debug(f"Query documents returning {len(results)} results: {results}")
            return results

        except Exception as e:
            logger.error(f"❌ Error in query_documents: {e}")
            self._handle_firebase_error(
                e,
                "query_documents",
                additional_info={"collection": collection, "filters": filters},
            )
            return []

    async def list_collections(self) -> List[str]:
        """
        List all collections in the database.
        
        Returns:
            List of collection names or empty list on error
        """
        try:
            # ALL business logic here
            collections = self.client.collections()
            return [col.id for col in collections]

        except Exception as e:
            logger.error(f"❌ Error in list_collections: {e}")
            self._handle_firebase_error(e, "list_collections")
            return []

    # Player-specific operations
    async def create_player(self, player: Any) -> str:
        """Create a new player."""
        data = serialize_enums_for_firestore(player.to_dict())
        # Use team-specific collection for player data
        from kickai.core.firestore_constants import get_team_players_collection

        collection_name = get_team_players_collection(player.team_id)
        return await self.create_document(collection_name, data, player.player_id)

    async def get_player(self, player_id: str, team_id: str) -> Optional[Any]:
        """Get a player by ID."""
        from kickai.core.firestore_constants import get_team_players_collection

        collection_name = get_team_players_collection(team_id)
        data = await self.get_document(collection_name, player_id)
        if data:
            return data
        return None

    async def update_player(
        self, player_id: str, updates: dict[str, Any], team_id: str = None
    ) -> Optional[Any]:
        """
        Update a player by ID with specific fields and return the updated player.
        
        Args:
            player_id: Player ID
            updates: Update data
            team_id: Team ID (optional)
            
        Returns:
            Updated player data or None on error
        """
        try:
            # ALL business logic here
            # Use team-specific collection if team_id is provided
            if team_id:
                from kickai.core.firestore_constants import get_team_players_collection

                collection_name = get_team_players_collection(team_id)
            else:
                collection_name = get_collection_name(COLLECTION_PLAYERS)

            # First get the current player data
            current_data = await self.get_document(collection_name, player_id)
            if not current_data:
                return None

            # Update the data with the provided updates
            current_data.update(updates)

            # Ensure enums are serialized for Firestore
            updates_serialized = serialize_enums_for_firestore(updates)
            success = await self.update_document(collection_name, player_id, updates_serialized)
            if not success:
                return None

            # Return the updated player data
            return current_data

        except Exception as e:
            logger.error(f"❌ Error in update_player: {e}")
            return None

    async def delete_player(self, player_id: str, team_id: str) -> bool:
        """Delete a player."""
        from kickai.core.firestore_constants import get_team_players_collection

        collection_name = get_team_players_collection(team_id)
        return await self.delete_document(collection_name, player_id)

    async def get_players_by_team(self, team_id: str) -> List[Any]:
        """Get all players for a team."""
        from kickai.core.firestore_constants import get_team_players_collection

        collection_name = get_team_players_collection(team_id)
        data_list = await self.query_documents(collection_name, [])
        players = []
        for data in data_list:
            if data:
                players.append(data)
            else:
                logger.warning(
                    f"[Firestore] Skipping bad player document (id={data.get('id', 'unknown')}) in get_players_by_team"
                )
        return players

    async def get_player_by_phone(self, phone: str, team_id: Optional[str] = None) -> Optional[Any]:
        """Get a player by phone number, optionally filtered by team."""
        from kickai.utils.phone_validation import get_phone_variants

        # Use team-specific collection if team_id is provided
        if team_id:
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)
        else:
            collection_name = get_collection_name(COLLECTION_PLAYERS)

        # Get all phone variants for flexible matching using enhanced validation
        phone_variants = get_phone_variants(phone)

        # Try to find player with any of the phone variants
        for variant in phone_variants:
            filters = [{"field": "phone_number", "operator": "==", "value": variant}]
            if team_id:
                filters.append({"field": "team_id", "operator": "==", "value": team_id})
            data_list = await self.query_documents(collection_name, filters, limit=1)
            for data in data_list:
                if data:
                    return data
                else:
                    logger.warning(
                        f"[Firestore] Skipping bad player document (id={data.get('id', 'unknown')}) in get_player_by_phone"
                    )
        return None

    async def get_team_players(self, team_id: str) -> List[Any]:
        """Get all players for a team."""
        return await self.get_players_by_team(team_id)

    async def get_players_by_status(self, team_id: str, status: Any) -> List[Any]:
        """Get players by onboarding status."""
        from kickai.core.firestore_constants import get_team_players_collection

        collection_name = get_team_players_collection(team_id)
        filters = [{"field": "onboarding_status", "operator": "==", "value": status.value}]
        data_list = await self.query_documents(collection_name, filters)
        players = []
        for data in data_list:
            if data:
                players.append(data)
            else:
                logger.warning(
                    f"[Firestore] Skipping bad player document (id={data.get('id', 'unknown')}) in get_players_by_status"
                )
        return players

    async def get_all_players(self, team_id: str) -> List[Any]:
        """Get all players for a team (alias for get_players_by_team)."""
        return await self.get_players_by_team(team_id)

    # Team-specific operations
    async def create_team(self, team: Any) -> str:
        """Create a new team."""
        data = team.to_dict()
        from kickai.core.firestore_constants import COLLECTION_TEAMS, get_collection_name

        collection_name = get_collection_name(COLLECTION_TEAMS)
        return await self.create_document(collection_name, data, team.id)

    async def get_team(self, team_id: str) -> Optional[Any]:
        """Get a team by ID."""
        from kickai.core.firestore_constants import COLLECTION_TEAMS, get_collection_name

        collection_name = get_collection_name(COLLECTION_TEAMS)
        data = await self.get_document(collection_name, team_id)
        if data:
            return data
        return None

    async def update_team(self, team: Any) -> bool:
        """Update a team."""
        data = team.to_dict()
        from kickai.core.firestore_constants import COLLECTION_TEAMS, get_collection_name

        collection_name = get_collection_name(COLLECTION_TEAMS)
        return await self.update_document(collection_name, team.id, data)

    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        from kickai.core.firestore_constants import COLLECTION_TEAMS, get_collection_name

        collection_name = get_collection_name(COLLECTION_TEAMS)
        return await self.delete_document(collection_name, team_id)

    async def get_team_by_name(self, name: str) -> Optional[Any]:
        """Get a team by name."""
        from kickai.core.firestore_constants import COLLECTION_TEAMS, get_collection_name

        collection_name = get_collection_name(COLLECTION_TEAMS)
        filters = [{"field": "name", "operator": "==", "value": name}]
        data_list = await self.query_documents(collection_name, filters, limit=1)
        if data_list:
            return data_list[0]
        return None

    async def get_all_teams(self, status: Optional[Any] = None) -> List[Any]:
        """Get all teams, optionally filtered by status."""
        from kickai.core.firestore_constants import COLLECTION_TEAMS, get_collection_name

        collection_name = get_collection_name(COLLECTION_TEAMS)
        filters = []
        if status:
            filters.append({"field": "status", "operator": "==", "value": status.value})
        data_list = await self.query_documents(collection_name, filters)
        return data_list

    # Match-specific operations
    async def create_match(self, match: Any) -> str:
        """Create a new match."""
        data = match.to_dict()
        from kickai.core.firestore_constants import get_team_matches_collection

        collection_name = get_team_matches_collection(match.team_id)
        return await self.create_document(collection_name, data, match.id)

    async def get_match(self, match_id: str, team_id: str) -> Optional[Any]:
        """Get a match by ID."""
        from kickai.core.firestore_constants import get_team_matches_collection

        collection_name = get_team_matches_collection(team_id)
        data = await self.get_document(collection_name, match_id)
        if data:
            return data
        return None

    async def update_match(self, match: Any) -> bool:
        """Update a match."""
        data = match.to_dict()
        from kickai.core.firestore_constants import get_team_matches_collection

        collection_name = get_team_matches_collection(match.team_id)
        return await self.update_document(collection_name, match.id, data)

    async def delete_match(self, match_id: str, team_id: str) -> bool:
        """Delete a match."""
        from kickai.core.firestore_constants import get_team_matches_collection

        collection_name = get_team_matches_collection(team_id)
        return await self.delete_document(collection_name, match_id)

    async def get_matches_by_team(self, team_id: str) -> List[Any]:
        """Get all matches for a team."""
        from kickai.core.firestore_constants import get_team_matches_collection

        collection_name = get_team_matches_collection(team_id)
        data_list = await self.query_documents(collection_name, [])
        return data_list

    async def get_team_matches(self, team_id: str) -> List[Any]:
        """Get all matches for a team."""
        return await self.get_matches_by_team(team_id)

    # Team Member methods
    async def create_team_member(self, team_member: TeamMember) -> str:
        """Create a new team member."""
        data = team_member.to_dict()
        # Use centralized collection naming
        collection_name = get_team_members_collection(team_member.team_id)
        return await self.create_document(collection_name, data)

    async def get_team_member(self, member_id: str, team_id: str) -> Optional[TeamMember]:
        """Get a team member by ID."""
        # Use centralized collection naming
        collection_name = get_team_members_collection(team_id)
        data = await self.get_document(collection_name, member_id)
        if data:
            data["id"] = member_id
            return TeamMember.from_dict(data)
        return None

    async def update_team_member(self, team_member: TeamMember) -> bool:
        """Update a team member."""
        data = team_member.to_dict()
        # Use centralized collection naming
        collection_name = get_team_members_collection(team_member.team_id)
        return await self.update_document(collection_name, team_member.id, data)

    async def delete_team_member(self, member_id: str, team_id: str) -> bool:
        """Delete a team member."""
        # Use centralized collection naming
        collection_name = get_team_members_collection(team_id)
        return await self.delete_document(collection_name, member_id)

    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        """
        Get all team members for a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of team members or empty list on error
        """
        try:
            # ALL business logic here
            # Use centralized collection naming
            collection_name = get_team_members_collection(team_id)
            filters = [{"field": "team_id", "operator": "==", "value": team_id}]
            documents = await self.query_documents(collection_name, filters)
            return [TeamMember.from_dict(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"❌ Error in get_team_members_by_team: {e}")
            return []

    async def get_team_member_by_telegram_id(
        self, telegram_id: Union[str, int], team_id: str
    ) -> Optional[TeamMember]:
        """
        Get a team member by telegram_id and team_id.
        
        Args:
            telegram_id: Telegram ID
            team_id: Team ID
            
        Returns:
            Team member or None if not found/error
        """
        try:
            # ALL business logic here
            # Normalize telegram_id to int for consistent querying
            normalized_telegram_id = int(telegram_id) if telegram_id else None
            if normalized_telegram_id is None:
                logger.warning(f"❌ Invalid telegram_id: {telegram_id}")
                return None
            
            # Use centralized collection naming
            collection_name = get_team_members_collection(team_id)
            filters = [
                {"field": "telegram_id", "operator": "==", "value": normalized_telegram_id},
                {"field": "team_id", "operator": "==", "value": team_id},
            ]
            documents = await self.query_documents(collection_name, filters)

            if documents:
                return TeamMember.from_dict(documents[0])
            return None

        except Exception as e:
            logger.error(f"❌ Error in get_team_member_by_telegram_id: {e}")
            return None

    async def get_team_members_by_role(self, team_id: str, role: str) -> List[TeamMember]:
        """Get team members by role."""
        # Use centralized collection naming
        collection_name = get_team_members_collection(team_id)
        filters = [
            {"field": "team_id", "operator": "==", "value": team_id},
            {"field": "role", "operator": "==", "value": role},
        ]
        data_list = await self.query_documents(collection_name, filters)

        team_members = []
        for data in data_list:
            if "id" in data:
                team_members.append(TeamMember.from_dict(data))

        return team_members

    async def get_leadership_members(self, team_id: str) -> List[Any]:
        """Get all leadership members (with leadership chat access)."""
        team_members = await self.get_team_members_by_team(team_id)
        return [
            member for member in team_members if member.chat_access.get("leadership_chat", False)
        ]

    async def get_player_by_telegram_id(self, telegram_id: Union[str, int], team_id: str) -> Optional[Any]:
        """
        Get a player by telegram_id and team_id efficiently.
        
        Args:
            telegram_id: Telegram ID
            team_id: Team ID
            
        Returns:
            Player data or None if not found/error
        """
        logger.debug(
            f"get_player_by_telegram_id called with telegram_id={telegram_id}, team_id={team_id}"
        )
        try:
            # ALL business logic here
            # Normalize telegram_id to handle both string and integer inputs
            from kickai.utils.telegram_id_converter import normalize_telegram_id_for_query
            normalized_telegram_id = normalize_telegram_id_for_query(telegram_id)
            
            if normalized_telegram_id is None:
                logger.warning(f"❌ Invalid telegram_id format: {telegram_id}")
                return None
                
            # Use team-specific collection
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)
            filters = [
                {"field": "telegram_id", "operator": "==", "value": normalized_telegram_id},
                {"field": "team_id", "operator": "==", "value": team_id},
            ]
            logger.debug(f"calling query_documents('{collection_name}', {filters}, limit=1)")
            data_list = await self.query_documents(collection_name, filters, limit=1)
            logger.debug(f"query_documents result: {data_list}")
            if data_list:
                player = data_list[0]
                logger.debug(f"found player data: {player}")
                return player
            logger.debug(f"No player found with telegram_id={telegram_id}, team_id={team_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in get_player_by_telegram_id: {e}")
            return None

    async def health_check(self) -> dict[str, Any]:
        """
        Perform a health check on the database connection.
        
        Returns:
            Health check status dictionary
        """
        try:
            # ALL business logic here
            start_time = time.time()

            # Test basic operations
            collections = await self.list_collections()

            duration = (time.time() - start_time) * 1000

            return {
                "status": "healthy",
                "collections_count": len(collections),
                "response_time_ms": duration,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error in health_check: {e}")
            return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}


# Global Firebase client instance
_firebase_client: Optional[FirebaseClient] = None


def get_firebase_client() -> FirebaseClient:
    """Get the global Firebase client instance."""
    global _firebase_client

    # Check if mock data store is enabled
    use_mock_datastore = os.getenv("USE_MOCK_DATASTORE", "false").lower() == "true"
    if use_mock_datastore:
        raise RuntimeError(
            "Firebase client requested but USE_MOCK_DATASTORE=true. "
            "Use MockDataStore instead for development/testing."
        )

    if _firebase_client is None:
        config = get_settings()
        _firebase_client = FirebaseClient(config)
    return _firebase_client


def initialize_firebase_client(config=None) -> FirebaseClient:
    """Initialize the global Firebase client."""
    global _firebase_client

    # Check if mock data store is enabled
    use_mock_datastore = os.getenv("USE_MOCK_DATASTORE", "false").lower() == "true"
    if use_mock_datastore:
        raise RuntimeError(
            "Firebase client initialization requested but USE_MOCK_DATASTORE=true. "
            "Use MockDataStore instead for development/testing."
        )

    if config is None:
        config = get_settings()
    _firebase_client = FirebaseClient(config)
    return _firebase_client


# Utility function to seed bot mappings for testing
async def seed_kickai_testing_bot_mapping():
    """Seed Firestore with the KickAI Testing bot mapping for local testing."""
    client = get_firebase_client()
    from kickai.features.team_administration.domain.entities.bot_mapping import BotMapping

    # SECURITY: Get bot token from environment variable
    bot_token = os.getenv("KICKAI_TESTING_BOT_TOKEN")
    if not bot_token:
        logger.error("❌ KICKAI_TESTING_BOT_TOKEN environment variable not set")
        raise ValueError("Bot token must be provided via environment variable KICKAI_TESTING_BOT_TOKEN")

    mapping = BotMapping.create(
        team_name="KAI",
        bot_username="KickAITesting_bot",
        chat_id="-4889304885",  # main chat
        bot_token=bot_token,
    )
    await client.create_document("teams", mapping.to_dict(), mapping.id)
    # Add leadership chat as a separate mapping if needed
    mapping_leadership = BotMapping.create(
        team_name="KAI",
        bot_username="KickAITesting_bot",
        chat_id="-4814449926",  # leadership chat
        bot_token=bot_token,
    )
    await client.create_document("teams", mapping_leadership.to_dict(), mapping_leadership.id)
    logger.info("✅ Seeded KickAI Testing bot mappings in Firestore.")
