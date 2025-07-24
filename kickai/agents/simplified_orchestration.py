#!/usr/bin/env python3
"""
Simplified Orchestration Pipeline

This module provides a simplified, maintainable orchestration pipeline that uses
modular components and follows the pipeline pattern for better separation of concerns.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from kickai.agents.complexity_assessor import RequestComplexityAssessor
from kickai.agents.entity_specific_agents import (
    EntitySpecificAgentManager,
)
from kickai.agents.task_decomposition import TaskDecompositionManager

logger = logging.getLogger(__name__)


# Import the correct AgentRole enum from the main enums file
from kickai.core.enums import AgentRole


@dataclass
class TaskContext:
    """Context for task execution."""
    task_id: str
    user_id: str
    team_id: str
    parameters: dict[str, Any]
    metadata: dict[str, Any]


@dataclass
class Subtask:
    """Represents a subtask in task decomposition."""
    task_id: str
    description: str
    agent_role: AgentRole
    capabilities_required: list
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
    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the pipeline step."""
        pass

    @abstractmethod
    def get_step_name(self) -> str:
        """Get the name of this pipeline step."""
        pass


from kickai.features.player_registration.domain.state_machine import (
    RegistrationState,
    RegistrationStateMachine,
)


class IntentClassificationStep(PipelineStep):
    """Step for intent classification."""

    def __init__(self, intent_classifier):
        self.intent_classifier = intent_classifier
        self.state_machine = RegistrationStateMachine()

    def get_step_name(self) -> str:
        return "Intent Classification"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute intent classification."""
        task_description = context.get('task_description')
        execution_context = context.get('execution_context', {})

        # Check for confirmation
        if self.state_machine.state == RegistrationState.AWAITING_CONFIRMATION and task_description.lower() in ['yes', 'y']:
            self.state_machine.transition(RegistrationState.REGISTERED)
            return {
                **context,
                'intent_result': type('IntentResult', (), {
                    'intent': 'confirm_registration',
                    'confidence': 1.0,
                    'entities': execution_context.get('registration_details')
                })(),
                'step_results': {
                    'intent_classification': {
                        'status': 'completed',
                        'intent': 'confirm_registration',
                        'confidence': 1.0
                    }
                }
            }

        # Use the intent classifier
        try:
            intent_result = self.intent_classifier.classify(task_description, execution_context)
            logger.info(f"🔍 Intent classification result: {intent_result.intent} (confidence: {intent_result.confidence})")

            return {
                **context,
                'intent_result': intent_result,
                'step_results': {
                    'intent_classification': {
                        'status': 'completed',
                        'intent': intent_result.intent,
                        'confidence': intent_result.confidence
                    }
                }
            }
        except Exception as e:
            logger.error(f"❌ Intent classification failed: {e}")
            return {
                **context,
                'intent_result': type('IntentResult', (), {
                    'intent': 'unknown',
                    'confidence': 0.0,
                    'entities': {}
                })(),
                'step_results': {
                    'intent_classification': {
                        'status': 'failed',
                        'error': str(e)
                    }
                }
            }


class EntityValidationStep(PipelineStep):
    """Step for entity-specific validation."""

    def __init__(self, entity_manager: EntitySpecificAgentManager):
        self.entity_manager = entity_manager

    def get_step_name(self) -> str:
        return "Entity Validation"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute entity validation."""
        task_description = context.get('task_description')
        execution_context = context.get('execution_context', {})
        intent_result = context.get('intent_result')

        try:
            # Extract parameters from execution context and add missing context
            parameters = execution_context.get('parameters', {})
            
            # Add missing context information to parameters
            if 'chat_type' in execution_context:
                parameters['chat_type'] = execution_context['chat_type']
            if 'is_team_member' in execution_context:
                parameters['is_team_member'] = execution_context['is_team_member']
            if 'is_player' in execution_context:
                parameters['is_player'] = execution_context['is_player']

            # Extract command name from task description for proper validation
            command_name = task_description.split()[0] if task_description else ""

            # Validate the operation using command name
            validation_result = self.entity_manager.validator.validate_operation(
                command_name, parameters
            )

            logger.info(f"🔍 Entity validation result: {validation_result.entity_type} (valid: {validation_result.is_valid})")

            if not validation_result.is_valid:
                logger.warning(f"⚠️ Entity validation failed: {validation_result.error_message}")

            return {
                **context,
                'entity_validation_result': validation_result,
                'step_results': {
                    'entity_validation': {
                        'status': 'completed',
                        'is_valid': validation_result.is_valid,
                        'entity_type': validation_result.entity_type.value if validation_result.entity_type else None,
                        'error_message': validation_result.error_message,
                        'suggested_agent': validation_result.suggested_agent.value if validation_result.suggested_agent else None
                    }
                }
            }
        except Exception as e:
            logger.error(f"❌ Entity validation failed: {e}")
            return {
                **context,
                'entity_validation_result': type('EntityValidationResult', (), {
                    'is_valid': False,
                    'entity_type': None,
                    'error_message': f"Entity validation error: {e!s}",
                    'suggested_agent': None
                })(),
                'step_results': {
                    'entity_validation': {
                        'status': 'failed',
                        'error': str(e)
                    }
                }
            }


class ComplexityAssessmentStep(PipelineStep):
    """Step for complexity assessment."""

    def __init__(self, complexity_assessor: RequestComplexityAssessor):
        self.complexity_assessor = complexity_assessor

    def get_step_name(self) -> str:
        return "Complexity Assessment"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute complexity assessment."""
        task_description = context.get('task_description')
        execution_context = context.get('execution_context', {})
        intent_result = context.get('intent_result')
        entity_validation_result = context.get('entity_validation_result')

        try:
            # Assess complexity
            complexity_result = self.complexity_assessor.assess(
                request=task_description,
                intent=intent_result.intent if intent_result else 'general_inquiry',
                entities=intent_result.entities if intent_result else {},
                context=execution_context,
                user_id=execution_context.get('user_id')
            )

            logger.info(f"🔍 Complexity assessment: {complexity_result.complexity_level} (score: {complexity_result.score})")

            return {
                **context,
                'complexity_result': complexity_result,
                'step_results': {
                    'complexity_assessment': {
                        'status': 'completed',
                        'complexity_level': complexity_result.complexity_level,
                        'complexity_score': complexity_result.score,
                        'reasoning': complexity_result.reasoning
                    }
                }
            }
        except Exception as e:
            logger.error(f"❌ Complexity assessment failed: {e}")
            return {
                **context,
                'complexity_result': type('ComplexityAssessment', (), {
                    'complexity_level': 'medium',
                    'score': 0.5,
                    'reasoning': f"Complexity assessment error: {e!s}"
                })(),
                'step_results': {
                    'complexity_assessment': {
                        'status': 'failed',
                        'error': str(e)
                    }
                }
            }


class TaskDecompositionStep(PipelineStep):
    """Step for task decomposition."""

    def __init__(self, task_decomposer: TaskDecompositionManager):
        self.task_decomposer = task_decomposer

    def get_step_name(self) -> str:
        return "Task Decomposition"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute task decomposition."""
        task_description = context.get('task_description')
        execution_context = context.get('execution_context', {})
        intent_result = context.get('intent_result')
        complexity_result = context.get('complexity_result')
        entity_validation_result = context.get('entity_validation_result')

        try:
            # Decompose task if complex
            if complexity_result.complexity_level in ['high', 'very_high']:
                subtasks = self.task_decomposer.decompose_task(
                    task_description, execution_context, intent_result, complexity_result
                )
                logger.info(f"🔍 Task decomposed into {len(subtasks)} subtasks")
            else:
                subtasks = []
                logger.info("🔍 Task is simple, no decomposition needed")

            return {
                **context,
                'subtasks': subtasks,
                'step_results': {
                    'task_decomposition': {
                        'status': 'completed',
                        'subtasks_count': len(subtasks),
                        'subtasks': [subtask.__dict__ for subtask in subtasks]
                    }
                }
            }
        except Exception as e:
            logger.error(f"❌ Task decomposition failed: {e}")
            return {
                **context,
                'subtasks': [],
                'step_results': {
                    'task_decomposition': {
                        'status': 'failed',
                        'error': str(e)
                    }
                }
            }


class EntityAwareAgentRoutingStep(PipelineStep):
    """Step for entity-aware agent routing."""

    def __init__(self, entity_manager: EntitySpecificAgentManager):
        self.entity_manager = entity_manager

    def get_step_name(self) -> str:
        return "Entity-Aware Agent Routing"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute entity-aware agent routing."""
        task_description = context.get('task_description')
        execution_context = context.get('execution_context', {})
        intent_result = context.get('intent_result')
        entity_validation_result = context.get('entity_validation_result')
        available_agents = context.get('available_agents', {})

        try:
            # Extract parameters for routing
            parameters = execution_context.get('parameters', {})

            # Extract command name from task description for proper routing
            command_name = task_description.split()[0] if task_description else ""

            # Route operation to appropriate agent using command name
            selected_agent_role = self.entity_manager.route_operation_to_agent(
                command_name, parameters, available_agents
            )

            if selected_agent_role:
                logger.info(f"🔍 Routed to agent: {selected_agent_role.value}")

                # Create entity operation context
                entity_context = self.entity_manager.create_entity_operation_context(
                    task_description,
                    selected_agent_role,
                    "unknown_tool",  # Will be determined by agent
                    parameters
                )

                return {
                    **context,
                    'selected_agent_role': selected_agent_role,
                    'entity_operation_context': entity_context,
                    'step_results': {
                        'agent_routing': {
                            'status': 'completed',
                            'selected_agent': selected_agent_role.value,
                            'entity_type': entity_context.entity_type.value,
                            'validation_result': entity_context.validation_result.is_valid
                        }
                    }
                }
            else:
                logger.warning("⚠️ No suitable agent found, using fallback")
                return {
                    **context,
                    'selected_agent_role': AgentRole.MESSAGE_PROCESSOR,
                    'step_results': {
                        'agent_routing': {
                            'status': 'completed',
                            'selected_agent': 'message_processor',
                            'fallback_used': True
                        }
                    }
                }
        except Exception as e:
            logger.error(f"❌ Agent routing failed: {e}")
            return {
                **context,
                'selected_agent_role': AgentRole.MESSAGE_PROCESSOR,
                'step_results': {
                    'agent_routing': {
                        'status': 'failed',
                        'error': str(e),
                        'fallback_used': True
                    }
                }
            }


class TaskExecutionStep(PipelineStep):
    """Step for task execution."""

    def get_step_name(self) -> str:
        return "Task Execution"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the task."""
        selected_agent_role = context.get('selected_agent_role')
        available_agents = context.get('available_agents', {})
        task_description = context.get('task_description')
        execution_context = context.get('execution_context', {})
        entity_operation_context = context.get('entity_operation_context')

        try:
            if selected_agent_role and selected_agent_role in available_agents:
                agent = available_agents[selected_agent_role]

                # Validate agent can handle this entity type
                if entity_operation_context:
                    entity_manager = EntitySpecificAgentManager(agent.context.tool_registry)
                    can_handle = entity_manager.validate_agent_entity_access(
                        selected_agent_role, entity_operation_context.entity_type
                    )

                    if not can_handle:
                        logger.warning(f"⚠️ Agent {selected_agent_role.value} cannot handle entity type {entity_operation_context.entity_type.value}")
                        # Fallback to message processor
                        if AgentRole.MESSAGE_PROCESSOR in available_agents:
                            agent = available_agents[AgentRole.MESSAGE_PROCESSOR]
                            logger.info("🔄 Fallback to Message Processor")

                # Execute the task
                logger.info(f"🚀 Executing task with agent: {selected_agent_role.value}")
                result = await agent.execute(task_description, execution_context)

                return {
                    **context,
                    'execution_result': result,
                    'step_results': {
                        'task_execution': {
                            'status': 'completed',
                            'agent_used': selected_agent_role.value,
                            'result_length': len(str(result)) if result else 0
                        }
                    }
                }
            else:
                logger.error("❌ No suitable agent available for task execution")
                return {
                    **context,
                    'execution_result': "Sorry, I'm unable to process your request at the moment. Please try again later.",
                    'step_results': {
                        'task_execution': {
                            'status': 'failed',
                            'error': 'No suitable agent available'
                        }
                    }
                }
        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            return {
                **context,
                'execution_result': f"Sorry, I encountered an error while processing your request: {e!s}",
                'step_results': {
                    'task_execution': {
                        'status': 'failed',
                        'error': str(e)
                    }
                }
            }


class ResultAggregationStep(PipelineStep):
    """Step for result aggregation."""

    def get_step_name(self) -> str:
        return "Result Aggregation"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute result aggregation."""
        execution_result = context.get('execution_result')
        step_results = context.get('step_results', {})
        entity_operation_context = context.get('entity_operation_context')

        try:
            # Aggregate results from all steps
            aggregated_result = {
                'final_result': execution_result,
                'pipeline_summary': {
                    'total_steps': len(step_results),
                    'successful_steps': len([s for s in step_results.values() if s.get('status') == 'completed']),
                    'failed_steps': len([s for s in step_results.values() if s.get('status') == 'failed'])
                },
                'entity_context': {
                    'entity_type': entity_operation_context.entity_type.value if entity_operation_context else None,
                    'operation_type': entity_operation_context.operation_type if entity_operation_context else None,
                    'validation_passed': entity_operation_context.validation_result.is_valid if entity_operation_context else None
                },
                'step_details': step_results
            }

            logger.info(f"✅ Pipeline completed successfully. Final result length: {len(str(execution_result))}")

            return {
                **context,
                'aggregated_result': aggregated_result,
                'step_results': {
                    'result_aggregation': {
                        'status': 'completed',
                        'result_summary': aggregated_result['pipeline_summary']
                    }
                }
            }
        except Exception as e:
            logger.error(f"❌ Result aggregation failed: {e}")
            return {
                **context,
                'aggregated_result': {
                    'final_result': execution_result,
                    'error': f"Result aggregation failed: {e!s}"
                },
                'step_results': {
                    'result_aggregation': {
                        'status': 'failed',
                        'error': str(e)
                    }
                }
            }


class SimplifiedOrchestrationPipeline:
    """
    Simplified orchestration pipeline with entity-specific validation.

    This pipeline includes:
    1. Intent Classification
    2. Entity Validation
    3. Complexity Assessment
    4. Task Decomposition (if needed)
    5. Entity-Aware Agent Routing
    6. Task Execution
    7. Result Aggregation
    """

    def __init__(self, llm=None):
        self.llm = llm
        self.steps = []
        self.pipeline_analytics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0
        }

        # Initialize components
        self._create_intent_classifier()
        self._create_entity_manager()
        self._create_complexity_assessor()
        self._create_task_decomposer()

        # Build pipeline
        self._build_pipeline()

        logger.info("🚀 SimplifiedOrchestrationPipeline initialized with entity-specific validation")

    def _create_intent_classifier(self):
        """Create the intent classifier."""
        self.intent_classifier = self._create_fallback_intent_classifier()

    def _create_fallback_intent_classifier(self):
        """Create a fallback intent classifier."""
        class FallbackIntentClassifier:
            def classify(self, task_description: str, execution_context: dict[str, Any]):
                # Simple rule-based intent classification
                task_lower = task_description.lower()

                if any(word in task_lower for word in ['help', 'what', 'how', 'command']):
                    return type('IntentResult', (), {
                        'intent': 'help_request',
                        'confidence': 0.8,
                        'entities': {}
                    })()
                elif any(word in task_lower for word in ['status', 'info', 'myinfo']):
                    return type('IntentResult', (), {
                        'intent': 'status_inquiry',
                        'confidence': 0.9,
                        'entities': {}
                    })()
                elif any(word in task_lower for word in ['register', 'join', 'signup']):
                    return type('IntentResult', (), {
                        'intent': 'registration',
                        'confidence': 0.9,
                        'entities': {}
                    })()
                elif any(word in task_lower for word in ['list', 'show', 'all']):
                    return type('IntentResult', (), {
                        'intent': 'list_request',
                        'confidence': 0.8,
                        'entities': {}
                    })()
                else:
                    return type('IntentResult', (), {
                        'intent': 'general_inquiry',
                        'confidence': 0.5,
                        'entities': {}
                    })()

        return FallbackIntentClassifier()

    def _create_entity_manager(self):
        """Create the entity-specific agent manager."""
        from kickai.agents.tool_registry import get_tool_registry
        tool_registry = get_tool_registry()
        self.entity_manager = EntitySpecificAgentManager(tool_registry)

    def _create_complexity_assessor(self):
        """Create the complexity assessor."""
        self.complexity_assessor = RequestComplexityAssessor()

    def _create_task_decomposer(self):
        """Create the task decomposer."""
        self.task_decomposer = TaskDecompositionManager()

    def _build_pipeline(self):
        """Build the orchestration pipeline."""
        self.steps = [
            IntentClassificationStep(self.intent_classifier),
            EntityValidationStep(self.entity_manager),
            ComplexityAssessmentStep(self.complexity_assessor),
            TaskDecompositionStep(self.task_decomposer),
            EntityAwareAgentRoutingStep(self.entity_manager),
            TaskExecutionStep(),
            ResultAggregationStep()
        ]

        logger.info(f"🔧 Built pipeline with {len(self.steps)} steps")

    def get_pipeline_analytics(self) -> dict[str, Any]:
        """Get analytics about pipeline execution."""
        return {
            'complexity_analytics': self.complexity_assessor.get_assessment_analytics(),
            'decomposition_analytics': self.task_decomposer.get_decomposition_analytics(),
            'pipeline_steps': [step.get_step_name() for step in self.steps]
        }

    def get_pipeline_status(self) -> dict[str, Any]:
        """Get the status of the orchestration pipeline."""
        return {
            'orchestration_pipeline': 'SimplifiedOrchestrationPipeline',
            'all_components_initialized': True,
            'pipeline_steps_count': len(self.steps),
            'pipeline_steps': [step.get_step_name() for step in self.steps],
            'llm_available': self.llm is not None,
            'intent_classifier_available': self.intent_classifier is not None,
            'complexity_assessor_available': self.complexity_assessor is not None,
            'task_decomposer_available': self.task_decomposer is not None
        }

    async def execute_task(self, task_description: str, execution_context: dict[str, Any], available_agents: dict[str, Any] = None) -> str:
        """
        Execute a task through the orchestration pipeline.

        Args:
            task_description: The task to execute
            execution_context: Context for execution
            available_agents: Dictionary of available agents for routing and execution

        Returns:
            The result of task execution
        """
        try:
            logger.info(f"🚀 [ORCHESTRATION] Starting task execution: {task_description[:50]}...")

            # Initialize context
            context = {
                'task_description': task_description,
                'execution_context': execution_context,
                'available_agents': available_agents or {},
                'pipeline_steps': [],
                'current_step': 0,
                'result': None,
                'error': None
            }

            # Execute each pipeline step
            for i, step in enumerate(self.steps):
                try:
                    logger.info(f"🔧 [ORCHESTRATION] Executing step {i+1}/{len(self.steps)}: {step.get_step_name()}")
                    context['current_step'] = i + 1

                    # Execute the step
                    step_result = await step.execute(context)
                    context.update(step_result)
                    context['pipeline_steps'].append({
                        'step': step.get_step_name(),
                        'status': 'completed',
                        'result': step_result
                    })

                    logger.info(f"✅ [ORCHESTRATION] Step {step.get_step_name()} completed")

                except Exception as e:
                    logger.error(f"❌ [ORCHESTRATION] Step {step.get_step_name()} failed: {e}")
                    context['error'] = str(e)
                    context['pipeline_steps'].append({
                        'step': step.get_step_name(),
                        'status': 'failed',
                        'error': str(e)
                    })
                    break

            # Update analytics
            self.pipeline_analytics['total_executions'] += 1
            if context.get('error'):
                self.pipeline_analytics['failed_executions'] += 1
                logger.error(f"❌ [ORCHESTRATION] Pipeline execution failed: {context['error']}")
                return f"❌ Sorry, I encountered an error while processing your request: {context['error']}"
            else:
                self.pipeline_analytics['successful_executions'] += 1

                # Extract the final result from the aggregated result
                aggregated_result = context.get('aggregated_result', {})
                final_result = aggregated_result.get('final_result')

                if final_result is None:
                    # Fallback: check if we have an execution result directly
                    execution_result = context.get('execution_result')
                    if execution_result:
                        final_result = execution_result
                    else:
                        final_result = "❌ Sorry, I'm unable to process your request at the moment. Please try again."

                logger.info("✅ [ORCHESTRATION] Pipeline execution completed successfully")
                return final_result

        except Exception as e:
            logger.error(f"❌ [ORCHESTRATION] Pipeline execution failed: {e}")
            self.pipeline_analytics['failed_executions'] += 1
            return f"❌ Sorry, I encountered an error while processing your request: {e!s}"
