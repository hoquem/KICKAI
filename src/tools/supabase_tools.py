import os
from dotenv import load_dotenv
from supabase import create_client, Client
from crewai.tools import BaseTool
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# Load environment variables from .env file
load_dotenv()

# --- Supabase Client Initialization ---
def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in the .env file.")
    return create_client(url, key)

# --- Player Management Tools ---

class PlayerTools(BaseTool):
    name: str = "Player Management Tool"
    description: str = "A tool to manage player data in the database. Use it to add, retrieve, update, or deactivate player information."

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
                'is_active': True
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
            response = supabase.table('players').select('id, name, phone_number, is_active, created_at').order('name').execute()
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
            query = supabase.table('players').select('*')
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
            
            response = supabase.table('players').update(update_data).eq('id', player_id).execute()
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
                'is_home_game': is_home_game
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
            query = supabase.table('fixtures').select('*').order('match_date')
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
            response = supabase.table('fixtures').select('*').eq('id', fixture_id).execute()
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
            
            response = supabase.table('fixtures').update(update_data).eq('id', fixture_id).execute()
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
    player_tool = PlayerTools()
    fixture_tool = FixtureTools()
    availability_tool = AvailabilityTools()
    
    # Test player tools
    print("=== Testing Player Tools ===")
    print(player_tool._run('get_all_players'))
    
    # Test fixture tools
    print("\n=== Testing Fixture Tools ===")
    print(fixture_tool._run('get_fixtures'))
