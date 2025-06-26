import os
from dotenv import load_dotenv
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.supabase_tools import PlayerTools, FixtureTools, AvailabilityTools
from tools.whatsapp_tools import get_whatsapp_tools

# Load environment variables
load_dotenv()

# Instantiate all the tools
player_tools = PlayerTools()
fixture_tools = FixtureTools()
availability_tools = AvailabilityTools()
whatsapp_tools = get_whatsapp_tools()

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
    """Create the Logistics Coordinator Agent with comprehensive data management capabilities."""
    llm = get_llm()
    if not llm:
        raise Exception("Failed to initialize LLM.")
            
    return Agent(
        role='Logistics Coordinator',
        goal='Manage all team logistics data including player registration, fixture management, availability tracking, and match coordination.',
        backstory='You are a meticulous and efficient data handler who manages all player data, fixtures, and match logistics for the Sunday League football team. You ensure accurate record-keeping and smooth team operations. You can add players, manage fixtures, track availability, and coordinate squad selections.',
        llm=llm,
        tools=[player_tools, fixture_tools, availability_tools],
        allow_delegation=False,
        verbose=True
    )

def create_manager_agent():
    """Create the Manager Agent for high-level team management and decision making."""
    llm = get_llm()
    if not llm:
        raise Exception("Failed to initialize LLM.")
    
    return Agent(
        role='Team Manager',
        goal='Oversee all team management tasks, make strategic decisions about squad selection, and coordinate team activities.',
        backstory='You are the experienced manager of the Sunday League football team. You make important decisions about squad selection, manage team morale, and ensure the team is well-organized for matches. You work closely with the Logistics Coordinator to ensure all data is accurate and up-to-date.',
        llm=llm,
        tools=[player_tools, fixture_tools, availability_tools] + whatsapp_tools,
        allow_delegation=True,
        verbose=True
    )

def create_communications_agent():
    """Create the Communications Officer Agent for team messaging and announcements."""
    llm = get_llm()
    if not llm:
        raise Exception("Failed to initialize LLM.")
    
    return Agent(
        role='Communications Officer',
        goal='Handle all team communications, announcements, and messaging to keep players informed and engaged.',
        backstory='You are the team\'s communications specialist responsible for keeping all players informed about fixtures, availability requests, squad announcements, and team updates. You craft clear, engaging messages and ensure everyone stays connected. You use WhatsApp to send messages, polls, and announcements to the team group.',
        llm=llm,
        tools=[player_tools, fixture_tools, availability_tools] + whatsapp_tools,
        allow_delegation=False,
        verbose=True
    )

def create_tactical_agent():
    """Create the Tactical Assistant Agent for squad selection and match strategy."""
    llm = get_llm()
    if not llm:
        raise Exception("Failed to initialize LLM.")
    
    return Agent(
        role='Tactical Assistant',
        goal='Assist with squad selection, analyze player availability, and provide tactical recommendations for matches.',
        backstory='You are the tactical expert who helps with squad selection based on player availability, form, and tactical requirements. You analyze the available players and recommend the best starting XI and substitutes for each match.',
        llm=llm,
        tools=[player_tools, fixture_tools, availability_tools],
        allow_delegation=False,
        verbose=True
    )

def create_finance_agent():
    """Create the Finance Manager Agent for payment tracking and financial management."""
    llm = get_llm()
    if not llm:
        raise Exception("Failed to initialize LLM.")
    
    return Agent(
        role='Finance Manager',
        goal='Track match fees, manage payment status, and ensure financial records are accurate and up-to-date.',
        backstory='You are responsible for managing all financial aspects of the team, including tracking match fee payments, identifying unpaid players, and maintaining accurate financial records. You work closely with the Logistics Coordinator to ensure payment data is properly recorded.',
        llm=llm,
        tools=[availability_tools, player_tools] + whatsapp_tools,
        allow_delegation=False,
        verbose=True
    )

# Create agent instances
logistics_agent = create_logistics_agent()
manager_agent = create_manager_agent()
communications_agent = create_communications_agent()
tactical_agent = create_tactical_agent()
finance_agent = create_finance_agent()

# Export all agents for use in other modules
__all__ = [
    'logistics_agent',
    'manager_agent', 
    'communications_agent',
    'tactical_agent',
    'finance_agent'
]
