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


def main():
    """Main function to run the KICKAI system."""
    print("##################################################")
    print("## Welcome to KICKAI - Your AI Football Manager ##")
    print("##################################################")

    # Validate environment
    if not validate_environment():
        sys.exit(1)

    try:
        # Import agents and tasks now that environment is validated
        from src.agents import logistics_agent
        from src.tasks import PlayerTasks

        # Validate agent creation
        if not logistics_agent:
            print("❌ Error: Failed to create logistics agent")
            sys.exit(1)

        # Create tasks
        tasks = PlayerTasks()
        add_player_task = tasks.add_player_task(logistics_agent)
        list_players_task = tasks.list_players_task(logistics_agent)

        # --- CHOOSE WHICH TASK TO RUN ---
        # To run the 'add_player_task', set this to True.
        # To run the 'list_players_task', set this to False.
        run_add_player = False
        
        active_task = None
        if run_add_player:
            player_inputs = {
                'name': 'Phil Foden',
                'phone_number': '+447112233445'
            }
            # Format the task's description with the inputs
            add_player_task.description = add_player_task.description.format(**player_inputs)
            active_task = add_player_task
        else:
            active_task = list_players_task
        
        # Create the crew
        crew = Crew(
            agents=[logistics_agent],
            tasks=[active_task],
            process=Process.sequential,
            verbose=True
        )

        print("✅ Crew created successfully")
        
        # Kick off the work
        print("\n🚀 Starting KICKAI system...")
        result = crew.kickoff()

        print("\n\n############################")
        print("## Here is the result:")
        print("############################\n")
        print(result)

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed by running:")
        print("pip install crewai langchain-google-genai python-dotenv supabase")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
