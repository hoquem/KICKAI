#!/usr/bin/env python3
"""
Task Decomposition Module

This module breaks down the complex DynamicTaskDecomposer into smaller, focused classes
following the single responsibility principle and making the code more maintainable.
"""

import logging
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple

# Stub classes for compatibility - these should be imported from the new modular structure
class AgentRole(Enum):
    """Agent roles for task routing."""
    MESSAGE_PROCESSOR = "message_processor"
    TEAM_MANAGER = "team_manager"
    PLAYER_COORDINATOR = "player_coordinator"
    FINANCE_MANAGER = "finance_manager"
    PERFORMANCE_ANALYST = "performance_analyst"
    LEARNING_AGENT = "learning_agent"
    ONBOARDING_AGENT = "onboarding_agent"
    COMMAND_FALLBACK_AGENT = "command_fallback_agent"


class CapabilityType(Enum):
    """Capability types for task routing."""
    PLAYER_ONBOARDING = "player_onboarding"
    PLAYER_STATUS_TRACKING = "player_status_tracking"
    PLAYER_APPROVAL_MANAGEMENT = "player_approval_management"
    PAYMENT_TRACKING = "payment_tracking"
    PAYMENT_PROCESSING = "payment_processing"
    BASIC_ANALYTICS = "basic_analytics"
    STRATEGIC_PLANNING = "strategic_planning"
    MESSAGE_COMPOSITION = "message_composition"
    STRATEGIC_DECISION_MAKING = "strategic_decision_making"
    NATURAL_LANGUAGE_UNDERSTANDING = "natural_language_understanding"
    MULTI_AGENT_COORDINATION = "multi_agent_coordination"
    CONTEXT_MANAGEMENT = "context_management"
    DATA_RETRIEVAL = "data_retrieval"
    ROUTING = "routing"
    USER_REGISTRATION = "user_registration"
    FINANCIAL_RECORD_KEEPING = "financial_record_keeping"
    PAYMENT_PLAN_SETUP = "payment_plan_setup"
    FINANCIAL_PLANNING = "financial_planning"
    ONBOARDING_GUIDANCE = "onboarding_guidance"
    FINANCIAL_QUERY_HANDLING = "financial_query_handling"


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
    """Represents a subtask in task decomposition."""
    task_id: str
    description: str
    agent_role: AgentRole
    capabilities_required: List[CapabilityType]
    parameters: Dict[str, Any] = None
    dependencies: List[str] = None
    estimated_duration: int = 60
    priority: int = 1

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels."""
    SIMPLE = 1      # Single agent, single capability
    MODERATE = 2    # Single agent, multiple capabilities
    COMPLEX = 3     # Multiple agents, coordinated
    VERY_COMPLEX = 4 # Multiple agents, complex dependencies


@dataclass
class TaskTemplate:
    """Template for common task types."""
    name: str
    description: str
    capabilities: List[CapabilityType]
    agent_role: AgentRole
    estimated_duration: int


class TaskTemplateLoader:
    """Loads and manages task templates."""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, TaskTemplate]:
        """Load task templates for common operations."""
        return {
            'player_registration': TaskTemplate(
                name='player_registration',
                description='Register new player {player_name} with phone {phone}',
                capabilities=[CapabilityType.PLAYER_ONBOARDING, CapabilityType.USER_REGISTRATION],
                agent_role=AgentRole.PLAYER_COORDINATOR,
                estimated_duration=60
            ),
            'player_approval': TaskTemplate(
                name='player_approval',
                description='Approve player {player_id} for team participation',
                capabilities=[CapabilityType.PLAYER_APPROVAL_MANAGEMENT, CapabilityType.STRATEGIC_DECISION_MAKING],
                agent_role=AgentRole.TEAM_MANAGER,
                estimated_duration=30
            ),
            'status_inquiry': TaskTemplate(
                name='status_inquiry',
                description='Check registration status for user {user_id}',
                capabilities=[CapabilityType.PLAYER_STATUS_TRACKING, CapabilityType.NATURAL_LANGUAGE_UNDERSTANDING],
                agent_role=AgentRole.MESSAGE_PROCESSOR,
                estimated_duration=15
            ),
            'match_creation': TaskTemplate(
                name='match_creation',
                description='Create new match with details {match_details}',
                capabilities=[CapabilityType.STRATEGIC_PLANNING, CapabilityType.MULTI_AGENT_COORDINATION],
                agent_role=AgentRole.TEAM_MANAGER,
                estimated_duration=120
            ),
            'payment_processing': TaskTemplate(
                name='payment_processing',
                description='Process payment for {amount} from {payer}',
                capabilities=[CapabilityType.PAYMENT_PROCESSING, CapabilityType.FINANCIAL_RECORD_KEEPING],
                agent_role=AgentRole.FINANCE_MANAGER,
                estimated_duration=90
            ),
            'performance_analysis': TaskTemplate(
                name='performance_analysis',
                description='Analyze performance data for {time_period}',
                capabilities=[CapabilityType.BASIC_ANALYTICS, CapabilityType.DATA_RETRIEVAL],
                agent_role=AgentRole.PERFORMANCE_ANALYST,
                estimated_duration=180
            )
        }
    
    def get_template(self, template_name: str) -> Optional[TaskTemplate]:
        """Get a task template by name."""
        return self.templates.get(template_name)
    
    def get_all_templates(self) -> Dict[str, TaskTemplate]:
        """Get all task templates."""
        return self.templates.copy()


class ComplexityAnalyzer:
    """Analyzes task complexity using simple heuristics."""
    
    def __init__(self):
        self.multi_step_indicators = ['and', 'then', 'also', 'additionally', 'furthermore']
        self.coordination_indicators = ['coordinate', 'organize', 'manage', 'plan']
        self.analysis_indicators = ['analyze', 'review', 'assess', 'evaluate', 'report']
        self.simple_indicators = ['check', 'get', 'show', 'display', 'status']
    
    def analyze_complexity(self, task: str, context: TaskContext) -> TaskComplexity:
        """Analyze the complexity of a task based on content and context."""
        task_lower = task.lower()
        
        # Check for multi-step operations
        if any(indicator in task_lower for indicator in self.multi_step_indicators):
            return TaskComplexity.COMPLEX
        
        # Check for coordination requirements
        if any(indicator in task_lower for indicator in self.coordination_indicators):
            return TaskComplexity.MODERATE
        
        # Check for analysis tasks
        if any(indicator in task_lower for indicator in self.analysis_indicators):
            return TaskComplexity.MODERATE
        
        # Check for simple operations
        if any(indicator in task_lower for indicator in self.simple_indicators):
            return TaskComplexity.SIMPLE
        
        return TaskComplexity.MODERATE


class CapabilityIdentifier:
    """Identifies required capabilities based on task content."""
    
    def __init__(self):
        self.primary_mappings = {
            CapabilityType.PLAYER_ONBOARDING: ['player', 'registration', 'register', 'onboard'],
            CapabilityType.PLAYER_STATUS_TRACKING: ['status', 'info', 'myinfo', 'check', 'list'],
            CapabilityType.PLAYER_APPROVAL_MANAGEMENT: ['approve', 'reject', 'approval'],
            CapabilityType.PAYMENT_TRACKING: ['payment', 'pay', 'money', 'fee', 'financial'],
            CapabilityType.PAYMENT_PROCESSING: ['process', 'payment', 'transaction'],
            CapabilityType.BASIC_ANALYTICS: ['performance', 'analyze', 'stats', 'data', 'metrics'],
            CapabilityType.STRATEGIC_PLANNING: ['plan', 'strategy', 'match', 'fixture', 'tactical'],
            CapabilityType.MESSAGE_COMPOSITION: ['send', 'message', 'notify', 'announce', 'broadcast'],
            CapabilityType.STRATEGIC_DECISION_MAKING: ['decide', 'choose', 'select', 'decision']
        }
        
        self.secondary_mappings = {
            CapabilityType.NATURAL_LANGUAGE_UNDERSTANDING: ['what', 'how', 'why', 'understand', 'interpret', 'parse'],
            CapabilityType.MULTI_AGENT_COORDINATION: ['coordinate', 'organize', 'manage', 'arrange'],
            CapabilityType.CONTEXT_MANAGEMENT: ['context', 'history', 'previous', 'last'],
            CapabilityType.DATA_RETRIEVAL: ['get', 'fetch', 'retrieve', 'query'],
            CapabilityType.ROUTING: ['route', 'direct', 'forward', 'send to']
        }
    
    def identify_capabilities(self, task: str) -> List[CapabilityType]:
        """Identify required capabilities based on task content with intelligent prioritization."""
        required_capabilities = []
        task_lower = task.lower()
        
        # Check primary capabilities first
        for capability, keywords in self.primary_mappings.items():
            if any(keyword in task_lower for keyword in keywords):
                required_capabilities.append(capability)
                break  # Only take the first primary capability match
        
        # Check secondary capabilities (limit to 1-2)
        secondary_caps = []
        for capability, keywords in self.secondary_mappings.items():
            if any(keyword in task_lower for keyword in keywords):
                secondary_caps.append(capability)
        
        # Add up to 2 secondary capabilities
        required_capabilities.extend(secondary_caps[:2])
        
        # Ensure we don't have too many capabilities (max 3 total)
        required_capabilities = required_capabilities[:3]
        
        # If no capabilities identified, add a default
        if not required_capabilities:
            if 'status' in task_lower or 'info' in task_lower:
                required_capabilities.append(CapabilityType.PLAYER_STATUS_TRACKING)
            else:
                required_capabilities.append(CapabilityType.NATURAL_LANGUAGE_UNDERSTANDING)
        
        logger.debug(f"Identified capabilities for '{task}': {[cap.value for cap in required_capabilities]}")
        return required_capabilities


class AgentRouter:
    """Routes tasks to the most appropriate agent based on capabilities."""
    
    def __init__(self):
        pass
    
    def find_best_agent(self, capabilities: List[CapabilityType]) -> AgentRole:
        """Find the best agent for the given capabilities."""
        if not capabilities:
            logger.warning("No capabilities provided, defaulting to MESSAGE_PROCESSOR.")
            return AgentRole.MESSAGE_PROCESSOR
        
        # Simplified agent routing - capability matrix moved to modular structure
        # Default routing based on primary capability
        primary_capability = capabilities[0] if capabilities else None
        
        if primary_capability == CapabilityType.PLAYER_ONBOARDING:
            return AgentRole.PLAYER_COORDINATOR
        elif primary_capability == CapabilityType.PAYMENT_PROCESSING:
            return AgentRole.FINANCE_MANAGER
        elif primary_capability == CapabilityType.STRATEGIC_PLANNING:
            return AgentRole.TEAM_MANAGER
        elif primary_capability == CapabilityType.BASIC_ANALYTICS:
            return AgentRole.PERFORMANCE_ANALYST
        else:
            return AgentRole.MESSAGE_PROCESSOR


class LLMDecomposer:
    """Handles LLM-based task decomposition."""
    
    def __init__(self, llm):
        self.llm = llm
    
    def _create_decomposition_prompt(self, task: str, context: TaskContext) -> str:
        """Create a structured prompt for LLM-based task decomposition."""
        return f"""
You are an expert task decomposer for the KICKAI football team management system. Your role is to break down complex user requests into specific, actionable subtasks that can be executed by specialized agents.

**SYSTEM CONTEXT:**
- Team ID: {context.team_id}
- User ID: {context.user_id}
- Context Parameters: {context.parameters}

**AVAILABLE AGENTS AND CAPABILITIES:**

1. **MESSAGE_PROCESSOR**: 
   - Intent analysis and classification
   - Context management and conversation flow
   - Agent routing and load balancing
   - Help system and user guidance

2. **TEAM_MANAGER**: 
   - Strategic planning and coordination
   - Decision making for team operations
   - Performance monitoring and improvement
   - Conflict resolution and team dynamics

3. **PLAYER_COORDINATOR**: 
   - Player registration and onboarding
   - Individual player support and queries
   - Player status tracking and updates
   - Personal development guidance

4. **FINANCE_MANAGER**: 
   - Payment tracking and management
   - Financial reporting and transparency
   - Budget oversight and planning
   - Financial query handling

5. **PERFORMANCE_ANALYST**: 
   - Performance data analysis and interpretation
   - Statistical insights and trend identification
   - Tactical recommendations and strategy support
   - Player development guidance

6. **LEARNING_AGENT**: 
   - Pattern recognition and learning
   - User preference analysis and personalization
   - System performance optimization
   - Process improvement recommendations

7. **ONBOARDING_AGENT**: 
   - New player registration guidance
   - Step-by-step onboarding process
   - Information validation and confirmation
   - Team integration support

8. **COMMAND_FALLBACK_AGENT**: 
   - Unrecognized command handling
   - Helpful guidance and alternative solutions
   - Intent recognition from unclear requests
   - User experience maintenance

**DECOMPOSITION GUIDELINES:**

1. **Task Analysis**: Understand the user's goal and break it into logical steps
2. **Agent Selection**: Choose the most appropriate agent for each subtask based on capabilities
3. **Dependency Management**: Identify which subtasks depend on others
4. **Time Estimation**: Provide realistic duration estimates for each subtask
5. **Priority Assignment**: Assign priorities (1-5, where 5 is highest) based on importance and dependencies

**VALIDATION CRITERIA:**
- Each subtask must be specific and actionable
- Agent assignments must match agent capabilities
- Dependencies must be logical and necessary
- Time estimates must be realistic
- Priorities must reflect task importance and dependencies

**ERROR HANDLING:**
- If task is unclear, create a single subtask for clarification
- If multiple agents could handle a task, choose the most specialized one
- If dependencies are complex, break them into smaller, manageable steps
- Always provide fallback options for critical tasks

**USER REQUEST:** {task}

**RESPONSE FORMAT:**
Respond with valid JSON only. Do not include any explanatory text outside the JSON structure.

{{
    "subtasks": [
        {{
            "description": "Clear, specific description of what needs to be done",
            "agent_role": "AGENT_ROLE_NAME",
            "capabilities_required": ["CAPABILITY1", "CAPABILITY2"],
            "parameters": {{"key": "value"}},
            "dependencies": ["subtask_id_1", "subtask_id_2"],
            "estimated_duration": 30,
            "priority": 1
        }}
    ],
    "complexity": "SIMPLE|MODERATE|COMPLEX|VERY_COMPLEX",
    "reasoning": "Brief explanation of the decomposition strategy and agent selection logic"
}}

**EXAMPLES:**

Example 1 - Simple Request: "What's my payment status?"
{{
    "subtasks": [
        {{
            "description": "Fetch user's payment records and current status",
            "agent_role": "FINANCE_MANAGER",
            "capabilities_required": ["payment_tracking", "financial_query_handling"],
            "parameters": {{"user_id": "user123"}},
            "dependencies": [],
            "estimated_duration": 15,
            "priority": 5
        }}
    ],
    "complexity": "SIMPLE",
    "reasoning": "Single subtask handled by Finance Manager who specializes in payment tracking"
}}

Example 2 - Complex Request: "I want to register a new player and set up their payment plan"
{{
    "subtasks": [
        {{
            "description": "Guide new player through registration process",
            "agent_role": "ONBOARDING_AGENT",
            "capabilities_required": ["player_registration", "onboarding_guidance"],
            "parameters": {{"registration_type": "new_player"}},
            "dependencies": [],
            "estimated_duration": 120,
            "priority": 5
        }},
        {{
            "description": "Set up payment plan for registered player",
            "agent_role": "FINANCE_MANAGER",
            "capabilities_required": ["payment_plan_setup", "financial_planning"],
            "parameters": {{"plan_type": "new_player"}},
            "dependencies": ["subtask_1"],
            "estimated_duration": 45,
            "priority": 4
        }}
    ],
    "complexity": "MODERATE",
    "reasoning": "Two sequential subtasks: registration first, then payment setup with dependency"
}}

Now decompose the user request above following these guidelines and examples.
"""
    
    def decompose_with_llm(self, task: str, context: TaskContext) -> List[Subtask]:
        """Decompose complex tasks using LLM."""
        if not self.llm:
            raise ValueError("LLM not available for decomposition")
        
        try:
            prompt = self._create_decomposition_prompt(task, context)
            response = self.llm.invoke(prompt)
            
            try:
                data = json.loads(response.content)
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
                
                return subtasks
                
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON response from LLM: {response}")
                raise ValueError("Invalid JSON response from LLM")
                
        except Exception as e:
            logger.error(f"Error in LLM decomposition: {e}")
            raise


class SimpleTaskDecomposer:
    """Simple rule-based task decomposition."""
    
    def __init__(self):
        self.complexity_analyzer = ComplexityAnalyzer()
        self.capability_identifier = CapabilityIdentifier()
        self.agent_router = AgentRouter()
    
    def decompose_simple_task(self, task: str, context: TaskContext) -> List[Subtask]:
        """Decompose a simple task into a single subtask."""
        required_capabilities = self.capability_identifier.identify_capabilities(task)
        agent_role = self.agent_router.find_best_agent(required_capabilities)
        
        subtask = Subtask(
            task_id=f"{context.task_id}_subtask_1",
            description=task,
            agent_role=agent_role,
            capabilities_required=required_capabilities,
            parameters=context.parameters,
            estimated_duration=30
        )
        return [subtask]
    
    def decompose_moderate_task(self, task: str, context: TaskContext) -> List[Subtask]:
        """Decompose a moderate task into multiple subtasks for the same agent."""
        required_capabilities = self.capability_identifier.identify_capabilities(task)
        agent_role = self.agent_router.find_best_agent(required_capabilities)
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


class TaskDecompositionManager:
    """Main task decomposition manager that orchestrates the decomposition process."""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.template_loader = TaskTemplateLoader()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.capability_identifier = CapabilityIdentifier()
        self.agent_router = AgentRouter()
        self.simple_decomposer = SimpleTaskDecomposer()
        self.llm_decomposer = LLMDecomposer(llm) if llm else None
        self.decomposition_history = []
        
        logger.info("TaskDecompositionManager initialized")
    
    def decompose(self, task: str, context: TaskContext, _recursion_depth: int = 0) -> List[Subtask]:
        """Decompose a task into subtasks using rule-based approach, with recursion protection."""
        MAX_RECURSION_DEPTH = 3
        
        if _recursion_depth > MAX_RECURSION_DEPTH:
            logger.error(f"Max recursion depth reached in TaskDecompositionManager.decompose for task: {task}")
            # Fallback: return a single subtask
            agent_role = self.agent_router.find_best_agent(self.capability_identifier.identify_capabilities(task))
            return [Subtask(
                task_id=f"{context.task_id}_subtask_fallback",
                description=task,
                agent_role=agent_role,
                capabilities_required=self.capability_identifier.identify_capabilities(task),
                parameters=context.parameters,
                estimated_duration=60
            )]
        
        complexity = self.complexity_analyzer.analyze_complexity(task, context)
        
        if complexity == TaskComplexity.SIMPLE:
            return self.simple_decomposer.decompose_simple_task(task, context)
        
        elif complexity == TaskComplexity.MODERATE:
            return self.simple_decomposer.decompose_moderate_task(task, context)
        
        else:
            # Complex tasks - use LLM if available
            if self.llm_decomposer:
                try:
                    return self.llm_decomposer.decompose_with_llm(task, context)
                except Exception as e:
                    logger.warning(f"LLM decomposition failed, falling back to simple: {e}")
                    return self.simple_decomposer.decompose_simple_task(task, context)
            else:
                return self.simple_decomposer.decompose_simple_task(task, context)
    
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