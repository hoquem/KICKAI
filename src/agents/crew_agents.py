#!/usr/bin/env python3
"""
Robust CrewAI Football Team Management System - 8-Agent Architecture

This module implements a comprehensive team management system consisting
of a specialized 8-agent system for managing Sunday League football teams.

8-Agent Architecture:
1. Message Processor: Primary user interface and command parsing
2. Team Manager: Strategic coordination and high-level planning
3. Player Coordinator: Operational player management and registration
4. Finance Manager: Financial tracking and payment management
5. Performance Analyst: Performance analysis and tactical insights
6. Learning Agent: Continuous learning and system improvement
7. Onboarding Agent: Specialized player onboarding and registration
8. Command Fallback Agent: Handles unrecognized commands and fallback scenarios

Each agent has specific responsibilities and tools tailored to their role.
The system uses CrewAI for agent coordination and communication.
"""

import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager
from functools import wraps
from core.improved_config_system import get_improved_config, TeamConfig
from datetime import datetime
import time # Added for timestamp in store_memory

# Import shared enums
from src.core.enums import AgentRole, AIProvider

# Import LLM factory components
from src.utils.llm_factory import LLMFactory, LLMConfig, LLMProviderError

# Import capabilities
from src.agents.intelligent_system import AgentCapabilityMatrix

# Import intelligent system components
try:
    from .intelligent_system import (
        IntentClassifier, RequestComplexityAssessor, DynamicTaskDecomposer,
        CapabilityBasedRouter, TaskExecutionOrchestrator, UserPreferenceLearner,
        TaskContext, TaskComplexity, Subtask, CapabilityType
    )
except ImportError:
    # Fallback if intelligent system is not available
    class IntentClassifier:
        def __init__(self, llm):
            self.llm = llm
        def classify(self, text):
            return type('obj', (object,), {
                'primary_intent': 'help_request',
                'confidence': 0.9,
                'entities': {}
            })
    
    class DynamicTaskDecomposer:
        def __init__(self, llm):
            self.llm = llm
        def decompose(self, task_description, task_context):
            # Create a simple subtask for help commands
            return [type('obj', (object,), {
                'description': task_description,
                'agent_role': AgentRole.MESSAGE_PROCESSOR,
                'capabilities_required': [CapabilityType.INTENT_ANALYSIS]
            })]
    
    class CapabilityBasedRouter:
        def __init__(self, capability_matrix):
            self.capability_matrix = capability_matrix
        def route_multiple(self, subtasks, agents):
            # Simple routing - assign to first available agent
            results = {}
            for i, subtask in enumerate(subtasks):
                results[f"task_{i}"] = {
                    'agent_role': subtask.agent_role,
                    'agent': agents[0] if agents else None
                }
            return results
    
    class TaskExecutionOrchestrator:
        def __init__(self, capability_matrix):
            self.capability_matrix = capability_matrix
        def execute_tasks(self, subtasks, agents, selected_agents):
            # Simple execution - return success for all tasks
            results = {}
            for i, subtask in enumerate(subtasks):
                results[f"task_{i}"] = type('obj', (object,), {
                    'agent_role': subtask.agent_role,
                    'success': True,
                    'result': "Help command processed successfully",
                    'error': None,
                    'execution_time': 0.1
                })
            return results
    
    class UserPreferenceLearner:
        def __init__(self):
            pass
        def learn_from_interaction(self, user_id, interaction_data):
            pass
        def personalize_response(self, user_id, response, context):
            return response
    
    class TaskContext:
        def __init__(self, task_id, user_id, team_id, parameters, metadata):
            self.task_id = task_id
            self.user_id = user_id
            self.team_id = team_id
            self.parameters = parameters
            self.metadata = metadata
    
    class TaskComplexity(Enum):
        SIMPLE = "simple"
        COMPLEX = "complex"
    
    class Subtask:
        def __init__(self, task_id, description, agent_role, capabilities_required, parameters=None, dependencies=None, estimated_duration=30, priority=1, user_id=None, team_id=None, metadata=None):
            self.task_id = task_id
            self.description = description
            self.agent_role = agent_role
            self.capabilities_required = capabilities_required
            self.parameters = parameters or {}
            self.dependencies = dependencies or []
            self.estimated_duration = estimated_duration
            self.priority = priority
            self.user_id = user_id
            self.team_id = team_id
            self.metadata = metadata or {}
    
    class CapabilityType(Enum):
        INTENT_ANALYSIS = "intent_analysis"
        DATA_RETRIEVAL = "data_retrieval"
        USER_MANAGEMENT = "user_management"
        PLAYER_MANAGEMENT = "player_management"
        FINANCIAL_MANAGEMENT = "financial_management"
        STRATEGIC_PLANNING = "strategic_planning"
        COORDINATION = "coordination"
        DECISION_MAKING = "decision_making"
        HIGH_LEVEL_OPERATIONS = "high_level_operations"
        OPERATIONAL_TASKS = "operational_tasks"
        CONTEXT_MANAGEMENT = "context_management"
        ROUTING = "routing"
        NATURAL_LANGUAGE_UNDERSTANDING = "natural_language_understanding"

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


# Remove the local AgentRole definition and import from src.core.enums
from src.core.enums import AgentRole
from src.utils.llm_factory import LLMFactory, LLMConfig, LLMProviderError


@dataclass
class AIConfig:
    """Configuration for Gemini provider only."""
    provider: AIProvider
    model_name: str
    api_key: Optional[str] = None
    temperature: float = 0.7
    timeout_seconds: int = 30
    max_retries: int = 3


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
        try:
            # Enhanced logging for help command tracing
            is_help_command = description.lower().strip() == "/help"
            if is_help_command:
                logger.info(f"🔧 MESSAGE_PROCESSOR STEP 1: Help command received in execute method")
                logger.info(f"🔧 MESSAGE_PROCESSOR STEP 1a: description='{description}'")
                logger.info(f"🔧 MESSAGE_PROCESSOR STEP 1b: parameters keys={list(parameters.keys())}")
                
                # Special handling for help command
                return self._handle_help_command(parameters)
            
            # For non-help commands, use process_with_memory
            logger.info(f"🔧 MESSAGE_PROCESSOR: Processing non-help command with memory")
            return self.process_with_memory(description, context=parameters)
            
        except Exception as e:
            logger.error(f"Error in MessageProcessorAgent.execute: {e}", exc_info=True)
            return f"❌ Sorry, I encountered an error processing your request: {str(e)}"
    
    def _handle_help_command(self, parameters: dict) -> str:
        """Handle help command specifically."""
        try:
            logger.info(f"🔧 MESSAGE_PROCESSOR STEP 2: Starting help command handler")
            
            # Extract context information
            user_id = parameters.get('user_id', 'unknown')
            chat_id = parameters.get('chat_id', 'unknown')
            is_leadership_chat = parameters.get('is_leadership_chat', False)
            user_role = parameters.get('user_role', 'player')
            
            logger.info(f"🔧 MESSAGE_PROCESSOR STEP 2a: Context - user_id={user_id}, chat_id={chat_id}, is_leadership_chat={is_leadership_chat}, user_role={user_role}")
            
            # Generate help message based on context
            if is_leadership_chat:
                logger.info(f"🔧 MESSAGE_PROCESSOR STEP 3: Generating leadership chat help")
                help_message = self._get_leadership_help_message()
            else:
                logger.info(f"🔧 MESSAGE_PROCESSOR STEP 3: Generating main chat help")
                help_message = self._get_main_chat_help_message()
            
            logger.info(f"🔧 MESSAGE_PROCESSOR STEP 4: Help message generated, length={len(help_message)}")
            logger.info(f"🔧 MESSAGE_PROCESSOR STEP 5: Returning help message")
            
            return help_message
            
        except Exception as e:
            logger.error(f"Error in _handle_help_command: {e}", exc_info=True)
            return "❌ Sorry, I encountered an error generating help information."
    
    def _get_leadership_help_message(self) -> str:
        """Get help message for leadership chat."""
        return """🤖 <b>KICKAI BOT HELP (LEADERSHIP)</b>

📋 <b>AVAILABLE COMMANDS:</b>

🌐 <b>GENERAL:</b>
• /help - Show this help message
• /start - Start the bot
• /register - Register as a new player

👥 <b>PLAYER:</b>
• /myinfo - Get your player information
• /list - See all team players
• /status [phone] - Check player status

👑 <b>LEADERSHIP:</b>
• /add [name] [phone] [position] - Add new player
• /remove [phone_or_player_id] - Remove player
• /approve [player_id] - Approve player
• /reject [player_id] [reason] - Reject player
• /pending - Show pending approvals
• /invite [phone_or_player_id] - Generate invitation
• /stats - Team statistics
• /checkfa - Check FA registration status
• /dailystatus - Daily status report
• /remind [message] - Send reminder to team
• /broadcast [message] - Broadcast message to team

🔧 <b>ADMIN:</b>
• /createteam [name] - Create new team
• /deleteteam [team_id] - Delete team
• /listteams - List all teams
• /backgroundtasks - Manage background tasks

💡 <b>TIPS:</b>
• Use natural language: "Add John Smith as midfielder"
• Type /help [command] for detailed help
• All admin commands available in leadership chat"""

    def _get_main_chat_help_message(self) -> str:
        """Get help message for main chat."""
        return """🤖 <b>KICKAI BOT HELP</b>

📋 <b>AVAILABLE COMMANDS:</b>

🌐 <b>GENERAL:</b>
• /help - Show this help message
• /start - Start the bot
• /register - Register as a new player

👥 <b>PLAYER:</b>
• /myinfo - Get your player information
• /list - See all team players
• /status [phone] - Check player status

💡 <b>TIPS:</b>
• Use natural language: "What's my phone number?"
• Type /help [command] for detailed help
• Admin commands available in leadership chat
• Need to update something? Contact team admin"""


class MessageProcessorAgent(BaseTeamAgent):
    """Agent responsible for processing and routing messages."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.MESSAGE_PROCESSOR
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            'role': 'User Interface Specialist',
            'goal': 'Focus on parsing user input, extracting initial context, and providing immediate responses for simple queries. For complex commands, consistently pass parsed information to TeamManagementSystem.execute_task for full orchestration.',
            'backstory': f"""You are the User Interface Specialist for {self.team_config.team_name}. 
            Your primary responsibilities are:
            - Parse and understand user input and commands
            - Extract initial context and user intent
            - Provide immediate responses for simple queries (like /help)
            - For complex commands, pass parsed information to the central orchestrator
            
            IMPORTANT: You are NOT the primary router for all commands.
            The TeamManagementSystem.execute_task method serves as the central orchestrator.
            Your role is to parse input and either handle simple queries directly or pass complex commands to the orchestrator.
            
            You excel at natural language understanding and can provide helpful guidance to users while ensuring all complex operations are properly routed through the system's orchestration layer."""
        }


class TeamManagerAgent(BaseTeamAgent):
    """Agent responsible for overall team management."""
    
    def _get_agent_role(self) -> AgentRole:
        return AgentRole.TEAM_MANAGER
    
    def _get_agent_definition(self) -> Dict[str, Any]:
        return {
            'role': 'Head of Football Operations',
            'goal': 'Act as the strategic coordinator for high-level team administrative tasks, ensuring seamless coordination between player management, match scheduling, and financial operations. Your primary focus is on team configuration, operational oversight, and delegating sub-tasks that arise from your own administrative duties.',
            'backstory': f"""You are the strategic Head of Football Operations for {self.team_config.team_name}. 
            You are responsible for high-level administrative and configuration tasks within your domain:
            - Modifying core team settings (e.g., team name, FA website URLs).
            - Managing the team's budget and financial rules at a high level.
            - Delegating specific sub-tasks to other specialized agents when they arise from your own administrative duties.
            
            IMPORTANT: You are NOT the central dispatcher for all incoming user commands. 
            The TeamManagementSystem.execute_task method serves as the primary orchestrator for all commands.
            Your delegation scope is limited to sub-tasks that arise from your own administrative responsibilities.
            
            You must use your tools to fetch and update team-wide configurations and ensure all operational aspects are aligned with the team's strategic goals. You are the final point of authority on team settings within your domain."""
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
    Factory for creating team management agents in the 8-agent system.
    
    Maps AgentRole enum values to their corresponding agent classes:
    - MESSAGE_PROCESSOR -> MessageProcessorAgent
    - TEAM_MANAGER -> TeamManagerAgent  
    - PLAYER_COORDINATOR -> PlayerCoordinatorAgent
    - FINANCE_MANAGER -> FinanceManagerAgent
    - PERFORMANCE_ANALYST -> PerformanceAnalystAgent
    - LEARNING_AGENT -> LearningAgent
    - ONBOARDING_AGENT -> OnboardingAgent
    - COMMAND_FALLBACK_AGENT -> CommandFallbackAgent
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


class AgentToolsManager:
    """
    Manager for handling agent tools in the 8-agent system.
    
    This class provides tools to each agent based on their role and capabilities.
    Tools are organized by agent role and can be dynamically loaded based on
    the specific needs of each agent.
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
            from src.domain.tools import (
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
            from src.services.command_operations_factory import get_command_operations
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
    Main system for managing football team operations using the 8-agent architecture.
    
    The system coordinates 8 specialized agents:
    1. Message Processor: Handles user interface and command parsing
    2. Team Manager: Provides strategic coordination and planning
    3. Player Coordinator: Manages player operations and registration
    4. Finance Manager: Handles financial tracking and payments
    5. Performance Analyst: Analyzes performance and provides insights
    6. Learning Agent: Continuously learns and improves the system
    7. Onboarding Agent: Specializes in player onboarding workflows
    8. Command Fallback Agent: Handles unrecognized commands and fallback scenarios
    
    Each agent has specific tools and capabilities tailored to their role.
    """
    
    def __init__(self, team_id: str):
        logger.info(f"[TEAM INIT] Starting TeamManagementSystem initialization for team {team_id}")
        self.team_id = team_id
        logger.info(f"[TEAM INIT] Getting improved config")
        self.config_manager = get_improved_config()
        logger.info(f"[TEAM INIT] Getting team config for {team_id}")
        self.team_config = self.config_manager.get_team_config(team_id)
        logger.info(f"[TEAM INIT] Loaded team_config: {self.team_config}")
        logger.info(f"[TEAM INIT] Loaded metadata: {self.config_manager.configuration.metadata}")
        if not self.team_config:
            logger.error(f"[TEAM INIT] No configuration found for team_id: {team_id}")
            raise ValueError(f"No configuration found for team_id: {team_id}")
        logger.info(f"[TEAM INIT] Team config obtained successfully")
        logger.info(f"[TEAM INIT] Initializing LLM")
        self.llm = self._initialize_llm()
        logger.info(f"[TEAM INIT] LLM initialized successfully")
        logger.info(f"[TEAM INIT] Initializing agents dictionary")
        self.agents = {}
        logger.info(f"[TEAM INIT] Initializing capability matrix")
        self.capability_matrix = AgentCapabilityMatrix()
        logger.info(f"[TEAM INIT] Initializing user preference learner")
        self.user_preference_learner = UserPreferenceLearner()  # Add preference learner
        logger.info(f"[TEAM INIT] Calling _initialize_agents")
        self._initialize_agents()
        logger.info(f"[TEAM INIT] _initialize_agents completed")
        logger.info(f"✅ TeamManagementSystem initialized for team {team_id}")
    
    def _initialize_llm(self):
        """Initialize the LLM based on configuration."""
        ai_config = self.config_manager.configuration.ai
        
        # Convert AIConfig to LLMConfig for the new factory
        llm_config = LLMConfig(
            provider=ai_config.provider,
            model_name=ai_config.model_name,
            api_key=ai_config.api_key or "",
            temperature=ai_config.temperature,
            timeout_seconds=ai_config.timeout_seconds,
            max_retries=ai_config.max_retries
        )
        
        return LLMFactory.create_llm(llm_config)
    
    def _initialize_agents(self) -> None:
        """Initialize all agents."""
        logger.info("[AGENT INIT] Initializing agents...")
        try:
            agent_configs = self.config_manager.configuration.metadata.get('agent_configs', {})
            logger.info(f"[AGENT INIT] Agent configs: {agent_configs}")
            errors = []
            for role in AgentRole:
                logger.info(f"[AGENT INIT] Processing role: {role.value}")
                agent_config_data = agent_configs.get(role.value, {})
                agent_config = AgentConfig(
                    role=role,
                    enabled=agent_config_data.get('enabled', True),
                    max_iterations=agent_config_data.get('max_iterations', 10),
                    allow_delegation=agent_config_data.get('allow_delegation', True),
                    verbose=agent_config_data.get('verbose', True)
                )
                logger.info(f"[AGENT INIT] Agent config for {role.value}: enabled={agent_config.enabled}")
                if not agent_config.enabled:
                    logger.info(f"[AGENT INIT] Skipping disabled agent: {role.value}")
                    continue
                try:
                    if not hasattr(self, 'tools_manager'):
                        logger.info(f"[AGENT INIT] Creating tools manager for {role.value}")
                        self.tools_manager = AgentToolsManager(self.team_config)
                    logger.info(f"[AGENT INIT] Configuring tools for {role.value}")
                    tools = self.tools_manager.get_tools_for_agent(role)
                    logger.info(f"[AGENT INIT] Got {len(tools)} tools for {role.value}")
                    logger.info(f"[AGENT INIT] Creating agent for {role.value}")
                    agent = AgentFactory.create_agent(role, self.team_config, agent_config, self.llm, tools)
                    logger.info(f"[AGENT INIT] Agent created for {role.value}, checking if enabled")
                    if agent.is_enabled():
                        self.agents[role] = agent
                        logger.info(f"[AGENT INIT] ✅ Agent {role.value} initialized successfully")
                    else:
                        logger.warning(f"[AGENT INIT] Agent {role.value} is disabled after creation")
                except Exception as e:
                    logger.error(f"[AGENT INIT] Failed to initialize agent {role.value}: {e}", exc_info=True)
                    errors.append((role.value, str(e)))
            logger.info(f"[AGENT INIT] Agent initialization complete. Agents created: {list(self.agents.keys())}")
            if not self.agents:
                logger.critical(f"[AGENT INIT] No agents were initialized! Errors: {errors}")
                raise AgentInitializationError(f"No agents initialized. Errors: {errors}")
            logger.info(f"[AGENT INIT] All enabled agents initialized: {list(self.agents.keys())}")
        except Exception as e:
            logger.error(f"[AGENT INIT] Critical error in agent initialization: {e}", exc_info=True)
            raise
    
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
    
    def execute_task(self, task_description: str, execution_context: Dict[str, Any]) -> str:
        """
        CENTRAL ORCHESTRATOR: Execute a task using the intelligent 8-agent system.
        
        This method serves as the PRIMARY DISPATCHER for all user commands and requests.
        It orchestrates the complete task execution pipeline:
        
        1. Intent classification and complexity assessment
        2. Task decomposition and capability matching  
        3. Agent selection and tool assignment
        4. Orchestrated execution with result aggregation
        5. User preference learning and response personalization
        
        ARCHITECTURAL ROLES:
        - TeamManagementSystem.execute_task: Central orchestrator for ALL commands
        - MessageProcessorAgent: Focuses on parsing and initial context extraction
        - TeamManagerAgent: Delegates sub-tasks from its own administrative duties
        - Other agents: Handle specific domain responsibilities
        
        All agents consistently pass parsed commands to this method for full orchestration.
        """
        try:
            # Enhanced logging for help command tracing
            is_help_command = task_description.lower().strip() == "/help"
            if is_help_command:
                logger.info(f"🤖 CENTRAL ORCHESTRATOR STEP 1: TeamManagementSystem.execute_task called for help command")
                logger.info(f"🤖 CENTRAL ORCHESTRATOR STEP 1a: task_description='{task_description}'")
                logger.info(f"🤖 CENTRAL ORCHESTRATOR STEP 1b: execution_context keys={list(execution_context.keys())}")
            
            # Special handling for help command - use direct agent execution
            if is_help_command:
                logger.info(f"🤖 CENTRAL ORCHESTRATOR STEP 2: Help command detected, using direct agent execution")
                
                # Get the Message Processor agent for help commands
                message_processor = self.get_agent(AgentRole.MESSAGE_PROCESSOR)
                if message_processor:
                    logger.info(f"🤖 CENTRAL ORCHESTRATOR STEP 3: Using MessageProcessorAgent for help command")
                    
                    # Execute help command directly
                    result = message_processor.execute(task_description, execution_context)
                    
                    logger.info(f"🤖 CENTRAL ORCHESTRATOR STEP 4: Help command executed successfully")
                    logger.info(f"🤖 CENTRAL ORCHESTRATOR STEP 4a: Result length={len(result) if result else 0}")
                    
                    return result
                else:
                    logger.error(f"🤖 CENTRAL ORCHESTRATOR ERROR: MessageProcessorAgent not available")
                    return "❌ Sorry, the help system is currently unavailable."
            
            # For non-help commands, use the full intelligent system pipeline
            logger.info(f"🤖 CENTRAL ORCHESTRATOR: Using full intelligent system for non-help command")
            
            # Step 1: Intent Classification and Complexity Assessment
            intent_result = self._classify_intent(task_description, execution_context)
            
            # Step 2: Task Decomposition and Capability Matching
            decomposed_tasks = self._decompose_task(task_description, intent_result, execution_context)
            
            # Step 3: Agent Selection and Tool Assignment
            selected_agents = self._select_agents(decomposed_tasks, execution_context)
            
            # Step 4: Orchestrated Execution
            execution_results = self._execute_orchestrated(selected_agents, decomposed_tasks, execution_context)
            
            # Step 5: Result Aggregation and Response Generation
            final_response = self._aggregate_results(execution_results, execution_context)
            
            # Step 6: User Preference Learning
            self._update_user_preferences(execution_context, intent_result, final_response)
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error in TeamManagementSystem.execute_task: {e}", exc_info=True)
            return f"❌ Sorry, I encountered an error processing your request: {str(e)}"
    
    def _classify_intent(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the intent of a task using the intelligent system.
        """
        try:
            classifier = IntentClassifier(llm=self.llm)
            intent_result = classifier.classify(task_description)
            
            # Convert to dictionary format and add missing fields
            intent_dict = {
                'intent': getattr(intent_result, 'primary_intent', 'unknown'),
                'confidence': getattr(intent_result, 'confidence', 0.5),
                'entities': getattr(intent_result, 'entities', {}),
                'secondary_intents': getattr(intent_result, 'secondary_intents', []),
                'context': getattr(intent_result, 'context', {}),
                'agent_used': 'intent_classifier'  # Add the missing agent_used field
            }
            
            logger.info(f"Intent classification result: {intent_dict}")
            return intent_dict
            
        except Exception as e:
            logger.error(f"Error in _classify_intent: {e}", exc_info=True)
            # Return a fallback intent result
            return {
                'intent': 'unknown',
                'confidence': 0.1,
                'entities': {},
                'secondary_intents': [],
                'context': {},
                'agent_used': 'fallback'
            }
    
    def _decompose_task(self, task_description: str, intent_result: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Decompose a complex task into subtasks based on intent and context.
        """
        try:
            decomposer = DynamicTaskDecomposer(llm=self.llm)
            
            # Create task context
            task_context = TaskContext(
                task_id=f"task_{int(datetime.now().timestamp())}",
                user_id=context.get('user_id', 'unknown'),
                team_id=self.team_id,
                parameters=intent_result['entities'],
                metadata={
                    'intent': intent_result['intent'],
                    'complexity': 'COMPLEX', # For now, all tasks are complex for decomposition
                    'confidence': intent_result['confidence']
                }
            )
            
            subtasks = decomposer.decompose(task_description, task_context)
            
            # Convert Subtask objects to dictionaries for easier JSON serialization
            decomposed_tasks = []
            for subtask in subtasks:
                decomposed_tasks.append({
                    'description': subtask.description,
                    'agent_role': subtask.agent_role,
                    'required_capabilities': [cap.value for cap in subtask.capabilities_required]
                })
            return decomposed_tasks
        except Exception as e:
            logger.error(f"Error in _decompose_task: {e}", exc_info=True)
            return []
    
    def _select_agents(self, decomposed_tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[AgentRole, BaseTeamAgent]:
        """
        Select the most appropriate agents for each subtask based on capabilities.
        """
        try:
            router = CapabilityBasedRouter(self.capability_matrix)
            
            # Create a list of all available agents
            available_agents = list(self.agents.values())
            
            if not available_agents:
                logger.warning("No available agents for selection")
                return {}
            
            logger.info(f"Available agents for routing: {[agent._get_agent_role().value for agent in available_agents]}")
            
            # Route subtasks to agents
            try:
                # Convert dictionary subtasks to Subtask objects
                subtask_objects = []
                for subtask_data in decomposed_tasks:
                    try:
                        # Create a proper Subtask object
                        subtask = Subtask(
                            task_id=subtask_data.get('task_id', f"task_{int(datetime.now().timestamp())}"),
                            description=subtask_data.get('description', ''),
                            agent_role=subtask_data.get('agent_role', AgentRole.MESSAGE_PROCESSOR),
                            capabilities_required=[
                                CapabilityType(cap) if isinstance(cap, str) else cap 
                                for cap in subtask_data.get('required_capabilities', [])
                            ],
                            parameters=subtask_data.get('parameters', {}),
                            dependencies=subtask_data.get('dependencies', []),
                            estimated_duration=subtask_data.get('estimated_duration', 30),
                            priority=subtask_data.get('priority', 1)
                        )
                        subtask_objects.append(subtask)
                        logger.info(f"Created subtask: {subtask.description} -> {subtask.agent_role.value}")
                    except Exception as subtask_error:
                        logger.error(f"Error creating Subtask object: {subtask_error}")
                        # Create a fallback subtask
                        fallback_subtask = Subtask(
                            task_id=f"fallback_{int(datetime.now().timestamp())}",
                            description=subtask_data.get('description', 'Unknown task'),
                            agent_role=AgentRole.MESSAGE_PROCESSOR,
                            capabilities_required=[CapabilityType.INTENT_ANALYSIS],
                            parameters=subtask_data.get('parameters', {})
                        )
                        subtask_objects.append(fallback_subtask)
                
                # Route each subtask individually
                selected_agents = {}
                for subtask in subtask_objects:
                    logger.info(f"Routing subtask: {subtask.description}")
                    agent = router.route(subtask, available_agents)
                    if agent:
                        agent_role = agent._get_agent_role()
                        selected_agents[agent_role] = agent
                        logger.info(f"✅ Routed subtask '{subtask.description}' to {agent_role.value}")
                    else:
                        logger.warning(f"❌ Failed to route subtask: {subtask.description}")
                
                if not selected_agents:
                    logger.warning("No agents were selected, using fallback")
                    # Fallback: use MessageProcessorAgent for all tasks
                    if AgentRole.MESSAGE_PROCESSOR in self.agents:
                        selected_agents = {AgentRole.MESSAGE_PROCESSOR: self.agents[AgentRole.MESSAGE_PROCESSOR]}
                    else:
                        # Last resort: return first available agent
                        first_agent_role = list(self.agents.keys())[0]
                        selected_agents = {first_agent_role: self.agents[first_agent_role]}
                
                logger.info(f"Selected agents: {[role.value for role in selected_agents.keys()]}")
                return selected_agents
                
            except Exception as routing_error:
                logger.warning(f"Routing failed, using fallback agent selection: {routing_error}")
                # Fallback: use MessageProcessorAgent for all tasks
                if AgentRole.MESSAGE_PROCESSOR in self.agents:
                    return {AgentRole.MESSAGE_PROCESSOR: self.agents[AgentRole.MESSAGE_PROCESSOR]}
                else:
                    # Last resort: return first available agent
                    first_agent_role = list(self.agents.keys())[0]
                    return {first_agent_role: self.agents[first_agent_role]}
                    
        except Exception as e:
            logger.error(f"Error in _select_agents: {e}", exc_info=True)
            # Return fallback agents
            if AgentRole.MESSAGE_PROCESSOR in self.agents:
                return {AgentRole.MESSAGE_PROCESSOR: self.agents[AgentRole.MESSAGE_PROCESSOR]}
            else:
                return {}
    
    def _execute_orchestrated(self, selected_agents: Dict[AgentRole, BaseTeamAgent], decomposed_tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Orchestrate the execution of subtasks across selected agents.
        """
        try:
            orchestrator = TaskExecutionOrchestrator(self.capability_matrix)
            
            # Create a list of all agents to pass to the orchestrator
            agents_to_execute = list(selected_agents.values())
            
            if not agents_to_execute:
                logger.warning("No agents available for execution")
                return []
            
            logger.info(f"Executing tasks with {len(agents_to_execute)} agents")
            
            # Execute tasks
            try:
                # Convert dictionary subtasks to Subtask objects
                subtask_objects = []
                for subtask_data in decomposed_tasks:
                    try:
                        # Create a proper Subtask object
                        subtask = Subtask(
                            task_id=subtask_data.get('task_id', f"task_{int(datetime.now().timestamp())}"),
                            description=subtask_data.get('description', ''),
                            agent_role=subtask_data.get('agent_role', AgentRole.MESSAGE_PROCESSOR),
                            capabilities_required=[
                                CapabilityType(cap) if isinstance(cap, str) else cap 
                                for cap in subtask_data.get('required_capabilities', [])
                            ],
                            parameters=subtask_data.get('parameters', {}),
                            dependencies=subtask_data.get('dependencies', []),
                            estimated_duration=subtask_data.get('estimated_duration', 30),
                            priority=subtask_data.get('priority', 1)
                        )
                        subtask_objects.append(subtask)
                    except Exception as subtask_error:
                        logger.error(f"Error creating Subtask object for execution: {subtask_error}")
                        # Create a fallback subtask
                        fallback_subtask = Subtask(
                            task_id=f"fallback_{int(datetime.now().timestamp())}",
                            description=subtask_data.get('description', 'Unknown task'),
                            agent_role=AgentRole.MESSAGE_PROCESSOR,
                            capabilities_required=[CapabilityType.INTENT_ANALYSIS],
                            parameters=subtask_data.get('parameters', {})
                        )
                        subtask_objects.append(fallback_subtask)
                
                # Execute each subtask with its assigned agent
                execution_results = []
                for subtask in subtask_objects:
                    logger.info(f"Executing subtask: {subtask.description}")
                    
                    # Find the agent for this subtask
                    agent = None
                    for agent_role, agent_instance in selected_agents.items():
                        if agent_role == subtask.agent_role:
                            agent = agent_instance
                            break
                    
                    if not agent:
                        logger.warning(f"No agent found for subtask {subtask.description}, using first available")
                        agent = list(selected_agents.values())[0]
                    
                    # Execute the subtask
                    try:
                        result = agent.execute(subtask.description, subtask.parameters)
                        execution_results.append({
                            'task_id': subtask.task_id,
                            'description': subtask.description,
                            'agent_role': agent._get_agent_role().value,
                            'result': result,
                            'success': True,
                            'timestamp': datetime.now().isoformat()
                        })
                        logger.info(f"✅ Executed subtask '{subtask.description}' successfully")
                    except Exception as exec_error:
                        logger.error(f"Error executing subtask {subtask.description}: {exec_error}")
                        execution_results.append({
                            'task_id': subtask.task_id,
                            'description': subtask.description,
                            'agent_role': agent._get_agent_role().value,
                            'result': f"Error: {str(exec_error)}",
                            'success': False,
                            'timestamp': datetime.now().isoformat()
                        })
                
                logger.info(f"Execution completed: {len(execution_results)} results")
                return execution_results
                
            except Exception as execution_error:
                logger.error(f"Error in task execution: {execution_error}", exc_info=True)
                return []
                
        except Exception as e:
            logger.error(f"Error in _execute_orchestrated: {e}", exc_info=True)
            return []
    
    def _aggregate_results(self, execution_results: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """
        Aggregate execution results into a final response.
        """
        try:
            if not execution_results:
                return "❌ No results to aggregate"
            
            # Check if all results were successful
            successful_results = [r for r in execution_results if r.get('success', False)]
            failed_results = [r for r in execution_results if not r.get('success', False)]
            
            if not successful_results:
                return "❌ All tasks failed to execute"
            
            # Combine successful results
            combined_result = ""
            for i, result in enumerate(successful_results):
                if i > 0:
                    combined_result += "\n\n"
                combined_result += f"**{result.get('description', 'Task')}**\n{result.get('result', 'No result')}"
            
            # Add failure information if any
            if failed_results:
                combined_result += "\n\n**Failed Tasks:**\n"
                for result in failed_results:
                    combined_result += f"- {result.get('description', 'Unknown task')}: {result.get('result', 'Unknown error')}\n"
            
            logger.info(f"Aggregated {len(successful_results)} successful and {len(failed_results)} failed results")
            return combined_result
            
        except Exception as e:
            logger.error(f"Error in _aggregate_results: {e}", exc_info=True)
            return "❌ Error aggregating results"
    
    def _update_user_preferences(self, context: Dict[str, Any], intent_result: Dict[str, Any], final_response: str):
        """
        Update user preferences based on the interaction.
        """
        try:
            # Extract user preferences from the interaction
            user_id = context.get('user_id', 'unknown')
            intent = intent_result.get('intent', 'unknown')
            confidence = intent_result.get('confidence', 0.0)
            
            # Update user preferences
            self.user_preference_learner.update_preferences(
                user_id=user_id,
                intent=intent,
                confidence=confidence,
                response_length=len(final_response),
                success=not final_response.startswith('❌')
            )
            
            logger.debug(f"Updated user preferences for {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}", exc_info=True)
    
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