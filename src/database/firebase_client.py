"""
Firebase Client Wrapper for KICKAI

This module provides a robust Firebase client wrapper with connection pooling,
error handling, batch operations, and performance optimization.
"""

import asyncio
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime
import json
import time
from contextlib import asynccontextmanager
from functools import wraps

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import DocumentReference, CollectionReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.api_core import retry, exceptions as google_exceptions
from google.cloud import firestore as firestore_client

from ..core.config import get_config, DatabaseConfig
from ..core.exceptions import (
    DatabaseError, ConnectionError, QueryError, NotFoundError, 
    DuplicateError, create_error_context
)
from ..core.logging import get_logger, performance_timer
from .models import Player, Team, Match, TeamMember, BotMapping


class FirebaseClient:
    """Robust Firebase client wrapper with connection pooling and error handling."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._client: Optional[firestore_client.Client] = None
        self._connection_pool: Dict[str, Any] = {}
        self._batch_operations: List[Dict[str, Any]] = []
        self._logger = get_logger("firebase")
        
        # Skip initialization in testing environment
        if config.project_id == "test_project":
            self._logger.info("Test environment detected, skipping Firebase initialization")
            return
            
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Firebase client with proper error handling."""
        try:
            if not firebase_admin._apps:
                import os
                import json
                
                self._logger.info("🔍 Starting Firebase client initialization...")
                
                # Check if Firebase app is already initialized
                try:
                    app = firebase_admin.get_app()
                    self._logger.info("✅ Using existing Firebase app")
                except ValueError:
                    self._logger.info("🔄 Initializing new Firebase app...")
                    
                    # Try to get credentials from environment variables
                    cred = None
                    
                    # Method 1: Plain text JSON with PEM repair (preferred)
                    firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
                    if firebase_creds_json:
                        try:
                            self._logger.info("🔄 Using FIREBASE_CREDENTIALS_JSON (plain text)...")
                            creds_dict = json.loads(firebase_creds_json)
                            
                            # Log private key details for debugging
                            private_key = creds_dict.get('private_key', '')
                            self._logger.info(f"🔍 Private key length: {len(private_key)} characters")
                            self._logger.info(f"🔍 Private key starts with: {private_key[:50]}...")
                            self._logger.info(f"🔍 Private key ends with: ...{private_key[-50:]}")
                            
                            # Validate and repair the private key
                            repaired_creds = self._extract_private_key_from_json(creds_dict)
                            
                            cred = credentials.Certificate(repaired_creds)
                            self._logger.info("✅ Credentials created from JSON string (with PEM repair)")
                        except Exception as e:
                            self._logger.warning(f"⚠️ JSON credentials failed: {e}")
                            self._logger.info("🔄 Trying alternative JSON parsing...")
                            
                            # Try alternative parsing method
                            try:
                                # Remove any potential encoding issues
                                cleaned_json = firebase_creds_json.replace('\\n', '\n').replace('\\"', '"')
                                creds_dict = json.loads(cleaned_json)
                                repaired_creds = self._extract_private_key_from_json(creds_dict)
                                cred = credentials.Certificate(repaired_creds)
                                self._logger.info("✅ Credentials created from cleaned JSON string")
                            except Exception as e2:
                                self._logger.warning(f"⚠️ Alternative JSON parsing also failed: {e2}")
                    
                    # Method 2: Individual variables with PEM repair
                    if not cred:
                        private_key = os.getenv('FIREBASE_PRIVATE_KEY')
                        client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
                        if private_key and client_email:
                            try:
                                self._logger.info("🔄 Using individual Firebase variables...")
                                
                                # Log private key details for debugging
                                self._logger.info(f"🔍 Individual private key length: {len(private_key)} characters")
                                self._logger.info(f"🔍 Individual private key starts with: {private_key[:50]}...")
                                
                                # Validate and repair the private key
                                repaired_private_key = self._validate_and_repair_pem_key(private_key)
                                
                                cred_dict = {
                                    "type": "service_account",
                                    "project_id": self.config.project_id,
                                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                                    "private_key": repaired_private_key,
                                    "client_email": client_email,
                                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                                    "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
                                    "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
                                    "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
                                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL')
                                }
                                cred = credentials.Certificate(cred_dict)
                                self._logger.info("✅ Credentials created from individual variables (with PEM repair)")
                            except Exception as e:
                                self._logger.warning(f"⚠️ Individual variables failed: {e}")
                    
                    # Method 3: Try using a temporary file approach
                    if not cred:
                        try:
                            self._logger.info("🔄 Trying temporary file approach...")
                            import tempfile
                            
                            # Get the JSON credentials
                            firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
                            if firebase_creds_json:
                                creds_dict = json.loads(firebase_creds_json)
                                repaired_creds = self._extract_private_key_from_json(creds_dict)
                                
                                # Create temporary file
                                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                                    json.dump(repaired_creds, f)
                                    temp_file_path = f.name
                                
                                try:
                                    cred = credentials.Certificate(temp_file_path)
                                    self._logger.info("✅ Credentials created from temporary file")
                                finally:
                                    # Clean up temporary file
                                    os.unlink(temp_file_path)
                                    
                        except Exception as e:
                            self._logger.warning(f"⚠️ Temporary file approach failed: {e}")
                    
                    if not cred:
                        raise RuntimeError("No valid Firebase credentials found. Please set FIREBASE_CREDENTIALS_JSON or individual Firebase variables.")
                    
                    # Initialize Firebase app
                    self._logger.info("🔄 Initializing Firebase app...")
                    firebase_admin.initialize_app(cred, {
                        'projectId': self.config.project_id
                    })
                    self._logger.info("✅ Firebase app initialized successfully")
            
            self._client = firestore.client()
            self._logger.info("✅ Firebase Firestore client created successfully")
            
        except Exception as e:
            self._logger.error("Failed to initialize Firebase client", error=e)
            raise ConnectionError(
                f"Failed to initialize Firebase client: {str(e)}",
                create_error_context("firebase", error=e)
            )
    
    @property
    def client(self) -> firestore_client.Client:
        """Get the Firebase client instance."""
        if self._client is None:
            if self.config.project_id == "test_project":
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
        full_name = f"{self.config.collection_prefix}_{collection_name}"
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
    
    @performance_timer("firebase_batch_operation")
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
            self._logger.info(f"Batch operation completed: {len(operations)} operations")
            return results
            
        except Exception as e:
            self._handle_firebase_error(e, "batch_execution", 
                                      additional_info={'operation_count': len(operations)})
    
    @performance_timer("firebase_create_document")
    async def create_document(self, collection: str, data: Dict[str, Any], 
                            document_id: Optional[str] = None) -> str:
        """Create a new document in the specified collection."""
        try:
            collection_ref = self._get_collection(collection)
            
            if document_id:
                doc_ref = collection_ref.document(document_id)
                doc_ref.set(data)
                return document_id
            else:
                doc_ref = collection_ref.add(data)[1]
                return doc_ref.id
                
        except Exception as e:
            self._handle_firebase_error(e, "create_document", 
                                      entity_id=document_id, additional_info={'collection': collection})
    
    @performance_timer("firebase_get_document")
    async def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        try:
            doc_ref = self._get_collection(collection).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            else:
                return None
                
        except Exception as e:
            self._handle_firebase_error(e, "get_document", 
                                      entity_id=document_id, additional_info={'collection': collection})
    
    @performance_timer("firebase_update_document")
    async def update_document(self, collection: str, document_id: str, 
                            data: Dict[str, Any]) -> bool:
        """Update an existing document."""
        try:
            doc_ref = self._get_collection(collection).document(document_id)
            doc_ref.update(data)
            return True
            
        except Exception as e:
            self._handle_firebase_error(e, "update_document", 
                                      entity_id=document_id, additional_info={'collection': collection})
    
    @performance_timer("firebase_delete_document")
    async def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document."""
        try:
            doc_ref = self._get_collection(collection).document(document_id)
            doc_ref.delete()
            return True
            
        except Exception as e:
            self._handle_firebase_error(e, "delete_document", 
                                      entity_id=document_id, additional_info={'collection': collection})
    
    @performance_timer("firebase_query_documents")
    async def query_documents(self, collection: str, filters: Optional[List[Dict[str, Any]]] = None,
                            order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query documents with filters and ordering."""
        try:
            query = self._get_collection(collection)
            
            # Apply filters
            if filters:
                for filter_item in filters:
                    field = filter_item['field']
                    operator = filter_item['operator']
                    value = filter_item['value']
                    query = query.where(field, operator, value)
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            # Execute query
            docs = query.stream()
            results = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
            
        except Exception as e:
            self._handle_firebase_error(e, "query_documents", 
                                      additional_info={'collection': collection, 'filters': filters})
    
    @performance_timer("firebase_list_collections")
    async def list_collections(self) -> List[str]:
        """List all collections in the database."""
        try:
            collections = self.client.collections()
            return [col.id for col in collections]
            
        except Exception as e:
            self._handle_firebase_error(e, "list_collections")
    
    # Player-specific operations
    async def create_player(self, player: Player) -> str:
        """Create a new player."""
        data = player.to_dict()
        return await self.create_document('players', data, player.id)
    
    async def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        data = await self.get_document('players', player_id)
        if data:
            return Player.from_dict(data)
        return None
    
    async def update_player(self, player: Player) -> bool:
        """Update a player."""
        data = player.to_dict()
        return await self.update_document('players', player.id, data)
    
    async def delete_player(self, player_id: str) -> bool:
        """Delete a player."""
        return await self.delete_document('players', player_id)
    
    async def get_players_by_team(self, team_id: str) -> List[Player]:
        """Get all players for a team."""
        filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
        data_list = await self.query_documents('players', filters)
        return [Player.from_dict(data) for data in data_list]
    
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[Player]:
        """Get a player by phone number and team."""
        filters = [
            {'field': 'phone', 'operator': '==', 'value': phone},
            {'field': 'team_id', 'operator': '==', 'value': team_id}
        ]
        data_list = await self.query_documents('players', filters, limit=1)
        if data_list:
            return Player.from_dict(data_list[0])
        return None
    
    # Team-specific operations
    async def create_team(self, team: Team) -> str:
        """Create a new team."""
        data = team.to_dict()
        return await self.create_document('teams', data, team.id)
    
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        data = await self.get_document('teams', team_id)
        if data:
            return Team.from_dict(data)
        return None
    
    async def update_team(self, team: Team) -> bool:
        """Update a team."""
        data = team.to_dict()
        return await self.update_document('teams', team.id, data)
    
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        return await self.delete_document('teams', team_id)
    
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Get a team by name."""
        filters = [{'field': 'name', 'operator': '==', 'value': name}]
        data_list = await self.query_documents('teams', filters, limit=1)
        if data_list:
            return Team.from_dict(data_list[0])
        return None
    
    # Bot mapping operations
    async def create_bot_mapping(self, mapping: BotMapping) -> str:
        """Create a new bot mapping."""
        data = mapping.to_dict()
        return await self.create_document('bot_mappings', data, mapping.id)
    
    async def get_bot_mapping(self, mapping_id: str) -> Optional[BotMapping]:
        """Get a bot mapping by ID."""
        data = await self.get_document('bot_mappings', mapping_id)
        if data:
            return BotMapping.from_dict(data)
        return None
    
    async def get_bot_mapping_by_team(self, team_name: str) -> Optional[BotMapping]:
        """Get a bot mapping by team name."""
        filters = [{'field': 'team_name', 'operator': '==', 'value': team_name}]
        data_list = await self.query_documents('bot_mappings', filters, limit=1)
        if data_list:
            return BotMapping.from_dict(data_list[0])
        return None
    
    async def update_bot_mapping(self, mapping: BotMapping) -> bool:
        """Update a bot mapping."""
        data = mapping.to_dict()
        return await self.update_document('bot_mappings', mapping.id, data)
    
    async def delete_bot_mapping(self, mapping_id: str) -> bool:
        """Delete a bot mapping."""
        return await self.delete_document('bot_mappings', mapping_id)
    
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
            self._logger.error("Database health check failed", error=e)
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _validate_and_repair_pem_key(self, private_key: str) -> str:
        """
        Validate and repair PEM private key format.
        
        Args:
            private_key: The private key string to validate/repair
            
        Returns:
            str: Repaired private key or original if valid
        """
        if not private_key:
            return private_key
        
        # Remove any extra whitespace and normalize line endings
        private_key = private_key.strip()
        
        # Check if it's already properly formatted
        if (private_key.startswith('-----BEGIN PRIVATE KEY-----') and 
            private_key.endswith('-----END PRIVATE KEY-----')):
            return private_key
        
        # Try to repair common issues
        lines = private_key.split('\n')
        repaired_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Remove any extra characters that might have been added
                if line.startswith('\\n'):
                    line = line[2:]
                if line.endswith('\\n'):
                    line = line[:-2]
                repaired_lines.append(line)
        
        # Reconstruct the PEM
        if len(repaired_lines) >= 3:
            header = repaired_lines[0]
            footer = repaired_lines[-1]
            key_lines = repaired_lines[1:-1]
            
            # Ensure proper header/footer
            if not header.startswith('-----BEGIN'):
                header = '-----BEGIN PRIVATE KEY-----'
            if not footer.startswith('-----END'):
                footer = '-----END PRIVATE KEY-----'
            
            # Join key lines with proper line breaks
            key_content = '\n'.join(key_lines)
            
            # Ensure proper PEM format
            repaired_key = f"{header}\n{key_content}\n{footer}"
            
            return repaired_key
        
        return private_key

    def _extract_private_key_from_json(self, creds_dict: dict) -> dict:
        """
        Extract and validate private key from credentials dictionary.
        
        Args:
            creds_dict: Firebase credentials dictionary
            
        Returns:
            dict: Credentials dict with repaired private key
        """
        private_key = creds_dict.get('private_key', '')
        if not private_key:
            return creds_dict
        
        # Validate and repair the private key
        repaired_key = self._validate_and_repair_pem_key(private_key)
        
        # Create a new dict with the repaired key
        repaired_creds = creds_dict.copy()
        repaired_creds['private_key'] = repaired_key
        
        return repaired_creds


# Global Firebase client instance
_firebase_client: Optional[FirebaseClient] = None


def get_firebase_client() -> FirebaseClient:
    """Get the global Firebase client instance."""
    global _firebase_client
    if _firebase_client is None:
        config = get_config().database
        _firebase_client = FirebaseClient(config)
    return _firebase_client


def initialize_firebase_client(config: Optional[DatabaseConfig] = None) -> FirebaseClient:
    """Initialize the global Firebase client."""
    global _firebase_client
    if config is None:
        config = get_config().database
    _firebase_client = FirebaseClient(config)
    return _firebase_client 