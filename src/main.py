"""
KICKAI - AI Football Team Management System
Main entry point for the CrewAI-based team management system.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from crewai import Crew, Process

# Load environment variables
load_dotenv()

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kickai_main.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def validate_environment():
    """Validate that all required environment variables are set."""
    logger.info("Validating environment variables...")
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the following variables:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False

    logger.info("All required environment variables are set")
    print("✅ All required environment variables are set")
    return True


def main():
    """Main function to run the KICKAI system."""
    logger.info("Starting KICKAI system...")
    
    print("##################################################")
    print("## Welcome to KICKAI - Your AI Football Manager ##")
    print("##################################################")

    # Validate environment
    if not validate_environment():
        sys.exit(1)

    try:
        # Import the new agent creation functions
        from src.agents import create_llm, create_agents, create_crew
        from src.tasks import create_tasks

        logger.info("Creating LLM...")
        llm = create_llm()
        
        logger.info("Creating agents...")
        agents = create_agents(llm)
        
        logger.info("Creating tasks...")
        tasks = create_tasks(agents)
        
        logger.info("Creating crew with tasks...")
        crew = create_crew(agents)
        
        # Update the crew with tasks
        crew.tasks = tasks

        print("✅ Crew created successfully")
        
        # Kick off the work
        print("\n🚀 Starting KICKAI system...")
        logger.info("Starting crew execution...")
        
        result = crew.kickoff()

        logger.info("Crew execution completed successfully")
        print("\n\n############################")
        print("## Here is the result:")
        print("############################\n")
        print(result)

    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed by running:")
        print("pip install crewai langchain-ollama python-dotenv supabase")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
