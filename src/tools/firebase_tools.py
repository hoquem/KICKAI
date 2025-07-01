#!/usr/bin/env python3
"""
Firebase Tools for KICKAI
Provides Firebase Firestore database functionality to replace Supabase.
Supports all existing database operations with Firebase Firestore.
"""

import os
import logging
import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from dotenv import load_dotenv
import json
import tempfile
import base64

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import BaseTool from LangChain (compatible with CrewAI 0.28.8)
try:
    from langchain.tools import BaseTool
    CREWAI_AVAILABLE = True
    logger.info("✅ LangChain BaseTool imported successfully")
except ImportError as e:
    logger.error(f"Failed to import LangChain BaseTool: {e}")
    # Fallback base class when langchain is not available
    class BaseTool:
        def __init__(self, name: str, description: str):
            self.name = name
            self.description = description
            self.team_id: Optional[str] = None  # Will be set by subclasses
        def _run(self, *args, **kwargs):
            raise NotImplementedError("BaseTool _run method must be implemented")
    CREWAI_AVAILABLE = False
    logger.warning("⚠️ Using fallback BaseTool class")

# Import MatchIDGenerator for human-readable fixture IDs
try:
    from src.telegram.telegram_command_handler import MatchIDGenerator
    match_id_generator = MatchIDGenerator()
    logger.info("✅ MatchIDGenerator imported successfully")
except ImportError as e:
    logger.error(f"Failed to import MatchIDGenerator: {e}")
    match_id_generator = None

# --- Firebase Client Factory ---
def get_firebase_client():
    """
    Get Firebase client with robust error handling.
    Creates credentials file at runtime to avoid environment variable size limits.
    Supports base64 encoded private keys for Railway compatibility.
    Returns:
        firebase_admin.firestore.Client: Firebase Firestore client instance
    Raises:
        ValueError: If Firebase credentials are not available
        Exception: If client creation fails
    """
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        import tempfile
        
        # Check if Firebase app is already initialized
        try:
            app = firebase_admin.get_app()
            logger.info("✅ Using existing Firebase app")
        except ValueError:
            # Initialize Firebase app
            logger.info("🔧 Initializing Firebase app...")

            # Try to create credentials from environment variables
            project_id = os.getenv('FIREBASE_PROJECT_ID')
            client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
            
            # Try to get private key (support both regular and base64 encoded)
            private_key = None
            private_key_b64 = os.getenv('FIREBASE_PRIVATE_KEY_B64')
            if private_key_b64:
                try:
                    # Decode base64 private key
                    private_key = base64.b64decode(private_key_b64).decode('utf-8')
                    logger.info("🔑 Using base64 encoded private key")
                except Exception as e:
                    logger.error(f"❌ Failed to decode base64 private key: {e}")
            else:
                # Try regular private key
                private_key = os.getenv('FIREBASE_PRIVATE_KEY')
                if private_key:
                    logger.info("🔑 Using regular private key")
            
            if project_id and private_key and client_email:
                logger.info("🔑 Creating Firebase credentials from environment variables")
                try:
                    # Build service account info
                    service_account_info = {
                        "type": "service_account",
                        "project_id": project_id,
                        "private_key": private_key.replace('\\n', '\n'),
                        "client_email": client_email,
                        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
                        "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
                        "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                        "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                        "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                        "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL', '')
                    }
                    
                    # Create a temporary credentials file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                        json.dump(service_account_info, temp_file, indent=2)
                        temp_file_path = temp_file.name
                    
                    logger.info(f"📁 Created temporary credentials file: {temp_file_path}")
                    
                    # Use the temporary file for credentials
                    cred = credentials.Certificate(temp_file_path)
                    app = firebase_admin.initialize_app(cred)
                    logger.info("✅ Firebase app initialized with environment variables")
                    
                    # Clean up the temporary file
                    try:
                        os.unlink(temp_file_path)
                        logger.info("🧹 Cleaned up temporary credentials file")
                    except:
                        pass  # Ignore cleanup errors
                        
                except Exception as cred_error:
                    logger.error(f"❌ Failed to create Firebase credentials from env vars: {cred_error}")
                    raise
            else:
                # Try FIREBASE_CREDENTIALS env var (fallback)
                firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS')
                if firebase_creds_json:
                    logger.info("🔑 Using FIREBASE_CREDENTIALS environment variable")
                    try:
                        # Parse the JSON and create a temporary file to avoid corruption issues
                        creds_dict = json.loads(firebase_creds_json)
                        
                        # Create a temporary file with the credentials
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                            json.dump(creds_dict, temp_file, indent=2)
                            temp_file_path = temp_file.name
                        
                        logger.info(f"📁 Created temporary credentials file: {temp_file_path}")
                        
                        # Use the temporary file for credentials
                        cred = credentials.Certificate(temp_file_path)
                        app = firebase_admin.initialize_app(cred)
                        logger.info("✅ Firebase app initialized with FIREBASE_CREDENTIALS env var")
                        
                        # Clean up the temporary file
                        try:
                            os.unlink(temp_file_path)
                            logger.info("🧹 Cleaned up temporary credentials file")
                        except:
                            pass  # Ignore cleanup errors
                            
                    except Exception as cred_error:
                        logger.error(f"❌ Failed to create Firebase credentials from FIREBASE_CREDENTIALS: {cred_error}")
                        raise
                else:
                    # Try firebase_settings.json file
                    project_root = os.getcwd()
                    service_account_path = os.path.join(project_root, 'firebase_settings.json')
                    logger.info(f"🔍 Looking for Firebase settings file at: {service_account_path}")
                    if os.path.exists(service_account_path):
                        logger.info(f"📁 Using Firebase service account file: {service_account_path}")
                        cred = credentials.Certificate(service_account_path)
                        app = firebase_admin.initialize_app(cred)
                        logger.info("✅ Firebase app initialized with service account file")
                    else:
                        # Fall back to legacy env vars (not recommended)
                        logger.info("📝 Using Firebase legacy environment variables (no other options found)")
                        project_id = os.getenv('FIREBASE_PROJECT_ID')
                        private_key = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
                        client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
                        logger.info(f"🔍 Checking Firebase environment variables:")
                        logger.info(f"   Project ID: {'✅ Set' if project_id else '❌ Missing'}")
                        logger.info(f"   Private Key: {'✅ Set' if private_key else '❌ Missing'}")
                        logger.info(f"   Client Email: {'✅ Set' if client_email else '❌ Missing'}")
                        if not project_id:
                            raise ValueError("Missing FIREBASE_PROJECT_ID environment variable")
                        if not private_key:
                            raise ValueError("Missing FIREBASE_PRIVATE_KEY environment variable")
                        if not client_email:
                            raise ValueError("Missing FIREBASE_CLIENT_EMAIL environment variable")
                        service_account_info = {
                            "type": "service_account",
                            "project_id": project_id,
                            "private_key": private_key,
                            "client_email": client_email,
                            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
                            "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
                            "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                            "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                            "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                            "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL', '')
                        }
                        try:
                            cred = credentials.Certificate(service_account_info)
                            app = firebase_admin.initialize_app(cred)
                            logger.info("✅ Firebase app initialized with legacy environment variables")
                        except Exception as cred_error:
                            logger.error(f"❌ Failed to create Firebase credentials from legacy env vars: {cred_error}")
                            raise
        # Get Firestore client
        try:
            db = firestore.client()
            logger.info("✅ Firebase Firestore client created successfully")
            return db
        except Exception as client_error:
            logger.error(f"❌ Failed to create Firestore client: {client_error}")
            raise
    except ImportError as e:
        logger.error(f"Firebase client not available: {e}")
        raise ImportError("Firebase client not available. Install with: pip install firebase-admin")
    except Exception as e:
        logger.error(f"Error in get_firebase_client: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise e

# --- Test Firebase Connection ---
def test_firebase_connection():
    """
    Test Firebase connection and return status.
    
    Returns:
        dict: Connection status and details
    """
    try:
        db = get_firebase_client()
        
        # Test a simple query
        teams_ref = db.collection('teams')
        docs = teams_ref.limit(1).stream()
        doc_count = len(list(docs))
        
        return {
            'status': 'success',
            'message': 'Firebase connection successful',
            'data': {'teams_count': doc_count}
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Firebase connection failed: {str(e)}',
            'data': None
        }

# --- Utility Functions ---
def generate_uuid():
    """Generate a UUID string for document IDs."""
    return str(uuid.uuid4())

def timestamp_to_datetime(timestamp):
    """Convert Firestore timestamp to datetime."""
    if hasattr(timestamp, 'timestamp'):
        return timestamp.timestamp()
    return timestamp

def datetime_to_timestamp(dt):
    """Convert datetime to Firestore timestamp."""
    from firebase_admin import firestore
    return firestore.SERVER_TIMESTAMP if dt is None else firestore.SERVER_TIMESTAMP

def get_user_role(team_id: str, user_id: str) -> str:
    """
    Get user role from Firebase database.
    
    Args:
        team_id: The team ID
        user_id: The Telegram user ID
        
    Returns:
        str: User role ('admin', 'captain', 'member', etc.) or 'member' as default
    """
    try:
        db = get_firebase_client()
        members_ref = db.collection('team_members')
        query = members_ref.where('team_id', '==', team_id).where('telegram_id', '==', user_id)
        docs = query.stream()
        
        for doc in docs:
            data = doc.to_dict()
            return data.get('role', 'member')
        
        # If user not found, return default role
        return 'member'
        
    except Exception as e:
        logger.error(f"Error getting user role: {e}")
        return 'member'

def is_leadership_chat(chat_id: str, team_id: str) -> bool:
    """
    Check if a chat is a leadership chat for the team.
    
    Args:
        chat_id: The Telegram chat ID
        team_id: The team ID
        
    Returns:
        bool: True if it's a leadership chat, False otherwise
    """
    try:
        db = get_firebase_client()
        bots_ref = db.collection('team_bots')
        query = bots_ref.where('team_id', '==', team_id).where('is_active', '==', True)
        docs = query.stream()
        
        for doc in docs:
            data = doc.to_dict()
            leadership_chat_id = data.get('leadership_chat_id')
            if leadership_chat_id and str(leadership_chat_id) == str(chat_id):
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking leadership chat: {e}")
        return False

# --- Player Management Tools ---

class PlayerTools(BaseTool):
    name: str = "Player Management Tool"
    description: str = "A tool to manage player data in the database. Use it to add, retrieve, update, or deactivate player information."

    def __init__(self, team_id: str):
        super().__init__(name="Player Management Tool", description="A tool to manage player data in the database. Use it to add, retrieve, update, or deactivate player information.")
        object.__setattr__(self, 'team_id', team_id)

    def _run(self, command: str, **kwargs) -> str:
        db = get_firebase_client()
        if command == 'add_player':
            return self._add_player(db, **kwargs)
        elif command == 'get_all_players':
            return self._get_all_players(db)
        elif command == 'get_player':
            return self._get_player(db, **kwargs)
        elif command == 'update_player':
            return self._update_player(db, **kwargs)
        elif command == 'deactivate_player':
            return self._deactivate_player(db, **kwargs)
        else:
            return "Error: Unknown command. Available commands: 'add_player', 'get_all_players', 'get_player', 'update_player', 'deactivate_player'."

    def _add_player(self, db, name: str, phone_number: str) -> str:
        if not name or not phone_number:
            return "Error: Both 'name' and 'phone_number' are required to add a player."
        try:
            player_data = {
                'name': name,
                'phone_number': phone_number,
                'is_active': True,
                'team_id': self.team_id,
                'created_at': datetime_to_timestamp(None),
                'updated_at': datetime_to_timestamp(None)
            }
            
            doc_ref = db.collection('team_members').document()
            doc_ref.set(player_data)
            
            return f"Successfully added player: {name} (ID: {doc_ref.id})."
        except Exception as e:
            return f"An exception occurred while adding a player: {e}"

    def _get_all_players(self, db) -> str:
        try:
            players_ref = db.collection('team_members')
            query = players_ref.where('team_id', '==', self.team_id).order_by('name')
            docs = query.stream()
            
            player_list = []
            for doc in docs:
                data = doc.to_dict()
                # Filter active players in Python to avoid composite index requirement
                if data.get('is_active', True):
                    player_list.append(data.get('name', 'Unknown'))
            
            if player_list:
                # Create a nice formatted list
                if len(player_list) == 1:
                    return f"👤 **Team Player:**\n{player_list[0]}"
                else:
                    formatted_list = "\n".join([f"• {name}" for name in player_list])
                    return f"👥 **Team Players ({len(player_list)}):**\n{formatted_list}"
            else:
                return "📝 No active players found in the team."
        except Exception as e:
            return f"❌ Error fetching players: {e}"

    def _get_player(self, db, player_id: Optional[str] = None, phone_number: Optional[str] = None) -> str:
        if not player_id and not phone_number:
            return "Error: Either 'player_id' or 'phone_number' is required."
        try:
            players_ref = db.collection('team_members')
            
            if player_id:
                doc = players_ref.document(player_id).get()
                if doc.exists:
                    data = doc.to_dict()
                    if data.get('team_id') == self.team_id:
                        return f"Player found: {data.get('name')} (ID: {doc.id}, Phone: {data.get('phone_number')}, Active: {data.get('is_active', True)})"
                    else:
                        return "Player not found in this team."
                else:
                    return "Player not found."
            else:
                query = players_ref.where('team_id', '==', self.team_id).where('phone_number', '==', phone_number)
                docs = query.stream()
                docs_list = list(docs)
                
                if docs_list:
                    doc = docs_list[0]
                    data = doc.to_dict()
                    return f"Player found: {data.get('name')} (ID: {doc.id}, Phone: {data.get('phone_number')}, Active: {data.get('is_active', True)})"
                else:
                    return "Player not found."
        except Exception as e:
            return f"An exception occurred while fetching player: {e}"

    def _update_player(self, db, player_id: str, **kwargs) -> str:
        if not player_id:
            return "Error: 'player_id' is required to update a player."
        try:
            valid_fields = ['name', 'phone_number', 'is_active']
            update_data = {k: v for k, v in kwargs.items() if k in valid_fields}
            
            if not update_data:
                return "Error: No valid fields to update. Valid fields: name, phone_number, is_active"
            
            update_data['updated_at'] = datetime_to_timestamp(None)
            
            doc_ref = db.collection('team_members').document(player_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return "Player not found."
            
            data = doc.to_dict()
            if data.get('team_id') != self.team_id:
                return "Player not found in this team."
            
            doc_ref.update(update_data)
            return f"Successfully updated player {player_id}."
        except Exception as e:
            return f"An exception occurred while updating player: {e}"

    def _deactivate_player(self, db, player_id: str) -> str:
        return self._update_player(db, player_id, is_active=False)

# --- Team Management Tools ---

class TeamTools(BaseTool):
    name: str = "Team Management Tool"
    description: str = "A tool to manage team data in the database. Use it to create teams, retrieve team information, and manage team settings."

    def __init__(self, team_id: str):
        super().__init__(name="Team Management Tool", description="A tool to manage team data in the database. Use it to create teams, retrieve team information, and manage team settings.")
        object.__setattr__(self, 'team_id', team_id)

    def _run(self, command: str, **kwargs) -> str:
        db = get_firebase_client()
        if command == 'get_team_info':
            return self._get_team_info(db)
        elif command == 'update_team_info':
            return self._update_team_info(db, **kwargs)
        else:
            return "Error: Unknown command. Available commands: 'get_team_info', 'update_team_info'."

    def _get_team_info(self, db) -> str:
        try:
            doc = db.collection('teams').document(self.team_id).get()
            if doc.exists:
                data = doc.to_dict()
                return f"Team: {data.get('name')} (ID: {doc.id}, Created: {timestamp_to_datetime(data.get('created_at'))})"
            else:
                return "Team not found."
        except Exception as e:
            return f"An exception occurred while fetching team info: {e}"

    def _update_team_info(self, db, **kwargs) -> str:
        try:
            valid_fields = ['name']
            update_data = {k: v for k, v in kwargs.items() if k in valid_fields}
            
            if not update_data:
                return "Error: No valid fields to update. Valid fields: name"
            
            update_data['updated_at'] = datetime_to_timestamp(None)
            
            doc_ref = db.collection('teams').document(self.team_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return "Team not found."
            
            doc_ref.update(update_data)
            return f"Successfully updated team {self.team_id}."
        except Exception as e:
            return f"An exception occurred while updating team: {e}"

# --- Fixture Management Tools ---

class FixtureTools(BaseTool):
    name: str = "Fixture Management Tool"
    description: str = "A tool to manage fixture data in the database. Use it to create, retrieve, update, or delete fixture information."

    def __init__(self, team_id: str):
        super().__init__(name="Fixture Management Tool", description="A tool to manage fixture data in the database. Use it to create, retrieve, update, or delete fixture information.")
        object.__setattr__(self, 'team_id', team_id)

    def _run(self, command: str, **kwargs) -> str:
        db = get_firebase_client()
        if command == 'add_fixture':
            return self._add_fixture(db, **kwargs)
        elif command == 'get_all_fixtures':
            return self._get_all_fixtures(db)
        elif command == 'get_fixture':
            return self._get_fixture(db, **kwargs)
        elif command == 'update_fixture':
            return self._update_fixture(db, **kwargs)
        elif command == 'delete_fixture':
            return self._delete_fixture(db, **kwargs)
        else:
            return "Error: Unknown command. Available commands: 'add_fixture', 'get_all_fixtures', 'get_fixture', 'update_fixture', 'delete_fixture'."

    def _add_fixture(self, db, opponent: str, match_date: str, kickoff_time: str, venue: str, competition: str = 'League', notes: str = '', created_by: str = '') -> str:
        if not all([opponent, match_date, kickoff_time, venue]):
            return "Error: 'opponent', 'match_date', 'kickoff_time', and 'venue' are required."
        try:
            # Generate human-readable fixture ID
            if match_id_generator:
                fixture_id = match_id_generator.generate_match_id(opponent, match_date, venue)
            else:
                # Fallback to GUID if MatchIDGenerator is not available
                fixture_id = generate_uuid()
            
            fixture_data = {
                'team_id': self.team_id,
                'opponent': opponent,
                'match_date': match_date,
                'kickoff_time': kickoff_time,
                'venue': venue,
                'competition': competition,
                'notes': notes,
                'status': 'scheduled',
                'created_by': created_by,
                'created_at': datetime_to_timestamp(None),
                'updated_at': datetime_to_timestamp(None)
            }
            
            # Use the generated human-readable ID instead of random GUID
            doc_ref = db.collection('fixtures').document(fixture_id)
            doc_ref.set(fixture_data)
            
            return f"Successfully added fixture: {opponent} on {match_date} at {kickoff_time} (ID: {fixture_id})."
        except Exception as e:
            return f"An exception occurred while adding fixture: {e}"

    def _get_all_fixtures(self, db) -> str:
        try:
            fixtures_ref = db.collection('fixtures')
            query = fixtures_ref.where('team_id', '==', self.team_id).order_by('match_date')
            docs = query.stream()
            
            fixture_list = []
            for doc in docs:
                data = doc.to_dict()
                fixture_list.append(f"- ID: {doc.id}, {data.get('opponent')} on {data.get('match_date')} at {data.get('kickoff_time')} ({data.get('status')})")
            
            if fixture_list:
                return f"All Fixtures:\n" + "\n".join(fixture_list)
            else:
                return "No fixtures found."
        except Exception as e:
            return f"An exception occurred while fetching fixtures: {e}"

    def _get_fixture(self, db, fixture_id: str) -> str:
        if not fixture_id:
            return "Error: 'fixture_id' is required."
        try:
            doc = db.collection('fixtures').document(fixture_id).get()
            if doc.exists:
                data = doc.to_dict()
                if data.get('team_id') == self.team_id:
                    return f"Fixture: {data.get('opponent')} on {data.get('match_date')} at {data.get('kickoff_time')} at {data.get('venue')} ({data.get('status')})"
                else:
                    return "Fixture not found in this team."
            else:
                return "Fixture not found."
        except Exception as e:
            return f"An exception occurred while fetching fixture: {e}"

    def _update_fixture(self, db, fixture_id: str, **kwargs) -> str:
        if not fixture_id:
            return "Error: 'fixture_id' is required to update a fixture."
        try:
            valid_fields = ['opponent', 'match_date', 'kickoff_time', 'venue', 'competition', 'notes', 'status']
            update_data = {k: v for k, v in kwargs.items() if k in valid_fields}
            
            if not update_data:
                return "Error: No valid fields to update. Valid fields: opponent, match_date, kickoff_time, venue, competition, notes, status"
            
            update_data['updated_at'] = datetime_to_timestamp(None)
            
            doc_ref = db.collection('fixtures').document(fixture_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return "Fixture not found."
            
            data = doc.to_dict()
            if data.get('team_id') != self.team_id:
                return "Fixture not found in this team."
            
            doc_ref.update(update_data)
            return f"Successfully updated fixture {fixture_id}."
        except Exception as e:
            return f"An exception occurred while updating fixture: {e}"

    def _delete_fixture(self, db, fixture_id: str) -> str:
        if not fixture_id:
            return "Error: 'fixture_id' is required to delete a fixture."
        try:
            doc_ref = db.collection('fixtures').document(fixture_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return "Fixture not found."
            
            data = doc.to_dict()
            if data.get('team_id') != self.team_id:
                return "Fixture not found in this team."
            
            doc_ref.delete()
            return f"Successfully deleted fixture {fixture_id}."
        except Exception as e:
            return f"An exception occurred while deleting fixture: {e}"

# --- Command Logging Tools ---

class CommandLoggingTools(BaseTool):
    name: str = "Command Logging Tool"
    description: str = "A tool to log command executions in the database for audit and debugging purposes."

    def __init__(self, team_id: str):
        super().__init__(name="Command Logging Tool", description="A tool to log command executions in the database for audit and debugging purposes.")
        object.__setattr__(self, 'team_id', team_id)

    def _run(self, *args, **kwargs) -> str:
        db = get_firebase_client()
        
        # Handle command parameter - it could be first positional arg or in kwargs
        if args and len(args) > 0:
            command = args[0]
        elif 'command' in kwargs:
            command = kwargs['command']  # Don't remove, just get the value
        else:
            return "Error: 'command' parameter is required."
        
        if command == 'log_command':
            return self._log_command(db, **kwargs)
        else:
            return "Error: Unknown command. Available commands: 'log_command'."

    def _log_command(self, db, chat_id: str, user_id: str, command: str, username: Optional[str] = None, arguments: Optional[str] = None, success: bool = True, error_message: Optional[str] = None) -> str:
        if not all([chat_id, user_id, command]):
            return "Error: 'chat_id', 'user_id', and 'command' are required."
        
        try:
            log_data = {
                'team_id': self.team_id,
                'chat_id': chat_id,
                'user_id': user_id,
                'command': command,
                'success': success,
                'created_at': datetime_to_timestamp(None)
            }
            
            if username:
                log_data['username'] = username
            if arguments:
                log_data['arguments'] = arguments
            if error_message:
                log_data['error_message'] = error_message
            
            doc_ref = db.collection('command_logs').document()
            doc_ref.set(log_data)
            
            return f"Successfully logged command: {command}"
        except Exception as e:
            return f"An exception occurred while logging command: {e}"

# --- Bot Management Tools ---

class BotTools(BaseTool):
    name: str = "Bot Management Tool"
    description: str = "A tool to manage bot configurations and retrieve bot tokens for different teams."

    def __init__(self, team_id: str):
        super().__init__(name="Bot Management Tool", description="A tool to manage bot configurations and retrieve bot tokens for different teams.")
        object.__setattr__(self, 'team_id', team_id)

    def _run(self, command: str, **kwargs) -> str:
        db = get_firebase_client()
        if command == 'get_bot_config':
            return self._get_bot_config(db)
        elif command == 'update_bot_config':
            return self._update_bot_config(db, **kwargs)
        else:
            return "Error: Unknown command. Available commands: 'get_bot_config', 'update_bot_config'."

    def _get_bot_config(self, db) -> str:
        try:
            bots_ref = db.collection('team_bots')
            query = bots_ref.where('team_id', '==', self.team_id).where('is_active', '==', True)
            docs = query.stream()
            docs_list = list(docs)
            
            if docs_list:
                data = docs_list[0].to_dict()
                return f"Bot: {data.get('bot_username')} (Token: {data.get('bot_token')[:10]}..., Chat: {data.get('chat_id')})"
            else:
                return "No active bot found for this team."
        except Exception as e:
            return f"An exception occurred while fetching bot config: {e}"

    def _update_bot_config(self, db, **kwargs) -> str:
        try:
            valid_fields = ['bot_token', 'bot_username', 'chat_id', 'leadership_chat_id', 'is_active']
            update_data = {k: v for k, v in kwargs.items() if k in valid_fields}
            
            if not update_data:
                return "Error: No valid fields to update. Valid fields: bot_token, bot_username, chat_id, leadership_chat_id, is_active"
            
            update_data['updated_at'] = datetime_to_timestamp(None)
            
            bots_ref = db.collection('team_bots')
            query = bots_ref.where('team_id', '==', self.team_id).where('is_active', '==', True)
            docs = query.stream()
            docs_list = list(docs)
            
            if docs_list:
                doc_ref = docs_list[0].reference
                doc_ref.update(update_data)
                return f"Successfully updated bot config for team {self.team_id}."
            else:
                return "No active bot found for this team."
        except Exception as e:
            return f"An exception occurred while updating bot config: {e}"
