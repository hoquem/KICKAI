"""
Multi-Team Manager for KICKAI
Manages multiple teams simultaneously with complete isolation between teams.
Each team has its own agents, tools, and Telegram bot/room.
"""

import logging
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from crewai import Crew

from src.agents import create_llm, create_agents_for_team, create_crew_for_team
from src.tasks import create_tasks

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kickai_multi_team.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """Get Supabase client with proper error handling."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("Missing Supabase environment variables")
    
    return create_client(url, key)


def get_active_teams() -> List[Dict]:
    """Get all active teams from the database."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('teams').select('*').eq('is_active', True).execute()
        
        if response.data:
            logger.info(f"Found {len(response.data)} active teams")
            return response.data
        else:
            logger.warning("No active teams found")
            return []
            
    except Exception as e:
        logger.error(f"Error fetching active teams: {e}")
        return []


def get_team_bot_mapping(team_id: str) -> Optional[Dict]:
    """Get the bot mapping for a specific team."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('team_bots').select('*').eq('team_id', team_id).eq('is_active', True).execute()
        
        if response.data:
            return response.data[0]
        else:
            logger.warning(f"No bot mapping found for team {team_id}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching bot mapping for team {team_id}: {e}")
        return None


class MultiTeamManager:
    """Manages multiple teams simultaneously with complete isolation."""
    
    def __init__(self):
        self.teams: Dict[str, Dict] = {}
        self.crews: Dict[str, Crew] = {}
        self.llm = None
        
    def initialize(self):
        """Initialize the multi-team manager."""
        logger.info("Initializing Multi-Team Manager...")
        
        # Create LLM instance (shared across teams)
        self.llm = create_llm()
        logger.info("LLM created successfully")
        
        # Load active teams
        active_teams = get_active_teams()
        
        for team in active_teams:
            team_id = team['id']
            team_name = team['name']
            
            # Check if team has bot mapping
            bot_mapping = get_team_bot_mapping(team_id)
            if not bot_mapping:
                logger.warning(f"Skipping team {team_name} (ID: {team_id}) - no bot mapping found")
                continue
            
            # Store team info
            self.teams[team_id] = {
                'name': team_name,
                'description': team.get('description', ''),
                'bot_mapping': bot_mapping
            }
            
            # Create agents and crew for this team
            try:
                agents = create_agents_for_team(self.llm, team_id)
                crew = create_crew_for_team(agents)
                self.crews[team_id] = crew
                logger.info(f"Successfully initialized team: {team_name} (ID: {team_id})")
                
            except Exception as e:
                logger.error(f"Failed to initialize team {team_name} (ID: {team_id}): {e}")
                continue
        
        logger.info(f"Multi-Team Manager initialized with {len(self.crews)} teams")
    
    def get_team_info(self, team_id: str) -> Optional[Dict]:
        """Get information about a specific team."""
        return self.teams.get(team_id)
    
    def list_teams(self) -> List[Dict]:
        """List all managed teams."""
        return [
            {
                'id': team_id,
                'name': team_info['name'],
                'description': team_info['description'],
                'has_crew': team_id in self.crews
            }
            for team_id, team_info in self.teams.items()
        ]
    
    def run_team_tasks(self, team_id: str, tasks: List) -> Optional[str]:
        """Run tasks for a specific team."""
        if team_id not in self.crews:
            logger.error(f"No crew found for team {team_id}")
            return None
        
        try:
            crew = self.crews[team_id]
            team_name = self.teams[team_id]['name']
            
            logger.info(f"Running tasks for team: {team_name} (ID: {team_id})")
            
            # Set tasks for the crew
            crew.tasks = tasks
            
            # Execute the crew
            result = crew.kickoff()
            
            logger.info(f"Completed tasks for team: {team_name} (ID: {team_id})")
            return str(result)
            
        except Exception as e:
            logger.error(f"Error running tasks for team {team_id}: {e}")
            return None
    
    def run_all_teams(self, task_creator_func) -> Dict[str, str]:
        """Run tasks for all teams using a task creator function."""
        results = {}
        
        for team_id in self.crews.keys():
            team_name = self.teams[team_id]['name']
            logger.info(f"Running tasks for team: {team_name} (ID: {team_id})")
            
            try:
                # Create tasks for this team
                agents = self.crews[team_id].agents
                tasks = task_creator_func(agents, team_id)
                
                # Run the tasks
                result = self.run_team_tasks(team_id, tasks)
                results[team_id] = result or "No result"
                
            except Exception as e:
                logger.error(f"Error processing team {team_id}: {e}")
                results[team_id] = f"Error: {str(e)}"
        
        return results
    
    def add_team(self, team_id: str, team_info: Dict, bot_mapping: Dict) -> bool:
        """Add a new team to the manager."""
        try:
            # Create agents and crew for the new team
            agents = create_agents_for_team(self.llm, team_id)
            crew = create_crew_for_team(agents)
            
            # Store team info
            self.teams[team_id] = {
                'name': team_info['name'],
                'description': team_info.get('description', ''),
                'bot_mapping': bot_mapping
            }
            self.crews[team_id] = crew
            
            logger.info(f"Successfully added team: {team_info['name']} (ID: {team_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add team {team_id}: {e}")
            return False
    
    def remove_team(self, team_id: str) -> bool:
        """Remove a team from the manager."""
        if team_id in self.teams:
            team_name = self.teams[team_id]['name']
            del self.teams[team_id]
            
            if team_id in self.crews:
                del self.crews[team_id]
            
            logger.info(f"Removed team: {team_name} (ID: {team_id})")
            return True
        else:
            logger.warning(f"Team {team_id} not found in manager")
            return False


def create_multi_team_tasks(agents, team_id: str):
    """Create tasks for a specific team."""
    # This is a placeholder - you would implement team-specific task creation here
    # For now, we'll use the existing task creation function
    return create_tasks(agents)


def main():
    """Main function to demonstrate multi-team management."""
    print("##################################################")
    print("## KICKAI Multi-Team Manager ##")
    print("##################################################")
    
    try:
        # Initialize the multi-team manager
        manager = MultiTeamManager()
        manager.initialize()
        
        # List all managed teams
        teams = manager.list_teams()
        print(f"\n📋 Managed Teams ({len(teams)}):")
        for team in teams:
            status = "✅ Ready" if team['has_crew'] else "❌ No Crew"
            print(f"  - {team['name']} (ID: {team['id'][:8]}...) - {status}")
        
        if not teams:
            print("❌ No teams available. Please ensure teams are created and have bot mappings.")
            return
        
        # Example: Run tasks for the first team
        if teams:
            first_team = teams[0]
            team_id = first_team['id']
            
            print(f"\n🚀 Running tasks for team: {first_team['name']}")
            
            # Create tasks for this team
            crew = manager.crews[team_id]
            tasks = create_multi_team_tasks(crew.agents, team_id)
            
            # Run the tasks
            result = manager.run_team_tasks(team_id, tasks)
            
            if result:
                print(f"\n✅ Results for {first_team['name']}:")
                print(result)
            else:
                print(f"❌ No results for {first_team['name']}")
        
    except Exception as e:
        logger.error(f"Error in multi-team manager: {e}")
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 