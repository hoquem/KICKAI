"""
Robust CrewAI Football Team Management System - 7-Agent Architecture

This module provides a comprehensive, maintainable, and debuggable implementation
of a specialized 7-agent system for managing Sunday League football teams.

7-Agent Architecture:
1. Message Processor: Primary user interface and command parsing
2. Team Manager: Strategic coordination and high-level planning
3. Player Coordinator: Operational player management and registration
4. Finance Manager: Financial tracking and payment management
5. Performance Analyst: Performance analysis and tactical insights
6. Learning Agent: Continuous learning and system improvement
7. Onboarding Agent: Specialized player onboarding and registration

Key improvements:
- Centralized configuration management
- Robust error handling and logging
- Clear separation of concerns
- Comprehensive validation
- Specialized agent roles with focused responsibilities
- Improved debugging capabilities
- Memory-enhanced agent capabilities
"""

import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager
from functools import wraps
from core.improved_config_system import get_improved_config
from datetime import datetime
import time # Added for timestamp in store_memory

# Define missing classes if they don't exist
class MemoryEnhancedAgent:
    """Base class for agents with memory capabilities."""
    def __init__(self, memory_enabled: bool = True):
        self.memory_enabled = memory_enabled
        self._memory_store = {}  # Simple in-memory storage for patterns and memories
        
    def store_memory(self, *args, **kwargs):
        """Store memory with optional parameters."""
        if not self.memory_enabled:
            return
            
        content = kwargs.get('content', '')
        memory_type = kwargs.get('memory_type', MemoryType.SHORT_TERM)
        priority = kwargs.get('priority', MemoryPriority.MEDIUM)
        user_id = kwargs.get('user_id', 'system')
        context = kwargs.get('context', {})
        
        # Store in memory store
        memory_key = f"{memory_type.value}_{user_id}_{int(time.time())}"
        self._memory_store[memory_key] = {
            'content': content,
            'memory_type': memory_type,
            'priority': priority,
            'user_id': user_id,
            'context': context,
            'timestamp': time.time()
        }
        
        logger.debug(f"Stored memory: {memory_key}")
        
    def retrieve_memory(self, *args, **kwargs):
        """Retrieve memories based on query and filters."""
        if not self.memory_enabled:
            return []
            
        query = kwargs.get('query', '')
        memory_type = kwargs.get('memory_type', None)
        user_id = kwargs.get('user_id', None)
        limit = kwargs.get('limit', 10)
        
        # Filter memories based on criteria
        relevant_memories = []
        for key, memory in self._memory_store.items():
            # Check memory type filter
            if memory_type and memory['memory_type'] != memory_type:
                continue
                
            # Check user filter
            if user_id and memory['user_id'] != user_id:
                continue
                
            # Check if content matches query (simple substring match)
            if query and query.lower() in memory['content'].lower():
                relevant_memories.append(memory['content'])
            elif not query:
                relevant_memories.append(memory['content'])
        
        # Sort by timestamp (newest first) and limit results
        relevant_memories.sort(key=lambda x: self._memory_store.get(x, {}).get('timestamp', 0), reverse=True)
        return relevant_memories[:limit]
        
    def get_relevant_patterns(self, context: Dict[str, Any] = None, pattern_type: str = None) -> List[str]:
        """
        Get relevant patterns based on context and pattern type.
        
        Args:
            context: Context dictionary (e.g., {'team_id': 'KAI'})
            pattern_type: Type of patterns to retrieve (e.g., 'team_interaction', 'user_behavior')
            
        Returns:
            List of relevant patterns as strings
        """
        if not self.memory_enabled:
            return []
            
        # Extract context information
        team_id = context.get('team_id') if context else None
        user_id = context.get('user_id') if context else None
        
        # Define pattern templates based on pattern type
        pattern_templates = {
            'team_interaction': [
                f"Team {team_id} members typically ask about registration status",
                f"Team {team_id} leadership frequently approves new players",
                f"Team {team_id} players often inquire about match schedules",
                f"Team {team_id} has regular payment inquiries"
            ],
            'user_behavior': [
                f"User {user_id} prefers concise responses",
                f"User {user_id} frequently asks for status updates",
                f"User {user_id} tends to use natural language queries",
                f"User {user_id} responds well to structured information"
            ],
            'system_performance': [
                "Player registration typically takes 30-60 seconds",
                "Approval processes are usually completed within 1-2 minutes",
                "Status inquiries are resolved in under 10 seconds",
                "Payment processing requires additional verification steps"
            ],
            'error_patterns': [
                "Duplicate player registrations are common",
                "Missing phone numbers cause registration failures",
                "Invalid player IDs lead to approval errors",
                "Incomplete information requires follow-up questions"
            ]
        }
        
        # Get patterns based on type
        if pattern_type and pattern_type in pattern_templates:
            patterns = pattern_templates[pattern_type]
        else:
            # Return general patterns if no specific type
            patterns = [
                "Users prefer immediate responses to status inquiries",
                "Team management tasks require careful validation",
                "Player registration is the most common operation",
                "Leadership chat handles approval workflows"
            ]
        
        # Filter patterns based on context
        relevant_patterns = []
        for pattern in patterns:
            # Simple relevance check - if context matches pattern content
            if team_id and team_id in pattern:
                relevant_patterns.append(pattern)
            elif user_id and user_id in pattern:
                relevant_patterns.append(pattern)
            elif not team_id and not user_id:
                # If no specific context, return general patterns
                relevant_patterns.append(pattern)
        
        # Limit results to avoid overwhelming the agent
        return relevant_patterns[:5]


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


# Remove the local AgentRole definition and import from src.core.enums
from src.core.enums import AgentRole


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
        provider_str = get_improved_config().configuration.ai.provider.value
        
        try:
            provider = AIProvider(provider_str)
        except ValueError:
            logger.warning(f"Unknown AI provider: {provider_str}, defaulting to Ollama")
            provider = AIProvider.OLLAMA
        
        ai_config = get_improved_config().configuration.ai
        return AIConfig(
            provider=provider,
            model_name=ai_config.model_name,
            api_key=ai_config.api_key,
            base_url=getattr(ai_config, 'base_url', None),
            temperature=float(getattr(ai_config, 'temperature', 0.7)),
            timeout_seconds=int(getattr(ai_config, 'timeout_seconds', 30)),
            max_retries=int(getattr(ai_config, 'max_retries', 3))
        )
    
    def _load_agent_configs(self) -> Dict[AgentRole, AgentConfig]:
        """Load agent configurations."""
        configs = {}
        agent_configs = get_improved_config().configuration.metadata.get('agent_configs', {})
        for role in AgentRole:
            config = agent_configs.get(role.value, {})
            enabled = config.get('enabled', True)
            max_iterations = config.get('max_iterations', 10)
            allow_delegation = config.get('allow_delegation', True)
            verbose = config.get('verbose', True)
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
        team_config = get_improved_config().configuration.team
        return TeamConfig(
            team_id=team_id,
            team_name=getattr(team_config, 'default_team_id', team_id),
            chat_id=getattr(team_config, 'chat_id', None),
            leadership_chat_id=getattr(team_config, 'leadership_chat_id', None),
            bot_token=getattr(team_config, 'bot_token', None),
            bot_username=getattr(team_config, 'bot_username', None),
            is_active=getattr(team_config, 'is_active', True)
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
            base_url = config.base_url or 'http://localhost:11434'
            llm = Ollama(
                model=config.model_name,
                base_url=base_url,
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
    
    def __init__(self, team_config: TeamConfig, llm=None, tools: List[BaseTool] = None, agent_config: AgentConfig = None):
        self.team_config = team_config
        super().__init__(memory_enabled=True)
        self.llm = llm
        self.tools = tools or []
        # Use passed agent_config if provided, otherwise load default
        self.agent_config = agent_config or self._get_agent_config()
        # Initialize memory with team context
        if self.memory_enabled:
            self._initialize_team_memory()

    def is_enabled(self):
        return self.agent_config.enabled
    
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

    def execute(self, description: str, parameters: dict) -> str:
        """Unified agent execution interface for subtasks."""
        # By default, use process_with_memory for execution
        return self.process_with_memory(description, context=parameters)


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

            5.  **Monitor and Improve (Feedback Loop)**: If you are uncertain about the user's intent or if a request is too ambiguous, you MUST delegate the task to the `LearningAgent`. This is your protocol for handling uncertainty and ensuring the system improves over time. You will log the confusing interaction for future analysis.

            **COMMON USER QUERIES AND EXPECTED RESPONSES:**

            **Player Information Queries:**
            - "What's my registration status?" → Check player database, show registration status, FA status, onboarding progress
            - "What's my player ID?" → Look up and display player ID
            - "Show me my phone number" → Display player's phone number
            - "What position do I play?" → Show player's position
            - "Am I FA registered?" → Check and display FA registration status
            - "What's my status?" → Show overall player status (active, pending, etc.)
            - "How do I update my info?" → Provide guidance on updating player information

            **Team Information Queries:**
            - "How many players do we have?" → Count and display total players
            - "Show me all players" → List all team players with basic info
            - "Who are the goalkeepers?" → Filter and show players by position
            - "List pending players" → Show players awaiting approval
            - "Show me active players" → Display currently active players
            - "What's the team status?" → Provide team overview and statistics

            **Match and Fixture Queries:**
            - "When's the next match?" → Check match schedule and show next fixture
            - "Show me upcoming matches" → Display future match schedule
            - "What was the last result?" → Show most recent match result
            - "Who's playing this weekend?" → Check match attendance and squad
            - "What time is kickoff?" → Show match details including time

            **Financial Queries:**
            - "What do I owe?" → Check player's outstanding payments
            - "Show me my payment history" → Display player's payment records
            - "How much are subs?" → Show current subscription fees
            - "When are payments due?" → Display payment deadlines
            - "Am I paid up?" → Check if player is financially current

            **Registration and Onboarding:**
            - "How do I register?" → Provide registration instructions
            - "I want to join the team" → Guide through registration process
            - "What do I need to register?" → List registration requirements
            - "Is my registration complete?" → Check onboarding status

            **Admin/Leadership Queries (Leadership Chat Only):**
            - "Add a new player" → Guide through player addition process
            - "Approve John Smith" → Process player approval
            - "Show pending approvals" → List players awaiting approval
            - "Remove inactive players" → Help with player removal
            - "Update team settings" → Assist with team configuration

            **General Help Queries:**
            - "What can you help me with?" → Provide overview of available features
            - "How do I use this bot?" → Show available commands and features
            - "Help" → Display help information
            - "What commands are available?" → List available slash commands

            **RESPONSE FORMAT GUIDELINES:**
            - Use emojis for visual appeal and quick recognition
            - Keep responses concise and scannable
            - Use bullet points for lists
            - Include relevant data when available
            - Provide clear next steps when needed
            - Be helpful and encouraging in tone

            **CONTEXT AWARENESS:**
            - Leadership chat users have admin privileges
            - Main chat users have limited access
            - Check user permissions before providing sensitive information
            - Adapt response detail based on user role

            **ERROR HANDLING:**
            - If information is missing, ask specific questions
            - If user is not registered, guide them to registration
            - If permission denied, explain why and suggest alternatives
            - Always be helpful, even when declining requests"""
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
        return AgentRole.PERFORMANCE_ANALYST
    
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
    """Specialized agent for player onboarding and registration."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.ONBOARDING_AGENT
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            "name": "Onboarding Specialist",
            "role": """You are a specialized onboarding agent for Sunday League football teams. 
            Your expertise is in guiding new players through the registration process with patience and clarity.
            
            Key responsibilities:
            - Guide players through step-by-step registration
            - Collect and validate player information
            - Explain team policies and requirements
            - Handle registration errors gracefully
            - Provide clear next steps
            
            You excel at:
            - Breaking down complex processes into simple steps
            - Adapting to different user communication styles
            - Providing helpful error messages and solutions
            - Maintaining a welcoming and professional tone""",
            "goal": "Ensure smooth and complete player onboarding with excellent user experience",
            "backstory": """You have years of experience in sports team administration and understand 
            the importance of making new players feel welcome while ensuring all necessary information 
            is collected accurately. You know that a good onboarding experience sets the tone for 
            a player's entire team experience.""",
            "verbose": True,
            "allow_delegation": True
        }


class CommandFallbackAgent(BaseTeamAgent):
    """Sophisticated NLP agent for handling failed command parsing with context awareness."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.COMMAND_FALLBACK_AGENT
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            "name": "Command Interpreter",
            "role": """You are a sophisticated natural language processing agent specialized in 
            interpreting failed command parsing scenarios. You excel at understanding user intent 
            even when commands are malformed, incomplete, or use natural language instead of 
            structured commands.
            
            Your expertise includes:
            - Understanding user intent from failed slash commands
            - Extracting structured data from natural language
            - Providing helpful suggestions and corrections
            - Collaborating with other agents to execute actions
            - Learning from user patterns to improve future interactions
            
            Key capabilities:
            - Command intent recognition (add, register, approve, list, etc.)
            - Entity extraction (names, phone numbers, positions, etc.)
            - Context awareness (user role, chat type, team context)
            - Error recovery and user guidance
            - Seamless integration with existing command system
            
            You work closely with:
            - PlayerCoordinatorAgent for player management actions
            - TeamManagerAgent for team-level operations
            - OnboardingAgent for registration processes
            - MessageProcessorAgent for command routing
            
            ---
            
            Examples of user input and how you should interpret them:
            
            1. /add John Smith 07123456789 midfielder
               → Add player: name=John Smith, phone=+447123456789, position=midfielder
            2. add Sarah O'Connor 07987654321 defender
               → Add player: name=Sarah O'Connor, phone=+447987654321, position=defender
            3. Please add a new player called Mike Brown, phone 07811223344, position striker
               → Add player: name=Mike Brown, phone=+447811223344, position=striker
            4. /register Jane Doe 07700900123 goalkeeper
               → Register player: name=Jane Doe, phone=+447700900123, position=goalkeeper
            5. approve player 12345
               → Approve player: player_id=12345
            6. /approve Sarah O'Connor
               → Approve player: name=Sarah O'Connor
            7. /add John 07123456789
               → Add player: name=John, phone=+447123456789, position=Any (default)
            8. /add 07123456789 midfielder
               → Missing name. Ask user for name.
            9. /add John Smith midfielder
               → Missing phone. Ask user for phone.
            10. /add John Smith 07123456789
                → Add player: name=John Smith, phone=+447123456789, position=Any (default)
            11. /add John Smith 07123456789 midfielder true
                → Add player: name=John Smith, phone=+447123456789, position=midfielder, admin_approved=True
            12. /add John Smith 07123456789
                → Add player: name=John Smith, phone=+447123456789, position=Any (default)
            
            What to do if information is missing:
            - If a required field is missing (name or phone), ask the user for it in a friendly, clear way.
            - If the position is missing, default to 'Any'. Optionally, ask the user if they want to specify a position.
            - If the command is ambiguous, clarify with the user before taking action.
            - Always confirm the extracted information before executing an action.
            
            ---
            
            Your goal is to transform failed command parsing into successful user actions through intelligent NLP and agent collaboration.
            """,
            "goal": "Transform failed command parsing into successful user actions through intelligent NLP and agent collaboration",
            "backstory": """You were designed specifically to handle the complex scenarios where 
            users attempt to use commands but they fail due to parsing issues. You understand that 
            users often think in natural language even when trying to use structured commands, and 
            you bridge this gap with sophisticated language understanding and agent collaboration.
            
            You've learned to recognize patterns like:
            - Multi-word names in commands
            - Various phone number formats
            - Position variations and abbreviations
            - Context-dependent command meanings
            - User intent even with typos or missing parameters""",
            "verbose": True,
            "allow_delegation": True
        }
    
    async def process_failed_command(self, failed_command: str, error_message: str, 
                                   user_context: Dict[str, Any]) -> str:
        """
        Process a failed command using sophisticated NLP and agent collaboration.
        
        Args:
            failed_command: The original command that failed
            error_message: The error message from command parsing
            user_context: User context including role, chat type, etc.
            
        Returns:
            Response message with action taken or guidance provided
        """
        try:
            # Create a specialized task for command interpretation
            task_description = f"""
            COMMAND FALLBACK ANALYSIS:
            
            Failed Command: {failed_command}
            Error Message: {error_message}
            User Context: {user_context}
            
            Your task is to:
            1. Analyze the failed command and understand user intent
            2. Extract relevant entities (names, phone numbers, positions, etc.)
            3. Determine the appropriate action to take
            4. Collaborate with other agents if needed
            5. Provide a helpful response to the user
            
            Focus on:
            - Understanding what the user was trying to accomplish
            - Extracting structured data from the command
            - Providing clear guidance or executing the intended action
            - Learning from this interaction to improve future parsing
            """
            
            # Process with memory and context
            result = self.process_with_memory(
                task_description=task_description,
                user_id=user_context.get('user_id'),
                chat_id=user_context.get('chat_id'),
                context={
                    'failed_command': failed_command,
                    'error_message': error_message,
                    'user_context': user_context,
                    'team_id': self.team_config.team_id
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in command fallback processing: {e}")
            return f"🤖 I understand you're trying to use a command, but I'm having trouble processing it. Could you try rephrasing your request in natural language? For example, instead of '/add name phone position', you could say 'Add a new player named [name] with phone [phone] as [position]'."


class AgentFactory:
    """
    Factory for creating team management agents in the 7-agent system.
    
    Maps AgentRole enum values to their corresponding agent classes:
    - MESSAGE_PROCESSOR -> MessageProcessorAgent
    - TEAM_MANAGER -> TeamManagerAgent  
    - PLAYER_COORDINATOR -> PlayerCoordinatorAgent
    - FINANCE_MANAGER -> FinanceManagerAgent
    - PERFORMANCE_ANALYST -> PerformanceAnalystAgent
    - LEARNING_AGENT -> LearningAgent
    - ONBOARDING_AGENT -> OnboardingAgent
    """
    
    AGENT_CLASSES = {
        AgentRole.MESSAGE_PROCESSOR: MessageProcessorAgent,
        AgentRole.TEAM_MANAGER: TeamManagerAgent,
        AgentRole.PLAYER_COORDINATOR: PlayerCoordinatorAgent,
        AgentRole.FINANCE_MANAGER: FinanceManagerAgent,
        AgentRole.PERFORMANCE_ANALYST: PerformanceAnalystAgent,
        AgentRole.LEARNING_AGENT: LearningAgent,
        AgentRole.ONBOARDING_AGENT: OnboardingAgent,
        AgentRole.COMMAND_FALLBACK_AGENT: CommandFallbackAgent
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
        return agent_class(team_config, llm, tools, agent_config)


class ToolsManager:
    """
    Manager for handling agent tools in the 7-agent system.
    
    Maps tools to specific agent roles based on their responsibilities:
    
    - MESSAGE_PROCESSOR: Logging and messaging tools
    - TEAM_MANAGER: Player management, messaging, and announcement tools
    - PLAYER_COORDINATOR: Player management, polling, and coordination tools
    - FINANCE_MANAGER: Messaging and logging tools for financial operations
    - PERFORMANCE_ANALYST: Player analysis and announcement tools
    - LEARNING_AGENT: Comprehensive tools for learning and analysis
    - ONBOARDING_AGENT: Player management and messaging tools for onboarding
    """
    
    def __init__(self, team_config: TeamConfig):
        self.team_config = team_config
        self._tools_cache = {}
        self.logger = logging.getLogger(__name__)
    
    @log_errors
    def get_tools_for_agent(self, role: AgentRole) -> List[BaseTool]:
        """Get tools for a specific agent role."""
        if role in self._tools_cache:
            return self._tools_cache[role]
        
        tools = []
        
        try:
            # Import domain tools that are actually implemented
            from domain.tools import (
                GetAllPlayersTool,
                GetPlayerByIdTool,
                GetPendingApprovalsTool,
                SendMessageTool,
                SendPollTool,
                SendAnnouncementTool,
                LogCommandTool,
                LogEventTool
            )
            
            # Get command operations for tool dependencies
            from services.command_operations_factory import get_command_operations
            command_operations = get_command_operations()
            
            # Configure tools based on agent role
            if role == AgentRole.MESSAGE_PROCESSOR:
                tools.extend([
                    LogCommandTool(self.team_config.team_id),
                    SendMessageTool(self.team_config.team_id),
                    LogEventTool(self.team_config.team_id)
                ])
            
            elif role == AgentRole.TEAM_MANAGER:
                tools.extend([
                    GetAllPlayersTool(self.team_config.team_id, command_operations),
                    GetPlayerByIdTool(self.team_config.team_id, command_operations),
                    SendMessageTool(self.team_config.team_id),
                    SendAnnouncementTool(self.team_config.team_id),
                    LogCommandTool(self.team_config.team_id),
                    LogEventTool(self.team_config.team_id)
                ])
            
            elif role == AgentRole.PLAYER_COORDINATOR:
                tools.extend([
                    GetAllPlayersTool(self.team_config.team_id, command_operations),
                    GetPlayerByIdTool(self.team_config.team_id, command_operations),
                    GetPendingApprovalsTool(self.team_config.team_id, command_operations),
                    SendMessageTool(self.team_config.team_id),
                    SendPollTool(self.team_config.team_id),
                    LogCommandTool(self.team_config.team_id),
                    LogEventTool(self.team_config.team_id)
                ])
            
            elif role == AgentRole.FINANCE_MANAGER:
                tools.extend([
                    SendMessageTool(self.team_config.team_id),
                    LogCommandTool(self.team_config.team_id),
                    LogEventTool(self.team_config.team_id)
                ])
            
            elif role == AgentRole.PERFORMANCE_ANALYST:
                tools.extend([
                    GetAllPlayersTool(self.team_config.team_id, command_operations),
                    GetPlayerByIdTool(self.team_config.team_id, command_operations),
                    SendAnnouncementTool(self.team_config.team_id),
                    LogCommandTool(self.team_config.team_id),
                    LogEventTool(self.team_config.team_id)
                ])
            
            elif role == AgentRole.LEARNING_AGENT:
                tools.extend([
                    LogCommandTool(self.team_config.team_id),
                    SendMessageTool(self.team_config.team_id),
                    GetAllPlayersTool(self.team_config.team_id, command_operations),
                    GetPlayerByIdTool(self.team_config.team_id, command_operations),
                    LogEventTool(self.team_config.team_id)
                ])
            
            elif role == AgentRole.ONBOARDING_AGENT:
                tools.extend([
                    GetAllPlayersTool(self.team_config.team_id, command_operations),
                    GetPlayerByIdTool(self.team_config.team_id, command_operations),
                    SendMessageTool(self.team_config.team_id),
                    LogCommandTool(self.team_config.team_id),
                    LogEventTool(self.team_config.team_id)
                ])
            
            self.logger.info(f"✅ Configured {len(tools)} tools for {role.value}")
        
        except ImportError as e:
            self.logger.warning(f"Could not import tools for {role.value}: {e}")
        except Exception as e:
            self.logger.error(f"Error configuring tools for {role.value}: {e}")
        
        self._tools_cache[role] = tools
        return tools


class TeamManagementSystem:
    """
    Main system for managing football team operations using the 7-agent architecture.
    
    The system coordinates 7 specialized agents:
    1. Message Processor: Handles user interface and command parsing
    2. Team Manager: Provides strategic coordination and planning
    3. Player Coordinator: Manages player operations and registration
    4. Finance Manager: Handles financial tracking and payments
    5. Performance Analyst: Analyzes performance and provides insights
    6. Learning Agent: Continuously learns and improves the system
    7. Onboarding Agent: Specializes in player onboarding workflows
    
    Each agent has specific tools and capabilities tailored to their role.
    """
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.team_config = get_improved_config(team_id)
        self.llm = self._initialize_llm()
        self.agents = {}
        self.capability_matrix = AgentCapabilityMatrix()
        self.user_preference_learner = UserPreferenceLearner()  # Add preference learner
        self._initialize_agents()
        logger.info(f"✅ TeamManagementSystem initialized for team {team_id}")
    
    def _initialize_llm(self):
        """Initialize the LLM based on configuration."""
        config_manager = ConfigurationManager()
        llm_config = config_manager.ai_config
        return LLMFactory.create_llm(llm_config)
    
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
        """
        Expert-level intelligent task execution using the full intelligent system pipeline.
        
        This method implements sophisticated task processing:
        1. Intent classification to understand user intent
        2. Complexity assessment to determine processing approach
        3. Dynamic task decomposition for complex requests
        4. Capability-based routing to optimal agents
        5. Orchestrated execution with dependency management
        6. Result aggregation and user preference learning
        
        Args:
            task_description: The user's request or task description
            context: Additional context including user_id, team_id, etc.
            
        Returns:
            str: The processed result or error message
        """
        if not self.crew:
            raise AgentInitializationError("Crew not initialized")
        
        logger.info(f"🔍 [Intelligent System] Processing task: {task_description}")
        
        try:
            # Initialize intelligent system components
            from .intelligent_system import (
                IntentClassifier, RequestComplexityAssessor, DynamicTaskDecomposer,
                CapabilityBasedRouter, TaskExecutionOrchestrator, UserPreferenceLearner,
                TaskContext, TaskComplexity, Subtask, CapabilityType
            )
            
            # Extract context information
            user_id = context.get('user_id', 'unknown') if context else 'unknown'
            team_id = self.team_id
            user_history = context.get('user_history', []) if context else []
            
            # 1. INTENT CLASSIFICATION
            logger.info(f"🎯 [Step 1] Classifying intent for user {user_id}")
            intent_classifier = IntentClassifier(llm=self.llm)
            intent_result = intent_classifier.classify(task_description)
            primary_intent = intent_result.primary_intent
            entities = intent_result.entities or {}
            confidence = intent_result.confidence
            
            logger.info(f"✅ Intent classified: {primary_intent} (confidence: {confidence:.2f})")
            logger.debug(f"📋 Extracted entities: {entities}")
            
            # 2. COMPLEXITY ASSESSMENT
            logger.info(f"🧠 [Step 2] Assessing request complexity")
            complexity_assessor = RequestComplexityAssessor()
            complexity_result = complexity_assessor.assess(
                request=task_description,
                intent=primary_intent,
                entities=entities,
                context=context or {},
                dependencies=[],
                user_id=user_id,
                user_history=user_history
            )
            
            complexity_level = complexity_result.complexity_level
            complexity_score = complexity_result.score
            reasoning = complexity_result.reasoning
            
            logger.info(f"✅ Complexity assessed: {complexity_level.name} (score: {complexity_score:.2f})")
            logger.debug(f"💭 Reasoning: {reasoning}")
            
            # 3. TASK DECOMPOSITION (if complex)
            if complexity_level.value > TaskComplexity.SIMPLE.value:
                logger.info(f"🔧 [Step 3] Decomposing complex task into subtasks")
                decomposer = DynamicTaskDecomposer(llm=self.llm)
                
                # Create task context
                task_context = TaskContext(
                    task_id=f"task_{int(datetime.now().timestamp())}",
                    user_id=user_id,
                    team_id=team_id,
                    parameters=entities,
                    metadata={
                        'intent': primary_intent,
                        'complexity': complexity_level.name,
                        'confidence': confidence
                    }
                )
                
                subtasks = decomposer.decompose(task_description, task_context)
                logger.info(f"✅ Task decomposed into {len(subtasks)} subtasks")
                
                for i, subtask in enumerate(subtasks, 1):
                    logger.debug(f"  Subtask {i}: {subtask.description} -> {subtask.agent_role.name}")
            else:
                logger.info(f"⚡ [Step 3] Simple task - no decomposition needed")
                # Create single subtask for simple requests using the unified Subtask type
                task_context = TaskContext(
                    task_id=f"task_{int(datetime.now().timestamp())}",
                    user_id=user_id,
                    team_id=team_id,
                    parameters=entities,
                    metadata={'intent': primary_intent}
                )
                
                # Create a proper Subtask from the TaskContext
                subtasks = [Subtask.from_task_context(
                    task_context=task_context,
                    description=task_description,
                    agent_role=AgentRole.MESSAGE_PROCESSOR,  # Default for simple tasks
                    capabilities_required=[CapabilityType.INTENT_ANALYSIS]
                )]
            
            # 4. CAPABILITY-BASED ROUTING
            logger.info(f"🎯 [Step 4] Routing subtasks to optimal agents")
            router = CapabilityBasedRouter(self.capability_matrix)
            routing_results = router.route_multiple(subtasks, list(self.agents.values()))
            
            logger.info(f"✅ Routed {len(routing_results)} subtasks to agents")
            for task_id, routing_info in routing_results.items():
                agent_role = routing_info['agent_role']
                logger.debug(f"  Task {task_id} -> {agent_role.value}")
            
            # 5. TASK EXECUTION ORCHESTRATION
            logger.info(f"🚀 [Step 5] Executing subtasks with orchestration")
            orchestrator = TaskExecutionOrchestrator(self.capability_matrix)
            execution_results = orchestrator.execute_tasks(subtasks, list(self.agents.values()), router)
            
            # 6. RESULT AGGREGATION
            logger.info(f"📊 [Step 6] Aggregating execution results")
            successful_results = []
            failed_results = []
            
            for task_id, result in execution_results.items():
                if result.success:
                    successful_results.append(result.result)
                    logger.debug(f"✅ Subtask {task_id} completed successfully")
                else:
                    failed_results.append(f"Subtask {task_id}: {result.error}")
                    logger.warning(f"❌ Subtask {task_id} failed: {result.error}")
            
            # 7. USER PREFERENCE LEARNING
            logger.info(f"🧠 [Step 7] Learning from user interaction")
            interaction_data = {
                'user_message': task_description,
                'intent': primary_intent,
                'entities': entities,
                'complexity': complexity_level.name,
                'success': len(failed_results) == 0,
                'agent_used': routing_results[list(routing_results.keys())[0]]['agent_role'].value if routing_results else 'unknown',
                'execution_time': sum(r.execution_time for r in execution_results.values()),
                'subtasks_count': len(subtasks),
                'context': context or {}
            }
            
            # Learn from the interaction
            self.user_preference_learner.learn_from_interaction(user_id, interaction_data)
            
            # 8. RESPONSE GENERATION AND PERSONALIZATION
            logger.info(f"💬 [Step 8] Generating personalized response")
            
            if successful_results and not failed_results:
                # All subtasks succeeded
                if len(successful_results) == 1:
                    base_response = successful_results[0]
                else:
                    # Aggregate multiple results
                    base_response = "\n\n".join(successful_results)
                
                # Personalize the response based on user preferences
                personalized_response = self.user_preference_learner.personalize_response(
                    user_id, base_response, context
                )
                
                logger.info(f"✅ Task completed successfully with personalized response")
                return personalized_response
                
            elif successful_results and failed_results:
                # Partial success
                base_response = f"✅ Completed some tasks successfully:\n\n" + "\n\n".join(successful_results)
                if failed_results:
                    base_response += f"\n\n❌ Some tasks failed:\n" + "\n".join(failed_results)
                
                personalized_response = self.user_preference_learner.personalize_response(
                    user_id, base_response, context
                )
                
                logger.warning(f"⚠️ Task completed with partial success")
                return personalized_response
                
            else:
                # All tasks failed
                error_response = f"❌ All tasks failed:\n" + "\n".join(failed_results)
                
                personalized_response = self.user_preference_learner.personalize_response(
                    user_id, error_response, context
                )
                
                logger.error(f"❌ Task execution failed completely")
                return personalized_response
                
        except Exception as e:
            error_msg = f"❌ Error in intelligent task execution: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Learn from the failed interaction
            if context and 'user_id' in context:
                interaction_data = {
                    'user_message': task_description,
                    'intent': 'error',
                    'success': False,
                    'error': str(e),
                    'context': context
                }
                self.user_preference_learner.learn_from_interaction(context['user_id'], interaction_data)
            
            return error_msg
    
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