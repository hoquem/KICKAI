import os
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Gemini model
def get_llm():
    """Initialize and return the LLM with proper error handling."""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        return ChatGoogleGenerativeAI(
            model="gemini-pro",
            verbose=True,
            temperature=0.5,
            google_api_key=api_key
        )
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return None

# Create the Logistics Coordinator Agent
def create_logistics_agent():
    """Create the Logistics Coordinator Agent with proper error handling."""
    try:
        llm = get_llm()
        if not llm:
            return None
            
        return Agent(
            role='Logistics Coordinator',
            goal='Manage all team logistics data including player registration, availability tracking, and match coordination.',
            backstory='You are a meticulous and efficient data handler who manages all player data, fixtures, and match logistics for the Sunday League football team. You ensure accurate record-keeping and smooth team operations.',
            llm=llm,
            tools=[],  # Will be populated with PlayerTools and other database tools
            allow_delegation=False,
            verbose=True
        )
    except Exception as e:
        print(f"Error creating logistics agent: {e}")
        return None

# Create agent instances
logistics_agent = create_logistics_agent()

# TODO: Add other agents (ManagerAgent, CommunicationsOfficerAgent, TreasurerAgent, TeamAdminAgent)
# when the basic system is working
