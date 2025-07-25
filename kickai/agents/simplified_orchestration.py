#!/usr/bin/env python3
"""
Simplified Orchestration Pipeline

This module provides a simplified, maintainable orchestration pipeline that uses
3 core steps for better performance and reduced complexity.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from loguru import logger

from kickai.core.enums import AgentRole, ChatType
from kickai.core.enums import ChatType as ChatTypeEnum
# Removed custom tool output capture - using CrewAI native tools_results
from kickai.core.models.context_models import BaseContext, validate_context_data


@dataclass
class TaskContext:
    """Context for task execution."""
    task_id: str
    user_id: str
    team_id: str
    parameters: dict[str, Any]
    metadata: dict[str, Any]


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


class IntentClassificationStep(PipelineStep):
    """Step for intent classification with fallback."""

    def get_step_name(self) -> str:
        return "Intent Classification"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute intent classification with simplified logic."""
        task_description = context.get('task_description', '')
        execution_context = context.get('execution_context', {})

        # Simple intent classification based on command patterns
        intent = self._classify_intent(task_description, execution_context)

        return {
            **context,
            'intent_result': {
                'intent': intent,
                'confidence': 0.9,
                'entities': {}
            }
        }
    
    def _classify_intent(self, task_description: str, execution_context: dict) -> str:
        """Simple rule-based intent classification."""
        task_lower = task_description.lower().strip()
        
        # Command-based classification
        if task_lower.startswith('/'):
            command = task_lower.split()[0]
            return f"command_{command[1:]}"  # Remove leading slash
        
        # Natural language classification
        if any(word in task_lower for word in ['help', 'what', 'how', 'show']):
            return 'help_request'
        elif any(word in task_lower for word in ['status', 'info', 'my']):
            return 'status_request'
        elif any(word in task_lower for word in ['list', 'show', 'get']):
            return 'list_request'
        elif any(word in task_lower for word in ['add', 'register', 'create']):
            return 'creation_request'
        elif any(word in task_lower for word in ['approve', 'reject', 'update']):
            return 'approval_request'
        else:
            return 'general_query'


class AgentSelectionStep(PipelineStep):
    """Step for agent selection based on intent and context."""

    def get_step_name(self) -> str:
        return "Agent Selection"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute agent selection with direct mapping."""
        intent_result = context.get('intent_result', {})
        execution_context = context.get('execution_context', {})
        available_agents = context.get('available_agents', {})

        # Direct agent mapping based on intent
        selected_agent = self._select_agent(intent_result, execution_context, available_agents)
        
        # Track agent selection for analytics (will be handled by pipeline)
        if selected_agent and hasattr(selected_agent, 'role'):
            agent_role = selected_agent.role
            intent = intent_result.get('intent', 'general_query')
            chat_type = execution_context.get('chat_type', 'main_chat')
            agent_key = f"{agent_role}_{intent}_{chat_type}"
            context['agent_usage_key'] = agent_key

        return {
            **context,
            'selected_agent': selected_agent
        }
    
    def _select_agent(self, intent_result: dict, execution_context: dict, available_agents: dict) -> Any:
        """Select the most appropriate agent based on intent and context."""
        intent = intent_result.get('intent', 'general_query')
        chat_type = execution_context.get('chat_type', 'main_chat')
        
        # Direct mapping based on intent and chat type
        if intent.startswith('command_'):
            command = intent.replace('command_', '')
            
            # Help commands - available in both chats
            if command in ['help', 'start']:
                return available_agents.get(AgentRole.HELP_ASSISTANT) or available_agents.get(AgentRole.MESSAGE_PROCESSOR)
            
            # Player commands - context-aware selection
            if command in ['myinfo', 'register', 'approve']:
                if chat_type == 'main_chat' and command == 'approve':
                    # Approve command not available in main chat
                    return available_agents.get(AgentRole.MESSAGE_PROCESSOR)
                return available_agents.get(AgentRole.PLAYER_COORDINATOR) or available_agents.get(AgentRole.MESSAGE_PROCESSOR)
            
            # List commands - context-aware selection
            if command in ['list', 'players']:
                if chat_type == 'main_chat':
                    # Main chat: Use PLAYER_COORDINATOR for get_active_players
                    return available_agents.get(AgentRole.PLAYER_COORDINATOR) or available_agents.get(AgentRole.MESSAGE_PROCESSOR)
                else:
                    # Leadership chat: Use MESSAGE_PROCESSOR for list_team_members_and_players
                    return available_agents.get(AgentRole.MESSAGE_PROCESSOR)
        
        # Intent-based selection with context awareness
        if intent == 'help_request':
            return available_agents.get(AgentRole.HELP_ASSISTANT) or available_agents.get(AgentRole.MESSAGE_PROCESSOR)
        elif intent == 'status_request':
            return available_agents.get(AgentRole.PLAYER_COORDINATOR) or available_agents.get(AgentRole.MESSAGE_PROCESSOR)
        elif intent == 'list_request':
            if chat_type == 'main_chat':
                # Main chat: Use PLAYER_COORDINATOR for get_active_players
                return available_agents.get(AgentRole.PLAYER_COORDINATOR) or available_agents.get(AgentRole.MESSAGE_PROCESSOR)
            else:
                # Leadership chat: Use MESSAGE_PROCESSOR for list_team_members_and_players
                return available_agents.get(AgentRole.MESSAGE_PROCESSOR)
        elif intent == 'creation_request':
            if chat_type == 'main_chat':
                # Registration not available in main chat
                return available_agents.get(AgentRole.MESSAGE_PROCESSOR)
            return available_agents.get(AgentRole.ONBOARDING_AGENT) or available_agents.get(AgentRole.PLAYER_COORDINATOR)
        elif intent == 'approval_request':
            if chat_type == 'main_chat':
                # Approval not available in main chat
                return available_agents.get(AgentRole.MESSAGE_PROCESSOR)
            return available_agents.get(AgentRole.PLAYER_COORDINATOR)
        
        # Default to message processor
        return available_agents.get(AgentRole.MESSAGE_PROCESSOR)


class TaskExecutionStep(PipelineStep):
    """Step for task execution with agent output validation."""

    def get_step_name(self) -> str:
        return "Task Execution"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute a task using the selected agent."""
        try:
            task_description = context.get('task_description', '')
            logger.info(f"🚀 [TASK EXECUTION] Executing task: {task_description[:100]}...")
            
            # Get the selected agent
            agent = self._get_selected_agent(context)
            if not agent:
                logger.error("❌ [TASK EXECUTION] No agent selected for task execution")
                return {
                    **context,
                    'execution_result': "Unable to execute task: No suitable agent available."
                }
            
            logger.info(f"🤖 [TASK EXECUTION] Using agent: {agent.role}")
            
            # Validate context using Pydantic models
            execution_context = context.get('execution_context', {})
            if not validate_context_data(execution_context, 'base'):
                logger.error(f"❌ [TASK EXECUTION] Context validation failed for execution context")
                return {
                    **context,
                    'execution_result': "Context validation failed: missing required fields (team_id, user_id)"
                }
            
            # Extract context data for the agent
            # The execution_context might contain a complex security_context object
            # We need to extract the individual parameters that tools need
            agent_context = self._extract_agent_context(execution_context)
            
            # Execute the task with the agent
            agent_result = await agent.execute(task_description, agent_context)
            
            # Capture tool outputs from the execution context
            # For now, we'll use a simplified approach since CrewAI doesn't expose tool outputs directly
            # In a production system, you might want to implement a custom callback or monitor
            tool_outputs = self._extract_tool_outputs_from_execution(agent_result, context)
            
            # Validate the agent output
            validated_result = await self._validate_agent_output(agent_result, {'tool_outputs': tool_outputs})
            
            logger.info(f"✅ [TASK EXECUTION] Task completed successfully")
            return {
                **context,
                'execution_result': validated_result,
                'tool_outputs': tool_outputs
            }
            
        except Exception as e:
            logger.error(f"❌ [TASK EXECUTION] Task execution failed: {e}")
            return {
                **context,
                'execution_result': f"Task execution failed: {str(e)}"
            }

    def _get_selected_agent(self, context: dict) -> Any:
        """Get the selected agent from the context."""
        if not context:
            return None
        
        # Get the selected agent from the context
        selected_agent = context.get('selected_agent')
        if not selected_agent:
            logger.warning("No agent selected in context")
            return None
        
        return selected_agent

    def _extract_agent_context(self, execution_context: dict) -> dict:
        """Extract relevant context data for the agent from the execution_context."""
        try:
            # Extract all relevant context parameters from the execution_context
            # The execution_context might contain a security_context object
            team_id = None
            user_id = None
            chat_type = None
            telegram_username = None
            telegram_name = None
            
            # Try to extract from security_context if it exists
            if 'security_context' in execution_context:
                security_context = execution_context['security_context']
                if isinstance(security_context, dict):
                    team_id = security_context.get('team_id')
                    user_id = security_context.get('user_id')
                    chat_type = security_context.get('chat_type')
                    telegram_username = security_context.get('telegram_username')
                    telegram_name = security_context.get('telegram_name')
            
            # If not found in security_context, try direct extraction
            if not team_id:
                team_id = execution_context.get('team_id')
            if not user_id:
                user_id = execution_context.get('user_id')
            if not chat_type:
                chat_type = execution_context.get('chat_type')
            if not telegram_username:
                telegram_username = execution_context.get('telegram_username')
            if not telegram_name:
                telegram_name = execution_context.get('telegram_name')
            
            # Create a clean context dictionary with all the needed parameters
            agent_context = {}
            if team_id:
                agent_context['team_id'] = str(team_id)
            if user_id:
                agent_context['user_id'] = str(user_id)
            if chat_type:
                agent_context['chat_type'] = str(chat_type)
            if telegram_username:
                agent_context['telegram_username'] = str(telegram_username)
            if telegram_name:
                agent_context['telegram_name'] = str(telegram_name)
            
            logger.info(f"🔍 [TASK EXECUTION] Extracted context: team_id={team_id}, user_id={user_id}, chat_type={chat_type}, telegram_username={telegram_username}")
            return agent_context
            
        except Exception as e:
            logger.error(f"❌ [TASK EXECUTION] Failed to extract agent context: {e}")
            return {}

    def _extract_tool_outputs_from_execution(self, agent_result: Any, context: dict) -> dict:
        """Extract tool outputs from agent execution result using CrewAI's native tools_results."""
        tool_outputs = {}
        
        # Use CrewAI's native tools_results if available
        if hasattr(agent_result, 'tools_results') and agent_result.tools_results:
            for tool_result in agent_result.tools_results:
                if isinstance(tool_result, dict) and 'tool' in tool_result and 'result' in tool_result:
                    tool_name = tool_result['tool']
                    tool_output = tool_result['result']
                    tool_outputs[tool_name] = tool_output
                    logger.debug(f"🔍 [TASK EXECUTION] Captured {tool_name} output from CrewAI tools_results")
        
        # Add any context-based tool outputs
        if context and 'tool_outputs' in context:
            tool_outputs.update(context['tool_outputs'])
        
        logger.debug(f"🔍 [TASK EXECUTION] Final tool outputs: {list(tool_outputs.keys())}")
        return tool_outputs
    
    async def _validate_agent_output(self, agent_result: Any, context: dict) -> str:
        """Convert agent result to string using CrewAI native approach."""
        try:
            # Convert agent_result to string for response
            if hasattr(agent_result, 'raw') and hasattr(agent_result.raw, 'output'):
                # Handle CrewOutput objects
                result_text = str(agent_result.raw.output)
            elif hasattr(agent_result, 'output'):
                # Handle objects with output attribute
                result_text = str(agent_result.output)
            elif hasattr(agent_result, 'result'):
                # Handle objects with result attribute
                result_text = str(agent_result.result)
            elif isinstance(agent_result, str):
                # Already a string
                result_text = agent_result
            else:
                # Fallback: convert to string
                result_text = str(agent_result)
            
            # Log tool usage for analytics (optional)
            tool_outputs = self._extract_tool_outputs_from_execution(agent_result, context)
            if tool_outputs:
                logger.debug(f"🔧 [VALIDATION] Tools used: {list(tool_outputs.keys())}")
            else:
                logger.debug(f"🔧 [VALIDATION] No tools used - agent provided direct response")
            
            # Return the result - CrewAI handles validation natively
            return result_text
            
        except Exception as e:
            logger.error(f"Agent output processing failed: {e}")
            # Return the original result as string
            if hasattr(agent_result, 'raw') and hasattr(agent_result.raw, 'output'):
                return str(agent_result.raw.output)
            elif hasattr(agent_result, 'output'):
                return str(agent_result.output)
            elif hasattr(agent_result, 'result'):
                return str(agent_result.result)
            else:
                return str(agent_result)

    def _generate_safe_response(self, tool_outputs: dict, context: dict) -> str:
        """Generate a simple response based on tool outputs."""
        try:
            # Get the first available tool output
            for tool_name, output in tool_outputs.items():
                if isinstance(output, str) and output.strip():
                    return output
            
            return "No tool data available"
            
        except Exception as e:
            logger.error(f"Error generating safe response: {e}")
            return "Unable to generate response due to error."


class SimplifiedOrchestrationPipeline:
    """
    Simplified 3-step orchestration pipeline for better performance.
    
    Steps:
    1. Intent Classification - Determine what the user wants
    2. Agent Selection - Choose the best agent for the task
    3. Task Execution - Execute the task with error handling
    """

    def __init__(self, llm=None):
        """Initialize the simplified orchestration pipeline."""
        self.llm = llm
        self.steps = [
            IntentClassificationStep(),
            AgentSelectionStep(),
            TaskExecutionStep()
        ]
        
        # Analytics tracking
        self.pipeline_analytics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'agent_usage': {},  # Track which agents are used
            'tool_usage': {},   # Track which tools are used
            'step_executions': {} # Track executions per step
        }
        
        # Tool usage monitoring
        self.tool_monitor = {
            'get_active_players': {'main_chat': 0, 'leadership_chat': 0},
            'get_all_players': {'main_chat': 0, 'leadership_chat': 0},
            'get_my_status': {'main_chat': 0, 'leadership_chat': 0}
        }
        
        logger.info("🚀 SimplifiedOrchestrationPipeline initialized with 3-step pipeline")

    def get_pipeline_analytics(self) -> dict[str, Any]:
        """Get pipeline performance analytics."""
        return {
            'pipeline_type': 'SimplifiedOrchestrationPipeline',
            'total_executions': self.pipeline_analytics['total_executions'],
            'successful_executions': self.pipeline_analytics['successful_executions'],
            'failed_executions': self.pipeline_analytics['failed_executions'],
            'success_rate': (
                self.pipeline_analytics['successful_executions'] / 
                max(self.pipeline_analytics['total_executions'], 1)
            ) * 100,
            'steps': [step.get_step_name() for step in self.steps]
        }

    def get_pipeline_status(self) -> dict[str, Any]:
        """Get the status of the orchestration pipeline."""
        return {
            'orchestration_pipeline': 'SimplifiedOrchestrationPipeline',
            'steps_count': len(self.steps),
            'steps': [step.get_step_name() for step in self.steps],
            'llm_available': self.llm is not None,
            'status': 'ready'
        }

    async def execute_task(self, task_description: str, execution_context: dict[str, Any], available_agents: dict[str, Any] = None) -> str:
        """Execute a task through the simplified orchestration pipeline."""
        try:
            # Initialize context
            context = {
                'task_description': task_description,
                'execution_context': execution_context,
                'available_agents': available_agents or {},
                'tool_outputs': {},  # Track tool outputs for validation
                'pipeline_steps': []
            }

            logger.info(f"🚀 [SIMPLIFIED ORCHESTRATION] Starting pipeline execution for: {task_description[:50]}...")

            # Execute pipeline steps
            for step in self.steps:
                try:
                    logger.info(f"📋 [SIMPLIFIED ORCHESTRATION] Executing step: {step.get_step_name()}")
                    
                    # Execute step
                    step_result = await step.execute(context)
                    context.update(step_result)
                    
                    # Track step execution for analytics
                    step_name = step.get_step_name()
                    if step_name not in self.pipeline_analytics['step_executions']:
                        self.pipeline_analytics['step_executions'][step_name] = 0
                    self.pipeline_analytics['step_executions'][step_name] += 1
                    
                    # Track agent usage if available
                    if 'agent_usage_key' in step_result:
                        agent_key = step_result['agent_usage_key']
                        if agent_key not in self.pipeline_analytics['agent_usage']:
                            self.pipeline_analytics['agent_usage'][agent_key] = 0
                        self.pipeline_analytics['agent_usage'][agent_key] += 1
                    
                    # Track tool outputs if available
                    if 'tool_outputs' in step_result:
                        context['tool_outputs'].update(step_result['tool_outputs'])
                    
                    logger.info(f"✅ [SIMPLIFIED ORCHESTRATION] Step {step.get_step_name()} completed")
                    
                except Exception as e:
                    logger.error(f"❌ [SIMPLIFIED ORCHESTRATION] Step {step.get_step_name()} failed: {e}")
                    context['error'] = str(e)
                    break

            # Generate final response
            return self._generate_final_response(context)

        except Exception as e:
            logger.error(f"❌ [SIMPLIFIED ORCHESTRATION] Pipeline execution failed: {e}")
            self.pipeline_analytics['failed_executions'] += 1
            return f"❌ Error: Sorry, I encountered an error while processing your request: {e!s}"
    
    def _generate_final_response(self, context: dict) -> str:
        """Generate the final response from the pipeline context."""
        # Update analytics
        self.pipeline_analytics['total_executions'] += 1
        
        if context.get('error'):
            self.pipeline_analytics['failed_executions'] += 1
            logger.error(f"❌ [SIMPLIFIED ORCHESTRATION] Pipeline execution failed: {context['error']}")
            return f"❌ Error: Sorry, I encountered an error while processing your request: {context['error']}"
        else:
            self.pipeline_analytics['successful_executions'] += 1

            # Extract the final result
            final_result = context.get('execution_result')

            if final_result is None:
                final_result = "❌ Error: Sorry, I'm unable to process your request at the moment. Please try again."

            logger.info("✅ [SIMPLIFIED ORCHESTRATION] Pipeline execution completed successfully")
            return final_result
