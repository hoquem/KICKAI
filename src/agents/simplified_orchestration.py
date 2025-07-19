#!/usr/bin/env python3
"""
Simplified Orchestration Pipeline

This module provides a simplified, maintainable orchestration pipeline that uses
modular components and follows the pipeline pattern for better separation of concerns.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum

from agents.task_decomposition import TaskDecompositionManager
from agents.complexity_assessor import RequestComplexityAssessor, ComplexityAssessment
from agents.configurable_agent import ConfigurableAgent

logger = logging.getLogger(__name__)


# Import the correct AgentRole enum from the main enums file
from core.enums import AgentRole


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
    capabilities_required: List
    estimated_duration: int


@dataclass
class OrchestrationStep:
    """Represents a step in the orchestration pipeline."""
    name: str
    description: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    result: Any = None
    error: str = None


class PipelineStep(ABC):
    """Abstract base class for pipeline steps."""
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pipeline step."""
        pass
    
    @abstractmethod
    def get_step_name(self) -> str:
        """Get the name of this pipeline step."""
        pass


class IntentClassificationStep(PipelineStep):
    """Step for intent classification."""
    
    def __init__(self, intent_classifier):
        self.intent_classifier = intent_classifier
    
    def get_step_name(self) -> str:
        return "Intent Classification"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intent classification."""
        task_description = context.get('task_description')
        execution_context = context.get('execution_context', {})
        
        logger.info(f"🤖 ORCHESTRATION: Step 1 - Intent Classification")
        logger.info(f"[DEBUG] IntentClassificationStep: task_description='{task_description}' execution_context={execution_context}")
        intent_result = self.intent_classifier.classify(task_description, execution_context)
        logger.info(f"[DEBUG] IntentClassificationStep: intent='{getattr(intent_result, 'intent', None)}', confidence={getattr(intent_result, 'confidence', None)}, entities={getattr(intent_result, 'entities', None)}")
        logger.info(f"🤖 ORCHESTRATION: Intent classified as '{intent_result.intent}' with confidence {intent_result.confidence}")
        
        return {
            **context,
            'intent_result': intent_result,
            'step_results': {
                'intent_classification': {
                    'intent': intent_result.intent,
                    'confidence': intent_result.confidence,
                    'entities': intent_result.entities
                }
            }
        }


class ComplexityAssessmentStep(PipelineStep):
    """Step for complexity assessment."""
    
    def __init__(self, complexity_assessor: RequestComplexityAssessor):
        self.complexity_assessor = complexity_assessor
    
    def get_step_name(self) -> str:
        return "Complexity Assessment"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complexity assessment."""
        task_description = context.get('task_description')
        intent_result = context.get('intent_result')
        execution_context = context.get('execution_context', {})
        
        logger.info(f"🤖 ORCHESTRATION: Step 2 - Complexity Assessment")
        
        assessment = self.complexity_assessor.assess(
            request=task_description,
            intent=intent_result.intent,
            entities=intent_result.entities,
            context=execution_context
        )
        
        logger.info(f"🤖 ORCHESTRATION: Complexity assessed as {assessment.complexity_level} (score: {assessment.score:.2f})")
        
        return {
            **context,
            'complexity_assessment': assessment,
            'step_results': {
                **context.get('step_results', {}),
                'complexity_assessment': {
                    'level': assessment.complexity_level,
                    'score': assessment.score,
                    'reasoning': assessment.reasoning,
                    'estimated_time': assessment.estimated_processing_time,
                    'recommended_approach': assessment.recommended_approach
                }
            }
        }


class TaskDecompositionStep(PipelineStep):
    """Step for task decomposition."""
    
    def __init__(self, task_decomposer: TaskDecompositionManager):
        self.task_decomposer = task_decomposer
    
    def get_step_name(self) -> str:
        return "Task Decomposition"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task decomposition."""
        task_description = context.get('task_description')
        intent_result = context.get('intent_result')
        execution_context = context.get('execution_context', {})
        
        logger.info(f"🤖 ORCHESTRATION: Step 3 - Task Decomposition")
        
        # Create TaskContext for decomposition
        task_context = TaskContext(
            task_id=f"task_{int(execution_context.get('timestamp', 0))}",
            user_id=execution_context.get('user_id', 'unknown'),
            team_id=execution_context.get('team_id', 'unknown'),
            parameters=execution_context,
            metadata={}
        )
        
        subtasks = self.task_decomposer.decompose(task_description, task_context)
        
        logger.info(f"🤖 ORCHESTRATION: Task decomposed into {len(subtasks)} subtasks")
        
        # Log each subtask for debugging
        for i, subtask in enumerate(subtasks):
            logger.info(f"🤖 ORCHESTRATION: Subtask {i+1}: {subtask.task_id} - {subtask.description}")
        
        return {
            **context,
            'subtasks': subtasks,
            'step_results': {
                **context.get('step_results', {}),
                'task_decomposition': {
                    'subtask_count': len(subtasks),
                    'subtasks': [
                        {
                            'task_id': subtask.task_id,
                            'description': subtask.description,
                            'agent_role': subtask.agent_role.value,
                            'capabilities': [cap.value for cap in subtask.capabilities_required],
                            'estimated_duration': subtask.estimated_duration
                        }
                        for subtask in subtasks
                    ]
                }
            }
        }


class AgentRoutingStep(PipelineStep):
    """Step for agent routing."""
    
    def get_step_name(self) -> str:
        return "Agent Routing"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent routing."""
        subtasks = context.get('subtasks', [])
        available_agents = context.get('available_agents', {})
        
        logger.info(f"🤖 ORCHESTRATION: Step 4 - Agent Routing")
        logger.info(f"[DEBUG] AgentRoutingStep: available_agents={[role.value for role in available_agents.keys()]}")
        routed_tasks = []
        
        for subtask in subtasks:
            agent_role = subtask.agent_role
            logger.info(f"[DEBUG] AgentRoutingStep: subtask_id={subtask.task_id}, description='{subtask.description}', agent_role={agent_role.value}")
            if agent_role in available_agents:
                agent = available_agents[agent_role]
                routed_tasks.append({
                    'subtask': subtask,
                    'agent': agent,
                    'agent_role': agent_role
                })
                logger.info(f"🤖 ORCHESTRATION: Routed subtask '{subtask.task_id}' to {agent_role.value}")
            else:
                logger.warning(f"🤖 ORCHESTRATION: No agent available for role {agent_role.value}")
                # Fallback to message processor
                if AgentRole.MESSAGE_PROCESSOR in available_agents:
                    routed_tasks.append({
                        'subtask': subtask,
                        'agent': available_agents[AgentRole.MESSAGE_PROCESSOR],
                        'agent_role': AgentRole.MESSAGE_PROCESSOR
                    })
                    logger.info(f"🤖 ORCHESTRATION: Fallback routing for subtask '{subtask.task_id}' to MESSAGE_PROCESSOR")
        logger.info(f"[DEBUG] AgentRoutingStep: routed_tasks={[{'task_id': t['subtask'].task_id, 'agent_role': t['agent_role'].value} for t in routed_tasks]}")
        return {
            **context,
            'routed_tasks': routed_tasks,
            'step_results': {
                **context.get('step_results', {}),
                'agent_routing': {
                    'routed_task_count': len(routed_tasks),
                    'routed_tasks': [
                        {
                            'task_id': task['subtask'].task_id,
                            'agent_role': task['agent_role'].value,
                            'description': task['subtask'].description
                        }
                        for task in routed_tasks
                    ]
                }
            }
        }


class TaskExecutionStep(PipelineStep):
    """Step for task execution."""
    
    def get_step_name(self) -> str:
        return "Task Execution"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tasks."""
        routed_tasks = context.get('routed_tasks', [])
        execution_context = context.get('execution_context', {})
        
        logger.info(f"🤖 ORCHESTRATION: Step 5 - Task Execution")
        
        execution_results = []
        
        for i, task_info in enumerate(routed_tasks):
            subtask = task_info['subtask']
            agent = task_info['agent']
            
            logger.info(f"🤖 ORCHESTRATION: Executing subtask {i+1}/{len(routed_tasks)}: {subtask.task_id}")
            
            try:
                # Enhance task description with context for CrewAI
                enhanced_task = subtask.description
                if execution_context:
                    context_info = f"\n\nContext: Team ID: {execution_context.get('team_id', 'unknown')}, User ID: {execution_context.get('user_id', 'unknown')}, Chat Type: {'Leadership' if execution_context.get('is_leadership_chat', False) else 'Main'}"
                    enhanced_task = subtask.description + context_info
                
                # Execute the subtask using the agent with enhanced task description
                result = await agent.execute(enhanced_task, execution_context)
                
                execution_results.append({
                    'subtask_id': subtask.task_id,
                    'agent_role': task_info['agent_role'].value,
                    'success': True,
                    'result': result,
                    'error': None
                })
                
                logger.info(f"🤖 ORCHESTRATION: Subtask {subtask.task_id} completed successfully")
                
            except Exception as e:
                logger.error(f"🤖 ORCHESTRATION: Error executing subtask {subtask.task_id}: {e}")
                
                execution_results.append({
                    'subtask_id': subtask.task_id,
                    'agent_role': task_info['agent_role'].value,
                    'success': False,
                    'result': None,
                    'error': str(e)
                })
        
        return {
            **context,
            'execution_results': execution_results,
            'step_results': {
                'execution_completed': True,
                'successful_tasks': len([r for r in execution_results if r['success']]),
                'failed_tasks': len([r for r in execution_results if not r['success']])
            }
        }


class ResultAggregationStep(PipelineStep):
    """Step for result aggregation."""
    
    def get_step_name(self) -> str:
        return "Result Aggregation"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from all tasks."""
        execution_results = context.get('execution_results', [])
        
        logger.info(f"🤖 ORCHESTRATION: Step 6 - Result Aggregation")
        
        # Check if all tasks were successful
        successful_results = [r for r in execution_results if r['success']]
        failed_results = [r for r in execution_results if not r['success']]
        
        if failed_results:
            logger.warning(f"🤖 ORCHESTRATION: {len(failed_results)} tasks failed")
            # Return error message for failed tasks
            error_messages = [f"Task {r['subtask_id']}: {r['error']}" for r in failed_results]
            aggregated_result = f"❌ Some tasks failed:\n" + "\n".join(error_messages)
        else:
            logger.info(f"🤖 ORCHESTRATION: All {len(successful_results)} tasks completed successfully")
            # Aggregate successful results
            if len(successful_results) == 1:
                aggregated_result = str(successful_results[0]['result'])
            else:
                # Combine multiple results
                results = [str(r['result']) for r in successful_results]
                aggregated_result = "\n\n".join(results)
        
        return {
            **context,
            'final_result': aggregated_result,
            'step_results': {
                **context.get('step_results', {}),
                'result_aggregation': {
                    'total_tasks': len(execution_results),
                    'successful_tasks': len(successful_results),
                    'failed_tasks': len(failed_results),
                    'final_result_length': len(str(aggregated_result)) if aggregated_result else 0
                }
            }
        }


class SimplifiedOrchestrationPipeline:
    """
    Simplified orchestration pipeline using modular steps.
    
    This class breaks down the task execution process into separate,
    swappable components for better maintainability and testability.
    """
    
    def __init__(self, llm=None):
        """Initialize the orchestration pipeline."""
        self.llm = llm
        
        # Initialize components
        self.intent_classifier = self._create_intent_classifier()
        self.complexity_assessor = RequestComplexityAssessor()
        self.task_decomposer = TaskDecompositionManager(llm)
        
        # Initialize pipeline steps
        self.pipeline_steps = [
            IntentClassificationStep(self.intent_classifier),
            ComplexityAssessmentStep(self.complexity_assessor),
            TaskDecompositionStep(self.task_decomposer),
            AgentRoutingStep(),
            TaskExecutionStep(),
            ResultAggregationStep()
        ]
        
        logger.info("✅ SimplifiedOrchestrationPipeline initialized with all components")
    
    def _create_intent_classifier(self):
        """Create intent classifier."""
        try:
            from agents.intelligent_system import IntentClassifier
            return IntentClassifier(llm=self.llm)
        except ImportError:
            logger.warning("IntentClassifier not available, using fallback")
            return self._create_fallback_intent_classifier()
    
    def _create_fallback_intent_classifier(self):
        """Create a fallback intent classifier when the main one is not available."""
        class FallbackIntentClassifier:
            def classify(self, task_description: str, execution_context: Dict[str, Any]):
                # Simple rule-based intent classification
                task_lower = task_description.lower().strip()
                
                # Define intent patterns
                if task_lower.startswith('/myinfo'):
                    return type('IntentResult', (), {
                        'intent': 'get_my_status',
                        'confidence': 0.95,
                        'entities': {'command': 'myinfo'}
                    })()
                elif task_lower.startswith('/list'):
                    return type('IntentResult', (), {
                        'intent': 'list_players',
                        'confidence': 0.95,
                        'entities': {'command': 'list'}
                    })()
                elif task_lower.startswith('/status'):
                    return type('IntentResult', (), {
                        'intent': 'get_player_status',
                        'confidence': 0.95,
                        'entities': {'command': 'status'}
                    })()
                elif task_lower.startswith('/help'):
                    return type('IntentResult', (), {
                        'intent': 'help',
                        'confidence': 0.95,
                        'entities': {'command': 'help'}
                    })()
                elif 'help' in task_lower:
                    return type('IntentResult', (), {
                        'intent': 'help',
                        'confidence': 0.8,
                        'entities': {}
                    })()
                else:
                    return type('IntentResult', (), {
                        'intent': 'general_query',
                        'confidence': 0.5,
                        'entities': {}
                    })()
        
        return FallbackIntentClassifier()
    
    async def execute_task(
        self,
        task_description: str,
        available_agents: Dict[AgentRole, ConfigurableAgent],
        execution_context: Dict[str, Any]
    ) -> str:
        """
        Execute a task using the simplified orchestration pipeline.
        
        Args:
            task_description: Description of the task to execute
            available_agents: Dictionary of available agents by role
            execution_context: Execution context
            
        Returns:
            Result of task execution
        """
        try:
            # Validate inputs
            if not task_description or not task_description.strip():
                return "❌ Task description is required"
            
            if not available_agents:
                return "❌ No agents available for task execution"
            
            # Initialize pipeline context
            context = {
                'task_description': task_description,
                'available_agents': available_agents,
                'execution_context': execution_context or {},
                'step_results': {},
                'pipeline_start_time': time.time()
            }
            
            logger.info(f"🤖 SIMPLIFIED ORCHESTRATION: Starting task execution for '{task_description[:50]}...'")
            logger.info(f"🤖 SIMPLIFIED ORCHESTRATION: Available agents: {[role.value for role in available_agents.keys()]}")
            logger.info(f"🤖 SIMPLIFIED ORCHESTRATION: Execution context: {execution_context}")
            
            # Execute each pipeline step with robust error handling
            for i, step in enumerate(self.pipeline_steps):
                step_name = step.get_step_name()
                try:
                    logger.info(f"🤖 SIMPLIFIED ORCHESTRATION: Step {i+1}/{len(self.pipeline_steps)} - Executing {step_name}")
                    
                    # Add step timing
                    step_start_time = time.time()
                    context = await step.execute(context)
                    step_duration = time.time() - step_start_time
                    
                    logger.info(f"🤖 SIMPLIFIED ORCHESTRATION: Step {i+1}/{len(self.pipeline_steps)} - {step_name} completed in {step_duration:.2f}s")
                    
                    # Validate step output
                    if not isinstance(context, dict):
                        raise ValueError(f"Step {step_name} returned invalid context type: {type(context)}")
                    
                except Exception as e:
                    logger.error(f"🤖 SIMPLIFIED ORCHESTRATION: Error in {step_name}: {e}", exc_info=True)
                    
                    # Try to provide a meaningful error message
                    if "intent" in step_name.lower():
                        return f"❌ I couldn't understand your request. Please try rephrasing it."
                    elif "complexity" in step_name.lower():
                        return f"❌ I had trouble analyzing your request. Please try again."
                    elif "decomposition" in step_name.lower():
                        return f"❌ I couldn't break down your request into manageable tasks. Please try a simpler request."
                    elif "routing" in step_name.lower():
                        return f"❌ I couldn't find the right agent to handle your request. Please try again."
                    elif "execution" in step_name.lower():
                        return f"❌ There was an error processing your request. Please try again."
                    elif "aggregation" in step_name.lower():
                        return f"❌ I couldn't combine the results properly. Please try again."
                    else:
                        return f"❌ Error in {step_name}: {str(e)}"
            
            # Return final result
            final_result = context.get('final_result', '❌ No result generated')
            total_duration = time.time() - context.get('pipeline_start_time', 0)
            
            logger.info(f"🤖 SIMPLIFIED ORCHESTRATION: Task execution completed successfully in {total_duration:.2f}s")
            logger.info(f"🤖 SIMPLIFIED ORCHESTRATION: Final result length: {len(str(final_result))}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"🤖 SIMPLIFIED ORCHESTRATION: Error in pipeline execution: {e}", exc_info=True)
            return f"❌ Error in orchestration pipeline: {str(e)}"
    
    def get_pipeline_analytics(self) -> Dict[str, Any]:
        """Get analytics about pipeline execution."""
        return {
            'complexity_analytics': self.complexity_assessor.get_assessment_analytics(),
            'decomposition_analytics': self.task_decomposer.get_decomposition_analytics(),
            'pipeline_steps': [step.get_step_name() for step in self.pipeline_steps]
        }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the status of the orchestration pipeline."""
        return {
            'orchestration_pipeline': 'SimplifiedOrchestrationPipeline',
            'all_components_initialized': True,
            'pipeline_steps_count': len(self.pipeline_steps),
            'pipeline_steps': [step.get_step_name() for step in self.pipeline_steps],
            'llm_available': self.llm is not None,
            'intent_classifier_available': self.intent_classifier is not None,
            'complexity_assessor_available': self.complexity_assessor is not None,
            'task_decomposer_available': self.task_decomposer is not None
        } 