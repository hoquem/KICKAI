"""
Orchestration Pipeline for KICKAI Agent System

This module provides a dedicated orchestration pipeline that breaks down
task execution into separate, swappable components for better maintainability
and testability.
"""

import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
import traceback

from core.enums import AgentRole
from agents.configurable_agent import ConfigurableAgent
from agents.intelligent_system import AgentCapabilityMatrix, CapabilityType
from core.error_handling import (
    handle_agent_errors, handle_tool_errors, error_context,
    safe_execute_async, validate_input, ErrorHandlingConfig
)
from core.exceptions import (
    IntentClassificationError, TaskDecompositionError, AgentRoutingError,
    TaskExecutionError, ResultAggregationError, create_error_context
)

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    secondary_intents: List[str]
    context: Dict[str, Any]
    agent_used: str


@dataclass
class TaskDecomposition:
    """Result of task decomposition."""
    subtasks: List[Dict[str, Any]]
    complexity: str
    estimated_duration: int
    dependencies: List[str]


@dataclass
class AgentSelection:
    """Result of agent selection."""
    selected_agents: Dict[str, ConfigurableAgent]
    routing_reasoning: Dict[str, str]
    capability_matches: Dict[str, List[str]]


@dataclass
class ExecutionResult:
    """Result of task execution."""
    task_id: str
    success: bool
    result: str
    execution_time: float
    agent_role: AgentRole
    error: Optional[str] = None


class IntentClassifier(ABC):
    """Abstract base class for intent classification."""
    
    @abstractmethod
    def classify(self, task_description: str, context: Dict[str, Any]) -> IntentResult:
        """Classify the intent of a task."""
        pass


class TaskDecomposer(ABC):
    """Abstract base class for task decomposition."""
    
    @abstractmethod
    def decompose(self, task_description: str, intent_result: IntentResult, context: Dict[str, Any]) -> TaskDecomposition:
        """Decompose a task into subtasks."""
        pass


class AgentRouter(ABC):
    """Abstract base class for agent routing."""
    
    @abstractmethod
    def route(self, subtasks: List[Dict[str, Any]], available_agents: Dict[AgentRole, ConfigurableAgent], context: Dict[str, Any]) -> AgentSelection:
        """Route subtasks to appropriate agents."""
        pass


class TaskExecutor(ABC):
    """Abstract base class for task execution."""
    
    @abstractmethod
    async def execute(self, subtasks: List[Dict[str, Any]], selected_agents: AgentSelection, context: Dict[str, Any]) -> List[ExecutionResult]:
        """Execute subtasks using selected agents."""
        pass


class ResultAggregator(ABC):
    """Abstract base class for result aggregation."""
    
    @abstractmethod
    def aggregate(self, execution_results: List[ExecutionResult], context: Dict[str, Any]) -> str:
        """Aggregate execution results into a final response."""
        pass


class DefaultIntentClassifier(IntentClassifier):
    """Default implementation of intent classification."""
    
    def __init__(self, llm):
        self.llm = llm
    
    @handle_agent_errors(operation="intent_classification")
    def classify(self, task_description: str, context: Dict[str, Any]) -> IntentResult:
        """Classify the intent of a task using the intelligent system."""
        # Validate inputs
        validate_input(task_description, str, "task_description", required=True)
        validate_input(context, dict, "context", required=True)
        
        try:
            from agents.intelligent_system import IntentClassifier as IntelligentIntentClassifier
            
            classifier = IntelligentIntentClassifier(llm=self.llm)
            intent_result = classifier.classify(task_description)
            
            # Convert to our standardized format
            return IntentResult(
                intent=getattr(intent_result, 'primary_intent', 'unknown'),
                confidence=getattr(intent_result, 'confidence', 0.5),
                entities=getattr(intent_result, 'entities', {}),
                secondary_intents=getattr(intent_result, 'secondary_intents', []),
                context=getattr(intent_result, 'context', {}),
                agent_used='intent_classifier'
            )
            
        except Exception as e:
            # Raise a specific exception for better error handling
            raise IntentClassificationError(
                f"Failed to classify intent: {str(e)}",
                create_error_context("intent_classification", additional_info={
                    'task_description': task_description,
                    'context_keys': list(context.keys())
                })
            )


class DefaultTaskDecomposer(TaskDecomposer):
    """Default implementation of task decomposition."""
    
    def __init__(self, llm):
        self.llm = llm
    
    @handle_agent_errors(operation="task_decomposition")
    def decompose(self, task_description: str, intent_result: IntentResult, context: Dict[str, Any]) -> TaskDecomposition:
        """Decompose a task into subtasks using the intelligent system."""
        # Validate inputs
        validate_input(task_description, str, "task_description", required=True)
        validate_input(intent_result, IntentResult, "intent_result", required=True)
        validate_input(context, dict, "context", required=True)
        
        try:
            from agents.intelligent_system import DynamicTaskDecomposer as IntelligentTaskDecomposer, TaskContext
            from datetime import datetime
            
            # Convert dictionary context to TaskContext
            task_context = TaskContext(
                task_id=f"task_{int(datetime.now().timestamp())}",
                user_id=context.get('user_id', 'unknown'),
                team_id=context.get('team_id', 'unknown'),
                parameters=context,
                metadata={}
            )
            
            decomposer = IntelligentTaskDecomposer(llm=self.llm)
            subtasks = decomposer.decompose(task_description, task_context)
            
            # Calculate complexity and duration
            complexity = 'complex' if len(subtasks) > 1 else 'simple'
            estimated_duration = sum(getattr(subtask, 'estimated_duration', 30) for subtask in subtasks)
            
            return TaskDecomposition(
                subtasks=subtasks,
                complexity=complexity,
                estimated_duration=estimated_duration,
                dependencies=[]
            )
            
        except Exception as e:
            print(f"[AGENT ERROR TRACE] {traceback.format_exc()}")
            # Raise a specific exception for better error handling
            raise TaskDecompositionError(
                f"Failed to decompose task: {str(e)}",
                create_error_context("task_decomposition", additional_info={
                    'task_description': task_description,
                    'intent': intent_result.intent,
                    'context_keys': list(context.keys())
                })
            )


class DefaultAgentRouter(AgentRouter):
    """Default implementation of agent routing."""
    
    @handle_agent_errors(operation="agent_routing")
    def route(self, subtasks: List[Dict[str, Any]], available_agents: Dict[AgentRole, ConfigurableAgent], context: Dict[str, Any]) -> AgentSelection:
        """Route subtasks to appropriate agents."""
        # Validate inputs
        validate_input(subtasks, list, "subtasks", required=True)
        validate_input(available_agents, dict, "available_agents", required=True)
        validate_input(context, dict, "context", required=True)
        
        logger.info(f"[AGENT ROUTING] Starting agent routing for {len(subtasks)} subtasks")
        logger.info(f"[AGENT ROUTING] Available agents: {list(available_agents.keys())}")
        
        # Log detailed agent information
        for role, agent in available_agents.items():
            tools = agent.get_tools()
            logger.info(f"[AGENT ROUTING] Agent '{role.value}' has {len(tools)} tools: {[tool.name for tool in tools]}")
        
        try:
            from agents.intelligent_system import CapabilityBasedRouter, AgentCapabilityMatrix
            
            # Create a proper capability matrix for routing
            capability_matrix = self._create_capability_matrix(available_agents)
            router = CapabilityBasedRouter(capability_matrix)
            
            logger.info(f"[AGENT ROUTING] Capability matrix created with {len(capability_matrix._capability_matrix)} agent roles")
            
            # Log capability matrix details
            for role, capabilities in capability_matrix._capability_matrix.items():
                capability_names = [cap.capability.value for cap in capabilities]
                logger.info(f"[AGENT ROUTING] Agent '{role.value}' capabilities: {capability_names}")
            
            # Route the subtasks
            logger.info(f"[AGENT ROUTING] Starting capability-based routing for {len(subtasks)} subtasks")
            routing_result = router.route_multiple(subtasks, list(available_agents.values()))
            
            logger.info(f"[AGENT ROUTING] Routing result: {routing_result}")
            
            # Convert to our standardized format
            selected_agents = {}
            routing_reasoning = {}
            capability_matches = {}
            
            for task_id, result in routing_result.items():
                agent_role = result.get('agent_role')
                logger.info(f"[AGENT ROUTING] Task {task_id}: routed to agent_role={agent_role}")
                
                if agent_role and agent_role in available_agents:
                    selected_agents[task_id] = available_agents[agent_role]
                    routing_reasoning[task_id] = f"Routed to {agent_role.value} based on capabilities"
                    capability_matches[task_id] = [agent_role.value]
                    logger.info(f"[AGENT ROUTING] ✅ Task {task_id} successfully routed to {agent_role.value}")
                    
                    # Log the selected agent's details
                    agent = available_agents[agent_role]
                    agent_tools = [tool.name for tool in agent.get_tools()]
                    logger.info(f"[AGENT ROUTING] Selected agent '{agent_role.value}' for task '{task_id}' with tools: {agent_tools}")
                else:
                    logger.warning(f"[AGENT ROUTING] ❌ Task {task_id} could not be routed - agent_role={agent_role}, available={list(available_agents.keys())}")
            
            logger.info(f"[AGENT ROUTING] Final selection: {len(selected_agents)} tasks routed out of {len(subtasks)}")
            
            # Log final routing summary
            for task_id, agent in selected_agents.items():
                logger.info(f"[AGENT ROUTING] FINAL ROUTING: Task '{task_id}' → Agent '{agent.get_role().value}'")
            
            return AgentSelection(
                selected_agents=selected_agents,
                routing_reasoning=routing_reasoning,
                capability_matches=capability_matches
            )
            
        except Exception as e:
            print(f"[AGENT ERROR TRACE] {traceback.format_exc()}")
            logger.error(f"[AGENT ERROR TRACE] Error in agent routing: {e}", exc_info=True)
            # Raise a specific exception for better error handling
            raise AgentRoutingError(
                f"Failed to route agents: {str(e)}",
                create_error_context("agent_routing", additional_info={
                    'subtasks_count': len(subtasks),
                    'available_agents_count': len(available_agents),
                    'context_keys': list(context.keys())
                })
            )
    
    def _create_capability_matrix(self, available_agents: Dict[AgentRole, ConfigurableAgent]) -> AgentCapabilityMatrix:
        """Create a capability matrix for routing."""
        from agents.refined_capabilities import AgentCapabilityProfile, HierarchicalCapabilityManager
        
        # Create a hierarchical capability manager
        capability_manager = HierarchicalCapabilityManager()
        
        # Add custom capability profiles for the available agents
        for role, agent in available_agents.items():
            # Get tools from agent
            tools = agent.get_tools()
            
            # Create capability profiles for each tool
            for tool in tools:
                try:
                    # Map tool name to capability type
                    capability_type = self._map_tool_to_capability(tool.name)
                    
                    profile = AgentCapabilityProfile(
                        capability=capability_type,
                        proficiency_level=0.8,  # Default proficiency
                        is_primary=True,
                        is_specialized=False
                    )
                    
                    # Add to the manager's capability matrix
                    if role not in capability_manager._capability_matrix:
                        capability_manager._capability_matrix[role] = []
                    capability_manager._capability_matrix[role].append(profile)
                    
                except Exception as e:
                    # Silently continue - tool mapping is not critical
                    # System will default to COMMAND_PROCESSING capability
                    continue
        
        return capability_manager
    
    def _map_tool_to_capability(self, tool_name: str) -> CapabilityType:
        """Map tool name to capability type."""
        tool_mapping = {
            'player_management': CapabilityType.PLAYER_MANAGEMENT,
            'team_management': CapabilityType.TEAM_MANAGEMENT,
            'communication': CapabilityType.COMMUNICATION,
            'financial_management': CapabilityType.FINANCIAL_MANAGEMENT,
            'match_management': CapabilityType.MATCH_MANAGEMENT,
            'data_analysis': CapabilityType.DATA_ANALYSIS,
            'learning': CapabilityType.LEARNING,
            'onboarding': CapabilityType.ONBOARDING,
            'command_processing': CapabilityType.COMMAND_PROCESSING,
        }
        
        # Try exact match first
        if tool_name in tool_mapping:
            return tool_mapping[tool_name]
        
        # Try partial match
        for key, capability in tool_mapping.items():
            if key in tool_name.lower() or tool_name.lower() in key:
                return capability
        
        # Default to command processing
        return CapabilityType.COMMAND_PROCESSING


class DefaultTaskExecutor(TaskExecutor):
    """Default implementation of task execution."""
    
    @handle_agent_errors(operation="task_execution")
    async def execute(self, subtasks: List[Dict[str, Any]], selected_agents: AgentSelection, context: Dict[str, Any]) -> List[ExecutionResult]:
        """Execute subtasks using selected agents."""
        import time
        
        # Validate inputs
        validate_input(subtasks, list, "subtasks", required=True)
        validate_input(selected_agents, AgentSelection, "selected_agents", required=True)
        validate_input(context, dict, "context", required=True)
        
        logger.info(f"[TASK EXECUTION] Starting execution of {len(subtasks)} subtasks")
        logger.info(f"[TASK EXECUTION] Selected agents: {list(selected_agents.selected_agents.keys())}")
        
        # Log task-agent mapping
        for task_id, agent in selected_agents.selected_agents.items():
            logger.info(f"[TASK EXECUTION] Task '{task_id}' will be executed by agent '{agent.get_role().value}'")
        
        execution_results = []
        
        for i, subtask in enumerate(subtasks):
            start_time = time.time()
            
            # Handle both Subtask objects and dictionaries
            if hasattr(subtask, 'task_id'):
                # Subtask object
                task_id = subtask.task_id
                description = subtask.description
                agent_role = subtask.agent_role
            else:
                # Dictionary
                task_id = subtask.get('task_id', f"task_{i}")
                description = subtask.get('description', 'Unknown task')
                agent_role = subtask.get('agent_role', 'MESSAGE_PROCESSOR')
            
            logger.info(f"[TASK EXECUTION] Executing subtask {i+1}/{len(subtasks)}: {task_id}")
            logger.info(f"[TASK EXECUTION] Task description: {description}")
            logger.info(f"[TASK EXECUTION] Expected agent role: {agent_role}")
            
            # Find the agent for this task
            agent = selected_agents.selected_agents.get(task_id)
            if not agent:
                logger.warning(f"[TASK EXECUTION] ❌ No agent available for task {task_id}")
                logger.warning(f"[TASK EXECUTION] Available task-agent mappings: {list(selected_agents.selected_agents.keys())}")
                execution_results.append(ExecutionResult(
                    task_id=task_id,
                    success=False,
                    result=None,
                    error=f"No agent available for task {task_id}",
                    execution_time=0.0,
                    agent_role=agent_role
                ))
                continue
            
            logger.info(f"[TASK EXECUTION] ✅ Found agent '{agent.get_role().value}' for task '{task_id}'")
            logger.info(f"[TASK EXECUTION] Agent tools: {[tool.name for tool in agent.get_tools()]}")
            
            try:
                # Execute the task using the agent
                logger.info(f"[TASK EXECUTION] Starting agent execution for task '{task_id}'")
                logger.info(f"[TASK EXECUTION] Agent execution context: {context}")
                
                if hasattr(agent, 'execute') and callable(getattr(agent, 'execute')):
                    # Use the unified execute() interface
                    logger.info(f"[TASK EXECUTION] Using unified execute() interface")
                    result = await agent.execute(description, context)
                else:
                    # Fallback for legacy agents
                    logger.info(f"[TASK EXECUTION] Using legacy execute_task() interface")
                    result = await agent.execute_task(description, context)
                
                execution_time = time.time() - start_time
                
                logger.info(f"[TASK EXECUTION] ✅ Agent execution completed for task '{task_id}' in {execution_time:.2f}s")
                logger.info(f"[TASK EXECUTION] Agent execution result: {result[:200]}..." if len(str(result)) > 200 else f"[TASK EXECUTION] Agent execution result: {result}")
                
                execution_result = ExecutionResult(
                    task_id=task_id,
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    agent_role=agent_role
                )
                
                logger.info(f"[TASK EXECUTION] ✅ Subtask {task_id} completed successfully in {execution_time:.2f}s")
                execution_results.append(execution_result)
                
            except Exception as e:
                print(f"[AGENT ERROR TRACE] {traceback.format_exc()}")
                execution_time = time.time() - start_time
                error_msg = f"Error executing task {task_id}: {str(e)}"
                
                logger.error(f"[AGENT ERROR TRACE] [TASK EXECUTION] ❌ Error during agent execution for task '{task_id}': {e}", exc_info=True)
                
                execution_result = ExecutionResult(
                    task_id=task_id,
                    success=False,
                    result=None,
                    error=error_msg,
                    execution_time=execution_time,
                    agent_role=agent_role
                )
                
                logger.error(f"[TASK EXECUTION] ❌ Subtask {task_id} failed: {error_msg}")
                execution_results.append(execution_result)
        
        logger.info(f"[TASK EXECUTION] Completed execution of {len(execution_results)} subtasks")
        successful_count = len([r for r in execution_results if r.success])
        logger.info(f"[TASK EXECUTION] Success rate: {successful_count}/{len(execution_results)} tasks completed successfully")
        
        return execution_results


class DefaultResultAggregator(ResultAggregator):
    """Default implementation of result aggregation."""
    
    @handle_agent_errors(operation="result_aggregation")
    def aggregate(self, execution_results: List[ExecutionResult], context: Dict[str, Any]) -> str:
        """Aggregate execution results into a final response."""
        # Validate inputs
        validate_input(execution_results, list, "execution_results", required=True)
        validate_input(context, dict, "context", required=True)
        
        try:
            # Simple result aggregation
            successful_results = [r for r in execution_results if r.success]
            failed_results = [r for r in execution_results if not r.success]
            
            if not execution_results:
                return "❌ No results to aggregate"
            
            if len(successful_results) == len(execution_results):
                # All successful
                if len(execution_results) == 1:
                    return str(execution_results[0].result)
                else:
                    results_text = "\n".join([f"✅ {r.result}" for r in successful_results])
                    return f"✅ All tasks completed successfully:\n{results_text}"
            else:
                # Some failures
                success_text = "\n".join([f"✅ {r.result}" for r in successful_results]) if successful_results else "None"
                failure_text = "\n".join([f"❌ {r.error}" for r in failed_results]) if failed_results else "None"
                
                return f"""⚠️ Mixed results:

✅ Successful ({len(successful_results)}/{len(execution_results)}):
{success_text}

❌ Failed ({len(failed_results)}/{len(execution_results)}):
{failure_text}"""
            
        except Exception as e:
            print(f"[AGENT ERROR TRACE] {traceback.format_exc()}")
            # Raise a specific exception for better error handling
            raise ResultAggregationError(
                f"Failed to aggregate results: {str(e)}",
                create_error_context("result_aggregation", additional_info={
                    'execution_results_count': len(execution_results),
                    'successful_results_count': len([r for r in execution_results if r.success]),
                    'context_keys': list(context.keys())
                })
            )


class OrchestrationPipeline:
    """
    Dedicated orchestration pipeline for task execution.
    
    This class breaks down the task execution process into separate,
    swappable components for better maintainability and testability.
    """
    
    def __init__(
        self,
        intent_classifier: Optional[IntentClassifier] = None,
        task_decomposer: Optional[TaskDecomposer] = None,
        agent_router: Optional[AgentRouter] = None,
        task_executor: Optional[TaskExecutor] = None,
        result_aggregator: Optional[ResultAggregator] = None,
        llm=None
    ):
        """
        Initialize the orchestration pipeline.
        
        Args:
            intent_classifier: Intent classification component
            task_decomposer: Task decomposition component
            agent_router: Agent routing component
            task_executor: Task execution component
            result_aggregator: Result aggregation component
            llm: Language model for default components
        """
        self.intent_classifier = intent_classifier or DefaultIntentClassifier(llm)
        self.task_decomposer = task_decomposer or DefaultTaskDecomposer(llm)
        self.agent_router = agent_router or DefaultAgentRouter()
        self.task_executor = task_executor or DefaultTaskExecutor()
        self.result_aggregator = result_aggregator or DefaultResultAggregator()
        
        logger.info("✅ OrchestrationPipeline initialized with all components")
    
    async def execute_task(
        self,
        task_description: str,
        available_agents: Dict[AgentRole, ConfigurableAgent],
        execution_context: Dict[str, Any]
    ) -> str:
        """
        Execute a task using the orchestration pipeline.
        
        Args:
            task_description: The task to execute
            available_agents: Available agents for execution
            execution_context: Context information for execution
            
        Returns:
            The final result of task execution
        """
        # Use error context for unified error handling
        with error_context(
            operation="orchestration_pipeline_execution",
            context={
                'task_description': task_description[:100],  # Truncate for logging
                'available_agents_count': len(available_agents),
                'execution_context_keys': list(execution_context.keys())
            },
            config=ErrorHandlingConfig(
                log_errors=True,
                log_level=logging.INFO,
                include_traceback=False,
                user_friendly_messages=True,
                raise_on_critical=False
            )
        ):
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Starting task execution for '{task_description[:50]}...'")
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Available agents: {[role.value for role in available_agents.keys()]}")
            
            # Step 1: Intent Classification
            logger.info("🤖 ORCHESTRATION PIPELINE: Step 1 - Intent Classification")
            intent_result = self.intent_classifier.classify(task_description, execution_context)
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Intent classified as '{intent_result.intent}' with confidence {intent_result.confidence}")
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Intent entities: {intent_result.entities}")
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Secondary intents: {intent_result.secondary_intents}")
            
            # Step 2: Task Decomposition
            logger.info("🤖 ORCHESTRATION PIPELINE: Step 2 - Task Decomposition")
            decomposition = self.task_decomposer.decompose(task_description, intent_result, execution_context)
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Task decomposed into {len(decomposition.subtasks)} subtasks")
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Task complexity: {decomposition.complexity}")
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Estimated duration: {decomposition.estimated_duration}s")
            
            # Log each subtask for debugging
            for i, subtask in enumerate(decomposition.subtasks):
                if hasattr(subtask, 'task_id'):
                    logger.info(f"🤖 ORCHESTRATION PIPELINE: Subtask {i+1}: {subtask.task_id} - {subtask.description}")
                else:
                    logger.info(f"🤖 ORCHESTRATION PIPELINE: Subtask {i+1}: {subtask.get('task_id', 'unknown')} - {subtask.get('description', 'unknown')}")
            
            # Step 3: Agent Routing
            logger.info("🤖 ORCHESTRATION PIPELINE: Step 3 - Agent Routing")
            agent_selection = self.agent_router.route(decomposition.subtasks, available_agents, execution_context)
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Routed to {len(agent_selection.selected_agents)} agents")
            
            # Log agent selection details
            for task_id, agent in agent_selection.selected_agents.items():
                logger.info(f"🤖 ORCHESTRATION PIPELINE: Task '{task_id}' → Agent '{agent.get_role().value}'")
                logger.info(f"🤖 ORCHESTRATION PIPELINE: Agent '{agent.get_role().value}' tools: {[tool.name for tool in agent.get_tools()]}")
            
            # Log routing reasoning
            for task_id, reasoning in agent_selection.routing_reasoning.items():
                logger.info(f"🤖 ORCHESTRATION PIPELINE: Routing reasoning for '{task_id}': {reasoning}")
            
            # Step 4: Task Execution
            logger.info("🤖 ORCHESTRATION PIPELINE: Step 4 - Task Execution")
            execution_results = await self.task_executor.execute(decomposition.subtasks, agent_selection, execution_context)
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Executed {len(execution_results)} tasks")
            
            # Log execution results
            for result in execution_results:
                status = "✅ SUCCESS" if result.success else "❌ FAILED"
                logger.info(f"🤖 ORCHESTRATION PIPELINE: {status} - Task '{result.task_id}' ({result.agent_role.value}) in {result.execution_time:.2f}s")
                if not result.success:
                    logger.error(f"🤖 ORCHESTRATION PIPELINE: Task '{result.task_id}' error: {result.error}")
            
            # Step 5: Result Aggregation
            logger.info("🤖 ORCHESTRATION PIPELINE: Step 5 - Result Aggregation")
            final_response = self.result_aggregator.aggregate(execution_results, execution_context)
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Task execution completed successfully")
            logger.info(f"🤖 ORCHESTRATION PIPELINE: Final response length: {len(final_response)} characters")
            
            return final_response
    
    def update_component(self, component_type: str, new_component: Any) -> None:
        """
        Update a pipeline component.
        
        Args:
            component_type: Type of component to update ('intent_classifier', 'task_decomposer', etc.)
            new_component: New component instance
        """
        if component_type == 'intent_classifier':
            self.intent_classifier = new_component
        elif component_type == 'task_decomposer':
            self.task_decomposer = new_component
        elif component_type == 'agent_router':
            self.agent_router = new_component
        elif component_type == 'task_executor':
            self.task_executor = new_component
        elif component_type == 'result_aggregator':
            self.result_aggregator = new_component
        else:
            raise ValueError(f"Unknown component type: {component_type}")
        
        logger.info(f"Updated {component_type} component in orchestration pipeline")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the status of all pipeline components."""
        return {
            'intent_classifier': type(self.intent_classifier).__name__,
            'task_decomposer': type(self.task_decomposer).__name__,
            'agent_router': type(self.agent_router).__name__,
            'task_executor': type(self.task_executor).__name__,
            'result_aggregator': type(self.result_aggregator).__name__,
            'all_components_initialized': all([
                self.intent_classifier,
                self.task_decomposer,
                self.agent_router,
                self.task_executor,
                self.result_aggregator
            ])
        } 