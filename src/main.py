"""
KICKAI - AI Football Team Management System
Main entry point for the CrewAI-based team management system.
"""

import os
import sys
from dotenv import load_dotenv
from crewai import Crew, Process

# Load environment variables
load_dotenv()

def validate_environment():
    """Validate that all required environment variables are set."""
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the following variables:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False
    
    print("✅ All required environment variables are set")
    return True

def create_crew():
    """Create the CrewAI crew with proper error handling."""
    try:
        # Import agents and tasks
        from src.agents import logistics_agent
        from src.tasks import PlayerTasks
        
        # Validate agent creation
        if not logistics_agent:
            print("❌ Error: Failed to create logistics agent")
            return None
        
        # Create tasks
        tasks = PlayerTasks()
        add_player_task = tasks.add_player_task(logistics_agent)
        list_players_task = tasks.list_players_task(logistics_agent)
        
        # Create the crew
        crew = Crew(
            agents=[logistics_agent],
            tasks=[
                # To add a player, uncomment the line below and provide the details
                # add_player_task,
                
                # To list all players, use this task
                list_players_task
            ],
            process=Process.sequential,
            verbose=True
        )
        
        print("✅ Crew created successfully")
        return crew
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed: pip install -r requirements.txt")
        return None
    except Exception as e:
        print(f"❌ Error creating crew: {e}")
        return None

def main():
    """Main function to run the KICKAI system."""
    print("##################################################")
    print("## Welcome to KICKAI - Your AI Football Manager ##")
    print("##################################################")
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Create crew
    crew = create_crew()
    if not crew:
        sys.exit(1)
    
    try:
        # Define the inputs for the task you want to run.
        # To add a player:
        # inputs = {
        #     'name': 'Lionel Messi',
        #     'phone_number': '+34612345678'
        # }
        
        # To list players, no inputs are needed:
        inputs = {} 

        print("\n🚀 Starting KICKAI system...")
        result = crew.kickoff(inputs=inputs)
        
        print("\n\n############################")
        print("## Here is the result:")
        print("############################\n")
        print(result)
        
    except Exception as e:
        print(f"❌ Error running crew: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
