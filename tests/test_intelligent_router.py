#!/usr/bin/env python3
"""
Unit tests for intelligent router system.
"""

import unittest
import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.intelligent_router import IntelligentAgentRouter, RoutingDecision, RequestContext
from src.agent_capabilities import CapabilityType

class MockLLM:
    """Mock LLM for testing."""
    
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.call_count = 0
    
    async def ainvoke(self, prompt):
        self.call_count += 1
        
        # Return different responses based on prompt content
        if "complexity" in prompt.lower():
            return '{"complexity": 7, "intent": "team_management", "reasoning": "Test reasoning", "entities": [], "urgency": "normal", "estimated_agents_needed": 2}'
        elif "capability" in prompt.lower():
            return '["intent_analysis", "coordination"]'
        else:
            return '{"complexity": 5, "intent": "general_query", "reasoning": "Default reasoning", "entities": [], "urgency": "normal", "estimated_agents_needed": 1}'

class TestIntelligentRouter(unittest.TestCase):
    """Test cases for intelligent router system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_agents = {
            'message_processor': Mock(),
            'team_manager': Mock(),
            'player_coordinator': Mock(),
            'match_analyst': Mock(),
            'communication_specialist': Mock(),
            'finance_manager': Mock(),
            'squad_selection_specialist': Mock(),
            'analytics_specialist': Mock()
        }
        
        self.mock_llm = MockLLM()
        self.router = IntelligentAgentRouter(self.mock_agents, self.mock_llm)
        
        self.test_context = RequestContext(
            user_id="test_user",
            team_id="test_team",
            message="Test message",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
    
    def test_router_initialization(self):
        """Test that router initializes correctly."""
        self.assertIsNotNone(self.router)
        self.assertEqual(len(self.router.agents), 8)
        self.assertIsNotNone(self.router.capability_matrix)
        self.assertEqual(len(self.router.routing_history), 0)
        self.assertIsInstance(self.router.performance_metrics, dict)
    
    def test_analysis_prompt_creation(self):
        """Test that analysis prompts are created correctly."""
        prompt = self.router._create_analysis_prompt("Test message", self.test_context)
        
        self.assertIsInstance(prompt, str)
        self.assertIn("Test message", prompt)
        self.assertIn("test_user", prompt)
        self.assertIn("test_team", prompt)
        self.assertIn("complexity", prompt.lower())
    
    def test_analysis_response_parsing(self):
        """Test parsing of LLM analysis responses."""
        # Test valid JSON response
        valid_response = '{"complexity": 8, "intent": "player_management", "reasoning": "Test", "entities": [], "urgency": "high", "estimated_agents_needed": 3}'
        result = self.router._parse_analysis_response(valid_response)
        
        self.assertEqual(result['complexity'], 8.0)
        self.assertEqual(result['intent'], 'player_management')
        self.assertEqual(result['urgency'], 'high')
        self.assertEqual(result['estimated_agents_needed'], 3)
        
        # Test invalid response
        invalid_response = "Invalid response"
        result = self.router._parse_analysis_response(invalid_response)
        
        self.assertEqual(result['complexity'], 5.0)
        self.assertEqual(result['intent'], 'general_query')
    
    def test_capabilities_parsing(self):
        """Test parsing of capabilities from LLM response."""
        # Test valid capabilities response
        valid_response = '["intent_analysis", "coordination", "player_management"]'
        capabilities = self.router._parse_capabilities_response(valid_response)
        
        self.assertIn('intent_analysis', capabilities)
        self.assertIn('coordination', capabilities)
        self.assertIn('player_management', capabilities)
        
        # Test invalid response
        invalid_response = "Invalid capabilities"
        capabilities = self.router._parse_capabilities_response(invalid_response)
        
        self.assertEqual(capabilities, ['intent_analysis'])
    
    def test_agent_prioritization(self):
        """Test agent prioritization based on capabilities."""
        agents = ['message_processor', 'team_manager', 'player_coordinator']
        capabilities = ['intent_analysis', 'coordination']
        
        prioritized = self.router._prioritize_agents(agents, capabilities)
        
        self.assertIsInstance(prioritized, list)
        self.assertEqual(len(prioritized), 3)
        self.assertIn('message_processor', prioritized)
        self.assertIn('team_manager', prioritized)
        self.assertIn('player_coordinator', prioritized)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        selected_agents = ['message_processor', 'team_manager']
        required_capabilities = ['intent_analysis', 'coordination']
        
        confidence = self.router._calculate_confidence(selected_agents, required_capabilities)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_execution_time_estimation(self):
        """Test execution time estimation."""
        selected_agents = ['message_processor', 'team_manager']
        complexity = 7.0
        
        estimated_time = self.router._estimate_execution_time(selected_agents, complexity)
        
        self.assertIsInstance(estimated_time, int)
        self.assertGreater(estimated_time, 0)
    
    def test_performance_metrics_update(self):
        """Test performance metrics updating."""
        decision = RoutingDecision(
            selected_agents=['message_processor'],
            complexity_score=6.0,
            reasoning="Test",
            estimated_time=5,
            required_capabilities=['intent_analysis'],
            confidence_score=0.8,
            timestamp=datetime.now()
        )
        
        start_time = datetime.now()
        self.router._update_performance_metrics(decision, start_time)
        
        self.assertEqual(self.router.performance_metrics['total_requests'], 1)
        self.assertGreater(self.router.performance_metrics['avg_routing_time'], 0)
    
    def test_routing_decision_logging(self):
        """Test routing decision logging."""
        decision = RoutingDecision(
            selected_agents=['message_processor'],
            complexity_score=5.0,
            reasoning="Test reasoning",
            estimated_time=3,
            required_capabilities=['intent_analysis'],
            confidence_score=0.7,
            timestamp=datetime.now()
        )
        
        self.router._log_routing_decision(decision, "Test message")
        
        self.assertEqual(len(self.router.routing_history), 1)
        log_entry = self.router.routing_history[0]
        self.assertEqual(log_entry['selected_agents'], ['message_processor'])
        self.assertEqual(log_entry['complexity_score'], 5.0)
    
    def test_routing_analytics(self):
        """Test routing analytics generation."""
        # Add some test data
        decision = RoutingDecision(
            selected_agents=['message_processor'],
            complexity_score=6.0,
            reasoning="Test",
            estimated_time=4,
            required_capabilities=['intent_analysis'],
            confidence_score=0.8,
            timestamp=datetime.now()
        )
        
        start_time = datetime.now()
        self.router._update_performance_metrics(decision, start_time)
        self.router._log_routing_decision(decision, "Test message")
        
        analytics = self.router.get_routing_analytics()
        
        self.assertIn('total_decisions', analytics)
        self.assertIn('average_complexity', analytics)
        self.assertIn('average_confidence', analytics)
        self.assertIn('success_rate', analytics)
        self.assertIn('agent_usage', analytics)
        self.assertIn('capability_usage', analytics)
    
    def test_performance_metrics(self):
        """Test performance metrics retrieval."""
        metrics = self.router.get_performance_metrics()
        
        self.assertIn('total_requests', metrics)
        self.assertIn('successful_routes', metrics)
        self.assertIn('avg_routing_time', metrics)
        self.assertIn('complexity_distribution', metrics)
    
    @patch('src.intelligent_router.IntelligentAgentRouter._analyze_request')
    @patch('src.intelligent_router.IntelligentAgentRouter._determine_required_capabilities')
    @patch('src.intelligent_router.IntelligentAgentRouter._select_optimal_agents')
    async def test_full_routing_flow(self, mock_select_agents, mock_determine_capabilities, mock_analyze):
        """Test the full routing flow."""
        # Mock the analysis steps
        mock_analyze.return_value = {
            'complexity': 7.0,
            'intent': 'team_management',
            'reasoning': 'Test reasoning',
            'entities': [],
            'urgency': 'normal',
            'estimated_agents_needed': 2
        }
        
        mock_determine_capabilities.return_value = ['intent_analysis', 'coordination']
        mock_select_agents.return_value = ['message_processor', 'team_manager']
        
        # Test routing
        decision = await self.router.route_request("Test message", self.test_context)
        
        # Verify the decision
        self.assertIsInstance(decision, RoutingDecision)
        self.assertEqual(decision.selected_agents, ['message_processor', 'team_manager'])
        self.assertEqual(decision.complexity_score, 7.0)
        self.assertIn('intent_analysis', decision.required_capabilities)
        self.assertIn('coordination', decision.required_capabilities)
        
        # Verify mocks were called
        mock_analyze.assert_called_once()
        mock_determine_capabilities.assert_called_once()
        mock_select_agents.assert_called_once()

class TestIntelligentRouterIntegration(unittest.TestCase):
    """Integration tests for intelligent router."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_agents = {
            'message_processor': Mock(),
            'team_manager': Mock(),
            'player_coordinator': Mock(),
            'match_analyst': Mock(),
            'communication_specialist': Mock(),
            'finance_manager': Mock(),
            'squad_selection_specialist': Mock(),
            'analytics_specialist': Mock()
        }
        
        self.mock_llm = MockLLM()
        self.router = IntelligentAgentRouter(self.mock_agents, self.mock_llm)
    
    async def test_player_management_request(self):
        """Test routing for player management requests."""
        context = RequestContext(
            user_id="test_user",
            team_id="test_team",
            message="Add player John Doe with phone 123456789",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
        
        decision = await self.router.route_request(context.message, context)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertGreater(len(decision.selected_agents), 0)
        self.assertGreater(decision.confidence_score, 0)
    
    async def test_complex_coordination_request(self):
        """Test routing for complex coordination requests."""
        context = RequestContext(
            user_id="test_user",
            team_id="test_team",
            message="Create a match against Arsenal and notify the team about availability",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
        
        decision = await self.router.route_request(context.message, context)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertGreater(len(decision.selected_agents), 1)  # Should require multiple agents
        self.assertGreater(decision.complexity_score, 5.0)  # Should be complex
    
    async def test_simple_query_request(self):
        """Test routing for simple query requests."""
        context = RequestContext(
            user_id="test_user",
            team_id="test_team",
            message="What's our next match?",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
        
        decision = await self.router.route_request(context.message, context)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertLessEqual(len(decision.selected_agents), 2)  # Should require few agents
        self.assertLess(decision.complexity_score, 7.0)  # Should be relatively simple

class TestIntelligentRouterErrorHandling(unittest.TestCase):
    """Test error handling in intelligent router."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_agents = {
            'message_processor': Mock(),
            'team_manager': Mock()
        }
        
        self.mock_llm = MockLLM()
        self.router = IntelligentAgentRouter(self.mock_agents, self.mock_llm)
    
    async def test_llm_error_handling(self):
        """Test handling of LLM errors."""
        # Create a mock LLM that raises an exception
        error_llm = Mock()
        error_llm.ainvoke = AsyncMock(side_effect=Exception("LLM Error"))
        
        router = IntelligentAgentRouter(self.mock_agents, error_llm)
        
        context = RequestContext(
            user_id="test_user",
            team_id="test_team",
            message="Test message",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
        
        # Should not raise an exception
        decision = await router.route_request(context.message, context)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertEqual(decision.reasoning, "Fallback routing due to error")
    
    async def test_no_agents_available(self):
        """Test handling when no agents are available."""
        # Create router with no agents
        empty_router = IntelligentAgentRouter({}, self.mock_llm)
        
        context = RequestContext(
            user_id="test_user",
            team_id="test_team",
            message="Test message",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
        
        # Should use fallback routing
        decision = await empty_router.route_request(context.message, context)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertEqual(decision.reasoning, "Fallback routing due to error")

def run_async_test(coro):
    """Helper function to run async tests."""
    return asyncio.run(coro)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 