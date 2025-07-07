"""
Robust CrewAI Football Team Management System

This module provides a comprehensive, maintainable, and debuggable implementation
of a multi-agent system for managing Sunday League football teams.

Key improvements:
- Centralized configuration management
- Robust error handling and logging
- Clear separation of concerns
- Comprehensive validation
- Better agent specialization
- Improved debugging capabilities
"""

import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager
from functools import wraps
from src.core.config import get_config
from src.core.improved_config_system import get_improved_config

# Define missing classes if they don't exist
class MemoryEnhancedAgent:
    """Base class for agents with memory capabilities."""
    def __init__(self, memory_enabled: bool = True):
        self.memory_enabled = memory_enabled

class MemoryType(Enum):
    """Types of memory for agents."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"

class MemoryPriority(Enum):
    """Priority levels for memory storage."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Third-party imports with proper error handling
try:
    from dotenv import load_dotenv
    from crewai import Agent, Task, Crew
    from langchain.tools import BaseTool
    from langchain_community.llms import Ollama
except ImportError as e:
    raise ImportError(f"Required CrewAI dependencies missing: {e}")

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('team_management.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class AIProvider(Enum):
    """Supported AI providers."""
    GOOGLE_GEMINI = "google_gemini"
    OLLAMA = "ollama"
    OPENAI = "openai"


class AgentRole(Enum):
    """Defined agent roles in the system."""
    MESSAGE_PROCESSOR = "message_processor"
    TEAM_MANAGER = "team_manager"
    PLAYER_COORDINATOR = "player_coordinator"
    MATCH_ANALYST = "match_analyst"
    COMMUNICATION_SPECIALIST = "communication_specialist"
    FINANCE_MANAGER = "finance_manager"
    SQUAD_SELECTION_SPECIALIST = "squad_selection_specialist"
    ANALYTICS_SPECIALIST = "analytics_specialist"
    LEARNING_AGENT = "learning_agent"
    ONBOARDING_AGENT = "onboarding_agent"


@dataclass
class AIConfig:
    """Configuration for AI providers."""
    provider: AIProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    timeout_seconds: int = 30
    max_retries: int = 3


@dataclass
class TeamConfig:
    """Configuration for a football team."""
    team_id: str
    team_name: str
    chat_id: Optional[str] = None
    leadership_chat_id: Optional[str] = None
    bot_token: Optional[str] = None
    bot_username: Optional[str] = None
    is_active: bool = True


@dataclass
class AgentConfig:
    """Configuration for individual agents."""
    role: AgentRole
    enabled: bool = True
    max_iterations: int = 10
    allow_delegation: bool = True
    verbose: bool = True
    custom_tools: List[str] = field(default_factory=list)


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


class AgentInitializationError(Exception):
    """Raised when agent initialization fails."""
    pass


class LLMProviderError(Exception):
    """Raised when LLM provider encounters an error."""
    pass


def log_errors(func: Callable) -> Callable:
    """Decorator to log errors with full traceback."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    return wrapper


def validate_config(config: Any, required_fields: List[str]) -> None:
    """Validate that configuration has required fields."""
    missing_fields = []
    for field in required_fields:
        if not hasattr(config, field) or getattr(config, field) is None:
            missing_fields.append(field)
    
    if missing_fields:
        raise ConfigurationError(f"Missing required configuration fields: {missing_fields}")


class ConfigurationManager:
    """Centralized configuration management."""
    
    def __init__(self):
        self.ai_config = self._load_ai_config()
        self.agent_configs = self._load_agent_configs()
        self._validate_configurations()
    
    def _load_ai_config(self) -> AIConfig:
        """Load AI configuration from environment variables."""
        provider_str = get_config().ai.provider.value
        
        try:
            provider = AIProvider(provider_str)
        except ValueError:
            logger.warning(f"Unknown AI provider: {provider_str}, defaulting to Ollama")
            provider = AIProvider.OLLAMA
        
        return AIConfig(
            provider=provider,
            model_name=get_config().ai.model_name,
            api_key=get_config().ai.api_key,
            base_url=get_config().ai.base_url,
            temperature=float(get_config().ai.temperature),
            timeout_seconds=int(get_config().ai.timeout_seconds),
            max_retries=int(get_config().ai.max_retries)
        )
    
    def _load_agent_configs(self) -> Dict[AgentRole, AgentConfig]:
        """Load agent configurations."""
        configs = {}
        
        for role in AgentRole:
            enabled = get_config().agent[role.value].enabled == 'true'
            max_iterations = int(get_config().agent[role.value].max_iterations)
            allow_delegation = get_config().agent[role.value].allow_delegation == 'true'
            verbose = get_config().agent[role.value].verbose == 'true'
            
            configs[role] = AgentConfig(
                role=role,
                enabled=enabled,
                max_iterations=max_iterations,
                allow_delegation=allow_delegation,
                verbose=verbose
            )
        
        return configs
    
    def _validate_configurations(self) -> None:
        """Validate all configurations."""
        # Validate AI config
        if self.ai_config.provider in [AIProvider.GOOGLE_GEMINI, AIProvider.OPENAI]:
            if not self.ai_config.api_key:
                raise ConfigurationError(f"API key required for {self.ai_config.provider.value}")
        
        # Validate at least one agent is enabled
        if not any(config.enabled for config in self.agent_configs.values()):
            raise ConfigurationError("At least one agent must be enabled")
    
    def get_team_config(self, team_id: str) -> TeamConfig:
        """Get configuration for a specific team."""
        return TeamConfig(
            team_id=team_id,
            team_name=get_config().team[team_id].name,
            chat_id=get_config().team[team_id].chat_id,
            leadership_chat_id=get_config().team[team_id].leadership_chat_id,
            bot_token=get_config().team[team_id].bot_token,
            bot_username=get_config().team[team_id].bot_username,
            is_active=get_config().team[team_id].active == 'true'
        )


class LLMFactory:
    """Factory for creating LLM instances."""
    
    @staticmethod
    @log_errors
    def create_llm(config: AIConfig):
        """Create LLM instance based on configuration."""
        logger.info(f"Creating LLM with provider: {config.provider.value}")
        
        if config.provider == AIProvider.GOOGLE_GEMINI:
            return LLMFactory._create_google_llm(config)
        elif config.provider == AIProvider.OLLAMA:
            return LLMFactory._create_ollama_llm(config)
        elif config.provider == AIProvider.OPENAI:
            return LLMFactory._create_openai_llm(config)
        else:
            raise LLMProviderError(f"Unsupported AI provider: {config.provider}")
    
    @staticmethod
    def _create_google_llm(config: AIConfig):
        """Create Google Gemini LLM."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.api_key)
            llm = genai.GenerativeModel(config.model_name)
            logger.info("✅ Google Gemini LLM created successfully")
            return llm
        except ImportError:
            raise LLMProviderError("Google Generative AI package not installed")
        except Exception as e:
            raise LLMProviderError(f"Failed to create Google Gemini LLM: {e}")
    
    @staticmethod
    def _create_ollama_llm(config: AIConfig):
        """Create Ollama LLM."""
        try:
            llm = Ollama(
                model=config.model_name,
                base_url=config.base_url,
                temperature=config.temperature,
                timeout=config.timeout_seconds
            )
            logger.info("✅ Ollama LLM created successfully")
            return llm
        except Exception as e:
            raise LLMProviderError(f"Failed to create Ollama LLM: {e}")
    
    @staticmethod
    def _create_openai_llm(config: AIConfig):
        """Create OpenAI LLM."""
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=config.model_name,
                api_key=config.api_key,
                temperature=config.temperature,
                timeout=config.timeout_seconds
            )
            logger.info("✅ OpenAI LLM created successfully")
            return llm
        except ImportError:
            raise LLMProviderError("OpenAI package not installed")
        except Exception as e:
            raise LLMProviderError(f"Failed to create OpenAI LLM: {e}")


class BaseTeamAgent(MemoryEnhancedAgent):
    """Base class for all team-specific agents."""
    
    def __init__(self, team_config: TeamConfig, llm=None, tools: List[BaseTool] = None):
        """Initialize the base team agent."""
        super().__init__(team_config)
        
        self.llm = llm
        self.tools = tools or []
        self.agent_config = self._get_agent_config()
        
        # Initialize memory with team context
        if self.memory_enabled:
            self._initialize_team_memory()
    
    def _initialize_team_memory(self) -> None:
        """Initialize team-specific memory context."""
        try:
            # Store team information in semantic memory
            team_info = f"Team: {self.team_config.team_name} (ID: {self.team_config.team_id})"
            self.store_memory(
                content=team_info,
                memory_type=MemoryType.SEMANTIC,
                priority=MemoryPriority.HIGH,
                context={'team_id': self.team_config.team_id, 'type': 'team_info'}
            )
            
            logger.info(f"Initialized team memory for {self.team_config.team_name}")
        except Exception as e:
            logger.error(f"Failed to initialize team memory: {e}")
    
    def _get_agent_config(self) -> AgentConfig:
        """Get agent configuration from the config manager."""
        config_manager = get_improved_config()
        agent_configs = config_manager.configuration.metadata.get('agent_configs', {})
        
        # Get default config for this agent type
        default_config = AgentConfig(
            role=self._get_agent_role(),
            enabled=True,
            verbose=True,
            max_iterations=3,
            allow_delegation=True
        )
        
        # Override with specific config if available
        role_key = self._get_agent_role().value
        if role_key in agent_configs:
            specific_config = agent_configs[role_key]
            default_config.enabled = specific_config.get('enabled', default_config.enabled)
            default_config.verbose = specific_config.get('verbose', default_config.verbose)
            default_config.max_iterations = specific_config.get('max_iterations', default_config.max_iterations)
            default_config.allow_delegation = specific_config.get('allow_delegation', default_config.allow_delegation)
        
        return default_config
    
    @abstractmethod
    def _get_agent_role(self) -> AgentRole:
        """Get the role of this agent."""
        pass
    
    @abstractmethod
    def _get_agent_definition(self) -> Dict[str, Any]:
        """Get the agent definition for CrewAI."""
        pass
    
    def get_agent(self) -> Agent:
        """Get the CrewAI Agent instance."""
        if not self.agent_config.enabled:
            raise AgentInitializationError(f"Agent {self._get_agent_role().value} is disabled")
        
        definition = self._get_agent_definition()
        
        # Enhance backstory with memory context if available
        if self.memory_enabled:
            definition = self._enhance_definition_with_memory(definition)
        
        return Agent(
            role=definition['role'],
            goal=definition['goal'],
            backstory=definition['backstory'],
            verbose=self.agent_config.verbose,
            allow_delegation=self.agent_config.allow_delegation,
            max_iter=self.agent_config.max_iterations,
            max_rpm=self.agent_config.max_rpm,
            tools=self.tools,
            llm=self.llm
        )
    
    def _enhance_definition_with_memory(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance agent definition with memory context."""
        try:
            # Get team-specific memories
            team_memories = self.retrieve_memory(
                query=self.team_config.team_name,
                memory_type=MemoryType.SEMANTIC,
                limit=3
            )
            
            # Get recent patterns
            patterns = self.get_relevant_patterns(
                context={'team_id': self.team_config.team_id},
                pattern_type='team_interaction'
            )
            
            # Enhance backstory with memory context
            memory_context = ""
            if team_memories:
                memory_context += f"\n\nTeam Context: {' '.join(team_memories)}"
            
            if patterns:
                memory_context += f"\n\nRecent Patterns: {patterns}"
            
            if memory_context:
                definition['backstory'] += memory_context
                logger.debug(f"Enhanced agent definition with memory context for {self.team_config.team_name}")
        
        except Exception as e:
            logger.error(f"Failed to enhance definition with memory: {e}")
        
        return definition
    
    def process_with_memory(self, task_description: str, user_id: Optional[str] = None, 
                          chat_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a task with memory context."""
        try:
            # Store task in short-term memory
            if user_id and self.memory_enabled:
                self.store_memory(
                    content=f"Task: {task_description}",
                    memory_type=MemoryType.SHORT_TERM,
                    user_id=user_id,
                    priority=MemoryPriority.MEDIUM,
                    context=context or {}
                )
            
            # Get relevant memories for context
            relevant_memories = []
            if user_id and self.memory_enabled:
                relevant_memories = self.retrieve_memory(
                    query=task_description,
                    user_id=user_id,
                    limit=3
                )
            
            # Enhance task with memory context
            enhanced_task = task_description
            if relevant_memories:
                memory_context = f"\n\nRelevant context: {' '.join(relevant_memories)}"
                enhanced_task += memory_context
            
            # Get agent and execute task
            agent = self.get_agent()
            # Task creation (would be handled by crew in full implementation)
            # For now, return the enhanced task description
            return enhanced_task
            
        except Exception as e:
            logger.error(f"Failed to process task with memory: {e}")
            return task_description


class MessageProcessorAgent(BaseTeamAgent):
    """Agent responsible for processing and routing messages."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.MESSAGE_PROCESSOR
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            'role': 'AI Triage and Routing Specialist',
            'goal': 'Efficiently understand user intent from Telegram messages, ask for clarification on missing information, and route tasks to the correct specialized agent. Prioritize a smooth, concise, and helpful user experience.',
            'backstory': f"""You are the AI Triage and Routing Specialist for {self.team_config.team_name}, an expert in conversational AI for a Telegram-based chat system. Your primary responsibility is to be the first point of contact for all natural language requests.

            **Core Logic and Workflow:**

            1.  **Analyze Intent**: Scrutinize the user's message to determine their primary goal. Use the user's role and the chat type (Main vs. Leadership) as critical context.

            2.  **Handle Incomplete Information**: If a request is missing essential details (e.g., 'schedule a match' without a date), your immediate priority is to ask a clear, simple, and direct follow-up question to get the necessary information. Do not attempt to delegate a task that is incomplete.

            3.  **Ensure Clarity and Brevity**: All your responses and questions must be optimized for Telegram. Be concise, use bullet points for lists, and avoid long paragraphs. The user experience is paramount.

            4.  **Route to Specialists**: Once you have a clear, actionable request, delegate it to the appropriate agent (e.g., `PlayerCoordinatorAgent` for player-related tasks, `FinanceManagerAgent` for payments).

            5.  **Monitor and Improve (Feedback Loop)**: If you are uncertain about the user's intent or if a request is too ambiguous, you MUST delegate the task to the `LearningAgent`. This is your protocol for handling uncertainty and ensuring the system improves over time. You will log the confusing interaction for future analysis."""
        }


class TeamManagerAgent(BaseTeamAgent):
    """Agent responsible for overall team management."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.TEAM_MANAGER
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            'role': 'Head of Football Operations',
            'goal': 'Act as the central command for all team-related administrative tasks, ensuring seamless coordination between player management, match scheduling, and financial operations. Your primary focus is on high-level team configuration and operational oversight.',
            'backstory': f"""You are the strategic Head of Football Operations for {self.team_config.team_name}. 
            You are not just a manager; you are the operational backbone of the team. Your responsibilities include:
            - Modifying core team settings (e.g., team name, FA website URLs).
            - Managing the team's budget and financial rules at a high level.
            - Delegating specific tasks to other specialized agents (like Player Coordinator or Finance Manager).
            You must use your tools to fetch and update team-wide configurations and ensure all operational aspects are aligned with the team's strategic goals. You are the final point of authority on team settings."""
        }


class PlayerCoordinatorAgent(BaseTeamAgent):
    """Agent responsible for player management and coordination."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.PLAYER_COORDINATOR
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            'role': 'Club Secretary & Logistics Manager',
            'goal': 'To maintain a perfectly accurate register of all club personnel and assets, including player eligibility, equipment location, and volunteer duties.',
            'backstory': f"""You are the organizational backbone of {self.team_config.team_name}. You are a meticulous and highly organized administrator responsible for all non-financial records.

            **Your Core Responsibilities Are:**

            1.  **Player Administration**: 
                - Maintain the official player roster.
                - Track player status (e.g., injuries, suspensions).
                - Verify FA registration details to confirm eligibility for sanctioned matches.

            2.  **Equipment Logistics**:
                - Keep an up-to-date inventory of all club equipment (e.g., match kits, footballs, training cones, nets, recording equipment).
                - Track the custodian of each item (i.e., who is currently responsible for it).

            3.  **Volunteer & Duty Tracking**:
                - Record all non-playing, match-day duties assigned to players or members (e.g., acting as linesman, managing the kits, providing transport).

            You provide clear, factual answers based on the records. You collaborate closely with the `TreasurerAgent` to ensure a player's financial status is considered for eligibility, but you do not handle financial data yourself. You are the single source of truth for all administrative and logistical matters."""
        }


class FinanceManagerAgent(BaseTeamAgent):
    """Agent responsible for financial management and payments."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.FINANCE_MANAGER
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            'role': 'Team Treasurer',
            'goal': 'To ensure the team\'s finances are transparent, balanced, and every player\'s financial standing is accurately tracked.',
            'backstory': f"""You are the guardian of the team\'s finances for {self.team_config.team_name}. You meticulously track all incoming payments (subs, fines) and outgoing expenses (pitch fees, referees). You provide definitive answers on which players are paid-up and which are in arrears. You collaborate directly with the `ClubSecretaryAgent` to flag players who are financially ineligible."""
        }


class PerformanceAnalystAgent(BaseTeamAgent):
    """Agent responsible for strategic analysis of team performance and engagement."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.ANALYTICS_SPECIALIST # This will be mapped to the new role
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            'role': 'Performance & Engagement Analyst',
            'goal': 'To provide the team manager with actionable, data-driven insights into team performance, player engagement, and overall club health.',
            'backstory': f"""You are the strategic mind of {self.team_config.team_name}. You don't just report stats; you interpret them to tell a story about the team's performance and culture. Your analysis is holistic, covering both on-pitch and off-pitch contributions.

            **Your Analytical Workflow:**

            1.  **Delegate for Data**: Your first step is always to delegate. You will:
                - Task the `ClubSecretaryAgent` to get data on player eligibility, availability, and volunteer duties.
                - Task the `TreasurerAgent` to get data on players' financial standing.

            2.  **Synthesize and Analyze**: You will then synthesize this data to perform analyses such as:
                - **Performance Analysis**: Who are the top goal scorers? What is our win/loss record against certain teams? How does our performance change with different player lineups?
                - **Engagement Analysis**: Who are the most reliable players in terms of attendance? Who consistently volunteers for duties like linesman or managing equipment? Your reports should recognize and celebrate these club-focused contributions.

            3.  **Provide Strategic Recommendations**: Based on your analysis, you will provide clear, actionable recommendations. This could include suggesting a starting lineup for the next match, identifying players who deserve recognition, or highlighting a need for more players in a specific position.

            You are the gaffer's most trusted advisor, turning raw data into winning strategies."""
        }


class LearningAgent(BaseTeamAgent):

    """Agent responsible for learning and optimization."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.LEARNING_AGENT
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            'role': 'Learning and Optimization Specialist',
            'goal': 'Learn from interactions, improve natural language understanding, and optimize system performance',
            'backstory': f"""You are the advanced learning specialist for {self.team_config.team_name}. 
            You continuously improve the system's natural language processing capabilities. You analyze user 
            interactions, learn from patterns, and optimize how the system understands and responds to requests. 
            You work with the memory system to identify improvement opportunities and adapt to team-specific 
            communication patterns."""
        }


class OnboardingAgent(BaseTeamAgent):
    """Agent responsible for player onboarding."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.ONBOARDING_AGENT
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            'role': 'Club Welcome & Onboarding Guide',
            'goal': 'To provide a warm, welcoming, and fun onboarding experience for new players, while meticulously ensuring all required information is collected accurately and efficiently.',
            'backstory': f"""You are the official Welcome & Onboarding Guide for {self.team_config.team_name}. Your personality is that of the most enthusiastic and organized player on the team—the one who knows everyone and makes new people feel right at home.

            **Your Personality & Tone:**
            - **Fun & Informal**: Use a positive, encouraging, and slightly informal tone. Emojis are welcome! 👍⚽
            - **Patient & Clear**: Never overwhelm the user. Ask for one piece of information at a time and be very clear about what you need.
            - **Persistent but Polite**: While you're fun, you are also responsible for getting the job done. You must ensure the onboarding process is completed.

            **Your Onboarding Workflow:**

            1.  **The Welcome**: Always start with an enthusiastic welcome message, making the player feel excited to join.
            2.  **Step-by-Step Guidance**: Guide new players through each step of the onboarding process one by one (e.g., confirming name, providing emergency contact, etc.).
            3.  **Positive Reinforcement**: After a player provides a piece of information, confirm you've received it with a positive message (e.g., 'Awesome, got it!', 'Perfect, just a couple more things!').
            4.  **Timely Follow-ups**: If a player stalls during the process, you are responsible for sending a gentle and friendly reminder after a reasonable amount of time to encourage them to complete their registration.
            5.  **The Handover**: Once all information is collected, you will send a final congratulatory message and then formally notify the `ClubSecretaryAgent` that the new player is ready for final approval."""
        }


class AgentFactory:
    """Factory for creating team management agents."""
    
    AGENT_CLASSES = {
        AgentRole.MESSAGE_PROCESSOR: MessageProcessorAgent,
        AgentRole.TEAM_MANAGER: TeamManagerAgent,
        AgentRole.PLAYER_COORDINATOR: PlayerCoordinatorAgent,
        AgentRole.MATCH_ANALYST: MatchAnalystAgent,
        AgentRole.COMMUNICATION_SPECIALIST: CommunicationSpecialistAgent,
        AgentRole.FINANCE_MANAGER: FinanceManagerAgent,
        AgentRole.SQUAD_SELECTION_SPECIALIST: SquadSelectionSpecialistAgent,
        AgentRole.ANALYTICS_SPECIALIST: AnalyticsSpecialistAgent,
        AgentRole.LEARNING_AGENT: LearningAgent,
        AgentRole.ONBOARDING_AGENT: OnboardingAgent
    }
    
    @staticmethod
    @log_errors
    def create_agent(role: AgentRole,
                    team_config: TeamConfig,
                    agent_config: AgentConfig,
                    llm,
                    tools: List[BaseTool] = None) -> BaseTeamAgent:
        """Create a specific agent."""
        if role not in AgentFactory.AGENT_CLASSES:
            raise AgentInitializationError(f"Unknown agent role: {role}")
        
        agent_class = AgentFactory.AGENT_CLASSES[role]
        return agent_class(role, team_config, llm, tools)


class ToolsManager:
    """Manager for handling agent tools."""
    
    def __init__(self, team_config: TeamConfig):
        self.team_config = team_config
        self._tools_cache = {}
    
    @log_errors
    def get_tools_for_agent(self, role: AgentRole) -> List[BaseTool]:
        """Get tools for a specific agent role."""
        if role in self._tools_cache:
            return self._tools_cache[role]
        
        tools = []
        
        try:
            # Import tools dynamically to avoid circular dependencies
            from src.tools.firebase_tools import PlayerTools, FixtureTools, TeamTools, CommandLoggingTools, BotTools
            from src.tools.telegram_tools import (
                SendTelegramMessageTool, SendTelegramPollTool, SendAvailabilityPollTool,
                SendSquadAnnouncementTool, SendPaymentReminderTool, SendLeadershipMessageTool
            )
            from src.tools.learning_tools import LearningTools
            
            # Configure tools based on agent role
            if role == AgentRole.MESSAGE_PROCESSOR:
                tools.extend([
                    CommandLoggingTools(self.team_config.team_id),
                    SendTelegramMessageTool(self.team_config.team_id),
                    LearningTools(self.team_config.team_id)
                ])
            
            elif role == AgentRole.TEAM_MANAGER:
                tools.extend([
                    PlayerTools(self.team_config.team_id),
                    FixtureTools(self.team_config.team_id),
                    TeamTools(self.team_config.team_id),
                    BotTools(self.team_config.team_id),
                    SendTelegramMessageTool(self.team_config.team_id),
                    SendLeadershipMessageTool(self.team_config.team_id)
                ])
            
            elif role == AgentRole.PLAYER_COORDINATOR:
                tools.extend([
                    PlayerTools(self.team_config.team_id),
                    TeamTools(self.team_config.team_id),
                    SendTelegramMessageTool(self.team_config.team_id),
                    SendAvailabilityPollTool(self.team_config.team_id),
                    SendPaymentReminderTool(self.team_config.team_id),
                    CommandLoggingTools(self.team_config.team_id)
                ])
            
            elif role == AgentRole.MATCH_ANALYST:
                tools.extend([
                    FixtureTools(self.team_config.team_id),
                    PlayerTools(self.team_config.team_id),
                    TeamTools(self.team_config.team_id),
                    SendSquadAnnouncementTool(self.team_config.team_id),
                    CommandLoggingTools(self.team_config.team_id)
                ])
            
            elif role == AgentRole.COMMUNICATION_SPECIALIST:
                tools.extend([
                    SendTelegramMessageTool(self.team_config.team_id),
                    SendLeadershipMessageTool(self.team_config.team_id),
                    SendTelegramPollTool(self.team_config.team_id),
                    SendSquadAnnouncementTool(self.team_config.team_id),
                    SendPaymentReminderTool(self.team_config.team_id),
                    CommandLoggingTools(self.team_config.team_id)
                ])
            
            elif role == AgentRole.FINANCE_MANAGER:
                tools.extend([
                    SendPaymentReminderTool(self.team_config.team_id),
                    TeamTools(self.team_config.team_id),
                    CommandLoggingTools(self.team_config.team_id)
                ])
            
            elif role == AgentRole.SQUAD_SELECTION_SPECIALIST:
                tools.extend([
                    PlayerTools(self.team_config.team_id),
                    SendSquadAnnouncementTool(self.team_config.team_id),
                    CommandLoggingTools(self.team_config.team_id)
                ])
            
            elif role == AgentRole.ANALYTICS_SPECIALIST:
                tools.extend([
                    FixtureTools(self.team_config.team_id),
                    PlayerTools(self.team_config.team_id),
                    CommandLoggingTools(self.team_config.team_id)
                ])
            
            elif role == AgentRole.LEARNING_AGENT:
                tools.extend([
                    CommandLoggingTools(self.team_config.team_id),
                    SendTelegramMessageTool(self.team_config.team_id),
                    TeamTools(self.team_config.team_id),
                    PlayerTools(self.team_config.team_id)
                ])
            
            elif role == AgentRole.ONBOARDING_AGENT:
                tools.extend([
                    PlayerTools(self.team_config.team_id),
                    SendTelegramMessageTool(self.team_config.team_id),
                    CommandLoggingTools(self.team_config.team_id)
                ])
        
        except ImportError as e:
            logger.warning(f"Could not import tools for {role.value}: {e}")
        
        self._tools_cache[role] = tools
        return tools


class TeamManagementSystem:
    """Main system for managing football team operations."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.config_manager = ConfigurationManager()
        self.team_config = self.config_manager.get_team_config(team_id)
        self.tools_manager = ToolsManager(self.team_config)
        self.llm = None
        self.agents = {}
        self.crew = None
        
        self._initialize_system()
    
    @log_errors
    def _initialize_system(self) -> None:
        """Initialize the team management system."""
        logger.info(f"Initializing team management system for {self.team_config.team_name}")
        
        # Initialize LLM
        self.llm = LLMFactory.create_llm(self.config_manager.ai_config)
        if not self.llm:
            raise LLMProviderError("Failed to create LLM instance")
        
        # Initialize agents
        self._initialize_agents()
        
        # Create crew
        self._create_crew()
        
        logger.info(f"✅ Team management system initialized successfully for {self.team_config.team_name}")
    
    def _initialize_agents(self) -> None:
        """Initialize all agents."""
        logger.info("Initializing agents...")
        
        for role, agent_config in self.config_manager.agent_configs.items():
            if not agent_config.enabled:
                logger.info(f"Skipping disabled agent: {role.value}")
                continue
            
            try:
                tools = self.tools_manager.get_tools_for_agent(role)
                agent = AgentFactory.create_agent(role, self.team_config, agent_config, self.llm, tools)
                
                if agent.is_enabled():
                    self.agents[role] = agent
                    logger.info(f"✅ Agent {role.value} initialized successfully")
                else:
                    logger.warning(f"Agent {role.value} is disabled")
                    
            except Exception as e:
                logger.error(f"Failed to initialize agent {role.value}: {e}")
                # Continue with other agents
    
    def _create_crew(self) -> None:
        """Create the CrewAI crew."""
        if not self.agents:
            raise AgentInitializationError("No agents available to create crew")
        
        crew_agents = [agent.get_agent() for agent in self.agents.values() if agent.get_agent()]
        
        self.crew = Crew(
            agents=crew_agents,
            verbose=True,
            memory=True
        )
        
        logger.info(f"✅ Crew created successfully with {len(crew_agents)} agents")
    
    def get_agent(self, role: AgentRole) -> Optional[BaseTeamAgent]:
        """Get a specific agent by role."""
        return self.agents.get(role)
    
    def get_enabled_agents(self) -> List[BaseTeamAgent]:
        """Get all enabled agents."""
        return [agent for agent in self.agents.values() if agent.is_enabled()]
    
    def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> str:
        """Execute a task using the crew."""
        if not self.crew:
            raise AgentInitializationError("Crew not initialized")
        
        logger.info(f"Executing task: {task_description}")
        
        try:
            # Create task
            task = Task(
                description=task_description,
                agent=self.agents[AgentRole.MESSAGE_PROCESSOR].get_agent(),
                context=context or {}
            )
            
            # Execute task
            result = self.crew.kickoff(inputs={'task': task})
            
            logger.info("Task executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise
    
    @contextmanager
    def debug_mode(self):
        """Context manager for debug mode."""
        original_level = logger.level
        logger.setLevel(logging.DEBUG)
        
        try:
            logger.debug("Entering debug mode")
            yield
        finally:
            logger.setLevel(original_level)
            logger.debug("Exiting debug mode")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the system."""
        health_status = {
            'team_id': self.team_id,
            'team_name': self.team_config.team_name,
            'llm_initialized': self.llm is not None,
            'agents_count': len(self.agents),
            'crew_initialized': self.crew is not None,
            'enabled_agents': [],
            'disabled_agents': [],
            'errors': []
        }
        
        for role, agent_config in self.config_manager.agent_configs.items():
            if agent_config.enabled and role in self.agents:
                health_status['enabled_agents'].append(role.value)
            else:
                health_status['disabled_agents'].append(role.value)
        
        return health_status


# System prompt for CrewAI agents
SYSTEM_PROMPT = """
You are a world-class AI agent, operating as a specialized member of a sophisticated football team management system. Your persona is that of a highly efficient, detail-oriented, and proactive team operations expert.

**CORE DIRECTIVES - ADHERE AT ALL TIMES:**

1.  **Persona**: Act as a professional, knowledgeable, and helpful team assistant. Your tone should be clear, concise, and supportive.
2.  **Tool-First Approach**: You MUST use your tools to answer questions and perform actions. Do not rely on prior knowledge. Always assume the database is the single source of truth.
3.  **Formatting (Strict Adherence Required)**:

    *   **For Tool Use**:
        ```
        Thought: <Your logical reasoning for choosing the tool and parameters. Be explicit.>
        Action: <The exact name of the tool to be used.>
        Action Input: <A valid JSON object with the required parameters.>
        Observation: <The result from the tool.>
        ... (You can repeat this Thought/Action/Action Input/Observation cycle multiple times)
        Thought: <Your final thought process after analyzing all observations.>
        Final Answer: <The complete, final answer to the user's request.>
        ```

    *   **For General Responses (when no tool is needed)**:
        ```
        Thought: <A brief explanation of why no tool is necessary and how you arrived at the answer.>
        Final Answer: <The complete, final answer.>
        ```

4.  **Error Handling**:
    *   If a tool returns an error or unexpected output, do not stop.
    *   Your next `Thought` should be: "The previous tool call failed. I need to analyze the error and try a different approach."
    *   Attempt to recover by using a different tool or modifying the input. If you cannot recover after 2 attempts, your `Final Answer` should be: "I am sorry, but I was unable to complete your request due to an unexpected error. Please try again later."

5.  **Contextual Awareness**:
    *   Pay close attention to the `team_id` and other contextual information provided in the task.
    *   Use information from previous turns in the conversation to inform your actions, but always verify with your tools.

**EXAMPLE SCENARIO:**

User asks: "Who are the currently registered players on the team?"

**CORRECT RESPONSE:**
```
Thought: The user is asking for a list of registered players. The `PlayerTools` tool has a `get_all_players` function that should provide this information. I will call this tool to get the most up-to-date player list.
Action: PlayerTools
Action Input: { "action": "get_all_players" }
Observation: [{"player_id": "AB1", "name": "John Doe", "status": "active"}, {"player_id": "CD2", "name": "Jane Smith", "status": "pending"}]
Thought: The tool returned a list of two players. I will format this information into a clear, readable list for the user.
Final Answer: The currently registered players are:
- John Doe (ID: AB1, Status: Active)
- Jane Smith (ID: CD2, Status: Pending)
```
"""