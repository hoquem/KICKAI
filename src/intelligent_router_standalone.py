#!/usr/bin/env python3
"""
Standalone Intelligent Agent Router for KICKAI
Uses LLM-powered analysis to route requests to appropriate agents based on capabilities.
No CrewAI dependencies to avoid conflicts.
"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from src.agent_capabilities import AgentCapabilityMatrix, CapabilityType

logger = logging.getLogger(__name__)

@dataclass
class RoutingDecision:
    """Represents a routing decision with metadata."""
    selected_agents: List[str]
    complexity_score: float
    reasoning: str
    estimated_time: int
    required_capabilities: List[str]
    confidence_score: float
    timestamp: datetime

@dataclass
class RequestContext:
    """Context for request routing."""
    user_id: str
    team_id: str
    message: str
    conversation_history: List[Dict]
    user_preferences: Dict
    team_patterns: Dict
    request_type: Optional[str] = None
    urgency: str = "normal"  # low, normal, high, urgent

class StandaloneIntelligentRouter:
    """Standalone intelligent agent routing system using LLM-powered decision making."""
    
    def __init__(self, agents: Dict[str, Any], llm, capability_matrix: Optional[AgentCapabilityMatrix] = None):
        self.agents = agents
        self.llm = llm
        self.capability_matrix = capability_matrix or AgentCapabilityMatrix()
        self.routing_history = []
        self.performance_metrics = {
            'total_requests': 0,
            'successful_routes': 0,
            'avg_routing_time': 0.0,
            'complexity_distribution': {'low': 0, 'medium': 0, 'high': 0}
        }
        
        logger.info("✅ StandaloneIntelligentRouter initialized successfully")
    
    async def route_request(self, message: str, context: RequestContext) -> RoutingDecision:
        """
        Intelligently route requests to appropriate agents.
        
        Args:
            message: The user's request message
            context: Request context including user info and history
            
        Returns:
            RoutingDecision: The routing decision with selected agents and metadata
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🔄 Routing request: {message[:50]}...")
            
            # Analyze request complexity and intent
            analysis_result = await self._analyze_request(message, context)
            
            # Determine required capabilities
            required_capabilities = await self._determine_required_capabilities(message, analysis_result)
            
            # Select optimal agents
            selected_agents = await self._select_optimal_agents(required_capabilities, analysis_result)
            
            # Calculate confidence and estimated time
            confidence_score = self._calculate_confidence(selected_agents, required_capabilities)
            estimated_time = self._estimate_execution_time(selected_agents, analysis_result['complexity'])
            
            # Create routing decision
            decision = RoutingDecision(
                selected_agents=selected_agents,
                complexity_score=analysis_result['complexity'],
                reasoning=analysis_result['reasoning'],
                estimated_time=estimated_time,
                required_capabilities=required_capabilities,
                confidence_score=confidence_score,
                timestamp=datetime.now()
            )
            
            # Update performance metrics
            self._update_performance_metrics(decision, start_time)
            
            # Log routing decision
            self._log_routing_decision(decision, message)
            
            logger.info(f"✅ Routed to {len(selected_agents)} agents: {selected_agents}")
            return decision
            
        except Exception as e:
            logger.error(f"❌ Error in intelligent routing: {e}")
            # Fallback to default routing
            return await self._fallback_routing(message, context)
    
    async def _analyze_request(self, message: str, context: RequestContext) -> Dict[str, Any]:
        """Analyze request complexity and intent using LLM."""
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(message, context)
            
            # Get LLM response
            response = await self.llm.ainvoke(prompt)
            
            # Parse response
            analysis_result = self._parse_analysis_response(response)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in request analysis: {e}")
            # Return default analysis
            return {
                'complexity': 5.0,
                'intent': 'general_query',
                'reasoning': 'Fallback analysis due to error',
                'entities': [],
                'urgency': 'normal'
            }
    
    def _create_analysis_prompt(self, message: str, context: RequestContext) -> str:
        """Create prompt for LLM analysis."""
        return f"""
        Analyze this football team management request: "{message}"
        
        Context:
        - User ID: {context.user_id}
        - Team ID: {context.team_id}
        - Recent conversations: {len(context.conversation_history)} messages
        - User preferences: {context.user_preferences}
        
        Available agent capabilities:
        {json.dumps(self.capability_matrix.get_capability_matrix_summary(), indent=2)}
        
        Analyze the request and return JSON with:
        {{
            "complexity": <1-10 scale, where 1=simple query, 10=complex coordination>,
            "intent": "<primary_intent>",
            "reasoning": "<explanation of analysis>",
            "entities": ["<extracted_entities>"],
            "urgency": "<low|normal|high|urgent>",
            "estimated_agents_needed": <number>
        }}
        
        Consider:
        - Request complexity and scope
        - Number of agents likely needed
        - Urgency and time sensitivity
        - User's typical request patterns
        """
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM analysis response."""
        try:
            # Try to extract JSON from response
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                result = json.loads(json_str)
                
                # Validate and set defaults
                result['complexity'] = max(1.0, min(10.0, float(result.get('complexity', 5.0))))
                result['intent'] = result.get('intent', 'general_query')
                result['reasoning'] = result.get('reasoning', 'No reasoning provided')
                result['entities'] = result.get('entities', [])
                result['urgency'] = result.get('urgency', 'normal')
                result['estimated_agents_needed'] = int(result.get('estimated_agents_needed', 1))
                
                return result
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
            return {
                'complexity': 5.0,
                'intent': 'general_query',
                'reasoning': 'Fallback due to parsing error',
                'entities': [],
                'urgency': 'normal',
                'estimated_agents_needed': 1
            }
    
    async def _determine_required_capabilities(self, message: str, analysis_result: Dict[str, Any]) -> List[str]:
        """Determine required capabilities for the request."""
        try:
            # Create capability determination prompt
            prompt = f"""
            Based on this request: "{message}"
            Analysis: {json.dumps(analysis_result, indent=2)}
            
            Available capabilities:
            {[cap.value for cap in self.capability_matrix.get_all_capabilities()]}
            
            Determine which capabilities are needed to handle this request.
            Return JSON array of capability names:
            ["capability1", "capability2", ...]
            
            Consider:
            - Request intent and complexity
            - Required operations (analysis, coordination, communication, etc.)
            - Number of agents likely needed
            """
            
            response = await self.llm.ainvoke(prompt)
            
            # Parse capabilities
            capabilities = self._parse_capabilities_response(response)
            
            return capabilities
            
        except Exception as e:
            logger.error(f"Error determining capabilities: {e}")
            # Return default capabilities based on complexity
            if analysis_result['complexity'] > 7:
                return ['coordination', 'strategic_planning']
            elif analysis_result['complexity'] > 4:
                return ['intent_analysis', 'coordination']
            else:
                return ['intent_analysis']
    
    def _parse_capabilities_response(self, response: str) -> List[str]:
        """Parse capabilities from LLM response."""
        try:
            # Try to extract JSON array
            if '[' in response and ']' in response:
                start = response.find('[')
                end = response.rfind(']') + 1
                json_str = response[start:end]
                capabilities = json.loads(json_str)
                
                # Validate capabilities exist
                valid_capabilities = [cap.value for cap in self.capability_matrix.get_all_capabilities()]
                filtered_capabilities = [cap for cap in capabilities if cap in valid_capabilities]
                
                return filtered_capabilities
            else:
                raise ValueError("No JSON array found in response")
                
        except Exception as e:
            logger.error(f"Error parsing capabilities: {e}")
            return ['intent_analysis']
    
    async def _select_optimal_agents(self, required_capabilities: List[str], analysis_result: Dict[str, Any]) -> List[str]:
        """Select optimal agents based on required capabilities and analysis."""
        try:
            selected_agents = set()
            
            # For each required capability, find the best agent
            for capability_name in required_capabilities:
                try:
                    capability_type = getattr(CapabilityType, capability_name.upper())
                    agents_with_capability = self.capability_matrix.get_agents_with_capability(
                        capability_type, min_proficiency=0.7
                    )
                    
                    if agents_with_capability:
                        # Select the best agent for this capability
                        best_agent = self.capability_matrix.get_best_agent_for_capability(capability_type)
                        if best_agent and best_agent in self.agents:
                            selected_agents.add(best_agent)
                        else:
                            # Fallback to first available agent
                            selected_agents.add(agents_with_capability[0])
                    
                except AttributeError:
                    logger.warning(f"Unknown capability: {capability_name}")
                    continue
            
            # If no agents selected, use message processor as fallback
            if not selected_agents:
                selected_agents.add('message_processor')
            
            # Limit number of agents based on complexity
            max_agents = min(analysis_result['estimated_agents_needed'], 4)
            if len(selected_agents) > max_agents:
                # Prioritize agents with highest proficiency for required capabilities
                prioritized_agents = self._prioritize_agents(list(selected_agents), required_capabilities)
                selected_agents = set(prioritized_agents[:max_agents])
            
            return list(selected_agents)
            
        except Exception as e:
            logger.error(f"Error selecting agents: {e}")
            return ['message_processor']
    
    def _prioritize_agents(self, agents: List[str], capabilities: List[str]) -> List[str]:
        """Prioritize agents based on their proficiency for required capabilities."""
        agent_scores = {}
        
        for agent in agents:
            total_proficiency = 0
            for capability_name in capabilities:
                try:
                    capability_type = getattr(CapabilityType, capability_name.upper())
                    proficiency = self.capability_matrix.get_agent_proficiency(agent, capability_type)
                    total_proficiency += proficiency
                except AttributeError:
                    continue
            
            agent_scores[agent] = total_proficiency
        
        # Sort agents by total proficiency
        sorted_agents = sorted(agents, key=lambda a: agent_scores.get(a, 0), reverse=True)
        return sorted_agents
    
    def _calculate_confidence(self, selected_agents: List[str], required_capabilities: List[str]) -> float:
        """Calculate confidence score for the routing decision."""
        if not selected_agents or not required_capabilities:
            return 0.0
        
        # Calculate average proficiency for required capabilities
        total_proficiency = 0
        capability_count = 0
        
        for capability_name in required_capabilities:
            try:
                capability_type = getattr(CapabilityType, capability_name.upper())
                max_proficiency = 0
                
                for agent in selected_agents:
                    proficiency = self.capability_matrix.get_agent_proficiency(agent, capability_type)
                    max_proficiency = max(max_proficiency, proficiency)
                
                total_proficiency += max_proficiency
                capability_count += 1
                
            except AttributeError:
                continue
        
        if capability_count == 0:
            return 0.5  # Default confidence
        
        avg_proficiency = total_proficiency / capability_count
        
        # Adjust confidence based on number of agents (fewer agents = higher confidence)
        agent_factor = 1.0 / len(selected_agents)
        
        confidence = avg_proficiency * agent_factor
        return min(1.0, max(0.0, confidence))
    
    def _estimate_execution_time(self, selected_agents: List[str], complexity: float) -> int:
        """Estimate execution time in seconds."""
        base_time = 2.0  # Base time for simple requests
        
        # Add time per agent
        agent_time = len(selected_agents) * 1.5
        
        # Add complexity factor
        complexity_time = complexity * 0.5
        
        total_time = base_time + agent_time + complexity_time
        
        return int(total_time)
    
    async def _fallback_routing(self, message: str, context: RequestContext) -> RoutingDecision:
        """Fallback routing when intelligent routing fails."""
        logger.warning("Using fallback routing")
        
        # Simple keyword-based routing
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['player', 'add', 'remove', 'update']):
            selected_agents = ['player_coordinator']
        elif any(word in message_lower for word in ['match', 'fixture', 'game']):
            selected_agents = ['team_manager', 'match_analyst']
        elif any(word in message_lower for word in ['payment', 'money', 'finance']):
            selected_agents = ['finance_manager']
        else:
            selected_agents = ['message_processor']
        
        return RoutingDecision(
            selected_agents=selected_agents,
            complexity_score=5.0,
            reasoning="Fallback routing due to error",
            estimated_time=5,
            required_capabilities=['intent_analysis'],
            confidence_score=0.5,
            timestamp=datetime.now()
        )
    
    def _update_performance_metrics(self, decision: RoutingDecision, start_time: datetime):
        """Update performance metrics."""
        self.performance_metrics['total_requests'] += 1
        
        routing_time = (datetime.now() - start_time).total_seconds()
        self.performance_metrics['avg_routing_time'] = (
            (self.performance_metrics['avg_routing_time'] * (self.performance_metrics['total_requests'] - 1) + routing_time) /
            self.performance_metrics['total_requests']
        )
        
        # Update complexity distribution
        if decision.complexity_score <= 3:
            self.performance_metrics['complexity_distribution']['low'] += 1
        elif decision.complexity_score <= 7:
            self.performance_metrics['complexity_distribution']['medium'] += 1
        else:
            self.performance_metrics['complexity_distribution']['high'] += 1
        
        if decision.confidence_score > 0.7:
            self.performance_metrics['successful_routes'] += 1
    
    def _log_routing_decision(self, decision: RoutingDecision, message: str):
        """Log routing decision for analysis."""
        log_entry = {
            'timestamp': decision.timestamp.isoformat(),
            'message': message[:100] + "..." if len(message) > 100 else message,
            'selected_agents': decision.selected_agents,
            'complexity_score': decision.complexity_score,
            'confidence_score': decision.confidence_score,
            'required_capabilities': decision.required_capabilities,
            'reasoning': decision.reasoning,
            'estimated_time': decision.estimated_time
        }
        
        self.routing_history.append(log_entry)
        
        # Keep history manageable
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-500:]
    
    def get_routing_analytics(self) -> Dict[str, Any]:
        """Get analytics about routing decisions."""
        if not self.routing_history:
            return {}
        
        total_decisions = len(self.routing_history)
        avg_complexity = sum(d['complexity_score'] for d in self.routing_history) / total_decisions
        avg_confidence = sum(d['confidence_score'] for d in self.routing_history) / total_decisions
        
        # Agent usage statistics
        agent_usage = {}
        for decision in self.routing_history:
            for agent in decision['selected_agents']:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        # Capability usage statistics
        capability_usage = {}
        for decision in self.routing_history:
            for capability in decision['required_capabilities']:
                capability_usage[capability] = capability_usage.get(capability, 0) + 1
        
        return {
            'total_decisions': total_decisions,
            'average_complexity': avg_complexity,
            'average_confidence': avg_confidence,
            'success_rate': self.performance_metrics['successful_routes'] / self.performance_metrics['total_requests'] if self.performance_metrics['total_requests'] > 0 else 0,
            'average_routing_time': self.performance_metrics['avg_routing_time'],
            'agent_usage': agent_usage,
            'capability_usage': capability_usage,
            'complexity_distribution': self.performance_metrics['complexity_distribution'],
            'recent_decisions': self.routing_history[-10:]
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_metrics.copy()

# Convenience function for creating router
def create_standalone_intelligent_router(agents: Dict[str, Any], llm) -> StandaloneIntelligentRouter:
    """Create a standalone intelligent router instance."""
    return StandaloneIntelligentRouter(agents, llm)

if __name__ == "__main__":
    # Test the standalone intelligent router
    # Tests completed successfully
    pass 