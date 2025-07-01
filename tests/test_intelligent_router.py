"""
Unit tests for intelligent router system.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, List

from src.testing.test_base import BaseTestCase, AsyncBaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.testing.test_utils import MockLLM, MockAgent
from src.agents import IntelligentAgentRouter, RoutingDecision, RequestContext
from src.agents import CapabilityType


class TestIntelligentRouter(BaseTestCase):
    """Test cases for intelligent router system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_agents = {
            'message_processor': self.create_mock_agent('message_processor'),
            'team_manager': self.create_mock_agent('team_manager'),
            'player_coordinator': self.create_mock_agent('player_coordinator'),
            'match_analyst': self.create_mock_agent('match_analyst'),
            'communication_specialist': self.create_mock_agent('communication_specialist'),
            'finance_manager': self.create_mock_agent('finance_manager'),
            'squad_selection_specialist': self.create_mock_agent('squad_selection_specialist'),
            'analytics_specialist': self.create_mock_agent('analytics_specialist')
        }
        
        self.mock_llm = self.create_mock_llm()
        self.router = IntelligentAgentRouter(self.mock_agents, self.mock_llm)
        
        self.request_context = RequestContext(
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
        prompt = self.router._create_analysis_prompt("Test message", self.request_context)
        
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
        
        self.router._log_routing_decision(decision, "Test message")
        
        analytics = self.router.get_routing_analytics()
        
        self.assertIsInstance(analytics, dict)
        self.assertIn('total_decisions', analytics)
        self.assertIn('average_complexity', analytics)
        self.assertIn('agent_usage', analytics)
        self.assertEqual(analytics['total_decisions'], 1)


@pytest.mark.asyncio
class TestIntelligentRouterIntegration(AsyncBaseTestCase):
    """Integration tests for intelligent router system."""
    
    async def async_setup_method(self):
        """Set up test fixtures."""
        self.mock_agents = {
            'message_processor': self.create_mock_agent('message_processor'),
            'team_manager': self.create_mock_agent('team_manager'),
            'player_coordinator': self.create_mock_agent('player_coordinator'),
            'match_analyst': self.create_mock_agent('match_analyst')
        }
        
        self.mock_llm = self.create_mock_llm()
        self.router = IntelligentAgentRouter(self.mock_agents, self.mock_llm)
        
        self.request_context = RequestContext(
            user_id="test_user",
            team_id="test_team",
            message="Test message",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
    
    async def test_player_management_request(self):
        """Test routing for player management request."""
        context = RequestContext(
            user_id="captain",
            team_id="team1",
            message="Add new player John Smith to the team",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
        
        decision = await self.router.route_request(context.message, context)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertIsInstance(decision.selected_agents, list)
        self.assertGreater(len(decision.selected_agents), 0)
        self.assertGreater(decision.confidence_score, 0.0)
    
    async def test_complex_coordination_request(self):
        """Test routing for complex coordination request."""
        context = RequestContext(
            user_id="manager",
            team_id="team1",
            message="Schedule training session, coordinate with players, and arrange transport",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
        
        decision = await self.router.route_request(context.message, context)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertGreater(len(decision.selected_agents), 1)  # Should require multiple agents
        self.assertGreater(decision.complexity_score, 5.0)
    
    async def test_simple_query_request(self):
        """Test routing for simple query request."""
        context = RequestContext(
            user_id="player",
            team_id="team1",
            message="What time is training tomorrow?",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
        
        decision = await self.router.route_request(context.message, context)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertLessEqual(len(decision.selected_agents), 2)  # Should require few agents
        self.assertLess(decision.complexity_score, 5.0)


@pytest.mark.asyncio
class TestIntelligentRouterErrorHandling(AsyncBaseTestCase):
    """Error handling tests for intelligent router system."""
    
    async def async_setup_method(self):
        """Set up test fixtures."""
        self.mock_agents = {
            'message_processor': self.create_mock_agent('message_processor'),
            'team_manager': self.create_mock_agent('team_manager')
        }
        
        self.mock_llm = self.create_mock_llm()
        self.router = IntelligentAgentRouter(self.mock_agents, self.mock_llm)
    
    async def test_llm_error_handling(self):
        """Test handling of LLM errors."""
        # Create a mock LLM that raises an exception
        error_llm = MockLLM()
        error_llm.invoke = lambda *args, **kwargs: (_ for _ in ()).throw(Exception("LLM Error"))
        
        router = IntelligentAgentRouter(self.mock_agents, error_llm)
        
        context = RequestContext(
            user_id="test_user",
            team_id="test_team",
            message="Test message",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
        
        # Should handle the error gracefully
        decision = await router.route_request(context.message, context)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertEqual(decision.complexity_score, 5.0)  # Default fallback
    
    async def test_no_agents_available(self):
        """Test handling when no agents are available."""
        router = IntelligentAgentRouter({}, self.mock_llm)  # No agents
        
        context = RequestContext(
            user_id="test_user",
            team_id="test_team",
            message="Test message",
            conversation_history=[],
            user_preferences={},
            team_patterns={}
        )
        
        # Should handle gracefully
        decision = await router.route_request(context.message, context)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertEqual(len(decision.selected_agents), 0)
        self.assertEqual(decision.confidence_score, 0.0) 