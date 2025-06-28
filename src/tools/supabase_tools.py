import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime, date

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conditional import for crewai with proper typing
if TYPE_CHECKING:
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
else:
    try:
        from crewai.tools import BaseTool
        CREWAI_AVAILABLE = True
    except ImportError:
        # Fallback base class when crewai is not available
        class BaseTool:
            def __init__(self, name: str, description: str):
                self.name = name
                self.description = description
                self.team_id: Optional[str] = None  # Will be set by subclasses
            def _run(self, *args, **kwargs):
                raise NotImplementedError("BaseTool _run method must be implemented")
        CREWAI_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# --- Comprehensive Supabase Client Factory ---
def get_supabase_client():
    """
    Get Supabase client with comprehensive error handling and version compatibility.
    
    Returns:
        Client: Supabase client instance
        
    Raises:
        ValueError: If environment variables are missing
        Exception: If client creation fails
    """
    try:
        # Import with version compatibility handling
        try:
            from supabase import create_client, Client
        except ImportError as e:
            logger.error(f"Supabase client not available: {e}")
            raise ImportError("Supabase client not available. Install with: pip install supabase")
        
        # Get environment variables
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        # Create client with explicit options to avoid proxy issues
        try:
            # Try with explicit options first (for newer versions)
            from supabase.lib.client_options import SyncClientOptions
            
            options = SyncClientOptions(
                schema='public',
                auto_refresh_token=True,
                persist_session=False,  # Disable session persistence for server deployment
                postgrest_client_timeout=30,
                storage_client_timeout=10,
                function_client_timeout=10
            )
            
            client = create_client(url, key, options)
            logger.info("✅ Supabase client created successfully with explicit options")
            return client
            
        except Exception as options_error:
            logger.warning(f"Failed to create client with options: {options_error}")
            
            # Fallback to basic client creation
            try:
                client = create_client(url, key)
                logger.info("✅ Supabase client created successfully with basic options")
                return client
                
            except Exception as basic_error:
                logger.error(f"Failed to create basic client: {basic_error}")
                raise Exception(f"Failed to create Supabase client: {basic_error}")
                
    except Exception as e:
        logger.error(f"Error in get_supabase_client: {e}")
        raise e

# --- Test Supabase Connection ---
def test_supabase_connection():
    """
    Test Supabase connection and return status.
    
    Returns:
        dict: Connection status and details
    """
    try:
        client = get_supabase_client()
        
        # Test a simple query
        response = client.table('teams').select('count').limit(1).execute()
        
        return {
            'status': 'success',
            'message': 'Supabase connection successful',
            'data': response.data if hasattr(response, 'data') else None
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Supabase connection failed: {str(e)}',
            'data': None
        }

# --- Player Management Tools ---

class PlayerTools(BaseTool):
    name: str = "Player Management Tool"
    description: str = "A tool to manage player data in the database. Use it to add, retrieve, update, or deactivate player information."

    def __init__(self, team_id: str):
        super().__init__(name="Player Management Tool", description="A tool to manage player data in the database. Use it to add, retrieve, update, or deactivate player information.")
        object.__setattr__(self, 'team_id', team_id)

    def _run(self, command: str, **kwargs) -> str:
        supabase = get_supabase_client()
        if command == 'add_player':
            return self._add_player(supabase, **kwargs)
        elif command == 'get_all_players':
            return self._get_all_players(supabase)
        elif command == 'get_player':
            return self._get_player(supabase, **kwargs)
        elif command == 'update_player':
            return self._update_player(supabase, **kwargs)
        elif command == 'deactivate_player':
            return self._deactivate_player(supabase, **kwargs)
        else:
            return "Error: Unknown command. Available commands: 'add_player', 'get_all_players', 'get_player', 'update_player', 'deactivate_player'."

    def _add_player(self, supabase: Client, name: str, phone_number: str) -> str:
        if not name or not phone_number:
            return "Error: Both 'name' and 'phone_number' are required to add a player."
        try:
            response = supabase.table('players').insert({
                'name': name,
                'phone_number': phone_number,
                'is_active': True,
                'team_id': self.team_id
            }).execute()
            if response.data:
                player = response.data[0]
                return f"Successfully added player: {name} (ID: {player['id']})."
            else:
                return "Error adding player: No data returned from insert operation."
        except Exception as e:
            return f"An exception occurred while adding a player: {e}"

    def _get_all_players(self, supabase: Client) -> str:
        try:
            response = supabase.table('players').select('id, name, phone_number, is_active, created_at').eq('team_id', self.team_id).order('name').execute()
            if response.data:
                player_list = []
                for p in response.data:
                    status = "Active" if p['is_active'] else "Inactive"
                    player_list.append(f"- ID: {p['id']}, Name: {p['name']}, Phone: {p['phone_number']}, Status: {status}")
                return f"All Players:\n" + "\n".join(player_list)
            else:
                return "No players found."
        except Exception as e:
            return f"An exception occurred while fetching players: {e}"

    def _get_player(self, supabase: Client, player_id: Optional[str] = None, phone_number: Optional[str] = None) -> str:
        if not player_id and not phone_number:
            return "Error: Either 'player_id' or 'phone_number' is required."
        try:
            query = supabase.table('players').select('*').eq('team_id', self.team_id)
            if player_id:
                response = query.eq('id', player_id).execute()
            else:
                response = query.eq('phone_number', phone_number).execute()
            
            if response.data:
                player = response.data[0]
                return f"Player found: {player['name']} (ID: {player['id']}, Phone: {player['phone_number']}, Active: {player['is_active']})"
            else:
                return "Player not found."
        except Exception as e:
            return f"An exception occurred while fetching player: {e}"

    def _update_player(self, supabase: Client, player_id: str, **kwargs) -> str:
        if not player_id:
            return "Error: 'player_id' is required to update a player."
        try:
            update_data = {k: v for k, v in kwargs.items() if k in ['name', 'phone_number', 'is_active']}
            if not update_data:
                return "Error: No valid fields to update. Valid fields: name, phone_number, is_active"
            
            response = supabase.table('players').update(update_data).eq('id', player_id).eq('team_id', self.team_id).execute()
            if response.data:
                return f"Successfully updated player {player_id}."
            else:
                return "Error updating player: No data returned."
        except Exception as e:
            return f"An exception occurred while updating player: {e}"

    def _deactivate_player(self, supabase: Client, player_id: str) -> str:
        return self._update_player(supabase, player_id, is_active=False)

# --- Fixture Management Tools ---

class FixtureTools(BaseTool):
    name: str = "Fixture Management Tool"
    description: str = "A tool to manage match fixtures. Use it to create, retrieve, update, or list fixtures."

    def __init__(self, team_id: str):
        super().__init__(name="Fixture Management Tool", description="A tool to manage match fixtures. Use it to create, retrieve, update, or list fixtures.")
        object.__setattr__(self, 'team_id', team_id)

    def _run(self, command: str, **kwargs) -> str:
        supabase = get_supabase_client()
        if command == 'add_fixture':
            return self._add_fixture(supabase, **kwargs)
        elif command == 'get_fixtures':
            return self._get_fixtures(supabase, **kwargs)
        elif command == 'get_fixture':
            return self._get_fixture(supabase, **kwargs)
        elif command == 'update_fixture':
            return self._update_fixture(supabase, **kwargs)
        else:
            return "Error: Unknown command. Available commands: 'add_fixture', 'get_fixtures', 'get_fixture', 'update_fixture'."

    def _add_fixture(self, supabase: Client, opponent: str, match_date: str, location: Optional[str] = None, is_home_game: bool = True) -> str:
        if not opponent or not match_date:
            return "Error: Both 'opponent' and 'match_date' are required to add a fixture."
        try:
            # Parse the match date
            try:
                parsed_date = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
            except:
                return "Error: Invalid date format. Use ISO format (e.g., '2024-12-01T14:00:00Z')"
            
            fixture_data = {
                'opponent': opponent,
                'match_date': parsed_date.isoformat(),
                'is_home_game': is_home_game,
                'team_id': self.team_id
            }
            if location:
                fixture_data['location'] = location
            
            response = supabase.table('fixtures').insert(fixture_data).execute()
            if response.data:
                fixture = response.data[0]
                return f"Successfully added fixture: {opponent} vs KICKAI on {match_date} (ID: {fixture['id']})."
            else:
                return "Error adding fixture: No data returned from insert operation."
        except Exception as e:
            return f"An exception occurred while adding fixture: {e}"

    def _get_fixtures(self, supabase: Client, upcoming_only: bool = True) -> str:
        try:
            query = supabase.table('fixtures').select('*').eq('team_id', self.team_id).order('match_date')
            if upcoming_only:
                now = datetime.now().isoformat()
                query = query.gte('match_date', now)
            
            response = query.execute()
            if response.data:
                fixture_list = []
                for f in response.data:
                    home_away = "HOME" if f['is_home_game'] else "AWAY"
                    result = f" (Result: {f['result']})" if f['result'] else ""
                    fixture_list.append(f"- {f['opponent']} ({home_away}) on {f['match_date']}{result} (ID: {f['id']})")
                return f"Fixtures:\n" + "\n".join(fixture_list)
            else:
                return "No fixtures found."
        except Exception as e:
            return f"An exception occurred while fetching fixtures: {e}"

    def _get_fixture(self, supabase: Client, fixture_id: str) -> str:
        if not fixture_id:
            return "Error: 'fixture_id' is required."
        try:
            response = supabase.table('fixtures').select('*').eq('id', fixture_id).eq('team_id', self.team_id).execute()
            if response.data:
                fixture = response.data[0]
                home_away = "HOME" if fixture['is_home_game'] else "AWAY"
                result = f" (Result: {fixture['result']})" if fixture['result'] else ""
                return f"Fixture: {fixture['opponent']} ({home_away}) on {fixture['match_date']}{result}"
            else:
                return "Fixture not found."
        except Exception as e:
            return f"An exception occurred while fetching fixture: {e}"

    def _update_fixture(self, supabase: Client, fixture_id: str, **kwargs) -> str:
        if not fixture_id:
            return "Error: 'fixture_id' is required to update a fixture."
        try:
            update_data = {k: v for k, v in kwargs.items() if k in ['opponent', 'match_date', 'location', 'is_home_game', 'result']}
            if not update_data:
                return "Error: No valid fields to update. Valid fields: opponent, match_date, location, is_home_game, result"
            
            response = supabase.table('fixtures').update(update_data).eq('id', fixture_id).eq('team_id', self.team_id).execute()
            if response.data:
                return f"Successfully updated fixture {fixture_id}."
            else:
                return "Error updating fixture: No data returned."
        except Exception as e:
            return f"An exception occurred while updating fixture: {e}"

# --- Availability Management Tools ---

class AvailabilityTools(BaseTool):
    name: str = "Availability Management Tool"
    description: str = "A tool to manage player availability for fixtures. Use it to set availability, check squad status, and manage payments."

    def __init__(self, team_id: str):
        super().__init__(name="Availability Management Tool", description="A tool to manage player availability for fixtures. Use it to set availability, check squad status, and manage payments.")
        object.__setattr__(self, 'team_id', team_id)

    def _run(self, command: str, **kwargs) -> str:
        supabase = get_supabase_client()
        if command == 'set_availability':
            return self._set_availability(supabase, **kwargs)
        elif command == 'get_availability':
            return self._get_availability(supabase, **kwargs)
        elif command == 'get_squad':
            return self._get_squad(supabase, **kwargs)
        elif command == 'set_squad_status':
            return self._set_squad_status(supabase, **kwargs)
        elif command == 'mark_payment':
            return self._mark_payment(supabase, **kwargs)
        else:
            return "Error: Unknown command. Available commands: 'set_availability', 'get_availability', 'get_squad', 'set_squad_status', 'mark_payment'."

    def _set_availability(self, supabase: Client, player_id: str, fixture_id: str, status: str) -> str:
        if not all([player_id, fixture_id, status]):
            return "Error: 'player_id', 'fixture_id', and 'status' are required."
        if status not in ['Available', 'Unavailable', 'Maybe']:
            return "Error: Status must be 'Available', 'Unavailable', or 'Maybe'."
        
        try:
            # Use upsert to handle existing records
            response = supabase.table('availability').upsert({
                'player_id': player_id,
                'fixture_id': fixture_id,
                'status': status
            }).execute()
            
            if response.data:
                return f"Successfully set availability for player {player_id} to {status} for fixture {fixture_id}."
            else:
                return "Error setting availability: No data returned."
        except Exception as e:
            return f"An exception occurred while setting availability: {e}"

    def _get_availability(self, supabase: Client, fixture_id: str) -> str:
        if not fixture_id:
            return "Error: 'fixture_id' is required."
        try:
            response = supabase.table('availability').select(
                'status, squad_status, has_paid_fees, players(name, phone_number)'
            ).eq('fixture_id', fixture_id).execute()
            
            if response.data:
                availability_list = []
                for a in response.data:
                    player_name = a['players']['name'] if a['players'] else 'Unknown'
                    squad = f" ({a['squad_status']})" if a['squad_status'] else ""
                    paid = " [PAID]" if a['has_paid_fees'] else " [UNPAID]"
                    availability_list.append(f"- {player_name}: {a['status']}{squad}{paid}")
                return f"Availability for fixture {fixture_id}:\n" + "\n".join(availability_list)
            else:
                return "No availability records found for this fixture."
        except Exception as e:
            return f"An exception occurred while fetching availability: {e}"

    def _get_squad(self, supabase: Client, fixture_id: str) -> str:
        if not fixture_id:
            return "Error: 'fixture_id' is required."
        try:
            response = supabase.table('availability').select(
                'squad_status, players(name, phone_number)'
            ).eq('fixture_id', fixture_id).not_.is_('squad_status', 'null').execute()
            
            if response.data:
                starters = []
                substitutes = []
                for a in response.data:
                    player_name = a['players']['name'] if a['players'] else 'Unknown'
                    if a['squad_status'] == 'Starter':
                        starters.append(player_name)
                    elif a['squad_status'] == 'Substitute':
                        substitutes.append(player_name)
                
                squad_text = f"Squad for fixture {fixture_id}:\n"
                if starters:
                    squad_text += f"Starters: {', '.join(starters)}\n"
                if substitutes:
                    squad_text += f"Substitutes: {', '.join(substitutes)}"
                return squad_text
            else:
                return "No squad selected for this fixture."
        except Exception as e:
            return f"An exception occurred while fetching squad: {e}"

    def _set_squad_status(self, supabase: Client, player_id: str, fixture_id: str, squad_status: str) -> str:
        if not all([player_id, fixture_id, squad_status]):
            return "Error: 'player_id', 'fixture_id', and 'squad_status' are required."
        if squad_status not in ['Starter', 'Substitute', 'Not Selected']:
            return "Error: Squad status must be 'Starter', 'Substitute', or 'Not Selected'."
        
        try:
            response = supabase.table('availability').update({
                'squad_status': squad_status
            }).eq('player_id', player_id).eq('fixture_id', fixture_id).execute()
            
            if response.data:
                return f"Successfully set squad status for player {player_id} to {squad_status} for fixture {fixture_id}."
            else:
                return "Error setting squad status: No data returned."
        except Exception as e:
            return f"An exception occurred while setting squad status: {e}"

    def _mark_payment(self, supabase: Client, player_id: str, fixture_id: str, has_paid: bool = True) -> str:
        if not all([player_id, fixture_id]):
            return "Error: 'player_id' and 'fixture_id' are required."
        
        try:
            response = supabase.table('availability').update({
                'has_paid_fees': has_paid
            }).eq('player_id', player_id).eq('fixture_id', fixture_id).execute()
            
            if response.data:
                status = "paid" if has_paid else "unpaid"
                return f"Successfully marked player {player_id} as {status} for fixture {fixture_id}."
            else:
                return "Error marking payment: No data returned."
        except Exception as e:
            return f"An exception occurred while marking payment: {e}"

# --- Example Usage (for testing) ---
if __name__ == '__main__':
    # Example team ID - in real usage, this would be passed from the calling code
    example_team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # BP Hatters FC
    
    player_tool = PlayerTools(example_team_id)
    fixture_tool = FixtureTools(example_team_id)
    availability_tool = AvailabilityTools(example_team_id)
    
    # Test player tools
    print("=== Testing Player Tools ===")
    print(player_tool._run('get_all_players'))
    
    # Test fixture tools
    print("\n=== Testing Fixture Tools ===")
    print(fixture_tool._run('get_fixtures'))

# --- Team Management Tools (Dual-Channel Support) ---

class TeamManagementTools(BaseTool):
    name: str = "Team Management Tool"
    description: str = "A tool to manage team configuration, dual-channel setup, and team member roles."

    def __init__(self, team_id: str):
        super().__init__(name="Team Management Tool", description="A tool to manage team configuration, dual-channel setup, and team member roles.")
        object.__setattr__(self, 'team_id', team_id)

    def _run(self, command: str, **kwargs) -> str:
        supabase = get_supabase_client()
        if command == 'get_team_info':
            return self._get_team_info(supabase)
        elif command == 'update_leadership_chat':
            return self._update_leadership_chat(supabase, **kwargs)
        elif command == 'get_team_members':
            return self._get_team_members(supabase, **kwargs)
        elif command == 'add_team_member':
            return self._add_team_member(supabase, **kwargs)
        elif command == 'update_member_role':
            return self._update_member_role(supabase, **kwargs)
        elif command == 'get_members_by_role':
            return self._get_members_by_role(supabase, **kwargs)
        else:
            return "Error: Unknown command. Available commands: 'get_team_info', 'update_leadership_chat', 'get_team_members', 'add_team_member', 'update_member_role', 'get_members_by_role'."

    def _get_team_info(self, supabase: Client) -> str:
        try:
            response = supabase.table('teams').select('*').eq('id', self.team_id).execute()
            if response.data:
                team = response.data[0]
                return f"Team: {team['name']}\nDescription: {team['description']}\nMain Group: {team['telegram_group']}\nLeadership Chat: {team['leadership_chat_id'] or 'Not set'}\nActive: {team['is_active']}"
            else:
                return "Team not found."
        except Exception as e:
            return f"An exception occurred while fetching team info: {e}"

    def _update_leadership_chat(self, supabase: Client, leadership_chat_id: str) -> str:
        if not leadership_chat_id:
            return "Error: 'leadership_chat_id' is required."
        try:
            # Update teams table
            response = supabase.table('teams').update({
                'leadership_chat_id': leadership_chat_id
            }).eq('id', self.team_id).execute()
            
            # Update team_bots table
            supabase.table('team_bots').update({
                'leadership_chat_id': leadership_chat_id
            }).eq('team_id', self.team_id).execute()
            
            if response.data:
                return f"Successfully updated leadership chat ID to {leadership_chat_id}."
            else:
                return "Error updating leadership chat: No data returned."
        except Exception as e:
            return f"An exception occurred while updating leadership chat: {e}"

    def _get_team_members(self, supabase: Client, active_only: bool = True) -> str:
        try:
            query = supabase.table('team_members').select('*').eq('team_id', self.team_id)
            if active_only:
                query = query.eq('is_active', True)
            
            response = query.order('role').order('name').execute()
            if response.data:
                member_list = []
                for m in response.data:
                    status = "Active" if m['is_active'] else "Inactive"
                    member_list.append(f"- {m['name']} ({m['role']}) - {m['phone']} - {status}")
                return f"Team Members:\n" + "\n".join(member_list)
            else:
                return "No team members found."
        except Exception as e:
            return f"An exception occurred while fetching team members: {e}"

    def _add_team_member(self, supabase: Client, name: str, role: str, phone: str, telegram_username: Optional[str] = None) -> str:
        if not all([name, role, phone]):
            return "Error: 'name', 'role', and 'phone' are required."
        if role not in ['admin', 'secretary', 'manager', 'treasurer', 'player', 'helper']:
            return "Error: Role must be one of: admin, secretary, manager, treasurer, player, helper"
        
        try:
            member_data = {
                'team_id': self.team_id,
                'name': name,
                'role': role,
                'phone': phone,
                'is_active': True
            }
            if telegram_username:
                member_data['telegram_username'] = telegram_username
            
            response = supabase.table('team_members').insert(member_data).execute()
            if response.data:
                member = response.data[0]
                return f"Successfully added team member: {name} ({role}) (ID: {member['id']})."
            else:
                return "Error adding team member: No data returned."
        except Exception as e:
            return f"An exception occurred while adding team member: {e}"

    def _update_member_role(self, supabase: Client, member_id: str, new_role: str) -> str:
        if not all([member_id, new_role]):
            return "Error: 'member_id' and 'new_role' are required."
        if new_role not in ['admin', 'secretary', 'manager', 'treasurer', 'player', 'helper']:
            return "Error: Role must be one of: admin, secretary, manager, treasurer, player, helper"
        
        try:
            response = supabase.table('team_members').update({
                'role': new_role
            }).eq('id', member_id).eq('team_id', self.team_id).execute()
            
            if response.data:
                return f"Successfully updated member {member_id} role to {new_role}."
            else:
                return "Error updating member role: No data returned."
        except Exception as e:
            return f"An exception occurred while updating member role: {e}"

    def _get_members_by_role(self, supabase: Client, role: str) -> str:
        if not role:
            return "Error: 'role' is required."
        try:
            response = supabase.table('team_members').select('*').eq('team_id', self.team_id).eq('role', role).eq('is_active', True).order('name').execute()
            if response.data:
                member_list = []
                for m in response.data:
                    member_list.append(f"- {m['name']} ({m['phone']})")
                return f"Members with role '{role}':\n" + "\n".join(member_list)
            else:
                return f"No members found with role '{role}'."
        except Exception as e:
            return f"An exception occurred while fetching members by role: {e}"

# --- Command Logging Tools (Dual-Channel Support) ---

class CommandLoggingTools(BaseTool):
    name: str = "Command Logging Tool"
    description: str = "A tool to log bot commands and natural language interactions for audit purposes."

    def __init__(self, team_id: str):
        super().__init__(name="Command Logging Tool", description="A tool to log bot commands and natural language interactions for audit purposes.")
        object.__setattr__(self, 'team_id', team_id)

    def _run(self, command: str, **kwargs) -> str:
        supabase = get_supabase_client()
        if command == 'log_command':
            return self._log_command(supabase, **kwargs)
        elif command == 'get_command_logs':
            return self._get_command_logs(supabase, **kwargs)
        elif command == 'get_chat_logs':
            return self._get_chat_logs(supabase, **kwargs)
        else:
            return "Error: Unknown command. Available commands: 'log_command', 'get_command_logs', 'get_chat_logs'."

    def _log_command(self, supabase: Client, chat_id: str, user_id: str, command: str, username: Optional[str] = None, arguments: Optional[str] = None, success: bool = True, error_message: Optional[str] = None) -> str:
        if not all([chat_id, user_id, command]):
            return "Error: 'chat_id', 'user_id', and 'command' are required."
        
        try:
            log_data = {
                'team_id': self.team_id,
                'chat_id': chat_id,
                'user_id': user_id,
                'command': command,
                'success': success
            }
            if username:
                log_data['username'] = username
            if arguments:
                log_data['arguments'] = arguments
            if error_message:
                log_data['error_message'] = error_message
            
            response = supabase.table('command_logs').insert(log_data).execute()
            if response.data:
                return f"Successfully logged command: {command}"
            else:
                return "Error logging command: No data returned."
        except Exception as e:
            return f"An exception occurred while logging command: {e}"

    def _get_command_logs(self, supabase: Client, limit: int = 50, chat_id: Optional[str] = None) -> str:
        try:
            query = supabase.table('command_logs').select('*').eq('team_id', self.team_id).order('executed_at', desc=True).limit(limit)
            if chat_id:
                query = query.eq('chat_id', chat_id)
            
            response = query.execute()
            if response.data:
                log_list = []
                for log in response.data:
                    success = "✓" if log['success'] else "✗"
                    error = f" - Error: {log['error_message']}" if log['error_message'] else ""
                    log_list.append(f"{success} {log['command']} by {log['username'] or log['user_id']} at {log['executed_at']}{error}")
                return f"Command Logs:\n" + "\n".join(log_list)
            else:
                return "No command logs found."
        except Exception as e:
            return f"An exception occurred while fetching command logs: {e}"

    def _get_chat_logs(self, supabase: Client, chat_id: str, limit: int = 20) -> str:
        if not chat_id:
            return "Error: 'chat_id' is required."
        try:
            response = supabase.table('command_logs').select('*').eq('team_id', self.team_id).eq('chat_id', chat_id).order('executed_at', desc=True).limit(limit).execute()
            if response.data:
                log_list = []
                for log in response.data:
                    success = "✓" if log['success'] else "✗"
                    error = f" - Error: {log['error_message']}" if log['error_message'] else ""
                    log_list.append(f"{success} {log['command']} by {log['username'] or log['user_id']} at {log['executed_at']}{error}")
                return f"Chat Logs for {chat_id}:\n" + "\n".join(log_list)
            else:
                return f"No logs found for chat {chat_id}."
        except Exception as e:
            return f"An exception occurred while fetching chat logs: {e}"
