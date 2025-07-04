"""
Multi-Team Manager for KICKAI
Manages multiple teams and their associated bots/agents
"""

import asyncio
from typing import Dict, List, Optional, Any
import logging
from src.core.exceptions import KICKAIError, TeamError
from src.database.firebase_client import get_firebase_client
from src.services.team_service import get_team_service

class MultiTeamManager:
    """Manages multiple teams and their associated bots/agents."""
    
    def __init__(self):
        self.teams: Dict[str, Dict[str, Any]] = {}
        self.bots: Dict[str, Dict[str, Any]] = {}
        self.crews: Dict[str, Any] = {}
        self._initialize()
    
    def _initialize(self):
        """Initialize the multi-team manager."""
        try:
            # Get Firebase client
            firebase_client = get_firebase_client()
            self._load_teams(firebase_client)
            self._load_bots(firebase_client)
            self._initialize_crews()
        except Exception as e:
            logging.error("Failed to get Firebase client")
            raise TeamError(f"Failed to initialize multi-team manager: {str(e)}")
    
    def _load_teams(self, firebase_client):
        """Load all active teams from Firebase."""
        try:
            teams_ref = firebase_client.collection('teams')
            query = teams_ref.where('status', '==', 'active')
            docs = list(query.stream())
            
            for doc in docs:
                team_data = doc.to_dict()
                self.teams[doc.id] = team_data
            
            logging.info(f"Loaded {len(self.teams)} active teams")
        except Exception as e:
            logging.error("Failed to load teams")
            raise TeamError(f"Failed to load teams: {str(e)}")
    
    def _load_bots(self, firebase_client):
        """Load all bot mappings from Firebase."""
        try:
            bots_ref = firebase_client.collection('team_bots')
            query = bots_ref.where('is_active', '==', True)
            docs = list(query.stream())
            
            for doc in docs:
                bot_data = doc.to_dict()
                team_id = bot_data.get('team_id')
                if team_id:
                    self.bots[team_id] = bot_data
            
            logging.info(f"Loaded {len(self.bots)} bots for team {team_id}")
        except Exception as e:
            logging.error(f"Failed to load bots for team {team_id}")
            raise TeamError(f"Failed to load bots: {str(e)}")
    
    def _initialize_crews(self):
        """Initialize CrewAI crews for each team."""
        logging.info("Initializing Multi-Team Manager...")
        
        try:
            # Import CrewAI components
            from src.agents import create_llm, create_agents_for_team, create_crew_for_team
            
            # Create LLM
            llm = create_llm()
            if llm:
                logging.info("LLM created successfully")
            else:
                logging.warning("LLM creation failed, using fallback")
            
            # Initialize crews for each team
            for team_id, team_data in self.teams.items():
                team_name = team_data.get('name', 'Unknown Team')
                
                # Check if bot mapping exists
                if team_id not in self.bots:
                    logging.warning(f"Skipping team {team_name} (ID: {team_id}) - no bot mapping found")
                    continue
                
                try:
                    # Create agents and crew for this team
                    agents = create_agents_for_team(llm, team_id)
                    crew = create_crew_for_team(agents)
                    self.crews[team_id] = crew
                    
                    logging.info(f"Successfully initialized team: {team_name} (ID: {team_id})")
                except Exception as e:
                    logging.error(f"Failed to initialize team {team_name} (ID: {team_id})")
                    continue
            
            logging.info(f"Multi-Team Manager initialized with {len(self.crews)} teams")
        except Exception as e:
            logging.error("Failed to initialize crews")
            raise TeamError(f"Failed to initialize crews: {str(e)}")
    
    def get_crew(self, team_id: str) -> Optional[Any]:
        """Get the crew for a specific team."""
        if team_id not in self.crews:
            logging.error(f"No crew found for team {team_id}")
            return None
        return self.crews[team_id]
    
    async def run_team_tasks(self, team_id: str, tasks: List[str]) -> Optional[str]:
        """Run tasks for a specific team."""
        crew = self.get_crew(team_id)
        if not crew:
            return None
        
        team_name = self.teams.get(team_id, {}).get('name', 'Unknown Team')
        logging.info(f"Running tasks for team: {team_name} (ID: {team_id})")
        
        try:
            # Create tasks for the crew
            crew_tasks = []
            for task_description in tasks:
                from crewai import Task
                task = Task(
                    description=task_description,
                    agent=crew.agents[0]  # Use first agent for now
                )
                crew_tasks.append(task)
            
            # Execute tasks
            result = await crew.kickoff(tasks=crew_tasks)
            
            logging.info(f"Completed tasks for team: {team_name} (ID: {team_id})")
            return str(result)
        except Exception as e:
            logging.error(f"Error running tasks for team {team_id}")
            return None
    
    async def process_team_message(self, team_id: str, message: str, user_id: str) -> Optional[str]:
        """Process a message for a specific team."""
        crew = self.get_crew(team_id)
        if not crew:
            return None
        
        team_name = self.teams.get(team_id, {}).get('name', 'Unknown Team')
        logging.info(f"Running tasks for team: {team_name} (ID: {team_id})")
        
        try:
            # Create a task for message processing
            from crewai import Task
            task = Task(
                description=f"Process this message: {message}",
                agent=crew.agents[0]  # Use first agent for now
            )
            
            # Execute task
            result = await crew.kickoff(tasks=[task])
            
            return str(result)
        except Exception as e:
            logging.error(f"Error processing team {team_id}")
            return None
    
    def add_team(self, team_id: str, team_info: Dict[str, Any]) -> bool:
        """Add a new team to the manager."""
        try:
            self.teams[team_id] = team_info
            logging.info(f"Successfully added team: {team_info['name']} (ID: {team_id})")
            return True
        except Exception as e:
            logging.error(f"Failed to add team {team_id}")
            return False
    
    def remove_team(self, team_id: str) -> bool:
        """Remove a team from the manager."""
        if team_id in self.teams:
            team_name = self.teams[team_id].get('name', 'Unknown Team')
            del self.teams[team_id]
            if team_id in self.crews:
                del self.crews[team_id]
            logging.info(f"Removed team: {team_name} (ID: {team_id})")
            return True
        else:
            logging.warning(f"Team {team_id} not found in manager")
            return False

def main():
    """Main function for testing the multi-team manager."""
    logging.info("##################################################")
    logging.info("## KICKAI Multi-Team Manager ##")
    logging.info("##################################################")
    
    try:
        # Initialize manager
        manager = MultiTeamManager()
        
        # Get teams
        teams = list(manager.teams.values())
        
        if teams:
            logging.info(f"📋 Managed Teams ({len(teams)}):")
            for team in teams:
                status = "✅ Active" if team.get('status') == 'active' else "❌ Inactive"
                logging.info(f"  - {team['name']} (ID: {team['id'][:8]}...) - {status}")
        else:
            logging.warning("❌ No teams available. Please ensure teams are created and have bot mappings.")
            return
        
        # Run tasks for first team
        if teams:
            first_team = teams[0]
            team_id = first_team['id']
            
            logging.info(f"🚀 Running tasks for team: {first_team['name']}")
            
            # Example tasks
            tasks = [
                "List all players",
                "Show upcoming matches"
            ]
            
            result = asyncio.run(manager.run_team_tasks(team_id, tasks))
            
            if result:
                logging.info(f"✅ Results for {first_team['name']}:")
                logging.info(result)
            else:
                logging.warning(f"❌ No results for {first_team['name']}")
    except Exception as e:
        logging.error(f"Error in multi-team manager")

if __name__ == "__main__":
    main() 