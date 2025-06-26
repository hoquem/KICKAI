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
        from src.agents import (
            logistics_agent, 
            manager_agent, 
            communications_agent, 
            tactical_agent, 
            finance_agent
        )
        from src.tasks import (
            PlayerTasks, 
            FixtureTasks, 
            AvailabilityTasks, 
            TeamManagementTasks, 
            CommunicationTasks
        )

        # Validate agent creation
        if not all([logistics_agent, manager_agent, communications_agent, tactical_agent, finance_agent]):
            print("❌ Error: Failed to create one or more agents")
            sys.exit(1)

        # Create task instances
        player_tasks = PlayerTasks()
        fixture_tasks = FixtureTasks()
        availability_tasks = AvailabilityTasks()
        team_tasks = TeamManagementTasks()
        comm_tasks = CommunicationTasks()

        # --- CHOOSE WHICH DEMO TO RUN ---
        # Available demos:
        # 1: List all players
        # 2: List all fixtures  
        # 3: Get availability for first fixture
        # 4: Team status report
        # 5: Squad selection analysis
        # 6: Payment report
        # 7: Create availability request message
        # 8: Create squad announcement message
        
        demo_choice = 1  # Change this number to run different demos
        
        active_task = None
        crew_agents = []
        
        if demo_choice == 1:
            # Demo 1: List all players
            active_task = player_tasks.list_players_task(logistics_agent)
            crew_agents = [logistics_agent]
            print("🎯 Running Demo 1: List all players")
            
        elif demo_choice == 2:
            # Demo 2: List all fixtures
            active_task = fixture_tasks.list_fixtures_task(logistics_agent)
            crew_agents = [logistics_agent]
            print("🎯 Running Demo 2: List all fixtures")
            
        elif demo_choice == 3:
            # Demo 3: Get availability for first fixture
            # First get fixtures to find the first one
            fixtures_task = fixture_tasks.list_fixtures_task(logistics_agent)
            fixtures_task.description = fixtures_task.description.format(upcoming_only=True)
            
            # Then get availability for the first fixture
            availability_task = availability_tasks.get_availability_task(logistics_agent)
            availability_task.description = availability_task.description.format(
                fixture_id="093d9286-0cc2-4252-8410-04fe7c184a51"  # First fixture from sample data
            )
            
            active_task = availability_task
            crew_agents = [logistics_agent]
            print("🎯 Running Demo 3: Get availability for first fixture")
            
        elif demo_choice == 4:
            # Demo 4: Team status report
            active_task = team_tasks.team_status_report_task(manager_agent)
            crew_agents = [manager_agent]
            print("🎯 Running Demo 4: Team status report")
            
        elif demo_choice == 5:
            # Demo 5: Squad selection analysis
            active_task = team_tasks.analyze_availability_task(tactical_agent)
            active_task.description = active_task.description.format(
                fixture_id="093d9286-0cc2-4252-8410-04fe7c184a51"  # First fixture from sample data
            )
            crew_agents = [tactical_agent]
            print("🎯 Running Demo 5: Squad selection analysis")
            
        elif demo_choice == 6:
            # Demo 6: Payment report
            active_task = team_tasks.payment_report_task(finance_agent)
            active_task.description = active_task.description.format(
                fixture_id="093d9286-0cc2-4252-8410-04fe7c184a51"  # First fixture from sample data
            )
            crew_agents = [finance_agent]
            print("🎯 Running Demo 6: Payment report")
            
        elif demo_choice == 7:
            # Demo 7: Create availability request message
            active_task = comm_tasks.availability_request_task(communications_agent)
            active_task.description = active_task.description.format(
                fixture_id="093d9286-0cc2-4252-8410-04fe7c184a51"  # First fixture from sample data
            )
            crew_agents = [communications_agent]
            print("🎯 Running Demo 7: Create availability request message")
            
        elif demo_choice == 8:
            # Demo 8: Create squad announcement message
            active_task = comm_tasks.squad_announcement_task(communications_agent)
            active_task.description = active_task.description.format(
                fixture_id="093d9286-0cc2-4252-8410-04fe7c184a51"  # First fixture from sample data
            )
            crew_agents = [communications_agent]
            print("🎯 Running Demo 8: Create squad announcement message")
            
        else:
            print("❌ Invalid demo choice. Please choose 1-8.")
            sys.exit(1)
        
        # Create the crew
        crew = Crew(
            agents=crew_agents,  # type: ignore
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
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
