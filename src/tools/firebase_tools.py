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
from src.utils.match_id_generator import MatchIDGenerator
match_id_generator = MatchIDGenerator()
logger.info("✅ MatchIDGenerator imported from utils successfully")

# --- Firebase Client Factory ---
def validate_and_repair_pem_key(private_key: str) -> str:
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
    
    # CRITICAL FIX: Convert escaped newlines to actual newlines
    # This is the main issue - Firebase often provides keys with \\n instead of \n
    if '\\n' in private_key:
        private_key = private_key.replace('\\n', '\n')
        logger.info("🔧 Fixed escaped newlines in private key")
    
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

def extract_private_key_from_json(creds_dict: dict) -> dict:
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
    repaired_key = validate_and_repair_pem_key(private_key)
    
    # Create a new dict with the repaired key
    repaired_creds = creds_dict.copy()
    repaired_creds['private_key'] = repaired_key
    
    return repaired_creds

def get_firebase_client():
    """
    Get Firebase Firestore client with proper initialization.
    Uses Firebase Admin SDK's built-in credential handling for maximum compatibility.
    Returns:
        firestore.Client: Firebase Firestore client
    Raises:
        RuntimeError: If Firebase credentials are not available or invalid
    """
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        import json
        import os
        
        logger.info("🔍 Starting Firebase client initialization...")
        
        # Check if Firebase app is already initialized
        try:
            app = firebase_admin.get_app()
            logger.info("✅ Using existing Firebase app")
            return firestore.client()
        except ValueError:
            logger.info("🔄 Initializing new Firebase app...")
        
        project_id = os.getenv('FIREBASE_PROJECT_ID')
        if not project_id:
            raise RuntimeError("FIREBASE_PROJECT_ID environment variable is required.")
        
        logger.info(f"✅ Project ID: {project_id}")
        
        # Get credentials from environment variable
        firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
        if not firebase_creds_json:
            raise RuntimeError("FIREBASE_CREDENTIALS_JSON environment variable is required.")
        
        try:
            logger.info("🔄 Loading Firebase credentials from FIREBASE_CREDENTIALS_JSON...")
            creds_dict = json.loads(firebase_creds_json)
            
            # Validate and repair the private key
            repaired_creds = extract_private_key_from_json(creds_dict)
            
            cred = credentials.Certificate(repaired_creds)
            logger.info("✅ Firebase credentials created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
            raise RuntimeError(f"Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
        
        # Initialize Firebase app
        logger.info("🔄 Initializing Firebase app...")
        app = firebase_admin.initialize_app(cred, {'projectId': project_id})
        logger.info("✅ Firebase app initialized successfully")
        
        return firestore.client()
        
    except Exception as e:
        raise RuntimeError(f"Failed to get Firebase client: {e}")

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
# Updated Wed  2 Jul 2025 13:03:26 BST
