#!/usr/bin/env python3
"""
Improved Agentic System for KICKAI
Implements intelligent routing, dynamic task decomposition, and advanced communication protocols.
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommunicationType(Enum):
    """Types of agent communication protocols."""
    DELEGATION = "delegation"
    COLLABORATION = "collaboration"
    NEGOTIATION = "negotiation"
    CONSENSUS = "consensus"
    CONFLICT_RESOLUTION = "conflict_resolution"

@dataclass
class AgentCapability:
    """Represents an agent's capabilities."""
    agent_name: str
    capabilities: List[str]
    performance_score: float
    response_time_avg: float
    success_rate: float

@dataclass
class TaskContext:
    """Context for task execution."""
    user_id: str
    team_id: str
    conversation_history: List[Dict]
    user_preferences: Dict
    team_patterns: Dict
    complexity_score: float

class IntelligentAgentRouter:
    """Intelligent agent routing system using LLM-powered decision making."""
    
    def __init__(self, agents: Dict[str, Agent], llm):
        self.agents = agents
        self.llm = llm
        self.capability_matrix = self._build_capability_matrix()
        self.routing_history = []
        
    def _build_capability_matrix(self) -> Dict[str, List[str]]:
        """Build a matrix of agent capabilities based on tools and roles."""
        return {
            'message_processor': ['intent_analysis', 'context_management', 'routing', 'natural_language_understanding'],
            'team_manager': ['strategic_planning', 'coordination', 'decision_making', 'high_level_operations'],
            'player_coordinator': ['player_management', 'availability_tracking', 'communication', 'operational_tasks'],
            'match_analyst': ['performance_analysis', 'tactical_insights', 'opposition_analysis', 'match_planning'],
            'communication_specialist': ['messaging', 'announcements', 'polls', 'broadcast_management'],
            'finance_manager': ['payment_tracking', 'financial_reporting', 'reminders', 'budget_management'],
            'squad_selection_specialist': ['squad_selection', 'form_analysis', 'tactical_fit', 'player_evaluation'],
            'analytics_specialist': ['trend_analysis', 'performance_metrics', 'predictions', 'data_analysis']
        }
    
    async def route_request(self, message: str, context: TaskContext) -> List[Agent]:
        """Intelligently route requests to appropriate agents."""
        try:
            # Analyze request complexity and intent
            analysis_prompt = f"""
            Analyze this request: "{message}"
            Context: User ID: {context.user_id}, Team ID: {context.team_id}
            Recent conversations: {context.conversation_history[-3:] if context.conversation_history else 'None'}
            
            Available agents and capabilities: {json.dumps(self.capability_matrix, indent=2)}
            
            Determine:
            1. Request complexity (1-10 scale)
            2. Required capabilities
            3. Optimal agent sequence
            4. Expected execution time
            
            Return JSON format:
            {{
                "complexity": 7,
                "required_capabilities": ["player_management", "communication"],
                "agent_sequence": ["player_coordinator", "communication_specialist"],
                "estimated_time": 30,
                "reasoning": "Request involves player operations and team communication"
            }}
            """
            
            response = await self.llm.ainvoke(analysis_prompt)
            routing_decision = json.loads(response)
            
            # Update context with complexity score
            context.complexity_score = routing_decision.get('complexity', 5)
            
            # Get agent sequence
            agent_sequence = routing_decision.get('agent_sequence', [])
            selected_agents = [self.agents[agent_name] for agent_name in agent_sequence if agent_name in self.agents]
            
            # Log routing decision
            self.routing_history.append({
                'timestamp': datetime.now(),
                'message': message,
                'decision': routing_decision,
                'selected_agents': agent_sequence
            })
            
            logger.info(f"Intelligent routing: {len(selected_agents)} agents selected for complexity {context.complexity_score}")
            return selected_agents
            
        except Exception as e:
            logger.error(f"Error in intelligent routing: {e}")
            # Fallback to default routing
            return [self.agents.get('message_processor', list(self.agents.values())[0])]
    
    def get_routing_analytics(self) -> Dict:
        """Get analytics about routing decisions."""
        if not self.routing_history:
            return {}
        
        total_decisions = len(self.routing_history)
        avg_complexity = sum(d['decision'].get('complexity', 5) for d in self.routing_history) / total_decisions
        agent_usage = {}
        
        for decision in self.routing_history:
            for agent in decision['selected_agents']:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        return {
            'total_decisions': total_decisions,
            'average_complexity': avg_complexity,
            'agent_usage': agent_usage,
            'recent_decisions': self.routing_history[-10:]
        }

class DynamicTaskDecomposer:
    """Dynamic task decomposition system."""
    
    def __init__(self, llm):
        self.llm = llm
        self.task_templates = self._load_task_templates()
        
    def _load_task_templates(self) -> Dict[str, Dict]:
        """Load predefined task templates."""
        return {
            'intent_analysis': {
                'description': "Analyze the intent and entities in the request: '{request}'",
                'expected_output': "JSON with intent, entities, complexity score, and required actions",
                'agent_type': 'message_processor'
            },
            'player_management': {
                'description': "Handle player-related operations: {operation} for player: {player_info}",
                'expected_output': "Confirmation of player operation completion",
                'agent_type': 'player_coordinator'
            },
            'fixture_management': {
                'description': "Manage fixture: {operation} for fixture: {fixture_info}",
                'expected_output': "Confirmation of fixture operation completion",
                'agent_type': 'team_manager'
            },
            'communication': {
                'description': "Send communication: {message_type} to team with content: {content}",
                'expected_output': "Confirmation of message sent",
                'agent_type': 'communication_specialist'
            },
            'analysis': {
                'description': "Perform analysis: {analysis_type} with data: {data}",
                'expected_output': "Analysis results and recommendations",
                'agent_type': 'match_analyst'
            },
            'coordination': {
                'description': "Coordinate multiple operations: {operations}",
                'expected_output': "Coordinated response from all operations",
                'agent_type': 'team_manager'
            }
        }
    
    async def decompose_request(self, request: str, agents: List[Agent], context: TaskContext) -> List[Task]:
        """Decompose complex requests into atomic tasks."""
        try:
            # First, analyze the request to understand what tasks are needed
            analysis_prompt = f"""
            Analyze this request: "{request}"
            Context: {json.dumps(context.__dict__, default=str)}
            
            Available task templates: {list(self.task_templates.keys())}
            
            Determine which tasks are needed and in what order.
            Return JSON format:
            {{
                "tasks": [
                    {{
                        "template": "intent_analysis",
                        "parameters": {{"request": "original request"}},
                        "dependencies": []
                    }},
                    {{
                        "template": "player_management",
                        "parameters": {{"operation": "add", "player_info": "details"}},
                        "dependencies": ["intent_analysis"]
                    }}
                ]
            }}
            """
            
            response = await self.llm.ainvoke(analysis_prompt)
            task_plan = json.loads(response)
            
            # Create tasks based on the plan
            tasks = []
            task_map = {}
            
            for task_info in task_plan.get('tasks', []):
                template_name = task_info['template']
                parameters = task_info['parameters']
                dependencies = task_info.get('dependencies', [])
                
                if template_name in self.task_templates:
                    template = self.task_templates[template_name]
                    
                    # Find appropriate agent
                    agent = self._find_agent_by_type(agents, template['agent_type'])
                    
                    # Create task
                    task = Task(
                        description=template['description'].format(**parameters),
                        expected_output=template['expected_output'],
                        agent=agent,
                        context={
                            'template': template_name,
                            'parameters': parameters,
                            'dependencies': dependencies,
                            'context': context
                        }
                    )
                    
                    tasks.append(task)
                    task_map[template_name] = task
            
            logger.info(f"Decomposed request into {len(tasks)} tasks")
            return tasks
            
        except Exception as e:
            logger.error(f"Error in task decomposition: {e}")
            # Fallback to simple task
            fallback_task = Task(
                description=f"Handle request: {request}",
                expected_output="Response to user request",
                agent=agents[0] if agents else None
            )
            return [fallback_task]
    
    def _find_agent_by_type(self, agents: List[Agent], agent_type: str) -> Optional[Agent]:
        """Find agent by type."""
        for agent in agents:
            if agent_type in agent.role.lower():
                return agent
        return agents[0] if agents else None

class AgentCommunicationProtocol:
    """Advanced agent communication protocols."""
    
    def __init__(self, llm):
        self.llm = llm
        self.communication_history = []
        
    async def handle_delegation(self, from_agent: Agent, to_agent: Agent, task: Task, context: TaskContext) -> Dict:
        """Handle task delegation between agents."""
        try:
            delegation_message = {
                'type': CommunicationType.DELEGATION.value,
                'from': from_agent.role,
                'to': to_agent.role,
                'task': task.description,
                'context': context.__dict__,
                'timestamp': datetime.now(),
                'priority': 'high' if context.complexity_score > 7 else 'normal'
            }
            
            # Execute delegated task
            start_time = datetime.now()
            result = await self._execute_task_safely(to_agent, task)
            end_time = datetime.now()
            
            # Record communication
            self.communication_history.append({
                **delegation_message,
                'result': result,
                'execution_time': (end_time - start_time).total_seconds(),
                'success': result is not None
            })
            
            return {
                'type': 'delegation_result',
                'from': to_agent.role,
                'to': from_agent.role,
                'result': result,
                'success': result is not None,
                'execution_time': (end_time - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error in delegation: {e}")
            return {
                'type': 'delegation_error',
                'error': str(e),
                'success': False
            }
    
    async def handle_collaboration(self, agents: List[Agent], shared_task: Task, context: TaskContext) -> Dict:
        """Handle collaborative tasks requiring multiple agents."""
        try:
            collaboration_message = {
                'type': CommunicationType.COLLABORATION.value,
                'agents': [agent.role for agent in agents],
                'task': shared_task.description,
                'timestamp': datetime.now()
            }
            
            # Create shared workspace
            workspace = SharedWorkspace(agents, shared_task, self.llm)
            results = await workspace.execute_collaboratively(context)
            
            # Record collaboration
            self.communication_history.append({
                **collaboration_message,
                'results': results,
                'success': all(r.get('success', False) for r in results)
            })
            
            return {
                'type': 'collaboration_result',
                'results': results,
                'success': all(r.get('success', False) for r in results)
            }
            
        except Exception as e:
            logger.error(f"Error in collaboration: {e}")
            return {
                'type': 'collaboration_error',
                'error': str(e),
                'success': False
            }
    
    async def handle_negotiation(self, agents: List[Agent], conflict: Dict, context: TaskContext) -> Dict:
        """Handle conflicts between agents through negotiation."""
        try:
            negotiation_rounds = []
            
            for round_num in range(3):  # Max 3 rounds
                proposals = []
                for agent in agents:
                    proposal = await self._generate_proposal(agent, conflict, negotiation_rounds, context)
                    proposals.append(proposal)
                
                # Check for consensus
                if self._check_consensus(proposals):
                    return {
                        'type': 'negotiation_success',
                        'rounds': round_num + 1,
                        'final_proposal': self._select_best_proposal(proposals),
                        'consensus_reached': True
                    }
                
                negotiation_rounds.append(proposals)
            
            # If no consensus, escalate to human
            return {
                'type': 'negotiation_escalation',
                'rounds': 3,
                'final_proposals': negotiation_rounds[-1],
                'consensus_reached': False,
                'escalation_reason': 'No consensus after 3 rounds'
            }
            
        except Exception as e:
            logger.error(f"Error in negotiation: {e}")
            return {
                'type': 'negotiation_error',
                'error': str(e),
                'success': False
            }
    
    async def _execute_task_safely(self, agent: Agent, task: Task) -> Optional[str]:
        """Execute a task safely with error handling."""
        try:
            result = await task.execute()
            return str(result) if result else None
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            return None
    
    async def _generate_proposal(self, agent: Agent, conflict: Dict, previous_rounds: List, context: TaskContext) -> Dict:
        """Generate a proposal for conflict resolution."""
        prompt = f"""
        Agent: {agent.role}
        Conflict: {json.dumps(conflict)}
        Previous rounds: {json.dumps(previous_rounds)}
        Context: {json.dumps(context.__dict__, default=str)}
        
        Generate a proposal to resolve this conflict. Consider your role and expertise.
        Return JSON format:
        {{
            "proposal": "description of solution",
            "reasoning": "why this solution works",
            "confidence": 0.8,
            "trade_offs": ["list of trade-offs"]
        }}
        """
        
        response = await self.llm.ainvoke(prompt)
        return json.loads(response)
    
    def _check_consensus(self, proposals: List[Dict]) -> bool:
        """Check if proposals have reached consensus."""
        if len(proposals) < 2:
            return True
        
        # Simple consensus check - can be improved
        main_ideas = [p.get('proposal', '')[:50] for p in proposals]
        return len(set(main_ideas)) <= 1
    
    def _select_best_proposal(self, proposals: List[Dict]) -> Dict:
        """Select the best proposal based on confidence and reasoning."""
        if not proposals:
            return {}
        
        # Sort by confidence score
        sorted_proposals = sorted(proposals, key=lambda x: x.get('confidence', 0), reverse=True)
        return sorted_proposals[0]

class SharedWorkspace:
    """Shared workspace for collaborative tasks."""
    
    def __init__(self, agents: List[Agent], shared_task: Task, llm):
        self.agents = agents
        self.shared_task = shared_task
        self.llm = llm
        self.shared_data = {}
        
    async def execute_collaboratively(self, context: TaskContext) -> List[Dict]:
        """Execute task collaboratively with all agents."""
        results = []
        
        # Break down shared task into agent-specific subtasks
        subtasks = await self._create_subtasks(context)
        
        # Execute subtasks in parallel where possible
        tasks = []
        for agent, subtask in subtasks:
            task = asyncio.create_task(self._execute_agent_subtask(agent, subtask, context))
            tasks.append(task)
        
        # Wait for all tasks to complete
        agent_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(agent_results):
            if isinstance(result, Exception):
                results.append({
                    'agent': self.agents[i].role,
                    'success': False,
                    'error': str(result)
                })
            else:
                results.append({
                    'agent': self.agents[i].role,
                    'success': True,
                    'result': result
                })
        
        # Synthesize final result
        final_result = await self._synthesize_results(results, context)
        results.append({
            'agent': 'synthesis',
            'success': True,
            'result': final_result
        })
        
        return results
    
    async def _create_subtasks(self, context: TaskContext) -> List[Tuple[Agent, Task]]:
        """Create agent-specific subtasks."""
        subtasks = []
        
        for agent in self.agents:
            # Create subtask based on agent's role
            subtask_description = f"""
            As {agent.role}, contribute to: {self.shared_task.description}
            
            Focus on your area of expertise and provide your perspective.
            Consider the context: {json.dumps(context.__dict__, default=str)}
            """
            
            subtask = Task(
                description=subtask_description,
                expected_output=f"Contribution from {agent.role}",
                agent=agent
            )
            
            subtasks.append((agent, subtask))
        
        return subtasks
    
    async def _execute_agent_subtask(self, agent: Agent, subtask: Task, context: TaskContext) -> str:
        """Execute a subtask for a specific agent."""
        try:
            result = await subtask.execute()
            return str(result) if result else "No result"
        except Exception as e:
            logger.error(f"Error in agent subtask: {e}")
            raise
    
    async def _synthesize_results(self, results: List[Dict], context: TaskContext) -> str:
        """Synthesize results from all agents."""
        successful_results = [r for r in results if r.get('success', False)]
        
        if not successful_results:
            return "No successful results to synthesize"
        
        synthesis_prompt = f"""
        Synthesize the following agent contributions into a coherent final response:
        
        {json.dumps(successful_results, indent=2)}
        
        Context: {json.dumps(context.__dict__, default=str)}
        
        Provide a comprehensive response that addresses all aspects of the original request.
        """
        
        try:
            synthesis = await self.llm.ainvoke(synthesis_prompt)
            return synthesis
        except Exception as e:
            logger.error(f"Error in synthesis: {e}")
            return "Error synthesizing results"

class AdvancedMemorySystem:
    """Advanced memory system with multiple memory types."""
    
    def __init__(self):
        self.short_term_memory = {}  # Conversation context
        self.long_term_memory = {}   # User preferences, team patterns
        self.episodic_memory = []    # Task execution history
        self.semantic_memory = {}    # Learned patterns and rules
        
    def store_conversation_context(self, user_id: str, message: str, response: str, agents_used: List[str], success: bool):
        """Store conversation with agent usage tracking."""
        context = {
            'timestamp': datetime.now(),
            'message': message,
            'response': response,
            'agents_used': agents_used,
            'success': success,
            'message_length': len(message),
            'response_length': len(response)
        }
        
        if user_id not in self.short_term_memory:
            self.short_term_memory[user_id] = []
        
        self.short_term_memory[user_id].append(context)
        
        # Keep only last 10 conversations per user
        if len(self.short_term_memory[user_id]) > 10:
            self.short_term_memory[user_id] = self.short_term_memory[user_id][-10:]
        
        # Store in episodic memory
        self.episodic_memory.append(context)
        
        # Keep episodic memory manageable
        if len(self.episodic_memory) > 1000:
            self.episodic_memory = self.episodic_memory[-500:]
    
    def get_relevant_context(self, user_id: str, current_message: str) -> TaskContext:
        """Retrieve relevant context for current message."""
        # Get recent conversations
        recent_context = self.short_term_memory.get(user_id, [])
        
        # Get user preferences
        user_preferences = self.long_term_memory.get(user_id, {})
        
        # Get team patterns (simplified)
        team_patterns = self._get_team_patterns(user_id)
        
        # Calculate complexity score based on message characteristics
        complexity_score = self._calculate_complexity_score(current_message, recent_context)
        
        return TaskContext(
            user_id=user_id,
            team_id=user_preferences.get('team_id', 'unknown'),
            conversation_history=recent_context,
            user_preferences=user_preferences,
            team_patterns=team_patterns,
            complexity_score=complexity_score
        )
    
    def _get_team_patterns(self, user_id: str) -> Dict:
        """Get team-specific patterns."""
        # Simplified implementation - can be enhanced with actual team analysis
        return {
            'preferred_communication_time': 'evening',
            'common_request_types': ['fixture_info', 'player_status'],
            'team_size': 'medium'
        }
    
    def _calculate_complexity_score(self, message: str, recent_context: List[Dict]) -> float:
        """Calculate complexity score for a message."""
        base_score = 5.0
        
        # Adjust based on message length
        if len(message) > 100:
            base_score += 2
        elif len(message) < 20:
            base_score -= 1
        
        # Adjust based on keywords
        complex_keywords = ['plan', 'coordinate', 'analyze', 'manage', 'organize', 'strategy']
        if any(keyword in message.lower() for keyword in complex_keywords):
            base_score += 2
        
        # Adjust based on recent context
        if recent_context:
            recent_complexity = sum(ctx.get('complexity_score', 5) for ctx in recent_context[-3:]) / 3
            base_score = (base_score + recent_complexity) / 2
        
        return min(max(base_score, 1.0), 10.0)
    
    def learn_from_interaction(self, interaction: Dict):
        """Learn from interactions to improve future performance."""
        user_id = interaction.get('user_id')
        if not user_id:
            return
        
        # Update user preferences
        if user_id not in self.long_term_memory:
            self.long_term_memory[user_id] = {}
        
        # Extract preferences from interaction
        preferences = {
            'preferred_response_length': 'medium',
            'preferred_communication_style': 'direct',
            'common_topics': interaction.get('topics', [])
        }
        
        self.long_term_memory[user_id].update(preferences)
        
        # Update semantic memory with patterns
        pattern_type = interaction.get('pattern_type', 'general')
        if pattern_type not in self.semantic_memory:
            self.semantic_memory[pattern_type] = []
        
        self.semantic_memory[pattern_type].append(interaction)

class ImprovedAgenticSystem:
    """Main improved agentic system that orchestrates all components."""
    
    def __init__(self, agents: Dict[str, Agent], llm):
        self.agents = agents
        self.llm = llm
        
        # Initialize components
        self.router = IntelligentAgentRouter(agents, llm)
        self.task_decomposer = DynamicTaskDecomposer(llm)
        self.communication_protocol = AgentCommunicationProtocol(llm)
        self.memory_system = AdvancedMemorySystem()
        self.performance_monitor = AgentPerformanceMonitor()
        
    async def process_request(self, message: str, user_id: str, team_id: str) -> str:
        """Process a user request using the improved agentic system."""
        try:
            start_time = datetime.now()
            
            # Get context from memory
            context = self.memory_system.get_relevant_context(user_id, message)
            context.team_id = team_id
            
            # Route request to appropriate agents
            selected_agents = await self.router.route_request(message, context)
            
            if not selected_agents:
                return "❌ No suitable agents found to handle your request."
            
            # Decompose request into tasks
            tasks = await self.task_decomposer.decompose_request(message, selected_agents, context)
            
            # Execute tasks based on complexity and dependencies
            if context.complexity_score > 7 and len(selected_agents) > 1:
                # Use collaboration for complex multi-agent tasks
                shared_task = Task(
                    description=f"Collaboratively handle: {message}",
                    expected_output="Comprehensive response from all agents",
                    agent=selected_agents[0]
                )
                
                result = await self.communication_protocol.handle_collaboration(
                    selected_agents, shared_task, context
                )
                
                final_response = result.get('results', [{}])[-1].get('result', 'No response')
                
            elif any(getattr(task, 'dependencies', None) for task in tasks):
                # If any task has dependencies, use dependency-based execution
                final_response = await self._execute_tasks_with_dependencies(tasks, context)
            else:
                # Use delegation for simpler tasks
                final_response = await self._execute_simple_delegation(selected_agents, tasks, context)
            
            # Store interaction in memory
            self.memory_system.store_conversation_context(
                user_id, message, final_response, 
                [agent.role for agent in selected_agents], True
            )
            
            # Track performance
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self.performance_monitor.track_execution(
                selected_agents, tasks, execution_time, True, context
            )
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error in improved agentic system: {e}")
            return f"❌ Sorry, I encountered an error: {str(e)}"
    
    async def _execute_simple_delegation(self, agents: List[Agent], tasks: List[Task], context: TaskContext) -> str:
        """Execute tasks using simple delegation."""
        if not tasks:
            return "No tasks to execute."
        
        # Execute tasks sequentially
        results = []
        for i, task in enumerate(tasks):
            if i < len(agents):
                agent = agents[i]
                result = await self.communication_protocol.handle_delegation(
                    agents[0], agent, task, context
                )
                results.append(result.get('result', 'No result'))
            else:
                # Use first agent for remaining tasks
                result = await self.communication_protocol.handle_delegation(
                    agents[0], agents[0], task, context
                )
                results.append(result.get('result', 'No result'))
        
        # Combine results
        if len(results) == 1:
            return results[0]
        else:
            return "\n\n".join([f"Step {i+1}: {result}" for i, result in enumerate(results)])
    
    async def _execute_tasks_with_dependencies(self, tasks, context):
        """Execute tasks in dependency order, running independent tasks in parallel."""
        # Build dependency graph
        task_map = {getattr(task, 'context', {}).get('template', str(i)): task for i, task in enumerate(tasks)}
        dependencies = defaultdict(set)
        dependents = defaultdict(set)
        for task in tasks:
            name = getattr(task, 'context', {}).get('template', None)
            if not name:
                continue
            for dep in getattr(task, 'context', {}).get('dependencies', []):
                dependencies[name].add(dep)
                dependents[dep].add(name)
        # Find tasks with no dependencies
        ready = deque([name for name in task_map if not dependencies[name]])
        completed = set()
        results = {}
        errors = {}
        logger.info(f"[DependencyExecution] Task order will respect dependencies: {dict(dependencies)}")
        while ready:
            # Run all ready tasks in parallel
            current_batch = list(ready)
            ready.clear()
            logger.info(f"[DependencyExecution] Executing tasks in parallel: {current_batch}")
            coros = [self._execute_single_task(task_map[name], context) for name in current_batch]
            batch_results = await asyncio.gather(*coros, return_exceptions=True)
            for name, result in zip(current_batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"[DependencyExecution] Task {name} failed: {result}")
                    errors[name] = str(result)
                else:
                    results[name] = result
                completed.add(name)
                # Mark dependents as ready if all their dependencies are done
                for dep in dependents[name]:
                    if dependencies[dep].issubset(completed):
                        ready.append(dep)
        # Compose final response
        if errors:
            logger.error(f"[DependencyExecution] Some tasks failed: {errors}")
        ordered_results = [results.get(name, f"[FAILED: {errors.get(name)}]") for name in task_map]
        return "\n\n".join([f"{name}: {res}" for name, res in zip(task_map, ordered_results)])

    async def _execute_single_task(self, task, context):
        """Execute a single task and return its result."""
        try:
            if hasattr(task, 'execute') and callable(task.execute):
                return await task.execute()
            else:
                return str(task)
        except Exception as e:
            logger.error(f"[DependencyExecution] Error executing task: {e}")
            raise
    
    def get_system_analytics(self) -> Dict:
        """Get comprehensive system analytics."""
        return {
            'routing_analytics': self.router.get_routing_analytics(),
            'performance_metrics': self.performance_monitor.get_metrics(),
            'memory_stats': {
                'short_term_users': len(self.memory_system.short_term_memory),
                'long_term_users': len(self.memory_system.long_term_memory),
                'episodic_entries': len(self.memory_system.episodic_memory),
                'semantic_patterns': len(self.memory_system.semantic_memory)
            },
            'communication_stats': {
                'total_communications': len(self.communication_protocol.communication_history),
                'successful_delegations': len([c for c in self.communication_protocol.communication_history 
                                             if c.get('type') == 'delegation' and c.get('success')]),
                'collaborations': len([c for c in self.communication_protocol.communication_history 
                                     if c.get('type') == 'collaboration'])
            }
        }

class AgentPerformanceMonitor:
    """Monitor and optimize agent performance."""
    
    def __init__(self):
        self.metrics = {
            'response_times': {},
            'success_rates': {},
            'agent_usage': {},
            'task_complexity': {},
            'execution_history': []
        }
    
    def track_execution(self, agents: List[Agent], tasks: List[Task], execution_time: float, success: bool, context: TaskContext):
        """Track execution metrics."""
        for agent in agents:
            agent_name = agent.role
            
            # Track response times
            if agent_name not in self.metrics['response_times']:
                self.metrics['response_times'][agent_name] = []
            self.metrics['response_times'][agent_name].append(execution_time / len(agents))
            
            # Track success rates
            if agent_name not in self.metrics['success_rates']:
                self.metrics['success_rates'][agent_name] = {'success': 0, 'total': 0}
            self.metrics['success_rates'][agent_name]['total'] += 1
            if success:
                self.metrics['success_rates'][agent_name]['success'] += 1
            
            # Track usage
            self.metrics['agent_usage'][agent_name] = self.metrics['agent_usage'].get(agent_name, 0) + 1
        
        # Track task complexity
        complexity = context.complexity_score
        if 'complexity_distribution' not in self.metrics['task_complexity']:
            self.metrics['task_complexity']['complexity_distribution'] = []
        self.metrics['task_complexity']['complexity_distribution'].append(complexity)
        
        # Store execution history
        self.metrics['execution_history'].append({
            'timestamp': datetime.now(),
            'agents': [agent.role for agent in agents],
            'tasks_count': len(tasks),
            'execution_time': execution_time,
            'success': success,
            'complexity': complexity
        })
        
        # Keep history manageable
        if len(self.metrics['execution_history']) > 1000:
            self.metrics['execution_history'] = self.metrics['execution_history'][-500:]
    
    def get_metrics(self) -> Dict:
        """Get performance metrics."""
        metrics = {}
        
        # Calculate average response times
        metrics['avg_response_times'] = {}
        for agent, times in self.metrics['response_times'].items():
            if times:
                metrics['avg_response_times'][agent] = sum(times) / len(times)
        
        # Calculate success rates
        metrics['success_rates'] = {}
        for agent, data in self.metrics['success_rates'].items():
            if data['total'] > 0:
                metrics['success_rates'][agent] = data['success'] / data['total']
        
        # Agent usage
        metrics['agent_usage'] = self.metrics['agent_usage']
        
        # Complexity distribution
        if self.metrics['task_complexity']['complexity_distribution']:
            complexities = self.metrics['task_complexity']['complexity_distribution']
            metrics['avg_complexity'] = sum(complexities) / len(complexities)
            metrics['complexity_distribution'] = {
                'low': len([c for c in complexities if c <= 3]),
                'medium': len([c for c in complexities if 3 < c <= 7]),
                'high': len([c for c in complexities if c > 7])
            }
        
        return metrics
    
    def suggest_optimizations(self) -> List[str]:
        """Suggest system optimizations."""
        suggestions = []
        metrics = self.get_metrics()
        
        # Check for slow agents
        for agent, avg_time in metrics.get('avg_response_times', {}).items():
            if avg_time > 10.0:
                suggestions.append(f"Agent {agent} is slow (avg: {avg_time:.2f}s). Consider optimization.")
        
        # Check for low success rates
        for agent, success_rate in metrics.get('success_rates', {}).items():
            if success_rate < 0.8:
                suggestions.append(f"Agent {agent} has low success rate ({success_rate:.2%}). Review configuration.")
        
        # Check for overused agents
        total_usage = sum(metrics.get('agent_usage', {}).values())
        if total_usage > 0:
            for agent, usage in metrics.get('agent_usage', {}).items():
                usage_percentage = usage / total_usage
                if usage_percentage > 0.5:
                    suggestions.append(f"Agent {agent} is overused ({usage_percentage:.1%}). Consider load balancing.")
        
        return suggestions

# Example usage
async def create_improved_agentic_system(agents: Dict[str, Agent], llm) -> ImprovedAgenticSystem:
    """Create an improved agentic system instance."""
    return ImprovedAgenticSystem(agents, llm)

if __name__ == "__main__":
    # Example usage
    print("🚀 Improved Agentic System for KICKAI")
    print("This module provides advanced agentic capabilities including:")
    print("- Intelligent agent routing")
    print("- Dynamic task decomposition")
    print("- Advanced communication protocols")
    print("- Sophisticated memory management")
    print("- Performance monitoring and optimization")
    print("\nTo use this system, import and create an ImprovedAgenticSystem instance.") 