import os
from dotenv import load_dotenv
from supabase import create_client, Client
from crewai.tools import BaseTool

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
    description: str = "A tool to manage player data in the database. Use it to add, retrieve, or update player information."

    def _run(self, command: str, **kwargs) -> str:
        supabase = get_supabase_client()
        if command == 'add_player':
            return self._add_player(supabase, **kwargs)
        elif command == 'get_all_players':
            return self._get_all_players(supabase)
        else:
            return "Error: Unknown command. Available commands: 'add_player', 'get_all_players'."

    def _add_player(self, supabase: Client, name: str, phone_number: str) -> str:
        if not name or not phone_number:
            return "Error: Both 'name' and 'phone_number' are required to add a player."
        try:
            response = supabase.table('players').insert({
                'name': name,
                'phone_number': phone_number
            }).execute()
            if response.data:
                return f"Successfully added player: {name}."
            else:
                return "Error adding player: No data returned from insert operation."
        except Exception as e:
            return f"An exception occurred while adding a player: {e}"

    def _get_all_players(self, supabase: Client) -> str:
        try:
            response = supabase.table('players').select('id, name, phone_number').eq('is_active', True).execute()
            if response.data:
                player_list = "\n".join([f"- ID: {p['id']}, Name: {p['name']}, Phone: {p['phone_number']}" for p in response.data])
                return f"Active Players:\n{player_list}"
            else:
                return "No active players found."
        except Exception as e:
            return f"An exception occurred while fetching players: {e}"

# --- Example Usage (for testing) ---
if __name__ == '__main__':
    player_tool = PlayerTools()
    # print(player_tool._run('add_player', name='John Doe', phone_number='+447123456789'))
    print(player_tool._run('get_all_players'))
