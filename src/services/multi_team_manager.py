"""
Multi-Team Manager for KICKAI
Manages multiple teams and their associated bots/agents
"""

import asyncio
from typing import Dict, List, Optional, Any
from src.core.logging import get_logger
from src.core.exceptions import KICKAIError, TeamError
from src.database.firebase_client import get_firebase_client
from src.services.team_service import get_team_service

# Use new structured logging
logger = get_logger(__name__)

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
            logger.error("Failed to get Firebase client", error=e)
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
            
            logger.info(f"Loaded {len(self.teams)} active teams")
        except Exception as e:
            logger.error("Failed to load teams", error=e)
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
            
            logger.info(f"Loaded {len(self.bots)} bots for team {team_id}")
        except Exception as e:
            logger.error(f"Failed to load bots for team {team_id}", error=e)
            raise TeamError(f"Failed to load bots: {str(e)}")
    
    def _initialize_crews(self):
        """Initialize CrewAI crews for each team."""
        logger.info("Initializing Multi-Team Manager...")
        
        try:
            # Import CrewAI components
            from src.agents import create_llm, create_agents_for_team, create_crew_for_team
            
            # Create LLM
            llm = create_llm()
            if llm:
                logger.info("LLM created successfully")
            else:
                logger.warning("LLM creation failed, using fallback")
            
            # Initialize crews for each team
            for team_id, team_data in self.teams.items():
                team_name = team_data.get('name', 'Unknown Team')
                
                # Check if bot mapping exists
                if team_id not in self.bots:
                    logger.warning(f"Skipping team {team_name} (ID: {team_id}) - no bot mapping found")
                    continue
                
                try:
                    # Create agents and crew for this team
                    agents = create_agents_for_team(llm, team_id)
                    crew = create_crew_for_team(agents)
                    self.crews[team_id] = crew
                    
                    logger.info(f"Successfully initialized team: {team_name} (ID: {team_id})")
                except Exception as e:
                    logger.error(f"Failed to initialize team {team_name} (ID: {team_id})", error=e)
                    continue
            
            logger.info(f"Multi-Team Manager initialized with {len(self.crews)} teams")
        except Exception as e:
            logger.error("Failed to initialize crews", error=e)
            raise TeamError(f"Failed to initialize crews: {str(e)}")
    
    def get_crew(self, team_id: str) -> Optional[Any]:
        """Get the crew for a specific team."""
        if team_id not in self.crews:
            logger.error(f"No crew found for team {team_id}")
            return None
        return self.crews[team_id]
    
    async def run_team_tasks(self, team_id: str, tasks: List[str]) -> Optional[str]:
        """Run tasks for a specific team."""
        crew = self.get_crew(team_id)
        if not crew:
            return None
        
        team_name = self.teams.get(team_id, {}).get('name', 'Unknown Team')
        logger.info(f"Running tasks for team: {team_name} (ID: {team_id})")
        
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
            
            logger.info(f"Completed tasks for team: {team_name} (ID: {team_id})")
            return str(result)
        except Exception as e:
            logger.error(f"Error running tasks for team {team_id}", error=e)
            return None
    
    async def process_team_message(self, team_id: str, message: str, user_id: str) -> Optional[str]:
        """Process a message for a specific team."""
        crew = self.get_crew(team_id)
        if not crew:
            return None
        
        team_name = self.teams.get(team_id, {}).get('name', 'Unknown Team')
        logger.info(f"Running tasks for team: {team_name} (ID: {team_id})")
        
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
            logger.error(f"Error processing team {team_id}", error=e)
            return None
    
    def add_team(self, team_id: str, team_info: Dict[str, Any]) -> bool:
        """Add a new team to the manager."""
        try:
            self.teams[team_id] = team_info
            logger.info(f"Successfully added team: {team_info['name']} (ID: {team_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to add team {team_id}", error=e)
            return False
    
    def remove_team(self, team_id: str) -> bool:
        """Remove a team from the manager."""
        if team_id in self.teams:
            team_name = self.teams[team_id].get('name', 'Unknown Team')
            del self.teams[team_id]
            if team_id in self.crews:
                del self.crews[team_id]
            logger.info(f"Removed team: {team_name} (ID: {team_id})")
            return True
        else:
            logger.warning(f"Team {team_id} not found in manager")
            return False

def main():
    """Main function for testing the multi-team manager."""
    logger.info("##################################################")
    logger.info("## KICKAI Multi-Team Manager ##")
    logger.info("##################################################")
    
    try:
        # Initialize manager
        manager = MultiTeamManager()
        
        # Get teams
        teams = list(manager.teams.values())
        
        if teams:
            logger.info(f"📋 Managed Teams ({len(teams)}):")
            for team in teams:
                status = "✅ Active" if team.get('status') == 'active' else "❌ Inactive"
                logger.info(f"  - {team['name']} (ID: {team['id'][:8]}...) - {status}")
        else:
            logger.warning("❌ No teams available. Please ensure teams are created and have bot mappings.")
            return
        
        # Run tasks for first team
        if teams:
            first_team = teams[0]
            team_id = first_team['id']
            
            logger.info(f"🚀 Running tasks for team: {first_team['name']}")
            
            # Example tasks
            tasks = [
                "List all players",
                "Show upcoming matches"
            ]
            
            result = asyncio.run(manager.run_team_tasks(team_id, tasks))
            
            if result:
                logger.info(f"✅ Results for {first_team['name']}:")
                logger.info(result)
            else:
                logger.warning(f"❌ No results for {first_team['name']}")
    except Exception as e:
        logger.error(f"Error in multi-team manager", error=e)

if __name__ == "__main__":
    main() 