"""
Firebase Client Wrapper for KICKAI

This module provides a robust Firebase client wrapper with connection pooling,
error handling, batch operations, and performance optimization.
"""

import logging
import os
import json
import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from dataclasses import asdict
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import firestore as firestore_client
from google.cloud.firestore import CollectionReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.api_core import exceptions as google_exceptions

from src.core.logging_config import get_logger, LogContext
from src.core.settings import get_settings
from src.core.constants import FIRESTORE_COLLECTION_PREFIX
from src.core.exceptions import (
    DatabaseError, ConnectionError, NotFoundError, 
    DuplicateError, create_error_context
)
from src.utils.enum_utils import serialize_enums_for_firestore
from src.utils.async_utils import async_retry, async_timeout, async_operation_context, safe_async_call
from src.features.team_administration.domain.entities.bot_mapping import BotMapping

# Get logger for this module
logger = get_logger(__name__)

class FirebaseClient:
    """Robust Firebase client wrapper with connection pooling and error handling."""
    
    def __init__(self, config):
        self.config = config
        self._client: Optional[firestore_client.Client] = None
        self._connection_pool: Dict[str, Any] = {}
        self._batch_operations: List[Dict[str, Any]] = []
        
        # Skip initialization in testing environment
        if config.firebase_project_id == "test_project":
            logger.info("Test environment detected, skipping Firebase initialization")
            return
            
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Firebase client with proper error handling."""
        try:
            if not firebase_admin._apps:
                import os
                import json
                
                logger.info("🔍 Starting Firebase client initialization...")
                
                # Check if Firebase app is already initialized
                try:
                    firebase_admin.get_app()
                    logger.info("✅ Using existing Firebase app")
                except ValueError:
                    logger.info("🔄 Initializing new Firebase app...")
                    
                    # Get credentials from FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_FILE
                    firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
                    creds_dict = None
                    if firebase_creds_json:
                        try:
                            logger.info("🔄 Using FIREBASE_CREDENTIALS_JSON...")
                            creds_dict = json.loads(firebase_creds_json)
                        except json.JSONDecodeError as e:
                            raise RuntimeError(f"Invalid JSON in FIREBASE_CREDENTIALS_JSON: {e}")
                    else:
                        firebase_creds_file = os.getenv('FIREBASE_CREDENTIALS_FILE')
                        if firebase_creds_file:
                            try:
                                logger.info(f"🔄 Using FIREBASE_CREDENTIALS_FILE: {firebase_creds_file} ...")
                                with open(firebase_creds_file, 'r') as f:
                                    creds_dict = json.load(f)
                            except Exception as e:
                                raise RuntimeError(f"Failed to load credentials from file {firebase_creds_file}: {e}")
                        else:
                            raise RuntimeError("Neither FIREBASE_CREDENTIALS_JSON nor FIREBASE_CREDENTIALS_FILE environment variable is set. Please set one with your Firebase service account credentials.")

                    # Log private key details for debugging
                    private_key = creds_dict.get('private_key', '')
                    logger.info(f"🔍 Private key length: {len(private_key)} characters")
                    
                    # Create credentials
                    try:
                        cred = credentials.Certificate(creds_dict)
                        logger.info("✅ Credentials created from JSON string")
                    except Exception as e:
                        raise RuntimeError(f"Failed to create credentials from JSON: {e}")
                    
                    # Initialize Firebase app
                    try:
                        logger.info("🔄 Initializing Firebase app...")
                        firebase_admin.initialize_app(cred)
                        logger.info("✅ Firebase app initialized successfully")
                    except Exception as e:
                        raise RuntimeError(f"Failed to initialize Firebase app: {e}")
            
            # Create Firestore client with error handling
            try:
                self._client = firestore.client()
                logger.info("✅ Firebase Firestore client created successfully")
            except Exception as e:
                if "AuthMetadataPluginCallback" in str(e):
                    logger.warning("⚠️ gRPC AuthMetadataPluginCallback error in client creation (usually harmless): {e}")
                    # Try to continue anyway
                    self._client = firestore.client()
                else:
                    raise e
            
        except Exception as e:
            logger.error("Failed to initialize Firebase client")
            raise ConnectionError(
                f"Failed to initialize Firebase client: {str(e)}",
                create_error_context("firebase", error=e)
            )
    
    @property
    def client(self) -> firestore_client.Client:
        """Get the Firebase client instance."""
        if self._client is None:
            if self.config.firebase_project_id == "test_project":
                raise ConnectionError(
                    "Firebase client not available in test environment",
                    create_error_context("firebase_client_access")
                )
            raise ConnectionError(
                "Firebase client not initialized",
                create_error_context("firebase_client_access")
            )
        return self._client
    
    def _get_collection(self, collection_name: str) -> CollectionReference:
        """Get a collection reference with proper prefixing."""
        full_name = f"{FIRESTORE_COLLECTION_PREFIX}_{collection_name}"
        return self.client.collection(full_name)
    
    def _handle_firebase_error(self, error: Exception, operation: str, **context) -> None:
        """Handle Firebase errors and convert to KICKAI exceptions."""
        error_context = create_error_context(operation, **context)
        
        if isinstance(error, google_exceptions.NotFound):
            raise NotFoundError(f"Resource not found: {str(error)}", error_context)
        elif isinstance(error, google_exceptions.AlreadyExists):
            raise DuplicateError(f"Resource already exists: {str(error)}", error_context)
        elif isinstance(error, google_exceptions.PermissionDenied):
            raise DatabaseError(f"Permission denied: {str(error)}", error_context)
        elif isinstance(error, google_exceptions.DeadlineExceeded):
            raise DatabaseError(f"Operation timeout: {str(error)}", error_context)
        elif isinstance(error, google_exceptions.ResourceExhausted):
            raise DatabaseError(f"Resource exhausted: {str(error)}", error_context)
        else:
            raise DatabaseError(f"Database operation failed: {str(error)}", error_context)
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for Firebase transactions."""
        transaction = self.client.transaction()
        try:
            yield transaction
        except Exception as e:
            self._handle_firebase_error(e, "transaction")
    
    async def execute_batch(self, operations: List[Dict[str, Any]]) -> List[Any]:
        """Execute a batch of operations."""
        if not operations:
            return []
        
        batch = self.client.batch()
        results = []
        
        try:
            for operation in operations:
                op_type = operation['type']
                collection = operation['collection']
                data = operation.get('data', {})
                
                if op_type == 'create':
                    doc_ref = self._get_collection(collection).document()
                    batch.set(doc_ref, data)
                    results.append(doc_ref.id)
                
                elif op_type == 'update':
                    doc_id = operation['document_id']
                    doc_ref = self._get_collection(collection).document(doc_id)
                    batch.update(doc_ref, data)
                    results.append(doc_id)
                
                elif op_type == 'delete':
                    doc_id = operation['document_id']
                    doc_ref = self._get_collection(collection).document(doc_id)
                    batch.delete(doc_ref)
                    results.append(doc_id)
            
            batch.commit()
            logger.info(f"Batch operation completed: {len(operations)} operations")
            return results
            
        except Exception as e:
            self._handle_firebase_error(e, "batch_execution", 
                                      additional_info={'operation_count': len(operations)})
            return []  # Return empty list on error
    
    @async_retry(max_attempts=3, delay=1.0)
    @async_timeout(30.0)
    async def create_document(self, collection: str, data: Dict[str, Any], 
                            document_id: Optional[str] = None) -> str:
        """Create a new document with optional custom document ID."""
        async with async_operation_context("create_document", collection=collection, document_id=document_id):
            try:
                data_serialized = serialize_enums_for_firestore(data)
                logger.info(f"[Firestore] Creating document in '{collection}' with data: {data_serialized}")
                doc_ref = self._get_collection(collection).document(document_id) if document_id else self._get_collection(collection).document()
                doc_ref.set(data_serialized)
                logger.info(f"[Firestore] Document created: {doc_ref.id}")
                return doc_ref.id
            except Exception as e:
                logger.error(f"[Firestore] Failed to create document in '{collection}': {e}\n{traceback.format_exc()}")
                self._handle_firebase_error(e, "create_document", additional_info={'collection': collection})
                return ""
    
    @async_retry(max_attempts=3, delay=1.0)
    @async_timeout(30.0)
    async def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        async with async_operation_context("get_document", collection=collection, document_id=document_id):
            try:
                doc_ref = self._get_collection(collection).document(document_id)
                doc = doc_ref.get()
                
                if doc is not None and doc.exists:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    return data
                else:
                    return None
                    
            except Exception as e:
                self._handle_firebase_error(e, "get_document", 
                                          entity_id=document_id, additional_info={'collection': collection})
                return None  # Return None on error
    
    @async_retry(max_attempts=3, delay=1.0)
    @async_timeout(30.0)
    async def update_document(self, collection: str, document_id: str, 
                            data: Dict[str, Any]) -> bool:
        """Update an existing document."""
        async with async_operation_context("update_document", collection=collection, document_id=document_id):
            try:
                data_serialized = serialize_enums_for_firestore(data)
                logger.info(f"[Firestore] Updating document in '{collection}' with ID: {document_id}, data: {data_serialized}")
                doc_ref = self._get_collection(collection).document(document_id)
                doc_ref.update(data_serialized)
                logger.info(f"[Firestore] Document updated: {document_id}")
                return True
            except Exception as e:
                logger.error(f"[Firestore] Failed to update document in '{collection}' (document_id={document_id}): {e}\n{traceback.format_exc()}")
                self._handle_firebase_error(e, "update_document", 
                                          entity_id=document_id, additional_info={'collection': collection})
                return False  # Return False on error
    
    async def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document."""
        try:
            logger.info(f"[Firestore] Deleting document in '{collection}' with ID: {document_id}")
            doc_ref = self._get_collection(collection).document(document_id)
            doc_ref.delete()
            logger.info(f"[Firestore] Document deleted: {document_id}")
            return True
        except Exception as e:
            logger.error(f"[Firestore] Failed to delete document in '{collection}' (document_id={document_id}): {e}\n{traceback.format_exc()}")
            self._handle_firebase_error(e, "delete_document", 
                                      entity_id=document_id, additional_info={'collection': collection})
            return False  # Return False on error
    
    @async_retry(max_attempts=3, delay=1.0)
    @async_timeout(30.0)
    async def query_documents(self, collection: str, filters: Optional[List[Dict[str, Any]]] = None,
                            order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query documents with filters and ordering."""
        logger.debug(f"Query documents called with collection={collection}, filters={filters}, limit={limit}")
        async with async_operation_context("query_documents", collection=collection, filters_count=len(filters) if filters else 0):
            try:
                query = self._get_collection(collection)
                logger.debug(f"Got collection: {collection}")
                
                # Apply filters
                if filters:
                    for filter_item in filters:
                        field = filter_item['field']
                        operator = filter_item['operator']
                        value = filter_item['value']
                        logger.debug(f"Applying filter: {field} {operator} {value}")
                        query = query.where(field, operator, value)
                
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
                    data['id'] = doc.id
                    results.append(data)
                
                logger.debug(f"Query documents returning {len(results)} results: {results}")
                return results
                
            except Exception as e:
                logger.error(f"Query documents exception: {e}")
                self._handle_firebase_error(e, "query_documents", 
                                          additional_info={'collection': collection, 'filters': filters})
                return []  # Return empty list on error
    
    async def list_collections(self) -> List[str]:
        """List all collections in the database."""
        try:
            collections = self.client.collections()
            return [col.id for col in collections]
            
        except Exception as e:
            self._handle_firebase_error(e, "list_collections")
            return []  # Return empty list on error
    
    # Player-specific operations
    async def create_player(self, player: Any) -> str:
        """Create a new player."""
        data = serialize_enums_for_firestore(player.to_dict())
        # Use player_id as the document ID for predictable lookups
        return await self.create_document('players', data, player.player_id)
    
    async def get_player(self, player_id: str) -> Optional[Any]:
        """Get a player by ID."""
        data = await self.get_document('players', player_id)
        if data:
            return Any.from_dict(data)
        return None
    
    async def update_player(self, player_id: str, updates: Dict[str, Any]) -> Optional[Any]:
        """Update a player by ID with specific fields and return the updated player."""
        try:
            # First get the current player data
            current_data = await self.get_document('players', player_id)
            if not current_data:
                return None
            
            # Update the data with the provided updates
            current_data.update(updates)
            
            # Ensure enums are serialized for Firestore
            updates_serialized = serialize_enums_for_firestore(updates)
            success = await self.update_document('players', player_id, updates_serialized)
            if not success:
                return None
            
            # Return the updated player object
            return Any.from_dict(current_data)
            
        except Exception as e:
            logger.error(f"Failed to update player {player_id}: {e}")
            return None
    
    async def delete_player(self, player_id: str) -> bool:
        """Delete a player."""
        return await self.delete_document('players', player_id)
    
    async def get_players_by_team(self, team_id: str) -> List[Any]:
        """Get all players for a team."""
        filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
        data_list = await self.query_documents('players', filters)
        players = []
        for data in data_list:
            player = Any.from_dict(data)
            if player:
                players.append(player)
            else:
                logger.warning(f"[Firestore] Skipping bad player document (id={data.get('id', 'unknown')}) in get_players_by_team")
        return players
    
    async def get_player_by_phone(self, phone: str, team_id: Optional[str] = None) -> Optional[Any]:
        """Get a player by phone number, optionally filtered by team."""
        from utils.phone_utils import get_phone_variants
        
        # Get all phone variants for flexible matching
        phone_variants = get_phone_variants(phone)
        
        # Try to find player with any of the phone variants
        for variant in phone_variants:
            filters = [{'field': 'phone', 'operator': '==', 'value': variant}]
            if team_id:
                filters.append({'field': 'team_id', 'operator': '==', 'value': team_id})
            data_list = await self.query_documents('players', filters, limit=1)
            for data in data_list:
                player = Any.from_dict(data)
                if player:
                    return player
                else:
                    logger.warning(f"[Firestore] Skipping bad player document (id={data.get('id', 'unknown')}) in get_player_by_phone")
        return None
    
    async def get_team_players(self, team_id: str) -> List[Any]:
        """Get all players for a team."""
        return await self.get_players_by_team(team_id)
    
    async def get_players_by_status(self, team_id: str, status: Any) -> List[Any]:
        """Get players by onboarding status."""
        filters = [
            {'field': 'team_id', 'operator': '==', 'value': team_id},
            {'field': 'onboarding_status', 'operator': '==', 'value': status.value}
        ]
        data_list = await self.query_documents('players', filters)
        players = []
        for data in data_list:
            player = Any.from_dict(data)
            if player:
                players.append(player)
            else:
                logger.warning(f"[Firestore] Skipping bad player document (id={data.get('id', 'unknown')}) in get_players_by_status")
        return players
    
    async def get_all_players(self, team_id: str) -> List[Any]:
        """Get all players for a team (alias for get_players_by_team)."""
        return await self.get_players_by_team(team_id)
    
    # Team-specific operations
    async def create_team(self, team: Any) -> str:
        """Create a new team."""
        data = team.to_dict()
        return await self.create_document('teams', data, team.id)
    
    async def get_team(self, team_id: str) -> Optional[Any]:
        """Get a team by ID."""
        data = await self.get_document('teams', team_id)
        if data:
            return Any.from_dict(data)
        return None
    
    async def update_team(self, team: Any) -> bool:
        """Update a team."""
        data = team.to_dict()
        return await self.update_document('teams', team.id, data)
    
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        return await self.delete_document('teams', team_id)
    
    async def get_team_by_name(self, name: str) -> Optional[Any]:
        """Get a team by name."""
        filters = [{'field': 'name', 'operator': '==', 'value': name}]
        data_list = await self.query_documents('teams', filters, limit=1)
        if data_list:
            return Any.from_dict(data_list[0])
        return None
    
    async def get_all_teams(self, status: Optional[Any] = None) -> List[Any]:
        """Get all teams, optionally filtered by status."""
        filters = []
        if status:
            filters.append({'field': 'status', 'operator': '==', 'value': status.value})
        data_list = await self.query_documents('teams', filters)
        return [Any.from_dict(data) for data in data_list]
    
    # Bot mapping operations
    async def create_bot_mapping(self, mapping: Any) -> str:
        """Create a new bot mapping."""
        data = mapping.to_dict()
        return await self.create_document('bot_mappings', data, mapping.id)
    
    async def get_bot_mapping(self, team_name: str) -> Optional[Any]:
        """Get a bot mapping by team name."""
        filters = [{'field': 'team_name', 'operator': '==', 'value': team_name}]
        data_list = await self.query_documents('bot_mappings', filters, limit=1)
        if data_list:
            return Any.from_dict(data_list[0])
        return None
    
    async def get_bot_mapping_by_username(self, bot_username: str) -> Optional[Any]:
        """Get a bot mapping by bot username."""
        filters = [{'field': 'bot_username', 'operator': '==', 'value': bot_username}]
        data_list = await self.query_documents('bot_mappings', filters, limit=1)
        if data_list:
            return Any.from_dict(data_list[0])
        return None
    
    async def get_bot_mapping_by_team(self, team_name: str) -> Optional[Any]:
        """Get a bot mapping by team name (alias for get_bot_mapping)."""
        return await self.get_bot_mapping(team_name)
    
    async def get_bot_mapping_by_team_id(self, team_id: str) -> Optional[Any]:
        """Get a bot mapping by team ID."""
        filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
        data_list = await self.query_documents('bot_mappings', filters, limit=1)
        if data_list:
            return Any.from_dict(data_list[0])
        return None
    
    async def update_bot_mapping(self, mapping: Any) -> bool:
        """Update a bot mapping."""
        data = mapping.to_dict()
        return await self.update_document('bot_mappings', mapping.id, data)
    
    async def delete_bot_mapping(self, team_name: str) -> bool:
        """Delete a bot mapping by team name."""
        filters = [{'field': 'team_name', 'operator': '==', 'value': team_name}]
        data_list = await self.query_documents('bot_mappings', filters, limit=1)
        if data_list:
            return await self.delete_document('bot_mappings', data_list[0]['id'])
        return False
    
    async def get_all_bot_mappings(self) -> List[Any]:
        """Get all bot mappings from Firestore."""
        try:
            data_list = await self.query_documents('bot_mappings')
            return [Any.from_dict(data) for data in data_list]
        except Exception as e:
            logger.error(f"Failed to fetch bot mappings: {e}")
            return []
    
    # Match-specific operations
    async def create_match(self, match: Any) -> str:
        """Create a new match."""
        data = match.to_dict()
        return await self.create_document('matches', data, match.id)
    
    async def get_match(self, match_id: str) -> Optional[Any]:
        """Get a match by ID."""
        data = await self.get_document('matches', match_id)
        if data:
            return Any.from_dict(data)
        return None
    
    async def update_match(self, match: Any) -> bool:
        """Update a match."""
        data = match.to_dict()
        return await self.update_document('matches', match.id, data)
    
    async def delete_match(self, match_id: str) -> bool:
        """Delete a match."""
        return await self.delete_document('matches', match_id)
    
    async def get_matches_by_team(self, team_id: str) -> List[Any]:
        """Get all matches for a team."""
        filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
        data_list = await self.query_documents('matches', filters)
        return [Any.from_dict(data) for data in data_list]
    
    async def get_team_matches(self, team_id: str) -> List[Any]:
        """Get all matches for a team."""
        return await self.get_matches_by_team(team_id)
    
    # Team Member methods
    async def create_team_member(self, team_member: Any) -> str:
        """Create a new team member."""
        data = team_member.to_dict()
        return await self.create_document('team_members', data)
    
    async def get_team_member(self, member_id: str) -> Optional[Any]:
        """Get a team member by ID."""
        data = await self.get_document('team_members', member_id)
        if data:
            data['id'] = member_id
            return Any.from_dict(data)
        return None
    
    async def update_team_member(self, team_member: Any) -> bool:
        """Update a team member."""
        data = team_member.to_dict()
        return await self.update_document('team_members', team_member.id, data)
    
    async def delete_team_member(self, member_id: str) -> bool:
        """Delete a team member."""
        return await self.delete_document('team_members', member_id)
    
    async def get_team_members_by_team(self, team_id: str) -> List[Any]:
        """Get all team members for a team."""
        try:
            filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
            documents = await self.query_documents('team_members', filters)
            return [Any.from_dict(doc) for doc in documents]
        except Exception:
            logger.error("Error getting team members by team")
            return []  # Return empty list on error
    
    async def get_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[Any]:
        """Get a team member by telegram_id and team_id."""
        try:
            filters = [
                {'field': 'telegram_id', 'operator': '==', 'value': telegram_id},
                {'field': 'team_id', 'operator': '==', 'value': team_id}
            ]
            documents = await self.query_documents('team_members', filters)
            
            if documents:
                return Any.from_dict(documents[0])
            return None
            
        except Exception:
            logger.error("Error getting team member by telegram_id")
    
    async def get_team_members_by_role(self, team_id: str, role: str) -> List[Any]:
        """Get team members by role."""
        filters = [
            {'field': 'team_id', 'operator': '==', 'value': team_id},
            {'field': 'role', 'operator': '==', 'value': role}
        ]
        data_list = await self.query_documents('team_members', filters)
        
        team_members = []
        for data in data_list:
            if 'id' in data:
                team_members.append(Any.from_dict(data))
        
        return team_members
    
    async def get_leadership_members(self, team_id: str) -> List[Any]:
        """Get all leadership members (with leadership chat access)."""
        team_members = await self.get_team_members_by_team(team_id)
        return [member for member in team_members 
                if member.chat_access.get('leadership_chat', False)]
    
    async def get_player_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[Any]:
        """Get a player by telegram_id and team_id efficiently."""
        logger.debug(f"get_player_by_telegram_id called with telegram_id={telegram_id}, team_id={team_id}")
        try:
            filters = [
                {'field': 'telegram_id', 'operator': '==', 'value': telegram_id},
                {'field': 'team_id', 'operator': '==', 'value': team_id}
            ]
            logger.debug(f"calling query_documents('players', {filters}, limit=1)")
            data_list = await self.query_documents('players', filters, limit=1)
            logger.debug(f"query_documents result: {data_list}")
            if data_list:
                player = Any.from_dict(data_list[0])
                logger.debug(f"created Player object: {player}")
                return player
            logger.debug(f"No player found with telegram_id={telegram_id}, team_id={team_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting player by telegram_id: {e}")
            return None
    
    # Health check
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the database connection."""
        try:
            start_time = time.time()
            
            # Test basic operations
            collections = await self.list_collections()
            
            duration = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy',
                'collections_count': len(collections),
                'response_time_ms': duration,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Database health check failed")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Global Firebase client instance
_firebase_client: Optional[FirebaseClient] = None


def get_firebase_client() -> FirebaseClient:
    """Get the global Firebase client instance."""
    global _firebase_client
    if _firebase_client is None:
        config = get_settings()
        _firebase_client = FirebaseClient(config)
    return _firebase_client


def initialize_firebase_client(config=None) -> FirebaseClient:
    """Initialize the global Firebase client."""
    global _firebase_client
    if config is None:
        config = get_settings()
    _firebase_client = FirebaseClient(config)
    return _firebase_client 

# Utility function to seed bot mappings for testing
import asyncio
async def seed_kickai_testing_bot_mapping():
    """Seed Firestore with the KickAI Testing bot mapping for local testing."""
    client = get_firebase_client()
    from features.team_administration.domain.entities.bot_mapping import BotMapping
    mapping = BotMapping.create(
        team_name="KAI",
        bot_username="KickAITesting_bot",
        chat_id="-4889304885",  # main chat
        bot_token="7693359073:AAEnLqhdbCOfnf0RDfjn71z8GLRooNKNYsM"
    )
    await client.create_bot_mapping(mapping)
    # Add leadership chat as a separate mapping if needed
    mapping_leadership = BotMapping.create(
        team_name="KAI",
        bot_username="KickAITesting_bot",
        chat_id="-4814449926",  # leadership chat
        bot_token="7693359073:AAEnLqhdbCOfnf0RDfjn71z8GLRooNKNYsM"
    )
    await client.create_bot_mapping(mapping_leadership)
    logger.info("✅ Seeded KickAI Testing bot mappings in Firestore.") 