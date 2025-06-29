import logging
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.supabase_tools import PlayerTools, FixtureTools, AvailabilityTools, TeamManagementTools, CommandLoggingTools
from src.tools.telegram_tools import (
    SendTelegramMessageTool,
    SendTelegramPollTool,
    SendAvailabilityPollTool,
    SendSquadAnnouncementTool,
    SendPaymentReminderTool,
    SendLeadershipMessageTool,
    get_telegram_tools_dual
)

# Import configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kickai_crewai.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_messaging_tools(team_id: str):
    """Get Telegram messaging tools for a specific team."""
    try:
        logger.info(f"Creating Telegram messaging tools for team {team_id}")
        return {
            'message_tool': SendTelegramMessageTool(team_id),
            'leadership_message_tool': SendLeadershipMessageTool(team_id),
            'poll_tool': SendTelegramPollTool(team_id),
            'availability_poll_tool': SendAvailabilityPollTool(team_id),
            'squad_announcement_tool': SendSquadAnnouncementTool(team_id),
            'payment_reminder_tool': SendPaymentReminderTool(team_id),
            'platform': 'Telegram'
        }
    except Exception as e:
        logger.error(f"Error creating Telegram tools for team {team_id}: {e}")
        raise ValueError(f"Failed to create Telegram tools for team {team_id}: {e}")

# Robust system prompt for CrewAI output format
CREWAI_SYSTEM_PROMPT = '''
You are a helpful, precise, and format-strict AI agent for a football team management system.

**IMPORTANT:** You must ALWAYS respond in the following format, and never deviate from it:

```
Thought: <your reasoning here>
Final Answer: <your complete, direct answer here>
```

If you are asked to use tools, always return the format:
```
Thought: <your reasoning>
Action: <tool name>
Action Input: <JSON input for the tool>
Observation: <result from the tool>
```

Once all actions are complete, always return the final answer in the first format above. Never return anything outside these formats. Your job depends on it!

---

**Available Tools and Commands (Cheat Sheet):**

- **Player Management Tool**
  - `add_player` (name, phone_number)
  - `get_all_players`
  - `get_player` (player_id or phone_number)
  - `update_player` (player_id, name/phone_number/is_active)
  - `deactivate_player` (player_id)

- **Fixture Management Tool**
  - `add_fixture` (opponent, match_date, location, is_home_game)
  - `get_fixtures` (upcoming_only)
  - `get_fixture` (fixture_id)
  - `update_fixture` (fixture_id, opponent/match_date/location/is_home_game/result)

- **Telegram Messaging Tools**
  - `send_telegram_message` (message)
  - `send_telegram_poll` (question, options)
  - `send_availability_poll` (fixture_details, match_date, match_time, location)
  - `send_squad_announcement` (fixture_details, match_date, match_time, starters, substitutes)
  - `send_payment_reminder` (unpaid_players, amount, fixture_details)

**Never use a command that is not listed above. If you are unsure, ask for clarification or use only the valid commands.**

---

**Tool Usage Examples:**

Example 1: List all players
```
Thought: I want to list all players in the team.
Action: Player Management Tool
Action Input: {"command": "get_all_players"}
Observation: All Players: - ID: 1, Name: John Doe, Phone: 123456789, Status: Active
Thought: I now know the final answer
Final Answer: The team currently has the following players: John Doe (Active).
```

Example 2: Get a specific player
```
Thought: I need to get information for player with ID 1.
Action: Player Management Tool
Action Input: {"command": "get_player", "player_id": "1"}
Observation: Player found: John Doe (ID: 1, Phone: 123456789, Active: True)
Thought: I now know the final answer
Final Answer: Player John Doe (ID: 1) is active and can be contacted at 123456789.
```

Example 3: Invalid tool usage (do NOT do this)
```
Thought: I want to describe the system.
Action: Player Management Tool
Action Input: {"command": "describe"}
Observation: Error: Unknown command. Available commands: 'add_player', 'get_all_players', 'get_player', 'update_player', 'deactivate_player'.
Thought: I should only use valid commands as listed above.
Final Answer: [Do not use invalid tool commands.]
```

Example 4: Add a new player
```
Thought: We need to add a new player named Alice Smith.
Action: Player Management Tool
Action Input: {"command": "add_player", "name": "Alice Smith", "phone_number": "5551234567"}
Observation: Successfully added player: Alice Smith (ID: 2).
Thought: I now know the final answer
Final Answer: Player Alice Smith has been added to the team.
```

Example 5: List all fixtures
```
Thought: I want to see all upcoming fixtures.
Action: Fixture Management Tool
Action Input: {"command": "get_fixtures", "upcoming_only": true}
Observation: Fixtures: - KICKAI vs Rivals (HOME) on 2024-12-01T14:00:00Z (ID: 10)
Thought: I now know the final answer
Final Answer: The next fixture is KICKAI vs Rivals at home on 2024-12-01.
```

Example 6: Send a Telegram message
```
Thought: I need to notify the team about the next match.
Action: send_telegram_message
Action Input: {"message": "Reminder: Our next match is this Sunday at 2pm. Please confirm your availability."}
Observation: Telegram message sent successfully! Message ID: 12345
Thought: I now know the final answer
Final Answer: The team has been notified about the next match via Telegram.
```
'''

def create_llm():
    """Create and configure the LLM instance based on environment."""
    try:
        # Validate configuration first
        if not config.validate_config():
            raise ValueError("Invalid configuration")
        
        ai_config = config.ai_config
        logger.info(f"Creating LLM with provider: {ai_config['provider']}")
        
        if ai_config['provider'] == 'google':
            # Use Google AI for production
            llm = ChatGoogleGenerativeAI(
                model=ai_config['model'],
                google_api_key=ai_config['api_key'],
                temperature=0.7,
                max_output_tokens=1000,
                system=CREWAI_SYSTEM_PROMPT
            )
            logger.info("✅ Google AI LLM created successfully")
            
        else:
            # Use Ollama for local development
            llm = Ollama(
                model=ai_config['model'],
                base_url=ai_config['base_url'],
                system=CREWAI_SYSTEM_PROMPT
            )
            logger.info("✅ Ollama LLM created successfully")
        
        return llm
        
    except Exception as e:
        logger.error(f"Failed to create LLM: {e}")
        raise


def create_agents_for_team(llm, team_id: str):
    """Create CrewAI agents for a specific team with refined architecture."""
    logger.info(f"Creating CrewAI agents for team {team_id} with refined architecture...")
    
    # Initialize tools with team context
    player_tools = PlayerTools(team_id)
    fixture_tools = FixtureTools(team_id)
    availability_tools = AvailabilityTools(team_id)
    team_management_tools = TeamManagementTools(team_id)
    command_logging_tools = CommandLoggingTools(team_id)
    
    # Get Telegram messaging tools for this team
    messaging_tools = get_messaging_tools(team_id)
    logger.info(f"Using {messaging_tools['platform']} for messaging team {team_id}")

    # 1. Message Processing Specialist Agent (Primary Interface)
    message_processor = Agent(
        role='Message Processing Specialist',
        goal='Interpret incoming Telegram messages, understand user intent, and route requests to appropriate team agents',
        backstory="""You are an expert at understanding human communication in the context of football team management. 
        You excel at interpreting natural language, understanding context, and determining the best way to handle 
        user requests. You can distinguish between simple queries, complex operations, and requests that require 
        multiple agents to collaborate. You maintain context of ongoing conversations and can handle follow-up 
        questions intelligently.""",
        verbose=True,
        allow_delegation=True,  # This agent can delegate to other agents
        tools=[
            command_logging_tools,  # For logging all incoming messages
            messaging_tools['message_tool']  # For asking clarifying questions
        ],
        llm=llm
    )
    logger.info(f"Message Processing Specialist agent created for team {team_id}")

    # 2. Team Manager Agent (Strategic Coordination)
    team_manager = Agent(
        role='Team Manager',
        goal='Manage the Sunday League football team operations, coordinate players, and ensure smooth team functioning',
        backstory="""You are an experienced football team manager with years of experience managing Sunday League teams. 
        You understand player dynamics, team morale, and the importance of clear communication. You excel at making 
        strategic decisions and coordinating between different team roles. You have a holistic view of the team and 
        can coordinate complex operations involving multiple agents.""",
        verbose=True,
        allow_delegation=True,  # Can coordinate other agents
        tools=[
            player_tools, 
            fixture_tools, 
            availability_tools,  # Added for strategic planning
            team_management_tools, 
            messaging_tools['message_tool'], 
            messaging_tools['leadership_message_tool']
        ],
        llm=llm
    )
    logger.info(f"Team Manager agent created for team {team_id}")

    # 3. Player Coordinator Agent (Operational Management)
    player_coordinator = Agent(
        role='Player Coordinator',
        goal='Coordinate player availability, manage player information, and handle player communications',
        backstory="""You are a dedicated player coordinator who knows every player personally. You track their availability, 
        preferences, and performance. You're excellent at communicating with players and ensuring everyone is informed 
        about team activities and requirements. You handle the day-to-day operational aspects of player management.""",
        verbose=True,
        allow_delegation=True,  # Can delegate to specialized agents
        tools=[
            player_tools, 
            availability_tools, 
            team_management_tools, 
            messaging_tools['message_tool'], 
            messaging_tools['availability_poll_tool'],
            messaging_tools['payment_reminder_tool'],  # Added for payment tracking
            command_logging_tools
        ],
        llm=llm
    )
    logger.info(f"Player Coordinator agent created for team {team_id}")

    # 4. Match Analyst Agent (Tactical Analysis)
    match_analyst = Agent(
        role='Match Analyst',
        goal='Analyze team performance, provide insights on tactics, and suggest improvements',
        backstory="""You are a tactical football analyst with deep knowledge of the game. You analyze match performances, 
        identify areas for improvement, and provide strategic insights. You help the team understand their strengths 
        and weaknesses to improve their game. You work closely with the squad selection specialist for optimal team composition.""",
        verbose=True,
        allow_delegation=True,  # Can delegate to squad selection specialist
        tools=[
            fixture_tools, 
            player_tools, 
            availability_tools,  # Added for squad analysis
            team_management_tools, 
            messaging_tools['squad_announcement_tool'], 
            command_logging_tools
        ],
        llm=llm
    )
    logger.info(f"Match Analyst agent created for team {team_id}")

    # 5. Communication Specialist Agent (Broadcast Management)
    communication_specialist = Agent(
        role='Communication Specialist',
        goal='Handle all team communications, announcements, and ensure clear information flow',
        backstory="""You are a communication expert who ensures all team members are well-informed and connected. 
        You handle announcements, coordinate messaging, and maintain clear communication channels. You're skilled 
        at crafting clear, engaging messages that keep the team motivated and informed. You coordinate with other 
        agents to ensure accurate and timely communications.""",
        verbose=True,
        allow_delegation=False,  # Focused on communication, not delegation
        tools=[
            messaging_tools['message_tool'], 
            messaging_tools['leadership_message_tool'],
            messaging_tools['poll_tool'], 
            messaging_tools['squad_announcement_tool'], 
            messaging_tools['payment_reminder_tool'],
            command_logging_tools
        ],
        llm=llm
    )
    logger.info(f"Communication Specialist agent created for team {team_id}")

    # 6. Finance Manager Agent (NEW - Specialized)
    finance_manager = Agent(
        role='Finance Manager',
        goal='Manage team finances, track payments, and handle financial reporting',
        backstory="""You are a dedicated finance manager responsible for tracking all team financial matters. 
        You monitor match fees, track payment status, and ensure financial transparency. You work closely with 
        the player coordinator to manage payment reminders and financial reporting. You maintain accurate records 
        and provide financial insights to the team management.""",
        verbose=True,
        allow_delegation=False,  # Specialized role, focused on finance
        tools=[
            availability_tools,  # For payment tracking
            messaging_tools['payment_reminder_tool'],
            team_management_tools,  # For financial reporting
            command_logging_tools
        ],
        llm=llm
    )
    logger.info(f"Finance Manager agent created for team {team_id}")

    # 7. Squad Selection Specialist Agent (NEW - Specialized)
    squad_selection_specialist = Agent(
        role='Squad Selection Specialist',
        goal='Select optimal squads based on availability, form, and tactics',
        backstory="""You are a squad selection expert with deep understanding of player positions, form, and 
        tactical requirements. You analyze player availability, consider tactical needs, and select the optimal 
        squad for each match. You work closely with the match analyst to understand tactical requirements and 
        with the player coordinator to understand availability. You ensure balanced squad selection with proper 
        cover for all positions.""",
        verbose=True,
        allow_delegation=False,  # Specialized role, focused on squad selection
        tools=[
            availability_tools,  # For availability data
            player_tools,  # For player information
            messaging_tools['squad_announcement_tool'],  # For announcing squads
            command_logging_tools
        ],
        llm=llm
    )
    logger.info(f"Squad Selection Specialist agent created for team {team_id}")

    # 8. Analytics Specialist Agent (NEW - Specialized)
    analytics_specialist = Agent(
        role='Performance Analytics Specialist',
        goal='Analyze team and player performance, provide insights and recommendations',
        backstory="""You are a performance analytics expert who provides deep insights into team and individual 
        player performance. You analyze match data, track performance trends, and provide actionable recommendations 
        for improvement. You work with historical data to identify patterns and suggest strategic improvements. 
        You provide detailed reports and insights to help the team improve their performance.""",
        verbose=True,
        allow_delegation=False,  # Specialized role, focused on analytics
        tools=[
            fixture_tools,  # For match data
            player_tools,  # For player performance data
            availability_tools,  # For participation data
            command_logging_tools
        ],
        llm=llm
    )
    logger.info(f"Analytics Specialist agent created for team {team_id}")

    logger.info(f"All 8 agents created successfully for team {team_id}")
    return (
        message_processor,      # Primary interface
        team_manager,           # Strategic coordination
        player_coordinator,     # Operational management
        match_analyst,          # Tactical analysis
        communication_specialist, # Broadcast management
        finance_manager,        # Financial management
        squad_selection_specialist, # Squad selection
        analytics_specialist    # Performance analytics
    )


def create_crew_for_team(agents):
    """Create a CrewAI crew with the specified agents for a team."""
    logger.info("Creating CrewAI crew with refined architecture...")
    
    message_processor, team_manager, player_coordinator, match_analyst, communication_specialist, finance_manager, squad_selection_specialist, analytics_specialist = agents
    
    crew = Crew(
        agents=[
            message_processor,      # Primary interface
            team_manager,           # Strategic coordination
            player_coordinator,     # Operational management
            match_analyst,          # Tactical analysis
            communication_specialist, # Broadcast management
            finance_manager,        # Financial management
            squad_selection_specialist, # Squad selection
            analytics_specialist    # Performance analytics
        ],
        verbose=True,
        memory=True
    )
    
    logger.info("Crew created successfully with 8 agents")
    return crew


# Legacy function for backward compatibility
def create_agents(llm):
    """Legacy function - use create_agents_for_team instead."""
    logger.warning("Using legacy create_agents function. Use create_agents_for_team with team_id instead.")
    # Use a default team ID for backward compatibility
    default_team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # BP Hatters FC
    return create_agents_for_team(llm, default_team_id)


def create_crew(agents):
    """Legacy function - use create_crew_for_team instead."""
    logger.warning("Using legacy create_crew function. Use create_crew_for_team instead.")
    return create_crew_for_team(agents)
