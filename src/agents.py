import logging
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
from src.tools.supabase_tools import PlayerTools, FixtureTools, AvailabilityTools
from src.tools.telegram_tools import (
    SendTelegramMessageTool,
    SendTelegramPollTool,
    SendAvailabilityPollTool,
    SendSquadAnnouncementTool,
    SendPaymentReminderTool
)

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

def get_messaging_tools():
    """Get Telegram messaging tools."""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if telegram_token:
        logger.info("Using Telegram messaging tools")
        return {
            'message_tool': SendTelegramMessageTool(),
            'poll_tool': SendTelegramPollTool(),
            'availability_poll_tool': SendAvailabilityPollTool(),
            'squad_announcement_tool': SendSquadAnnouncementTool(),
            'payment_reminder_tool': SendPaymentReminderTool(),
            'platform': 'Telegram'
        }
    else:
        logger.error("TELEGRAM_BOT_TOKEN not configured. Please set up Telegram integration.")
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

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
    """Create and configure the LLM instance."""
    try:
        llm = Ollama(model="ollama/llama3.1:8b-instruct-q4_0", system=CREWAI_SYSTEM_PROMPT)
        logger.info("LLM created successfully with Ollama using robust system prompt")
        return llm
    except Exception as e:
        logger.error(f"Failed to create LLM: {e}")
        raise


def create_agents(llm):
    """Create CrewAI agents for the football team management system."""
    logger.info("Creating CrewAI agents...")
    
    # Initialize tools
    player_tools = PlayerTools()
    fixture_tools = FixtureTools()
    availability_tools = AvailabilityTools()
    
    # Get Telegram messaging tools
    messaging_tools = get_messaging_tools()
    logger.info(f"Using {messaging_tools['platform']} for messaging")

    # Team Manager Agent
    team_manager = Agent(
        role='Team Manager',
        goal='Manage the Sunday League football team operations, coordinate players, and ensure smooth team functioning',
        backstory="""You are an experienced football team manager with years of experience managing Sunday League teams. 
        You understand player dynamics, team morale, and the importance of clear communication. You excel at making 
        strategic decisions and coordinating between different team roles.""",
        verbose=True,
        allow_delegation=False,
        tools=[player_tools, fixture_tools, messaging_tools['message_tool']],
        llm=llm
    )
    logger.info("Team Manager agent created")

    # Player Coordinator Agent
    player_coordinator = Agent(
        role='Player Coordinator',
        goal='Coordinate player availability, manage player information, and handle player communications',
        backstory="""You are a dedicated player coordinator who knows every player personally. You track their availability, 
        preferences, and performance. You're excellent at communicating with players and ensuring everyone is informed 
        about team activities and requirements.""",
        verbose=True,
        allow_delegation=False,
        tools=[player_tools, availability_tools, messaging_tools['message_tool'], messaging_tools['availability_poll_tool']],
        llm=llm
    )
    logger.info("Player Coordinator agent created")

    # Match Analyst Agent
    match_analyst = Agent(
        role='Match Analyst',
        goal='Analyze team performance, provide insights on tactics, and suggest improvements',
        backstory="""You are a tactical football analyst with deep knowledge of the game. You analyze match performances, 
        identify areas for improvement, and provide strategic insights. You help the team understand their strengths 
        and weaknesses to improve their game.""",
        verbose=True,
        allow_delegation=False,
        tools=[fixture_tools, player_tools, messaging_tools['squad_announcement_tool']],
        llm=llm
    )
    logger.info("Match Analyst agent created")

    # Communication Specialist Agent
    communication_specialist = Agent(
        role='Communication Specialist',
        goal='Handle all team communications, announcements, and ensure clear information flow',
        backstory="""You are a communication expert who ensures all team members are well-informed and connected. 
        You handle announcements, coordinate messaging, and maintain clear communication channels. You're skilled 
        at crafting clear, engaging messages that keep the team motivated and informed.""",
        verbose=True,
        allow_delegation=False,
        tools=[
            messaging_tools['message_tool'], 
            messaging_tools['poll_tool'], 
            messaging_tools['squad_announcement_tool'], 
            messaging_tools['payment_reminder_tool']
        ],
        llm=llm
    )
    logger.info("Communication Specialist agent created")

    logger.info("All agents created successfully")
    return team_manager, player_coordinator, match_analyst, communication_specialist


def create_crew(agents):
    """Create a CrewAI crew with the specified agents."""
    logger.info("Creating CrewAI crew...")
    
    team_manager, player_coordinator, match_analyst, communication_specialist = agents
    
    crew = Crew(
        agents=[team_manager, player_coordinator, match_analyst, communication_specialist],
        verbose=True,
        memory=True
    )
    
    logger.info("Crew created successfully")
    return crew
