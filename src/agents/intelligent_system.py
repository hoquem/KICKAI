"""
Intelligent system components for KICKAI agents.
"""

from typing import Dict, Any, List, Optional, Tuple, DefaultDict
from dataclasses import dataclass
import json
import logging
from datetime import datetime, timedelta
import re
from enum import Enum
import threading
import os
from pathlib import Path
from collections import defaultdict

# Import our existing components
from .capabilities import AgentCapabilityMatrix, CapabilityType, AgentRole
from .crew_agents import AgentRole as CrewAgentRole

logger = logging.getLogger(__name__)

@dataclass
class TaskContext:
    """Context for task execution."""
    task_id: str
    user_id: str
    team_id: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class Subtask:
    """Represents a decomposed subtask with full context."""
    # Task identification and description
    task_id: str
    description: str
    
    # Agent assignment
    agent_role: AgentRole
    capabilities_required: List[CapabilityType]
    
    # Execution parameters
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    estimated_duration: int = 30  # seconds
    priority: int = 1  # 1-5, higher is more important
    
    # Context information (from TaskContext)
    user_id: str = None
    team_id: str = None
    metadata: Dict[str, Any] = None
    
    @classmethod
    def from_task_context(cls, task_context: TaskContext, description: str, 
                         agent_role: AgentRole, capabilities_required: List[CapabilityType] = None) -> 'Subtask':
        """Create a Subtask from a TaskContext."""
        return cls(
            task_id=task_context.task_id,
            description=description,
            agent_role=agent_role,
            capabilities_required=capabilities_required or [],
            parameters=task_context.parameters,
            user_id=task_context.user_id,
            team_id=task_context.team_id,
            metadata=task_context.metadata
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subtask':
        """Create a Subtask from a dictionary."""
        # Handle different possible key names for capabilities
        capabilities_key = None
        for key in ['capabilities_required', 'required_capabilities', 'capabilities']:
            if key in data:
                capabilities_key = key
                break
        
        if capabilities_key is None:
            # Default to empty list if no capabilities found
            capabilities_required = []
        else:
            capabilities_required = []
            for cap in data[capabilities_key]:
                if isinstance(cap, str):
                    try:
                        capabilities_required.append(CapabilityType(cap.lower()))
                    except ValueError:
                        # Skip invalid capability types
                        continue
                elif isinstance(cap, CapabilityType):
                    capabilities_required.append(cap)
        
        # Handle agent role
        agent_role_str = data.get('agent_role', 'MESSAGE_PROCESSOR')
        if isinstance(agent_role_str, str):
            try:
                agent_role = AgentRole(agent_role_str.lower())
            except ValueError:
                agent_role = AgentRole.MESSAGE_PROCESSOR
        else:
            agent_role = agent_role_str
        
        return cls(
            task_id=data.get('task_id', f"task_{int(datetime.now().timestamp())}"),
            description=data.get('description', ''),
            agent_role=agent_role,
            capabilities_required=capabilities_required,
            parameters=data.get('parameters', {}),
            dependencies=data.get('dependencies', []),
            estimated_duration=data.get('estimated_duration', 30),
            priority=data.get('priority', 1),
            user_id=data.get('user_id'),
            team_id=data.get('team_id'),
            metadata=data.get('metadata', {})
        )
    
    def to_task_context(self) -> TaskContext:
        """Convert Subtask back to TaskContext."""
        return TaskContext(
            task_id=self.task_id,
            user_id=self.user_id,
            team_id=self.team_id,
            parameters=self.parameters,
            metadata=self.metadata
        )

class TaskComplexity(Enum):
    """Task complexity levels."""
    SIMPLE = 1      # Single agent, single capability
    MODERATE = 2    # Single agent, multiple capabilities
    COMPLEX = 3     # Multiple agents, coordinated
    VERY_COMPLEX = 4 # Multiple agents, complex dependencies

MAX_RECURSION_DEPTH = 3

class DynamicTaskDecomposer:
    """Decomposes complex tasks into simpler subtasks using LLM and capability analysis."""
    
    def __init__(self, llm=None, capability_matrix: AgentCapabilityMatrix = None):
        self.llm = llm
        self.capability_matrix = capability_matrix or AgentCapabilityMatrix()
        self.task_templates = self._load_task_templates()
        self.decomposition_history = []
        logger.info("[DynamicTaskDecomposer] Initialized with capability matrix.")
    
    def _load_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load task templates for common operations."""
        return {
            'player_registration': {
                'description': 'Register new player {player_name} with phone {phone}',
                'capabilities': [CapabilityType.PLAYER_MANAGEMENT, CapabilityType.OPERATIONAL_TASKS],
                'agent_role': AgentRole.PLAYER_COORDINATOR,
                'estimated_duration': 60
            },
            'player_approval': {
                'description': 'Approve player {player_id} for team participation',
                'capabilities': [CapabilityType.PLAYER_MANAGEMENT, CapabilityType.DECISION_MAKING],
                'agent_role': AgentRole.TEAM_MANAGER,
                'estimated_duration': 30
            },
            'status_inquiry': {
                'description': 'Check registration status for user {user_id}',
                'capabilities': [CapabilityType.PLAYER_MANAGEMENT, CapabilityType.INTENT_ANALYSIS],
                'agent_role': AgentRole.MESSAGE_PROCESSOR,
                'estimated_duration': 15
            },
            'match_creation': {
                'description': 'Create new match with details {match_details}',
                'capabilities': [CapabilityType.STRATEGIC_PLANNING, CapabilityType.COORDINATION],
                'agent_role': AgentRole.TEAM_MANAGER,
                'estimated_duration': 120
            },
            'payment_processing': {
                'description': 'Process payment for {amount} from {payer}',
                'capabilities': [CapabilityType.PAYMENT_TRACKING, CapabilityType.FINANCIAL_REPORTING],
                'agent_role': AgentRole.FINANCE_MANAGER,
                'estimated_duration': 90
            },
            'performance_analysis': {
                'description': 'Analyze performance data for {time_period}',
                'capabilities': [CapabilityType.PERFORMANCE_ANALYSIS, CapabilityType.DATA_ANALYSIS],
                'agent_role': AgentRole.PERFORMANCE_ANALYST,
                'estimated_duration': 180
            }
        }
    
    def _analyze_task_complexity(self, task: str, context: TaskContext) -> TaskComplexity:
        """Analyze the complexity of a task based on content and context."""
        # Simple heuristics for complexity analysis
        task_lower = task.lower()
        
        # Check for multi-step operations
        multi_step_indicators = ['and', 'then', 'also', 'additionally', 'furthermore']
        if any(indicator in task_lower for indicator in multi_step_indicators):
            return TaskComplexity.COMPLEX
        
        # Check for coordination requirements
        coordination_indicators = ['coordinate', 'organize', 'manage', 'plan']
        if any(indicator in task_lower for indicator in coordination_indicators):
            return TaskComplexity.MODERATE
        
        # Check for analysis tasks
        analysis_indicators = ['analyze', 'review', 'assess', 'evaluate', 'report']
        if any(indicator in task_lower for indicator in analysis_indicators):
            return TaskComplexity.MODERATE
        
        # Check for simple operations
        simple_indicators = ['check', 'get', 'show', 'display', 'status']
        if any(indicator in task_lower for indicator in simple_indicators):
            return TaskComplexity.SIMPLE
        
        return TaskComplexity.MODERATE
    
    def _identify_required_capabilities(self, task: str) -> List[CapabilityType]:
        """Identify required capabilities based on task content with intelligent prioritization."""
        required_capabilities = []
        task_lower = task.lower()
        
        # Primary capabilities (must-have, high priority)
        primary_mappings = {
            CapabilityType.PLAYER_MANAGEMENT: ['player', 'registration', 'approve', 'status', 'info', 'myinfo'],
            CapabilityType.PAYMENT_TRACKING: ['payment', 'pay', 'money', 'fee', 'financial'],
            CapabilityType.PERFORMANCE_ANALYSIS: ['performance', 'analyze', 'stats', 'data', 'metrics'],
            CapabilityType.STRATEGIC_PLANNING: ['plan', 'strategy', 'match', 'fixture', 'tactical'],
            CapabilityType.MESSAGING: ['send', 'message', 'notify', 'announce', 'broadcast'],
            CapabilityType.DECISION_MAKING: ['decide', 'approve', 'reject', 'choose', 'select']
        }
        
        # Secondary capabilities (nice-to-have, lower priority)
        secondary_mappings = {
            CapabilityType.INTENT_ANALYSIS: ['what', 'how', 'why', 'check', 'query'],
            CapabilityType.COORDINATION: ['coordinate', 'organize', 'manage', 'arrange'],
            CapabilityType.CONTEXT_MANAGEMENT: ['context', 'history', 'previous', 'last'],
            CapabilityType.NATURAL_LANGUAGE_UNDERSTANDING: ['understand', 'interpret', 'parse']
        }
        
        # Check primary capabilities first
        for capability, keywords in primary_mappings.items():
            if any(keyword in task_lower for keyword in keywords):
                required_capabilities.append(capability)
                break  # Only take the first primary capability match
        
        # Check secondary capabilities (limit to 1-2)
        secondary_caps = []
        for capability, keywords in secondary_mappings.items():
            if any(keyword in task_lower for keyword in keywords):
                secondary_caps.append(capability)
        
        # Add up to 2 secondary capabilities
        required_capabilities.extend(secondary_caps[:2])
        
        # Ensure we don't have too many capabilities (max 3 total)
        required_capabilities = required_capabilities[:3]
        
        # If no capabilities identified, add a default
        if not required_capabilities:
            if 'status' in task_lower or 'info' in task_lower:
                required_capabilities.append(CapabilityType.PLAYER_MANAGEMENT)
            else:
                required_capabilities.append(CapabilityType.INTENT_ANALYSIS)
        
        logger.debug(f"[DynamicTaskDecomposer] Identified capabilities for '{task}': {[cap.value for cap in required_capabilities]}")
        return required_capabilities
    
    def _find_best_agent_for_capabilities(self, capabilities: List[CapabilityType]) -> AgentRole:
        if not capabilities:
            logger.warning("[DynamicTaskDecomposer] No capabilities provided, defaulting to MESSAGE_PROCESSOR.")
            return AgentRole.MESSAGE_PROCESSOR  # Default fallback
        agent_scores = {}
        for agent_role in AgentRole:
            score = 0
            for capability in capabilities:
                proficiency = self.capability_matrix.get_agent_proficiency(agent_role, capability)
                score += proficiency
            agent_scores[agent_role] = score
        best_agent = max(agent_scores.items(), key=lambda x: x[1])[0]
        logger.info(f"[DynamicTaskDecomposer] Routing: capabilities={capabilities}, agent_scores={agent_scores}, selected={best_agent}")
        return best_agent
    
    def _create_llm_decomposition_prompt(self, task: str, context: TaskContext) -> str:
        """Create a structured prompt for LLM-based task decomposition."""
        return f"""
You are an intelligent task decomposer for a football team management system. 
Your job is to break down complex user requests into specific, actionable subtasks.

Available agents and their primary capabilities:
- MESSAGE_PROCESSOR: Intent analysis, context management, routing
- TEAM_MANAGER: Strategic planning, coordination, decision making
- PLAYER_COORDINATOR: Player management, availability tracking, operational tasks
- FINANCE_MANAGER: Payment tracking, financial reporting, budget management
- PERFORMANCE_ANALYST: Performance analysis, tactical insights, data analysis
- LEARNING_AGENT: Pattern learning, user preference analysis, system improvement
- ONBOARDING_AGENT: Player onboarding, operational tasks, messaging
- COMMAND_FALLBACK_AGENT: Natural language understanding, intent analysis, routing

User Request: "{task}"
User ID: {context.user_id}
Team ID: {context.team_id}
Context Parameters: {context.parameters}

Please decompose this request into specific subtasks. For each subtask, provide:
1. A clear description of what needs to be done
2. Which agent should handle it
3. Required capabilities
4. Any dependencies on other subtasks
5. Estimated duration in seconds

Respond in JSON format:
{{
    "subtasks": [
        {{
            "description": "Clear description of the subtask",
            "agent_role": "AGENT_ROLE_NAME",
            "capabilities_required": ["CAPABILITY1", "CAPABILITY2"],
            "parameters": {{"key": "value"}},
            "dependencies": ["subtask_id_1", "subtask_id_2"],
            "estimated_duration": 30,
            "priority": 1
        }}
    ],
    "complexity": "SIMPLE|MODERATE|COMPLEX|VERY_COMPLEX",
    "reasoning": "Brief explanation of the decomposition strategy"
}}
"""
    
    def decompose(self, task: str, context: TaskContext, _recursion_depth: int = 0) -> List[Subtask]:
        """Decompose a task into subtasks using rule-based approach, with recursion protection."""
        if _recursion_depth > MAX_RECURSION_DEPTH:
            logger.error(f"Max recursion depth reached in DynamicTaskDecomposer.decompose for task: {task}")
            # Fallback: return a single subtask
            agent_role = self._find_best_agent_for_capabilities(self._identify_required_capabilities(task))
            return [Subtask(
                task_id=f"{context.task_id}_subtask_fallback",
                description=task,
                agent_role=agent_role,
                capabilities_required=self._identify_required_capabilities(task),
                parameters=context.parameters,
                estimated_duration=60
            )]
        complexity = self._analyze_task_complexity(task, context)
        required_capabilities = self._identify_required_capabilities(task)
        
        if complexity == TaskComplexity.SIMPLE:
            # Single subtask
            agent_role = self._find_best_agent_for_capabilities(required_capabilities)
            subtask = Subtask(
                task_id=f"{context.task_id}_subtask_1",
                description=task,
                agent_role=agent_role,
                capabilities_required=required_capabilities,
                parameters=context.parameters,
                estimated_duration=30
            )
            return [subtask]
        
        elif complexity == TaskComplexity.MODERATE:
            # Multiple subtasks, same agent
            agent_role = self._find_best_agent_for_capabilities(required_capabilities)
            subtasks = []
            
            # Split by capability if multiple capabilities required
            for i, capability in enumerate(required_capabilities):
                subtask = Subtask(
                    task_id=f"{context.task_id}_subtask_{i+1}",
                    description=f"Handle {capability.value} aspect of: {task}",
                    agent_role=agent_role,
                    capabilities_required=[capability],
                    parameters=context.parameters,
                    estimated_duration=45
                )
                subtasks.append(subtask)
            
            return subtasks
        
        else:
            # Complex tasks - use LLM if available
            return self._decompose_with_llm(task, context, _recursion_depth=_recursion_depth+1)
    
    def _decompose_with_llm(self, task: str, context: TaskContext, _recursion_depth: int = 0) -> List[Subtask]:
        """Decompose complex tasks using LLM, with recursion protection."""
        if _recursion_depth > MAX_RECURSION_DEPTH:
            logger.error(f"Max recursion depth reached in DynamicTaskDecomposer._decompose_with_llm for task: {task}")
            # Fallback: return a single subtask
            agent_role = self._find_best_agent_for_capabilities(self._identify_required_capabilities(task))
            return [Subtask(
                task_id=f"{context.task_id}_subtask_fallback",
                description=task,
                agent_role=agent_role,
                capabilities_required=self._identify_required_capabilities(task),
                parameters=context.parameters,
                estimated_duration=60
            )]
        if not self.llm:
            # Fallback to simple decomposition
            return self.decompose(task, context, _recursion_depth=_recursion_depth+1)
        try:
            prompt = self._create_llm_decomposition_prompt(task, context)
            response = self.llm.invoke(prompt)
            try:
                data = json.loads(response)
                subtasks = []
                for i, subtask_data in enumerate(data.get('subtasks', [])):
                    agent_role_str = subtask_data.get('agent_role', 'MESSAGE_PROCESSOR')
                    try:
                        agent_role = AgentRole(agent_role_str.lower())
                    except ValueError:
                        agent_role = AgentRole.MESSAGE_PROCESSOR
                    capabilities = []
                    for cap_str in subtask_data.get('capabilities_required', []):
                        try:
                            capability = CapabilityType(cap_str.lower())
                            capabilities.append(capability)
                        except ValueError:
                            continue
                    subtask = Subtask(
                        task_id=f"{context.task_id}_subtask_{i+1}",
                        description=subtask_data.get('description', task),
                        agent_role=agent_role,
                        capabilities_required=capabilities,
                        parameters=subtask_data.get('parameters', context.parameters),
                        dependencies=subtask_data.get('dependencies', []),
                        estimated_duration=subtask_data.get('estimated_duration', 60),
                        priority=subtask_data.get('priority', 1)
                    )
                    subtasks.append(subtask)
                self.decomposition_history.append({
                    'timestamp': datetime.now(),
                    'task': task,
                    'complexity': data.get('complexity', 'UNKNOWN'),
                    'subtasks_count': len(subtasks),
                    'reasoning': data.get('reasoning', '')
                })
                return subtasks
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON response from LLM: {response}")
                return self.decompose(task, context, _recursion_depth=_recursion_depth+1)  # Fallback
        except Exception as e:
            logger.error(f"Error in LLM decomposition: {e}")
            return self.decompose(task, context, _recursion_depth=_recursion_depth+1)  # Fallback
    
    async def adecompose(self, task: str, context: TaskContext) -> List[Subtask]:
        """Async decompose a task into subtasks."""
        return self.decompose(task, context)
    
    async def decompose_request(self, request: str, agents: List, context: Any) -> List[Subtask]:
        """Decompose a request into subtasks (legacy method for compatibility)."""
        # Convert to TaskContext if needed
        if isinstance(context, TaskContext):
            task_context = context
        else:
            task_context = TaskContext(
                task_id=f"request_{datetime.now().timestamp()}",
                user_id=context.get('user_id', 'unknown'),
                team_id=context.get('team_id', 'unknown'),
                parameters=context,
                metadata={}
            )
        
        return self.decompose(request, task_context)
    
    def get_decomposition_analytics(self) -> Dict[str, Any]:
        """Get analytics about task decomposition."""
        if not self.decomposition_history:
            return {}
        
        total_decompositions = len(self.decomposition_history)
        complexity_counts = {}
        avg_subtasks = 0
        
        for entry in self.decomposition_history:
            complexity = entry.get('complexity', 'UNKNOWN')
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
            avg_subtasks += entry.get('subtasks_count', 0)
        
        avg_subtasks = avg_subtasks / total_decompositions if total_decompositions > 0 else 0
        
        return {
            'total_decompositions': total_decompositions,
            'complexity_distribution': complexity_counts,
            'average_subtasks_per_decomposition': avg_subtasks,
            'recent_decompositions': self.decomposition_history[-10:]  # Last 10
        }


class ImprovedAgenticSystem:
    """Improved agentic system for task execution."""
    
    def __init__(self):
        self.mock = Mock()
    
    def execute(self, task: str, context: TaskContext) -> Dict[str, Any]:
        """Execute a task."""
        return self.mock(task, context)
    
    async def aexecute(self, task: str, context: TaskContext) -> Dict[str, Any]:
        """Async execute a task."""
        return self.execute(task, context)


class CapabilityBasedRouter:
    """Improved capability-based router with hierarchical routing strategy."""
    
    def __init__(self, capability_matrix: AgentCapabilityMatrix = None):
        self.capability_matrix = capability_matrix or AgentCapabilityMatrix()
        self.agent_loads = defaultdict(int)
        self.agent_availability = defaultdict(lambda: True)
        self.routing_history = []
        logger.info("[CapabilityBasedRouter] Initialized with hierarchical routing strategy")
    
    def _calculate_agent_score(self, agent_role: AgentRole, subtask: Subtask) -> float:
        """Calculate agent score with weighted capability matching."""
        score = 0.0
        
        # Primary capability match (weight: 0.6)
        primary_capabilities = self.capability_matrix.get_primary_capabilities(agent_role)
        for cap in subtask.capabilities_required:
            if cap in [pc.capability for pc in primary_capabilities]:
                score += 0.6 * self.capability_matrix.get_agent_proficiency(agent_role, cap)
        
        # Secondary capability match (weight: 0.3)
        all_capabilities = self.capability_matrix.get_agent_capabilities(agent_role)
        for cap in subtask.capabilities_required:
            if cap in [ac.capability for ac in all_capabilities]:
                score += 0.3 * self.capability_matrix.get_agent_proficiency(agent_role, cap)
        
        # Load balancing (weight: 0.1)
        load_factor = 1.0 / (1.0 + self.get_agent_load(agent_role))
        score += 0.1 * load_factor
        
        logger.debug(f"[CapabilityBasedRouter] Agent {agent_role.value} score: {score:.3f} for capabilities {[cap.value for cap in subtask.capabilities_required]}")
        return score
    
    def _find_available_agents(self, agents: List) -> List:
        """Find available agents from the list."""
        available_agents = []
        for agent in agents:
            # Use the same logic as _get_agent_role to find the agent's role
            agent_role = self._get_agent_role(agent)
            if agent_role and self.agent_availability.get(agent_role, True):
                available_agents.append(agent)
        return available_agents
    
    def _find_exact_capability_match(self, subtask: Subtask, agents: List) -> Optional[Any]:
        """Tier 1: Find agent with ALL required capabilities."""
        available_agents = self._find_available_agents(agents)
        
        for agent in available_agents:
            agent_role = self._get_agent_role(agent)
            agent_capabilities = [cap.capability for cap in self.capability_matrix.get_agent_capabilities(agent_role)]
            
            # Check if agent has ALL required capabilities
            if all(cap in agent_capabilities for cap in subtask.capabilities_required):
                logger.info(f"[CapabilityBasedRouter] Found exact capability match: {agent_role.value}")
                return agent
        
        return None
    
    def _find_partial_capability_match(self, subtask: Subtask, agents: List) -> Optional[Any]:
        """Tier 2: Find agent with best partial capability match."""
        available_agents = self._find_available_agents(agents)
        
        best_agent = None
        best_score = 0.0
        
        for agent in available_agents:
            agent_role = self._get_agent_role(agent)
            score = self._calculate_agent_score(agent_role, subtask)
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        if best_agent and best_score > 0.3:  # Minimum threshold for partial match
            logger.info(f"[CapabilityBasedRouter] Found partial capability match: {self._get_agent_role(best_agent).value} (score: {best_score:.3f})")
            return best_agent
        
        return None
    
    def _find_fallback_agent(self, subtask: Subtask, agents: List) -> Optional[Any]:
        """Tier 3: Find fallback agent when exact/partial matches fail."""
        available_agents = self._find_available_agents(agents)
        
        # Try COMMAND_FALLBACK_AGENT first
        for agent in available_agents:
            agent_role = self._get_agent_role(agent)
            if agent_role == AgentRole.COMMAND_FALLBACK_AGENT:
                logger.info(f"[CapabilityBasedRouter] Using fallback agent: {agent_role.value}")
                return agent
        
        # Try MESSAGE_PROCESSOR as general fallback
        for agent in available_agents:
            agent_role = self._get_agent_role(agent)
            if agent_role == AgentRole.MESSAGE_PROCESSOR:
                logger.info(f"[CapabilityBasedRouter] Using message processor fallback: {agent_role.value}")
                return agent
        
        # Last resort: any available agent
        if available_agents:
            agent_role = self._get_agent_role(available_agents[0])
            logger.info(f"[CapabilityBasedRouter] Using last resort agent: {agent_role.value}")
            return available_agents[0]
        
        return None
    
    def _update_agent_load(self, agent_role: AgentRole, increment: int = 1):
        """Update agent load tracking."""
        self.agent_loads[agent_role] += increment
    
    def _get_agent_role(self, agent) -> AgentRole:
        """Get agent role from agent object."""
        # Try to get role from agent_config
        if hasattr(agent, 'agent_config') and hasattr(agent.agent_config, 'role'):
            return agent.agent_config.role
        
        # Try to get role directly
        if hasattr(agent, 'role'):
            return agent.role
        
        # Try to get role from name
        if hasattr(agent, 'name'):
            try:
                return AgentRole(agent.name.lower())
            except ValueError:
                pass
        
        # Default fallback
        return AgentRole.MESSAGE_PROCESSOR
    
    def route(self, subtask: Subtask, agents: List) -> Optional[Any]:
        """Route a subtask using hierarchical routing strategy."""
        if not agents:
            logger.warning("[CapabilityBasedRouter] No agents available for routing")
            return None
        
        # Find available agents
        available_agents = self._find_available_agents(agents)
        if not available_agents:
            logger.warning("[CapabilityBasedRouter] No available agents for routing")
            return None
        
        # Tier 1: Exact capability match
        exact_match = self._find_exact_capability_match(subtask, available_agents)
        if exact_match:
            best_agent = exact_match
            routing_tier = "exact_match"
        else:
            # Tier 2: Partial capability match
            partial_match = self._find_partial_capability_match(subtask, available_agents)
            if partial_match:
                best_agent = partial_match
                routing_tier = "partial_match"
            else:
                # Tier 3: Fallback routing
                fallback_agent = self._find_fallback_agent(subtask, available_agents)
                if fallback_agent:
                    best_agent = fallback_agent
                    routing_tier = "fallback"
                else:
                    logger.error(f"[CapabilityBasedRouter] Failed to route subtask: {subtask.description}")
                    return None
        
        # Update load tracking
        best_role = self._get_agent_role(best_agent)
        self._update_agent_load(best_role)
        
        # Log routing decision
        routing_decision = {
            'timestamp': datetime.now(),
            'subtask_id': subtask.task_id,
            'subtask_description': subtask.description,
            'selected_agent': best_role.value,
            'routing_tier': routing_tier,
            'capabilities_required': [cap.value for cap in subtask.capabilities_required],
            'total_agents_considered': len(available_agents)
        }
        self.routing_history.append(routing_decision)
        
        logger.info(f"[CapabilityBasedRouter] Routed subtask '{subtask.description}' to {best_role.value} (tier: {routing_tier})")
        
        return best_agent
    
    def route_multiple(self, subtasks: List[Subtask], agents: List) -> Dict[str, Any]:
        """Route multiple subtasks to agents, considering dependencies."""
        if not subtasks:
            return {}
        
        # Sort subtasks by priority and dependencies
        sorted_subtasks = self._sort_subtasks_by_dependencies(subtasks)
        
        routing_results = {}
        for subtask in sorted_subtasks:
            agent = self.route(subtask, agents)
            if agent:
                routing_results[subtask.task_id] = {
                    'agent': agent,
                    'agent_role': self._get_agent_role(agent),
                    'subtask': subtask
                }
            else:
                logger.error(f"Failed to route subtask: {subtask.description}")
        
        return routing_results
    
    def _sort_subtasks_by_dependencies(self, subtasks: List[Subtask]) -> List[Subtask]:
        """Sort subtasks to respect dependencies."""
        # Create dependency graph
        dependency_graph = {}
        for subtask in subtasks:
            dependency_graph[subtask.task_id] = subtask.dependencies or []
        
        # Topological sort
        sorted_subtasks = []
        visited = set()
        temp_visited = set()
        
        def visit(subtask_id):
            if subtask_id in temp_visited:
                raise ValueError(f"Circular dependency detected: {subtask_id}")
            if subtask_id in visited:
                return
            
            temp_visited.add(subtask_id)
            
            # Visit dependencies first
            for dep_id in dependency_graph.get(subtask_id, []):
                # Find the subtask with this ID
                dep_subtask = next((s for s in subtasks if s.task_id == dep_id), None)
                if dep_subtask:
                    visit(dep_id)
            
            temp_visited.remove(subtask_id)
            visited.add(subtask_id)
            
            # Find and add the subtask
            subtask = next((s for s in subtasks if s.task_id == subtask_id), None)
            if subtask:
                sorted_subtasks.append(subtask)
        
        # Visit all subtasks
        for subtask in subtasks:
            if subtask.task_id not in visited:
                visit(subtask.task_id)
        
        # Sort by priority within dependency order
        sorted_subtasks.sort(key=lambda s: s.priority, reverse=True)
        
        return sorted_subtasks
    
    def set_agent_availability(self, agent_role: AgentRole, available: bool):
        """Set agent availability."""
        self.agent_availability[agent_role] = available
        logger.info(f"Agent {agent_role.value} availability set to: {available}")
    
    def get_agent_load(self, agent_role: AgentRole) -> int:
        """Get current load for an agent."""
        return self.agent_loads.get(agent_role, 0)
    
    def reset_agent_load(self, agent_role: AgentRole):
        """Reset load for an agent (e.g., after task completion)."""
        self.agent_loads[agent_role] = 0
        logger.debug(f"Reset load for agent {agent_role.value}")
    
    def get_routing_analytics(self) -> Dict[str, Any]:
        """Get analytics about routing decisions."""
        if not self.routing_history:
            return {}
        
        total_routes = len(self.routing_history)
        agent_usage = {}
        avg_scores = {}
        
        for entry in self.routing_history:
            agent = entry['selected_agent']
            score = entry['agent_score']
            
            if agent not in agent_usage:
                agent_usage[agent] = 0
                avg_scores[agent] = []
            
            agent_usage[agent] += 1
            avg_scores[agent].append(score)
        
        # Calculate average scores
        for agent in avg_scores:
            avg_scores[agent] = sum(avg_scores[agent]) / len(avg_scores[agent])
        
        return {
            'total_routes': total_routes,
            'agent_usage': agent_usage,
            'average_scores': avg_scores,
            'current_loads': self.agent_loads.copy(),
            'agent_availability': self.agent_availability.copy(),
            'recent_routes': self.routing_history[-10:]  # Last 10
        }
    
    async def aroute(self, subtask: Subtask, agents: List) -> Optional[Any]:
        """Async route a subtask to the best available agent."""
        return self.route(subtask, agents)
    
    async def aroute_multiple(self, subtasks: List[Subtask], agents: List) -> Dict[str, Any]:
        """Async route multiple subtasks to agents."""
        return self.route_multiple(subtasks, agents)


class StandaloneIntelligentRouter:
    """Standalone intelligent router."""
    
    def __init__(self):
        self.mock = Mock()
    
    def route(self, task: str, context: Dict[str, Any]) -> str:
        """Route a task to an agent."""
        return self.mock(task, context)
    
    async def aroute(self, task: str, context: Dict[str, Any]) -> str:
        """Async route a task to an agent."""
        return self.route(task, context)


@dataclass
class RoutingDecision:
    """Routing decision structure."""
    complexity: int
    agent_sequence: List[str]
    estimated_time: int
    reasoning: Optional[str] = None


@dataclass
class RequestContext:
    """Context for routing requests."""
    user_id: str
    team_id: str
    request_type: str
    parameters: Dict[str, Any]


class SimpleAgenticHandler:
    """Simple agentic handler."""
    
    def __init__(self):
        self.mock = Mock()
    
    def handle(self, request: str, context: RequestContext) -> str:
        """Handle a request."""
        return self.mock(request, context)
    
    async def ahandle(self, request: str, context: RequestContext) -> str:
        """Async handle a request."""
        return self.handle(request, context) 

@dataclass
class ExecutionResult:
    """Result of task execution."""
    task_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    agent_role: Optional[AgentRole] = None
    metadata: Dict[str, Any] = None

@dataclass
class ExecutionStatus:
    """Status of task execution."""
    task_id: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    progress: float = 0.0  # 0.0 to 1.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    agent_role: Optional[AgentRole] = None
    error: Optional[str] = None

class TaskExecutionOrchestrator:
    """Orchestrates task execution with dependency management and monitoring."""
    
    def __init__(self, capability_matrix: AgentCapabilityMatrix = None):
        self.capability_matrix = capability_matrix or AgentCapabilityMatrix()
        self.execution_history = []
        self.active_executions = {}  # task_id -> ExecutionStatus
        self.execution_results = {}  # task_id -> ExecutionResult
        self.dependency_graph = {}
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0
        }
    
    def _create_execution_status(self, subtask: Subtask) -> ExecutionStatus:
        """Create execution status for a subtask."""
        return ExecutionStatus(
            task_id=subtask.task_id,
            status='pending',
            agent_role=subtask.agent_role
        )
    
    def _update_execution_status(self, task_id: str, status: str, progress: float = None, error: str = None):
        """Update execution status."""
        if task_id in self.active_executions:
            exec_status = self.active_executions[task_id]
            exec_status.status = status
            
            if progress is not None:
                exec_status.progress = progress
            
            if error is not None:
                exec_status.error = error
            
            if status == 'running' and exec_status.start_time is None:
                exec_status.start_time = datetime.now()
            elif status in ['completed', 'failed', 'cancelled']:
                exec_status.end_time = datetime.now()
    
    def _check_dependencies_ready(self, subtask: Subtask) -> bool:
        """Check if all dependencies for a subtask are completed."""
        if not subtask.dependencies:
            return True
        
        for dep_id in subtask.dependencies:
            if dep_id not in self.execution_results:
                return False
            if not self.execution_results[dep_id].success:
                return False
        
        return True
    
    def _execute_subtask(self, subtask: Subtask, agent: Any) -> ExecutionResult:
        """
        Execute a single subtask with an agent using the unified interface.
        
        This method prioritizes the standardized agent.execute() method as the primary
        interface for all agent task execution, with fallbacks for legacy agents.
        """
        start_time = datetime.now()
        task_id = subtask.task_id
        
        try:
            # Update status to running
            self._update_execution_status(task_id, 'running', 0.1)
            
            # Primary: Use the unified execute() interface
            if hasattr(agent, 'execute') and callable(getattr(agent, 'execute')):
                logger.debug(f"Using unified agent.execute() interface for subtask {task_id}")
                result = agent.execute(subtask.description, subtask.parameters)
                
            # Fallback 1: Legacy execute_task method
            elif hasattr(agent, 'execute_task') and callable(getattr(agent, 'execute_task')):
                logger.debug(f"Using legacy agent.execute_task() for subtask {task_id}")
                result = agent.execute_task(subtask.description, subtask.parameters)
                
            # Fallback 2: Legacy process method
            elif hasattr(agent, 'process') and callable(getattr(agent, 'process')):
                logger.debug(f"Using legacy agent.process() for subtask {task_id}")
                result = agent.process(subtask.description, subtask.parameters)
                
            # Fallback 3: Legacy handle method
            elif hasattr(agent, 'handle') and callable(getattr(agent, 'handle')):
                logger.debug(f"Using legacy agent.handle() for subtask {task_id}")
                result = agent.handle(subtask.description, subtask.parameters)
                
            # Fallback 4: Direct callable agent
            elif callable(agent):
                logger.debug(f"Using direct agent call for subtask {task_id}")
                result = agent(subtask.description, subtask.parameters)
                
            else:
                # No suitable execution method found
                raise ValueError(
                    f"Agent {type(agent).__name__} does not implement any recognized execution interface. "
                    f"Expected: execute(), execute_task(), process(), handle(), or callable agent. "
                    f"Available methods: {[m for m in dir(agent) if not m.startswith('_')]}"
                )
            
            # Validate result
            if result is None:
                logger.warning(f"Agent returned None result for subtask {task_id}")
                result = "Task completed but no result returned"
            
            # Update status to completed
            self._update_execution_status(task_id, 'completed', 1.0)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            execution_result = ExecutionResult(
                task_id=task_id,
                success=True,
                result=result,
                execution_time=execution_time,
                agent_role=subtask.agent_role,
                metadata={
                    'subtask_description': subtask.description,
                    'execution_interface': 'execute' if hasattr(agent, 'execute') else 'legacy',
                    'agent_type': type(agent).__name__
                }
            )
            
            logger.info(f"✅ Subtask '{subtask.description}' completed successfully in {execution_time:.2f}s using {execution_result.metadata['execution_interface']} interface")
            return execution_result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error executing subtask '{subtask.description}': {str(e)}"
            
            # Update status to failed
            self._update_execution_status(task_id, 'failed', 1.0, error_msg)
            
            execution_result = ExecutionResult(
                task_id=task_id,
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time,
                agent_role=subtask.agent_role,
                metadata={
                    'subtask_description': subtask.description,
                    'agent_type': type(agent).__name__,
                    'exception_type': type(e).__name__
                }
            )
            
            logger.error(f"❌ Subtask '{subtask.description}' failed: {str(e)}")
            return execution_result
    
    def execute_tasks(self, subtasks: List[Subtask], agents: List, router: CapabilityBasedRouter) -> Dict[str, ExecutionResult]:
        """Execute multiple subtasks with dependency management."""
        if not subtasks:
            return {}
        
        # Initialize execution tracking
        for subtask in subtasks:
            self.active_executions[subtask.task_id] = self._create_execution_status(subtask)
        
        # Build dependency graph
        self.dependency_graph = {subtask.task_id: subtask.dependencies or [] for subtask in subtasks}
        
        # Execute tasks respecting dependencies
        completed_tasks = set()
        execution_results = {}
        
        while len(completed_tasks) < len(subtasks):
            # Find ready tasks (dependencies completed)
            ready_tasks = []
            for subtask in subtasks:
                if (subtask.task_id not in completed_tasks and 
                    self._check_dependencies_ready(subtask)):
                    ready_tasks.append(subtask)
            
            if not ready_tasks:
                # Check for circular dependencies or stuck tasks
                remaining_tasks = [s.task_id for s in subtasks if s.task_id not in completed_tasks]
                logger.error(f"Circular dependency or stuck tasks detected: {remaining_tasks}")
                break
            
            # Execute ready tasks
            for subtask in ready_tasks:
                # Route to best agent
                agent = router.route(subtask, agents)
                if not agent:
                    logger.error(f"No agent available for subtask: {subtask.description}")
                    continue
                
                # Execute the subtask
                result = self._execute_subtask(subtask, agent)
                execution_results[subtask.task_id] = result
                completed_tasks.add(subtask.task_id)
                
                # Update execution statistics
                self._update_execution_stats(result)
                
                # Reset agent load after completion
                router.reset_agent_load(subtask.agent_role)
        
        # Store results
        self.execution_results.update(execution_results)
        
        # Log execution summary
        successful = sum(1 for r in execution_results.values() if r.success)
        total = len(execution_results)
        logger.info(f"🎯 Task execution completed: {successful}/{total} successful")
        
        return execution_results
    
    def _update_execution_stats(self, result: ExecutionResult):
        """Update execution statistics."""
        self.execution_stats['total_executions'] += 1
        
        if result.success:
            self.execution_stats['successful_executions'] += 1
        else:
            self.execution_stats['failed_executions'] += 1
        
        # Update average execution time
        total_time = self.execution_stats['average_execution_time'] * (self.execution_stats['total_executions'] - 1)
        total_time += result.execution_time
        self.execution_stats['average_execution_time'] = total_time / self.execution_stats['total_executions']
    
    def get_execution_status(self, task_id: str) -> Optional[ExecutionStatus]:
        """Get execution status for a specific task."""
        return self.active_executions.get(task_id)
    
    def get_all_execution_statuses(self) -> Dict[str, ExecutionStatus]:
        """Get all current execution statuses."""
        return self.active_executions.copy()
    
    def get_execution_result(self, task_id: str) -> Optional[ExecutionResult]:
        """Get execution result for a specific task."""
        return self.execution_results.get(task_id)
    
    def cancel_execution(self, task_id: str) -> bool:
        """Cancel execution of a task."""
        if task_id in self.active_executions:
            self._update_execution_status(task_id, 'cancelled')
            logger.info(f"Cancelled execution of task: {task_id}")
            return True
        return False
    
    def get_execution_analytics(self) -> Dict[str, Any]:
        """Get comprehensive execution analytics."""
        analytics = {
            'execution_stats': self.execution_stats.copy(),
            'active_executions': len(self.active_executions),
            'completed_executions': len(self.execution_results),
            'recent_executions': []
        }
        
        # Add recent execution history
        recent_results = list(self.execution_results.values())[-10:]  # Last 10
        for result in recent_results:
            analytics['recent_executions'].append({
                'task_id': result.task_id,
                'success': result.success,
                'execution_time': result.execution_time,
                'agent_role': result.agent_role.value if result.agent_role else None,
                'error': result.error
            })
        
        # Add dependency analysis
        analytics['dependency_analysis'] = {
            'total_dependencies': sum(len(deps) for deps in self.dependency_graph.values()),
            'max_dependency_depth': self._calculate_max_dependency_depth(),
            'circular_dependencies': self._detect_circular_dependencies()
        }
        
        return analytics
    
    def _calculate_max_dependency_depth(self) -> int:
        """Calculate maximum dependency depth."""
        if not self.dependency_graph:
            return 0
        
        def calculate_depth(task_id, visited=None):
            if visited is None:
                visited = set()
            
            if task_id in visited:
                return 0  # Circular dependency
            
            visited.add(task_id)
            dependencies = self.dependency_graph.get(task_id, [])
            
            if not dependencies:
                return 1
            
            max_depth = 1
            for dep_id in dependencies:
                depth = calculate_depth(dep_id, visited.copy())
                max_depth = max(max_depth, depth + 1)
            
            return max_depth
        
        max_depth = 0
        for task_id in self.dependency_graph:
            depth = calculate_depth(task_id)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the dependency graph."""
        def find_cycles(task_id, path=None):
            if path is None:
                path = []
            
            if task_id in path:
                cycle_start = path.index(task_id)
                return [path[cycle_start:] + [task_id]]
            
            path.append(task_id)
            cycles = []
            
            for dep_id in self.dependency_graph.get(task_id, []):
                cycles.extend(find_cycles(dep_id, path.copy()))
            
            return cycles
        
        all_cycles = []
        for task_id in self.dependency_graph:
            cycles = find_cycles(task_id)
            all_cycles.extend(cycles)
        
        # Remove duplicates
        unique_cycles = []
        for cycle in all_cycles:
            if cycle not in unique_cycles:
                unique_cycles.append(cycle)
        
        return unique_cycles
    
    async def aexecute_tasks(self, subtasks: List[Subtask], agents: List, router: CapabilityBasedRouter) -> Dict[str, ExecutionResult]:
        """Async execute multiple subtasks."""
        return self.execute_tasks(subtasks, agents, router)
    
    def clear_execution_history(self):
        """Clear execution history and reset statistics."""
        self.execution_history.clear()
        self.active_executions.clear()
        self.execution_results.clear()
        self.dependency_graph.clear()
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0
        }
        logger.info("Cleared execution history and reset statistics") 

@dataclass
class IntentClassification:
    """Result of intent classification."""
    primary_intent: str
    confidence: float
    secondary_intents: List[Tuple[str, float]] = None
    entities: Dict[str, Any] = None
    context: Dict[str, Any] = None
    classification_method: str = 'keyword'  # 'keyword', 'pattern', 'llm'

class IntentClassifier:
    """Classifies user intent using multiple methods."""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.intent_patterns = self._load_intent_patterns()
        self.keyword_mappings = self._load_keyword_mappings()
        self.classification_history = []
        
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for intent classification."""
        return {
            'player_registration': [
                r'\b(?:register|sign up|join|add)\b.*\b(?:player|member|team)\b',
                r'\b(?:new player|new member)\b',
                r'\b(?:want to join|join the team)\b'
            ],
            'player_approval': [
                r'\b(?:approve|accept|confirm)\b.*\b(?:player|member)\b',
                r'\b(?:player approval|approve player)\b'
            ],
            'status_inquiry': [
                r'\b(?:status|check|what is|how is)\b.*\b(?:registration|approval|player)\b',
                r'\b(?:am i|are they)\b.*\b(?:approved|registered|accepted)\b',
                r'\b(?:registration status|approval status)\b'
            ],
            'payment_inquiry': [
                r'\b(?:payment|pay|fee|cost|money)\b',
                r'\b(?:how much|what is the cost|payment details)\b'
            ],
            'match_inquiry': [
                r'\b(?:match|game|fixture|when is|next game)\b',
                r'\b(?:schedule|calendar|upcoming)\b.*\b(?:match|game)\b'
            ],
            'availability_update': [
                r'\b(?:available|unavailable|can play|cannot play)\b',
                r'\b(?:available for|not available for)\b.*\b(?:match|game)\b'
            ],
            'help_request': [
                r'\b(?:help|support|assist|how to|what can)\b',
                r'\b(?:don\'t know|confused|need help)\b'
            ],
            'general_inquiry': [
                r'\b(?:what|how|why|when|where)\b',
                r'\b(?:tell me|explain|describe)\b'
            ]
        }
    
    def _load_keyword_mappings(self) -> Dict[str, List[str]]:
        """Load keyword mappings for intent classification."""
        return {
            'player_registration': [
                'register', 'signup', 'join', 'add', 'new player', 'new member',
                'registration', 'sign up', 'become a player', 'join team'
            ],
            'player_approval': [
                'approve', 'accept', 'confirm', 'approval', 'authorize',
                'grant access', 'give permission', 'allow'
            ],
            'status_inquiry': [
                'status', 'check', 'what is', 'how is', 'am i', 'are they',
                'registration status', 'approval status', 'player status'
            ],
            'payment_inquiry': [
                'payment', 'pay', 'fee', 'cost', 'money', 'price',
                'how much', 'payment details', 'financial'
            ],
            'match_inquiry': [
                'match', 'game', 'fixture', 'schedule', 'calendar',
                'when is', 'next game', 'upcoming', 'match details'
            ],
            'availability_update': [
                'available', 'unavailable', 'can play', 'cannot play',
                'availability', 'free', 'busy', 'occupied'
            ],
            'help_request': [
                'help', 'support', 'assist', 'how to', 'what can',
                'don\'t know', 'confused', 'need help', 'trouble'
            ],
            'general_inquiry': [
                'what', 'how', 'why', 'when', 'where', 'tell me',
                'explain', 'describe', 'information', 'details'
            ]
        }
    
    def _keyword_classification(self, text: str) -> Tuple[str, float]:
        """Classify intent using keyword matching."""
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, keywords in self.keyword_mappings.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            if score > 0:
                # Normalize score by number of keywords
                intent_scores[intent] = score / len(keywords)
        
        if not intent_scores:
            return 'general_inquiry', 0.3  # Default fallback
        
        # Return intent with highest score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent
    
    def _pattern_classification(self, text: str) -> Tuple[str, float]:
        """Classify intent using regex patterns."""
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                # Normalize score by number of patterns
                intent_scores[intent] = score / len(patterns)
        
        if not intent_scores:
            return 'general_inquiry', 0.2  # Default fallback
        
        # Return intent with highest score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text."""
        entities = {}
        text_lower = text.lower()
        
        # Extract phone numbers
        phone_pattern = r'\b(?:\+?44|0)?[17]\d{9}\b'
        phone_matches = re.findall(phone_pattern, text)
        if phone_matches:
            entities['phone'] = phone_matches[0]
        
        # Extract player names (simple heuristic)
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        name_matches = re.findall(name_pattern, text)
        if len(name_matches) >= 2:  # Likely first and last name
            entities['player_name'] = ' '.join(name_matches[:2])
        
        # Extract player IDs
        id_pattern = r'\b[A-Z]{2,4}\d*\b'
        id_matches = re.findall(id_pattern, text)
        if id_matches:
            entities['player_id'] = id_matches[0]
        
        # Extract amounts
        amount_pattern = r'\b\d+(?:\.\d{2})?\s*(?:pounds?|£|euros?|€|dollars?|\$)\b'
        amount_matches = re.findall(amount_pattern, text_lower)
        if amount_matches:
            entities['amount'] = amount_matches[0]
        
        # Extract dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        date_matches = re.findall(date_pattern, text)
        if date_matches:
            entities['date'] = date_matches[0]
        
        return entities
    
    def _create_llm_classification_prompt(self, text: str) -> str:
        """Create prompt for LLM-based intent classification."""
        return f"""
You are an intent classifier for a football team management system. 
Analyze the following user message and classify their intent.

Available intents:
- player_registration: User wants to register as a player
- player_approval: User wants to approve a player
- status_inquiry: User is asking about their status
- payment_inquiry: User is asking about payments or fees
- match_inquiry: User is asking about matches or games
- availability_update: User is updating their availability
- help_request: User needs help or support
- general_inquiry: General questions or information requests

User message: "{text}"

Please respond in JSON format:
{{
    "primary_intent": "intent_name",
    "confidence": 0.95,
    "secondary_intents": [
        ["intent_name", 0.8],
        ["intent_name", 0.6]
    ],
    "entities": {{
        "player_name": "John Smith",
        "phone": "+447123456789",
        "player_id": "JS1",
        "amount": "£25"
    }},
    "context": {{
        "urgency": "high|medium|low",
        "complexity": "simple|moderate|complex"
    }}
}}
"""
    
    def classify(self, text: str) -> IntentClassification:
        """Classify intent using multiple methods."""
        if not text or not text.strip():
            return IntentClassification(
                primary_intent='general_inquiry',
                confidence=0.1,
                classification_method='empty'
            )
        
        # Try LLM classification first if available
        if self.llm:
            try:
                llm_result = self._llm_classification(text)
                if llm_result.confidence > 0.7:  # High confidence threshold
                    return llm_result
            except Exception as e:
                logger.warning(f"LLM classification failed: {e}")
        
        # Fallback to pattern-based classification
        pattern_intent, pattern_confidence = self._pattern_classification(text)
        
        # Also try keyword classification
        keyword_intent, keyword_confidence = self._keyword_classification(text)
        
        # Combine results
        if pattern_intent == keyword_intent:
            # Both methods agree
            primary_intent = pattern_intent
            confidence = min(0.9, (pattern_confidence + keyword_confidence) / 2)
            classification_method = 'pattern_keyword_agreement'
        elif pattern_confidence > keyword_confidence:
            # Pattern method is more confident
            primary_intent = pattern_intent
            confidence = pattern_confidence
            classification_method = 'pattern'
        else:
            # Keyword method is more confident
            primary_intent = keyword_intent
            confidence = keyword_confidence
            classification_method = 'keyword'
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Create secondary intents
        secondary_intents = []
        if pattern_intent != primary_intent:
            secondary_intents.append((pattern_intent, pattern_confidence))
        if keyword_intent != primary_intent:
            secondary_intents.append((keyword_intent, keyword_confidence))
        
        # Sort secondary intents by confidence
        secondary_intents.sort(key=lambda x: x[1], reverse=True)
        
        result = IntentClassification(
            primary_intent=primary_intent,
            confidence=confidence,
            secondary_intents=secondary_intents,
            entities=entities,
            context={'classification_method': classification_method},
            classification_method=classification_method
        )
        
        # Log classification
        self.classification_history.append({
            'timestamp': datetime.now(),
            'text': text,
            'primary_intent': primary_intent,
            'confidence': confidence,
            'method': classification_method,
            'entities': entities
        })
        
        return result
    
    def _llm_classification(self, text: str) -> IntentClassification:
        """Classify intent using LLM."""
        prompt = self._create_llm_classification_prompt(text)
        response = self.llm.invoke(prompt)
        
        try:
            data = json.loads(response)
            
            return IntentClassification(
                primary_intent=data.get('primary_intent', 'general_inquiry'),
                confidence=data.get('confidence', 0.5),
                secondary_intents=data.get('secondary_intents', []),
                entities=data.get('entities', {}),
                context=data.get('context', {}),
                classification_method='llm'
            )
            
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON response from LLM: {response}")
            # Fallback to pattern classification
            intent, confidence = self._pattern_classification(text)
            return IntentClassification(
                primary_intent=intent,
                confidence=confidence,
                classification_method='llm_fallback'
            )
    
    def get_classification_analytics(self) -> Dict[str, Any]:
        """Get analytics about intent classification."""
        if not self.classification_history:
            return {}
        
        total_classifications = len(self.classification_history)
        intent_counts = {}
        method_counts = {}
        avg_confidence = 0.0
        
        for entry in self.classification_history:
            intent = entry['primary_intent']
            method = entry['method']
            confidence = entry['confidence']
            
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            method_counts[method] = method_counts.get(method, 0) + 1
            avg_confidence += confidence
        
        avg_confidence = avg_confidence / total_classifications if total_classifications > 0 else 0.0
        
        return {
            'total_classifications': total_classifications,
            'intent_distribution': intent_counts,
            'method_distribution': method_counts,
            'average_confidence': avg_confidence,
            'recent_classifications': self.classification_history[-10:]  # Last 10
        }
    
    async def aclassify(self, text: str) -> IntentClassification:
        """Async classify intent."""
        return self.classify(text) 

@dataclass
class ComplexityAssessment:
    """Result of complexity assessment."""
    complexity_level: TaskComplexity
    score: float  # 0.0 to 1.0
    factors: Dict[str, float]  # Individual factor scores
    reasoning: str
    estimated_processing_time: int  # seconds
    recommended_approach: str  # 'direct', 'decomposed', 'collaborative'

class RequestComplexityAssessor:
    """Assesses the complexity of user requests."""
    
    def __init__(self, capability_matrix: AgentCapabilityMatrix = None):
        self.capability_matrix = capability_matrix or AgentCapabilityMatrix()
        self.complexity_factors = self._load_complexity_factors()
        self.assessment_history = []
        
    def _load_complexity_factors(self) -> Dict[str, Dict[str, Any]]:
        """Load complexity assessment factors."""
        return {
            'intent_complexity': {
                'simple_intents': ['status_inquiry', 'help_request', 'general_inquiry'],
                'moderate_intents': ['player_registration', 'payment_inquiry', 'match_inquiry'],
                'complex_intents': ['player_approval', 'availability_update'],
                'very_complex_intents': ['multi_step_operation', 'coordination_task']
            },
            'entity_complexity': {
                'simple_entities': ['player_id', 'status'],
                'moderate_entities': ['player_name', 'phone', 'amount'],
                'complex_entities': ['match_details', 'payment_details', 'availability_schedule']
            },
            'context_complexity': {
                'simple_context': ['single_user', 'single_team'],
                'moderate_context': ['multiple_users', 'time_constraints'],
                'complex_context': ['multi_team', 'conflicting_requirements', 'urgent_deadlines']
            },
            'dependency_complexity': {
                'no_dependencies': 0.1,
                'single_dependency': 0.3,
                'multiple_dependencies': 0.6,
                'circular_dependencies': 0.9
            }
        }
    
    def _assess_intent_complexity(self, intent: str) -> float:
        """Assess complexity based on intent."""
        factors = self.complexity_factors['intent_complexity']
        
        if intent in factors['simple_intents']:
            return 0.2
        elif intent in factors['moderate_intents']:
            return 0.4
        elif intent in factors['complex_intents']:
            return 0.7
        elif intent in factors['very_complex_intents']:
            return 0.9
        else:
            return 0.5  # Default moderate complexity
    
    def _assess_entity_complexity(self, entities: Dict[str, Any]) -> float:
        """Assess complexity based on entities."""
        if not entities:
            return 0.1  # No entities = simple
        
        factors = self.complexity_factors['entity_complexity']
        entity_scores = []
        
        for entity_type in entities.keys():
            if entity_type in factors['simple_entities']:
                entity_scores.append(0.2)
            elif entity_type in factors['moderate_entities']:
                entity_scores.append(0.4)
            elif entity_type in factors['complex_entities']:
                entity_scores.append(0.7)
            else:
                entity_scores.append(0.5)  # Default
        
        # Return average entity complexity
        return sum(entity_scores) / len(entity_scores) if entity_scores else 0.1
    
    def _assess_context_complexity(self, context: Dict[str, Any]) -> float:
        """Assess complexity based on context."""
        if not context:
            return 0.1  # No context = simple
        
        factors = self.complexity_factors['context_complexity']
        context_score = 0.1  # Base score
        
        # Check for complexity indicators
        if context.get('multiple_users', False):
            context_score += 0.3
        if context.get('time_constraints', False):
            context_score += 0.2
        if context.get('multi_team', False):
            context_score += 0.4
        if context.get('conflicting_requirements', False):
            context_score += 0.5
        if context.get('urgent_deadlines', False):
            context_score += 0.3
        
        return min(1.0, context_score)
    
    def _assess_dependency_complexity(self, dependencies: List[str]) -> float:
        """Assess complexity based on dependencies."""
        if not dependencies:
            return self.complexity_factors['dependency_complexity']['no_dependencies']
        
        dependency_count = len(dependencies)
        
        if dependency_count == 1:
            return self.complexity_factors['dependency_complexity']['single_dependency']
        elif dependency_count <= 3:
            return self.complexity_factors['dependency_complexity']['multiple_dependencies']
        else:
            return self.complexity_factors['dependency_complexity']['circular_dependencies']
    
    def _assess_user_history_complexity(self, user_id: str, user_history: List[Dict[str, Any]]) -> float:
        """Assess complexity based on user interaction history."""
        if not user_history:
            return 0.3  # New user = moderate complexity
        
        # Analyze recent interactions
        recent_interactions = user_history[-10:]  # Last 10 interactions
        
        # Check for patterns that might indicate complexity
        complexity_indicators = 0
        
        for interaction in recent_interactions:
            # Check for errors or retries
            if interaction.get('had_error', False):
                complexity_indicators += 1
            
            # Check for multi-step operations
            if interaction.get('steps_required', 1) > 1:
                complexity_indicators += 1
            
            # Check for long processing times
            if interaction.get('processing_time', 0) > 30:  # More than 30 seconds
                complexity_indicators += 1
        
        # Normalize by number of interactions
        if recent_interactions:
            complexity_score = complexity_indicators / len(recent_interactions)
        else:
            complexity_score = 0.3
        
        return min(1.0, complexity_score)
    
    def _calculate_overall_complexity(self, factors: Dict[str, float]) -> Tuple[float, TaskComplexity]:
        """Calculate overall complexity score and level."""
        # Weight the factors
        weights = {
            'intent': 0.3,
            'entities': 0.2,
            'context': 0.2,
            'dependencies': 0.15,
            'user_history': 0.15
        }
        
        overall_score = 0.0
        for factor, weight in weights.items():
            if factor in factors:
                overall_score += factors[factor] * weight
        
        # Map score to complexity level
        if overall_score < 0.3:
            complexity_level = TaskComplexity.SIMPLE
        elif overall_score < 0.6:
            complexity_level = TaskComplexity.MODERATE
        elif overall_score < 0.8:
            complexity_level = TaskComplexity.COMPLEX
        else:
            complexity_level = TaskComplexity.VERY_COMPLEX
        
        return overall_score, complexity_level
    
    def _generate_reasoning(self, factors: Dict[str, float], complexity_level: TaskComplexity) -> str:
        """Generate reasoning for complexity assessment."""
        reasoning_parts = []
        
        # Add primary factors
        sorted_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)
        primary_factor, primary_score = sorted_factors[0]
        
        if primary_score > 0.7:
            reasoning_parts.append(f"High complexity in {primary_factor} ({primary_score:.2f})")
        elif primary_score > 0.4:
            reasoning_parts.append(f"Moderate complexity in {primary_factor} ({primary_score:.2f})")
        else:
            reasoning_parts.append(f"Low complexity in {primary_factor} ({primary_score:.2f})")
        
        # Add secondary factors if significant
        for factor, score in sorted_factors[1:3]:  # Top 3 factors
            if score > 0.5:
                reasoning_parts.append(f"Significant {factor} complexity ({score:.2f})")
        
        # Add overall assessment
        complexity_names = {
            TaskComplexity.SIMPLE: "simple",
            TaskComplexity.MODERATE: "moderate",
            TaskComplexity.COMPLEX: "complex",
            TaskComplexity.VERY_COMPLEX: "very complex"
        }
        
        reasoning_parts.append(f"Overall assessment: {complexity_names[complexity_level]} request")
        
        return "; ".join(reasoning_parts)
    
    def _estimate_processing_time(self, complexity_level: TaskComplexity, factors: Dict[str, float]) -> int:
        """Estimate processing time based on complexity."""
        base_times = {
            TaskComplexity.SIMPLE: 15,
            TaskComplexity.MODERATE: 45,
            TaskComplexity.COMPLEX: 120,
            TaskComplexity.VERY_COMPLEX: 300
        }
        
        base_time = base_times[complexity_level]
        
        # Adjust based on factors
        adjustments = 0
        
        # Entity complexity adjustment
        if factors.get('entities', 0) > 0.6:
            adjustments += 30
        
        # Dependency complexity adjustment
        if factors.get('dependencies', 0) > 0.5:
            adjustments += 60
        
        # Context complexity adjustment
        if factors.get('context', 0) > 0.7:
            adjustments += 45
        
        return base_time + adjustments
    
    def _recommend_approach(self, complexity_level: TaskComplexity, factors: Dict[str, float]) -> str:
        """Recommend processing approach based on complexity."""
        if complexity_level == TaskComplexity.SIMPLE:
            return 'direct'
        elif complexity_level == TaskComplexity.MODERATE:
            return 'decomposed'
        elif complexity_level == TaskComplexity.COMPLEX:
            return 'collaborative'
        else:  # VERY_COMPLEX
            return 'collaborative'
    
    def assess(self, request: str, intent: str, entities: Dict[str, Any], 
               context: Dict[str, Any], dependencies: List[str] = None,
               user_id: str = None, user_history: List[Dict[str, Any]] = None) -> ComplexityAssessment:
        """Assess the complexity of a request."""
        
        # Assess individual factors
        factors = {
            'intent': self._assess_intent_complexity(intent),
            'entities': self._assess_entity_complexity(entities),
            'context': self._assess_context_complexity(context),
            'dependencies': self._assess_dependency_complexity(dependencies or [])
        }
        
        # Add user history if available
        if user_id and user_history:
            factors['user_history'] = self._assess_user_history_complexity(user_id, user_history)
        else:
            factors['user_history'] = 0.3  # Default moderate complexity
        
        # Calculate overall complexity
        overall_score, complexity_level = self._calculate_overall_complexity(factors)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(factors, complexity_level)
        
        # Estimate processing time
        estimated_time = self._estimate_processing_time(complexity_level, factors)
        
        # Recommend approach
        recommended_approach = self._recommend_approach(complexity_level, factors)
        
        assessment = ComplexityAssessment(
            complexity_level=complexity_level,
            score=overall_score,
            factors=factors,
            reasoning=reasoning,
            estimated_processing_time=estimated_time,
            recommended_approach=recommended_approach
        )
        
        # Log assessment
        self.assessment_history.append({
            'timestamp': datetime.now(),
            'request': request,
            'intent': intent,
            'complexity_level': complexity_level.value,
            'score': overall_score,
            'factors': factors,
            'estimated_time': estimated_time,
            'recommended_approach': recommended_approach
        })
        
        logger.info(f"Complexity assessment: {complexity_level.value} (score: {overall_score:.2f}) - {reasoning}")
        
        return assessment
    
    def get_assessment_analytics(self) -> Dict[str, Any]:
        """Get analytics about complexity assessments."""
        if not self.assessment_history:
            return {}
        
        total_assessments = len(self.assessment_history)
        complexity_counts = {}
        approach_counts = {}
        avg_scores = {}
        avg_processing_times = {}
        
        for entry in self.assessment_history:
            complexity = entry['complexity_level']
            approach = entry['recommended_approach']
            score = entry['score']
            processing_time = entry['estimated_time']
            
            # Count complexity levels
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
            
            # Count approaches
            approach_counts[approach] = approach_counts.get(approach, 0) + 1
            
            # Track scores by complexity
            if complexity not in avg_scores:
                avg_scores[complexity] = []
            avg_scores[complexity].append(score)
            
            # Track processing times by complexity
            if complexity not in avg_processing_times:
                avg_processing_times[complexity] = []
            avg_processing_times[complexity].append(processing_time)
        
        # Calculate averages
        for complexity in avg_scores:
            avg_scores[complexity] = sum(avg_scores[complexity]) / len(avg_scores[complexity])
            avg_processing_times[complexity] = sum(avg_processing_times[complexity]) / len(avg_processing_times[complexity])
        
        return {
            'total_assessments': total_assessments,
            'complexity_distribution': complexity_counts,
            'approach_distribution': approach_counts,
            'average_scores_by_complexity': avg_scores,
            'average_processing_times_by_complexity': avg_processing_times,
            'recent_assessments': self.assessment_history[-10:]  # Last 10
        }
    
    async def aassess(self, request: str, intent: str, entities: Dict[str, Any], 
                     context: Dict[str, Any], dependencies: List[str] = None,
                     user_id: str = None, user_history: List[Dict[str, Any]] = None) -> ComplexityAssessment:
        """Async assess complexity."""
        return self.assess(request, intent, entities, context, dependencies, user_id, user_history) 

@dataclass
class UserPreference:
    """User preference data."""
    user_id: str
    preference_type: str  # 'communication_style', 'response_format', 'interaction_frequency', etc.
    value: Any
    confidence: float  # 0.0 to 1.0
    last_updated: datetime
    usage_count: int = 0

@dataclass
class UserProfile:
    """Complete user profile with preferences and patterns."""
    user_id: str
    preferences: Dict[str, UserPreference]
    interaction_patterns: Dict[str, Any]
    skill_level: str  # 'beginner', 'intermediate', 'advanced'
    preferred_agents: List[str]
    last_interaction: datetime
    total_interactions: int = 0

class UserPreferenceLearner:
    """Learns and adapts to user preferences and patterns."""
    
    def __init__(self, storage_backend=None):
        # Use the new InMemoryUserStorage if no backend provided
        self.storage_backend = storage_backend or InMemoryUserStorage()
        self.learning_config = self._load_learning_config()
        
    def _load_learning_config(self) -> Dict[str, Any]:
        """Load learning configuration."""
        return {
            'preference_types': {
                'communication_style': ['formal', 'casual', 'concise', 'detailed'],
                'response_format': ['text', 'structured', 'visual', 'summary'],
                'interaction_frequency': ['low', 'medium', 'high'],
                'complexity_preference': ['simple', 'moderate', 'advanced'],
                'agent_preference': ['message_processor', 'team_manager', 'player_coordinator'],
                'notification_preference': ['immediate', 'batched', 'summary_only']
            },
            'learning_rates': {
                'new_preference': 0.8,
                'existing_preference': 0.3,
                'conflicting_preference': 0.5
            },
            'confidence_thresholds': {
                'high_confidence': 0.8,
                'medium_confidence': 0.6,
                'low_confidence': 0.4
            }
        }
    
    def _extract_preferences_from_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Extract preference indicators from an interaction."""
        preferences = {}
        
        # Communication style preference
        message_length = len(interaction.get('user_message', ''))
        if message_length < 20:
            preferences['communication_style'] = 'concise'
        elif message_length > 100:
            preferences['communication_style'] = 'detailed'
        else:
            preferences['communication_style'] = 'casual'
        
        # Response format preference
        response = interaction.get('bot_response', '')
        if '|' in response or '\n' in response:
            preferences['response_format'] = 'structured'
        elif len(response) < 50:
            preferences['response_format'] = 'concise'
        else:
            preferences['response_format'] = 'text'
        
        # Complexity preference based on intent and success
        intent = interaction.get('intent', '')
        success = interaction.get('success', True)
        if intent in ['help_request', 'general_inquiry'] and not success:
            preferences['complexity_preference'] = 'simple'
        elif intent in ['player_approval', 'availability_update'] and success:
            preferences['complexity_preference'] = 'advanced'
        else:
            preferences['complexity_preference'] = 'moderate'
        
        # Agent preference based on successful interactions
        agent_used = interaction.get('agent_used', '')
        if agent_used and interaction.get('success', False):
            preferences['agent_preference'] = agent_used
        
        return preferences
    
    def _update_preference(self, user_id: str, preference_type: str, new_value: Any, 
                          interaction_success: bool = True) -> None:
        """Update a user preference."""
        # Get or create user profile from storage
        profile_data = self.storage_backend.get_user_profile(user_id)
        
        if profile_data is None:
            # Create new profile
            profile_data = {
                'user_id': user_id,
                'preferences': {},
                'interaction_patterns': {},
                'skill_level': 'beginner',
                'preferred_agents': [],
                'last_interaction': datetime.now(),
                'total_interactions': 0
            }
        
        # Update preference
        if preference_type in profile_data['preferences']:
            # Update existing preference
            preference = profile_data['preferences'][preference_type]
            old_value = preference['value']
            
            # Calculate learning rate
            if new_value == old_value:
                # Reinforce existing preference
                learning_rate = self.learning_config['learning_rates']['existing_preference']
                preference['confidence'] = min(1.0, preference['confidence'] + learning_rate * 0.1)
            else:
                # Conflicting preference
                learning_rate = self.learning_config['learning_rates']['conflicting_preference']
                if interaction_success:
                    # New preference is better
                    preference['value'] = new_value
                    preference['confidence'] = learning_rate
                else:
                    # Keep old preference, reduce confidence slightly
                    preference['confidence'] = max(0.1, preference['confidence'] - learning_rate * 0.1)
        else:
            # New preference
            learning_rate = self.learning_config['learning_rates']['new_preference']
            confidence = learning_rate if interaction_success else learning_rate * 0.5
            
            profile_data['preferences'][preference_type] = {
                'user_id': user_id,
                'preference_type': preference_type,
                'value': new_value,
                'confidence': confidence,
                'last_updated': datetime.now(),
                'usage_count': 1
            }
        
        # Update usage count and timestamp
        if preference_type in profile_data['preferences']:
            profile_data['preferences'][preference_type]['usage_count'] += 1
            profile_data['preferences'][preference_type]['last_updated'] = datetime.now()
        
        # Save updated profile
        self.storage_backend.save_user_profile(user_id, profile_data)
    
    def _update_skill_level(self, user_id: str, interaction: Dict[str, Any]) -> None:
        """Update user skill level based on interaction patterns."""
        profile_data = self.storage_backend.get_user_profile(user_id)
        if profile_data is None:
            return
        
        # Analyze recent interactions for skill indicators
        recent_interactions = self.storage_backend.get_interaction_history(user_id, limit=20)
        
        skill_indicators = {
            'beginner': 0,
            'intermediate': 0,
            'advanced': 0
        }
        
        for interaction in recent_interactions:
            # Check for error patterns
            if not interaction.get('success', True):
                skill_indicators['beginner'] += 1
            elif interaction.get('intent') in ['player_approval', 'availability_update']:
                skill_indicators['advanced'] += 1
            elif interaction.get('intent') in ['player_registration', 'payment_inquiry']:
                skill_indicators['intermediate'] += 1
            else:
                skill_indicators['intermediate'] += 1
        
        # Determine skill level
        if skill_indicators['advanced'] > skill_indicators['beginner'] * 2:
            new_skill_level = 'advanced'
        elif skill_indicators['intermediate'] > skill_indicators['beginner']:
            new_skill_level = 'intermediate'
        else:
            new_skill_level = 'beginner'
        
        profile_data['skill_level'] = new_skill_level
        self.storage_backend.save_user_profile(user_id, profile_data)
    
    def _update_interaction_patterns(self, user_id: str, interaction: Dict[str, Any]) -> None:
        """Update user interaction patterns."""
        profile_data = self.storage_backend.get_user_profile(user_id)
        if profile_data is None:
            return
        
        # Update interaction frequency
        current_time = datetime.now()
        time_since_last = (current_time - profile_data['last_interaction']).total_seconds()
        
        if 'interaction_frequency' not in profile_data['interaction_patterns']:
            profile_data['interaction_patterns']['interaction_frequency'] = []
        
        profile_data['interaction_patterns']['interaction_frequency'].append(time_since_last)
        
        # Keep only last 50 frequency measurements
        if len(profile_data['interaction_patterns']['interaction_frequency']) > 50:
            profile_data['interaction_patterns']['interaction_frequency'] = \
                profile_data['interaction_patterns']['interaction_frequency'][-50:]
        
        # Update last interaction time and total count
        profile_data['last_interaction'] = current_time
        profile_data['total_interactions'] += 1
        
        # Save updated profile
        self.storage_backend.save_user_profile(user_id, profile_data)
    
    def learn_from_interaction(self, user_id: str, interaction: Dict[str, Any]) -> None:
        """Learn from a user interaction."""
        # Add interaction to history
        interaction['user_id'] = user_id
        self.storage_backend.add_interaction(interaction)
        
        # Extract preferences from interaction
        preferences = self._extract_preferences_from_interaction(interaction)
        
        # Update preferences
        for preference_type, value in preferences.items():
            self._update_preference(user_id, preference_type, value, interaction.get('success', True))
        
        # Update skill level and patterns
        self._update_skill_level(user_id, interaction)
        self._update_interaction_patterns(user_id, interaction)
        
        logger.debug(f"Learned from interaction for user {user_id}: {preferences}")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, UserPreference]:
        """Get all preferences for a user."""
        profile_data = self.storage_backend.get_user_profile(user_id)
        if profile_data is None:
            return {}
        
        # Convert stored preferences to UserPreference objects
        preferences = {}
        for pref_type, pref_data in profile_data.get('preferences', {}).items():
            preferences[pref_type] = UserPreference(
                user_id=pref_data['user_id'],
                preference_type=pref_data['preference_type'],
                value=pref_data['value'],
                confidence=pref_data['confidence'],
                last_updated=pref_data['last_updated'],
                usage_count=pref_data['usage_count']
            )
        
        return preferences
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get complete user profile."""
        profile_data = self.storage_backend.get_user_profile(user_id)
        if profile_data is None:
            return None
        
        # Convert stored preferences to UserPreference objects
        preferences = {}
        for pref_type, pref_data in profile_data.get('preferences', {}).items():
            preferences[pref_type] = UserPreference(
                user_id=pref_data['user_id'],
                preference_type=pref_data['preference_type'],
                value=pref_data['value'],
                confidence=pref_data['confidence'],
                last_updated=pref_data['last_updated'],
                usage_count=pref_data['usage_count']
            )
        
        return UserProfile(
            user_id=profile_data['user_id'],
            preferences=preferences,
            interaction_patterns=profile_data['interaction_patterns'],
            skill_level=profile_data['skill_level'],
            preferred_agents=profile_data['preferred_agents'],
            last_interaction=profile_data['last_interaction'],
            total_interactions=profile_data['total_interactions']
        )
    
    def get_preference(self, user_id: str, preference_type: str) -> Optional[UserPreference]:
        """Get a specific preference for a user."""
        preferences = self.get_user_preferences(user_id)
        return preferences.get(preference_type)
    
    def get_high_confidence_preferences(self, user_id: str) -> Dict[str, UserPreference]:
        """Get preferences with high confidence."""
        preferences = self.get_user_preferences(user_id)
        threshold = self.learning_config['confidence_thresholds']['high_confidence']
        
        return {
            pref_type: pref for pref_type, pref in preferences.items()
            if pref.confidence >= threshold
        }
    
    def personalize_response(self, user_id: str, base_response: str, 
                           context: Dict[str, Any] = None) -> str:
        """Personalize a response based on user preferences."""
        preferences = self.get_user_preferences(user_id)
        
        # Get communication style preference
        comm_style = preferences.get('communication_style')
        if comm_style:
            if comm_style.value == 'formal':
                base_response = self._make_formal(base_response)
            elif comm_style.value == 'casual':
                base_response = self._make_casual(base_response)
            elif comm_style.value == 'concise':
                base_response = self._make_concise(base_response)
        
        # Get response format preference
        response_format = preferences.get('response_format')
        if response_format:
            if response_format.value == 'structured':
                base_response = self._make_structured(base_response)
            elif response_format.value == 'summary':
                base_response = self._make_summary(base_response)
        
        # Get complexity preference
        complexity = preferences.get('complexity_preference')
        if complexity:
            if complexity.value == 'simple':
                base_response = self._simplify_response(base_response)
            elif complexity.value == 'detailed':
                base_response = self._add_details(base_response, context)
        
        return base_response
    
    def _make_formal(self, response: str) -> str:
        """Make response more formal."""
        # Simple formalization rules
        replacements = {
            "Hi": "Hello",
            "Hey": "Hello",
            "Thanks": "Thank you",
            "Thx": "Thank you",
            "Ok": "Okay",
            "Yeah": "Yes"
        }
        
        for informal, formal in replacements.items():
            response = response.replace(informal, formal)
        
        return response
    
    def _make_casual(self, response: str) -> str:
        """Make response more casual."""
        # Simple casualization rules
        replacements = {
            "Hello": "Hi",
            "Thank you": "Thanks",
            "Okay": "Ok",
            "Yes": "Yeah",
            "Please": ""
        }
        
        for formal, casual in replacements.items():
            response = response.replace(formal, casual)
        
        return response
    
    def _make_concise(self, response: str) -> str:
        """Make response more concise."""
        # Simple conciseness rules
        lines = response.split('\n')
        concise_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Keep meaningful lines
                concise_lines.append(line)
        
        return '\n'.join(concise_lines)
    
    def _make_structured(self, response: str) -> str:
        """Make response more structured."""
        # Add structure if not already present
        if '|' not in response and '\n' not in response:
            # Try to add some structure
            if '✅' in response or '❌' in response:
                return response  # Already has some structure
            else:
                return f"📋 {response}"
        
        return response
    
    def _make_summary(self, response: str) -> str:
        """Make response more summary-like."""
        # Extract key information
        if '✅' in response:
            return "✅ Success"
        elif '❌' in response:
            return "❌ Error occurred"
        else:
            return response[:100] + "..." if len(response) > 100 else response
    
    def _simplify_response(self, response: str) -> str:
        """Simplify response for beginner users."""
        # Remove technical terms
        technical_terms = {
            "registration": "sign up",
            "approval": "permission",
            "coordination": "organization",
            "analytics": "information"
        }
        
        for technical, simple in technical_terms.items():
            response = response.replace(technical, simple)
        
        return response
    
    def _add_details(self, response: str, context: Dict[str, Any] = None) -> str:
        """Add details for advanced users."""
        if not context:
            return response
        
        details = []
        
        # Add relevant context details
        if 'processing_time' in context:
            details.append(f"⏱️ Processed in {context['processing_time']:.2f}s")
        
        if 'agent_used' in context:
            details.append(f"🤖 Handled by {context['agent_used']}")
        
        if 'complexity_level' in context:
            details.append(f"📊 Complexity: {context['complexity_level']}")
        
        if details:
            response += f"\n\n📈 Details: {' | '.join(details)}"
        
        return response
    
    def get_learning_analytics(self) -> Dict[str, Any]:
        """Get analytics about learning performance."""
        stats = self.storage_backend.get_storage_stats()
        
        # Get all user profiles
        all_profiles = self.storage_backend.get_all_user_profiles()
        
        # Calculate preference statistics
        preference_stats = {}
        skill_level_stats = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        
        for user_id, profile in all_profiles.items():
            # Count skill levels
            skill_level = profile.get('skill_level', 'beginner')
            skill_level_stats[skill_level] += 1
            
            # Count preferences
            for pref_type, pref_data in profile.get('preferences', {}).items():
                if pref_type not in preference_stats:
                    preference_stats[pref_type] = {}
                
                value = pref_data['value']
                if value not in preference_stats[pref_type]:
                    preference_stats[pref_type][value] = 0
                preference_stats[pref_type][value] += 1
        
        return {
            'storage_stats': stats,
            'total_users': len(all_profiles),
            'skill_level_distribution': skill_level_stats,
            'preference_distribution': preference_stats,
            'average_interactions_per_user': stats['total_interactions'] / max(1, len(all_profiles)),
            'learning_config': self.learning_config
        }
    
    def clear_user_data(self, user_id: str) -> bool:
        """Clear all data for a specific user."""
        return self.storage_backend.delete_user_profile(user_id)
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all data for a specific user."""
        profile = self.get_user_profile(user_id)
        if profile is None:
            return {}
        
        # Get interaction history
        interactions = self.storage_backend.get_interaction_history(user_id, limit=1000)
        
        return {
            'user_profile': {
                'user_id': profile.user_id,
                'skill_level': profile.skill_level,
                'preferred_agents': profile.preferred_agents,
                'last_interaction': profile.last_interaction.isoformat(),
                'total_interactions': profile.total_interactions,
                'interaction_patterns': profile.interaction_patterns
            },
            'preferences': {
                pref_type: {
                    'value': pref.value,
                    'confidence': pref.confidence,
                    'last_updated': pref.last_updated.isoformat(),
                    'usage_count': pref.usage_count
                }
                for pref_type, pref in profile.preferences.items()
            },
            'interaction_history': interactions,
            'export_timestamp': datetime.now().isoformat()
        }

@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    active_agents: int
    system_load: float
    memory_usage: float
    error_rate: float

@dataclass
class AgentMetrics:
    """Individual agent performance metrics."""
    agent_role: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    average_processing_time: float
    last_activity: datetime
    availability: float  # 0.0 to 1.0

class SystemAnalytics:
    """Comprehensive system analytics and monitoring."""
    
    def __init__(self):
        self.metrics_history = []
        self.agent_metrics = {}
        self.performance_thresholds = self._load_performance_thresholds()
        self.alert_history = []
        self.analytics_config = self._load_analytics_config()
        
    def _load_performance_thresholds(self) -> Dict[str, float]:
        """Load performance thresholds for monitoring."""
        return {
            'max_response_time': 30.0,  # seconds
            'max_error_rate': 0.1,  # 10%
            'max_system_load': 0.8,  # 80%
            'max_memory_usage': 0.9,  # 90%
            'min_agent_availability': 0.7,  # 70%
            'max_agent_failure_rate': 0.2  # 20%
        }
    
    def _load_analytics_config(self) -> Dict[str, Any]:
        """Load analytics configuration."""
        return {
            'metrics_retention_days': 30,
            'alert_cooldown_minutes': 15,
            'performance_window_minutes': 60,
            'trend_analysis_window_hours': 24
        }
    
    def record_request(self, request_data: Dict[str, Any]) -> None:
        """Record a request for analytics."""
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            total_requests=1,
            successful_requests=1 if request_data.get('success', True) else 0,
            failed_requests=0 if request_data.get('success', True) else 1,
            average_response_time=request_data.get('processing_time', 0.0),
            active_agents=request_data.get('active_agents', 0),
            system_load=request_data.get('system_load', 0.0),
            memory_usage=request_data.get('memory_usage', 0.0),
            error_rate=0.0 if request_data.get('success', True) else 1.0
        )
        
        self.metrics_history.append(metrics)
        
        # Update agent metrics
        agent_role = request_data.get('agent_role', 'unknown')
        if agent_role not in self.agent_metrics:
            self.agent_metrics[agent_role] = AgentMetrics(
                agent_role=agent_role,
                total_tasks=0,
                successful_tasks=0,
                failed_tasks=0,
                average_processing_time=0.0,
                last_activity=datetime.now(),
                availability=1.0
            )
        
        agent_metric = self.agent_metrics[agent_role]
        agent_metric.total_tasks += 1
        
        if request_data.get('success', True):
            agent_metric.successful_tasks += 1
        else:
            agent_metric.failed_tasks += 1
        
        # Update average processing time
        processing_time = request_data.get('processing_time', 0.0)
        if agent_metric.total_tasks > 1:
            agent_metric.average_processing_time = (
                (agent_metric.average_processing_time * (agent_metric.total_tasks - 1) + processing_time) /
                agent_metric.total_tasks
            )
        else:
            agent_metric.average_processing_time = processing_time
        
        agent_metric.last_activity = datetime.now()
        
        # Check for alerts
        self._check_alerts(metrics, agent_metric)
    
    def _check_alerts(self, metrics: SystemMetrics, agent_metric: AgentMetrics) -> None:
        """Check for performance alerts."""
        alerts = []
        
        # System-level alerts
        if metrics.average_response_time > self.performance_thresholds['max_response_time']:
            alerts.append(f"High response time: {metrics.average_response_time:.2f}s")
        
        if metrics.error_rate > self.performance_thresholds['max_error_rate']:
            alerts.append(f"High error rate: {metrics.error_rate:.2%}")
        
        if metrics.system_load > self.performance_thresholds['max_system_load']:
            alerts.append(f"High system load: {metrics.system_load:.2%}")
        
        if metrics.memory_usage > self.performance_thresholds['max_memory_usage']:
            alerts.append(f"High memory usage: {metrics.memory_usage:.2%}")
        
        # Agent-level alerts
        if agent_metric.availability < self.performance_thresholds['min_agent_availability']:
            alerts.append(f"Low agent availability ({agent_metric.agent_role}): {agent_metric.availability:.2%}")
        
        failure_rate = agent_metric.failed_tasks / agent_metric.total_tasks if agent_metric.total_tasks > 0 else 0
        if failure_rate > self.performance_thresholds['max_agent_failure_rate']:
            alerts.append(f"High agent failure rate ({agent_metric.agent_role}): {failure_rate:.2%}")
        
        # Record alerts
        for alert in alerts:
            self.alert_history.append({
                'timestamp': datetime.now(),
                'alert': alert,
                'severity': 'warning' if 'High' in alert else 'error'
            })
            logger.warning(f"🚨 System Alert: {alert}")
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get system overview metrics."""
        if not self.metrics_history:
            return {}
        
        # Calculate recent metrics (last hour)
        recent_metrics = self._get_recent_metrics(minutes=60)
        
        if not recent_metrics:
            return {}
        
        total_requests = len(recent_metrics)
        successful_requests = sum(1 for m in recent_metrics if m.successful_requests > 0)
        failed_requests = total_requests - successful_requests
        
        avg_response_time = sum(m.average_response_time for m in recent_metrics) / total_requests
        avg_system_load = sum(m.system_load for m in recent_metrics) / total_requests
        avg_memory_usage = sum(m.memory_usage for m in recent_metrics) / total_requests
        
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'average_response_time': avg_response_time,
            'average_system_load': avg_system_load,
            'average_memory_usage': avg_memory_usage,
            'error_rate': error_rate,
            'active_agents': len(self.agent_metrics),
            'recent_alerts': len([a for a in self.alert_history 
                                if (datetime.now() - a['timestamp']).total_seconds() < 3600])
        }
    
    def get_agent_performance(self) -> Dict[str, AgentMetrics]:
        """Get performance metrics for all agents."""
        return self.agent_metrics.copy()
    
    def get_agent_performance_summary(self) -> Dict[str, Any]:
        """Get summary of agent performance."""
        if not self.agent_metrics:
            return {}
        
        summary = {
            'total_agents': len(self.agent_metrics),
            'agent_details': {},
            'performance_ranking': []
        }
        
        for agent_role, metrics in self.agent_metrics.items():
            success_rate = metrics.successful_tasks / metrics.total_tasks if metrics.total_tasks > 0 else 0
            failure_rate = 1 - success_rate
            
            agent_detail = {
                'agent_role': agent_role,
                'total_tasks': metrics.total_tasks,
                'successful_tasks': metrics.successful_tasks,
                'failed_tasks': metrics.failed_tasks,
                'success_rate': success_rate,
                'failure_rate': failure_rate,
                'average_processing_time': metrics.average_processing_time,
                'availability': metrics.availability,
                'last_activity': metrics.last_activity.isoformat()
            }
            
            summary['agent_details'][agent_role] = agent_detail
            summary['performance_ranking'].append({
                'agent_role': agent_role,
                'success_rate': success_rate,
                'average_processing_time': metrics.average_processing_time
            })
        
        # Sort by success rate (descending)
        summary['performance_ranking'].sort(key=lambda x: x['success_rate'], reverse=True)
        
        return summary
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over time."""
        if not self.metrics_history:
            return {}
        
        # Get metrics from the specified time window
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {}
        
        # Group metrics by hour
        hourly_metrics = {}
        for metric in recent_metrics:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in hourly_metrics:
                hourly_metrics[hour_key] = []
            hourly_metrics[hour_key].append(metric)
        
        # Calculate trends
        trends = {
            'response_time_trend': [],
            'error_rate_trend': [],
            'system_load_trend': [],
            'request_volume_trend': []
        }
        
        for hour, metrics in sorted(hourly_metrics.items()):
            avg_response_time = sum(m.average_response_time for m in metrics) / len(metrics)
            total_requests = sum(m.total_requests for m in metrics)
            failed_requests = sum(m.failed_requests for m in metrics)
            error_rate = failed_requests / total_requests if total_requests > 0 else 0
            avg_system_load = sum(m.system_load for m in metrics) / len(metrics)
            
            trends['response_time_trend'].append({
                'timestamp': hour.isoformat(),
                'value': avg_response_time
            })
            trends['error_rate_trend'].append({
                'timestamp': hour.isoformat(),
                'value': error_rate
            })
            trends['system_load_trend'].append({
                'timestamp': hour.isoformat(),
                'value': avg_system_load
            })
            trends['request_volume_trend'].append({
                'timestamp': hour.isoformat(),
                'value': total_requests
            })
        
        return trends
    
    def get_system_health_score(self) -> float:
        """Calculate overall system health score (0.0 to 1.0)."""
        if not self.metrics_history:
            return 1.0  # No data = assume healthy
        
        # Get recent metrics
        recent_metrics = self._get_recent_metrics(minutes=60)
        if not recent_metrics:
            return 1.0
        
        # Calculate health factors
        total_requests = len(recent_metrics)
        successful_requests = sum(1 for m in recent_metrics if m.successful_requests > 0)
        success_rate = successful_requests / total_requests if total_requests > 0 else 1.0
        
        avg_response_time = sum(m.average_response_time for m in recent_metrics) / total_requests
        response_time_score = max(0, 1 - (avg_response_time / self.performance_thresholds['max_response_time']))
        
        avg_system_load = sum(m.system_load for m in recent_metrics) / total_requests
        system_load_score = max(0, 1 - (avg_system_load / self.performance_thresholds['max_system_load']))
        
        # Agent health
        agent_health_scores = []
        for agent_metric in self.agent_metrics.values():
            if agent_metric.total_tasks > 0:
                agent_success_rate = agent_metric.successful_tasks / agent_metric.total_tasks
                agent_health_scores.append(agent_success_rate)
        
        agent_health_score = sum(agent_health_scores) / len(agent_health_scores) if agent_health_scores else 1.0
        
        # Calculate overall health score
        health_score = (
            success_rate * 0.4 +
            response_time_score * 0.2 +
            system_load_score * 0.2 +
            agent_health_score * 0.2
        )
        
        return max(0.0, min(1.0, health_score))
    
    def get_recommendations(self) -> List[str]:
        """Get system improvement recommendations."""
        recommendations = []
        
        # Get current metrics
        overview = self.get_system_overview()
        if not overview:
            return recommendations
        
        # Check for issues and provide recommendations
        if overview.get('error_rate', 0) > 0.05:  # 5%
            recommendations.append("High error rate detected. Review recent failed requests and agent logs.")
        
        if overview.get('average_response_time', 0) > 20:  # 20 seconds
            recommendations.append("Slow response times detected. Consider optimizing agent processing or adding more agents.")
        
        if overview.get('average_system_load', 0) > 0.7:  # 70%
            recommendations.append("High system load detected. Consider scaling up resources or load balancing.")
        
        # Agent-specific recommendations
        agent_summary = self.get_agent_performance_summary()
        for agent_role, details in agent_summary.get('agent_details', {}).items():
            if details.get('failure_rate', 0) > 0.1:  # 10%
                recommendations.append(f"Agent {agent_role} has high failure rate. Review agent configuration and capabilities.")
            
            if details.get('average_processing_time', 0) > 30:  # 30 seconds
                recommendations.append(f"Agent {agent_role} is slow. Consider optimizing agent logic or reducing task complexity.")
        
        return recommendations
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of recent alerts."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [a for a in self.alert_history if a['timestamp'] >= cutoff_time]
        
        alert_counts = {}
        for alert in recent_alerts:
            alert_type = alert['alert'].split(':')[0] if ':' in alert['alert'] else 'General'
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        return {
            'total_alerts': len(recent_alerts),
            'alert_distribution': alert_counts,
            'recent_alerts': recent_alerts[-10:]  # Last 10 alerts
        }
    
    def _get_recent_metrics(self, minutes: int = 60) -> List[SystemMetrics]:
        """Get metrics from the recent time window."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def cleanup_old_data(self) -> None:
        """Clean up old metrics data."""
        retention_days = self.analytics_config['metrics_retention_days']
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        
        # Clean up metrics history
        self.metrics_history = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        # Clean up alert history
        self.alert_history = [a for a in self.alert_history if a['timestamp'] >= cutoff_time]
        
        logger.info(f"Cleaned up analytics data older than {retention_days} days")
    
    def export_analytics_report(self) -> Dict[str, Any]:
        """Export comprehensive analytics report."""
        return {
            'system_overview': self.get_system_overview(),
            'agent_performance': self.get_agent_performance_summary(),
            'performance_trends': self.get_performance_trends(),
            'system_health_score': self.get_system_health_score(),
            'recommendations': self.get_recommendations(),
            'alert_summary': self.get_alert_summary(),
            'export_timestamp': datetime.now().isoformat()
        }

class InMemoryUserStorage:
    """
    Simple in-memory storage backend for user preferences with persistence.
    
    Features:
    - Thread-safe in-memory storage
    - JSON-based persistence
    - Automatic data cleanup
    - Backup and restore functionality
    """
    
    def __init__(self, storage_dir: str = "user_preferences", auto_save: bool = True):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.auto_save = auto_save
        self._lock = threading.RLock()
        self._data = {
            'user_profiles': {},
            'interaction_history': [],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        self._load_data()
    
    def _get_storage_file(self) -> Path:
        """Get the storage file path."""
        return self.storage_dir / "user_preferences.json"
    
    def _get_backup_file(self) -> Path:
        """Get the backup file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.storage_dir / f"user_preferences_backup_{timestamp}.json"
    
    def _load_data(self) -> None:
        """Load data from storage file."""
        storage_file = self._get_storage_file()
        if storage_file.exists():
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert string timestamps back to datetime objects
                    self._convert_timestamps(data)
                    self._data.update(data)
                logger.info(f"Loaded user preferences from {storage_file}")
            except Exception as e:
                logger.warning(f"Failed to load user preferences: {e}")
    
    def _convert_timestamps(self, data: Dict[str, Any]) -> None:
        """Convert string timestamps back to datetime objects."""
        # Convert metadata timestamps
        if 'metadata' in data:
            for key in ['created_at', 'last_updated']:
                if key in data['metadata'] and isinstance(data['metadata'][key], str):
                    try:
                        data['metadata'][key] = datetime.fromisoformat(data['metadata'][key])
                    except ValueError:
                        pass
        
        # Convert user profile timestamps
        if 'user_profiles' in data:
            for user_id, profile in data['user_profiles'].items():
                if 'last_interaction' in profile and isinstance(profile['last_interaction'], str):
                    try:
                        profile['last_interaction'] = datetime.fromisoformat(profile['last_interaction'])
                    except ValueError:
                        pass
                
                # Convert preference timestamps
                if 'preferences' in profile:
                    for pref_type, preference in profile['preferences'].items():
                        if 'last_updated' in preference and isinstance(preference['last_updated'], str):
                            try:
                                preference['last_updated'] = datetime.fromisoformat(preference['last_updated'])
                            except ValueError:
                                pass
        
        # Convert interaction history timestamps
        if 'interaction_history' in data:
            for interaction in data['interaction_history']:
                if 'timestamp' in interaction and isinstance(interaction['timestamp'], str):
                    try:
                        interaction['timestamp'] = datetime.fromisoformat(interaction['timestamp'])
                    except ValueError:
                        pass
    
    def _save_data(self) -> None:
        """Save data to storage file."""
        if not self.auto_save:
            return
        
        with self._lock:
            try:
                # Update metadata
                self._data['metadata']['last_updated'] = datetime.now().isoformat()
                
                # Create backup before saving
                self._create_backup()
                
                # Save to main file
                storage_file = self._get_storage_file()
                with open(storage_file, 'w', encoding='utf-8') as f:
                    json.dump(self._data, f, indent=2, default=str)
                
                logger.debug(f"Saved user preferences to {storage_file}")
            except Exception as e:
                logger.error(f"Failed to save user preferences: {e}")
    
    def _create_backup(self) -> None:
        """Create a backup of the current data."""
        try:
            backup_file = self._get_backup_file()
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, default=str)
            
            # Keep only the last 5 backups
            backup_files = sorted(self.storage_dir.glob("user_preferences_backup_*.json"))
            if len(backup_files) > 5:
                for old_backup in backup_files[:-5]:
                    old_backup.unlink()
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from storage."""
        with self._lock:
            return self._data['user_profiles'].get(user_id)
    
    def save_user_profile(self, user_id: str, profile: Dict[str, Any]) -> None:
        """Save user profile to storage."""
        with self._lock:
            self._data['user_profiles'][user_id] = profile
            self._save_data()
    
    def delete_user_profile(self, user_id: str) -> bool:
        """Delete user profile from storage."""
        with self._lock:
            if user_id in self._data['user_profiles']:
                del self._data['user_profiles'][user_id]
                self._save_data()
                return True
            return False
    
    def add_interaction(self, interaction: Dict[str, Any]) -> None:
        """Add interaction to history."""
        with self._lock:
            interaction['timestamp'] = datetime.now()
            self._data['interaction_history'].append(interaction)
            
            # Keep only last 1000 interactions
            if len(self._data['interaction_history']) > 1000:
                self._data['interaction_history'] = self._data['interaction_history'][-1000:]
            
            self._save_data()
    
    def get_interaction_history(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get interaction history, optionally filtered by user."""
        with self._lock:
            history = self._data['interaction_history']
            if user_id:
                history = [i for i in history if i.get('user_id') == user_id]
            return history[-limit:]
    
    def get_all_user_profiles(self) -> Dict[str, Any]:
        """Get all user profiles."""
        with self._lock:
            return self._data['user_profiles'].copy()
    
    def clear_all_data(self) -> None:
        """Clear all stored data."""
        with self._lock:
            self._data = {
                'user_profiles': {},
                'interaction_history': [],
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'version': '1.0'
                }
            }
            self._save_data()
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        with self._lock:
            return {
                'total_users': len(self._data['user_profiles']),
                'total_interactions': len(self._data['interaction_history']),
                'storage_size': self._get_storage_file().stat().st_size if self._get_storage_file().exists() else 0,
                'last_updated': self._data['metadata'].get('last_updated'),
                'version': self._data['metadata'].get('version')
            }
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Clean up old interaction data."""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        with self._lock:
            original_count = len(self._data['interaction_history'])
            self._data['interaction_history'] = [
                i for i in self._data['interaction_history']
                if isinstance(i.get('timestamp'), datetime) and i['timestamp'] > cutoff_date
            ]
            cleaned_count = original_count - len(self._data['interaction_history'])
            
            if cleaned_count > 0:
                self._save_data()
        
        return cleaned_count