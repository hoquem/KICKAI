import os
from dotenv import load_dotenv
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.supabase_tools import PlayerTools

# Load environment variables
load_dotenv()

# Instantiate the tools
player_tools = PlayerTools()

def get_llm():
    """Initialize and return the LLM with proper error handling."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        verbose=True,
        temperature=0.5,
        google_api_key=api_key
    )

def create_logistics_agent():
    """Create the Logistics Coordinator Agent with proper error handling."""
    llm = get_llm()
    if not llm:
        raise Exception("Failed to initialize LLM.")
            
    return Agent(
        role='Logistics Coordinator',
        goal='Manage all team logistics data including player registration, availability tracking, and match coordination.',
        backstory='You are a meticulous and efficient data handler who manages all player data, fixtures, and match logistics for the Sunday League football team. You ensure accurate record-keeping and smooth team operations.',
        llm=llm,
        tools=[player_tools],
        allow_delegation=False,
        verbose=True
    )

# Create agent instances
logistics_agent = create_logistics_agent()
