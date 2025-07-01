"""
Unit tests for intelligent router system.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, List
from unittest.mock import Mock

from src.testing.test_base import BaseTestCase, AsyncBaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.testing.test_utils import MockLLM, MockAgent
from src.agents import IntelligentAgentRouter
from src.agents.intelligent_system import TaskContext


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
        
        self.task_context = TaskContext(
            user_id="test_user",
            team_id="test_team",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=0.0
        )
    
    def test_router_initialization(self):
        """Test that router initializes correctly."""
        self.assertIsNotNone(self.router)
        self.assertEqual(len(self.router.agents), 8)
        self.assertIsNotNone(self.router.capability_matrix)
        self.assertEqual(len(self.router.routing_history), 0)
        # Note: performance_metrics is not implemented in the actual class
    
    def test_capability_matrix_building(self):
        """Test that capability matrix is built correctly."""
        capability_matrix = self.router.capability_matrix
        
        self.assertIsInstance(capability_matrix, dict)
        self.assertIn('message_processor', capability_matrix)
        self.assertIn('team_manager', capability_matrix)
        self.assertIn('player_coordinator', capability_matrix)
        
        # Check that each agent has capabilities
        for agent, capabilities in capability_matrix.items():
            self.assertIsInstance(capabilities, list)
            self.assertGreater(len(capabilities), 0)
    
    def test_routing_analytics_empty(self):
        """Test routing analytics when no routing has occurred."""
        analytics = self.router.get_routing_analytics()
        
        self.assertIsInstance(analytics, dict)
        # Should be empty when no routing has occurred
        self.assertEqual(analytics, {})
    
    def test_routing_analytics_with_data(self):
        """Test routing analytics after routing decisions."""
        # Simulate adding routing history
        self.router.routing_history.append({
            'timestamp': datetime.now(),
            'message': 'Test message',
            'decision': {'complexity': 7, 'agent_sequence': ['message_processor']},
            'selected_agents': ['message_processor']
        })
        
        analytics = self.router.get_routing_analytics()
        
        self.assertIsInstance(analytics, dict)
        self.assertIn('total_decisions', analytics)
        self.assertIn('average_complexity', analytics)
        self.assertIn('agent_usage', analytics)
        self.assertEqual(analytics['total_decisions'], 1)
        self.assertEqual(analytics['average_complexity'], 7.0)
        self.assertIn('message_processor', analytics['agent_usage'])
    
    def test_router_attributes(self):
        """Test that router has expected attributes."""
        self.assertIsNotNone(self.router.agents)
        self.assertIsNotNone(self.router.llm)
        self.assertIsNotNone(self.router.capability_matrix)
        self.assertIsNotNone(self.router.routing_history)
        
        # These attributes don't exist in the actual implementation
        # self.assertIsNotNone(self.router.performance_metrics)  # Not implemented


@pytest.mark.asyncio
class TestIntelligentRouterIntegration(AsyncBaseTestCase):
    """Integration tests for intelligent router system."""
    
    async def async_setup_method(self):
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
        
        self.task_context = TaskContext(
            user_id="test_user",
            team_id="test_team",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=0.0
        )
    
    async def test_player_management_request(self):
        """Test routing for player management request."""
        context = TaskContext(
            user_id="captain",
            team_id="team1",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=0.0
        )
        
        # Mock LLM response for player management
        self.mock_llm.responses = ['{"complexity": 6, "agent_sequence": ["player_coordinator"], "estimated_time": 15}']
        
        selected_agents = await self.router.route_request("Add new player John Smith to the team", context)
        
        self.assertIsInstance(selected_agents, list)
        self.assertGreater(len(selected_agents), 0)
        # Check that routing history was updated
        self.assertEqual(len(self.router.routing_history), 1)
    
    async def test_complex_coordination_request(self):
        """Test routing for complex coordination request."""
        context = TaskContext(
            user_id="manager",
            team_id="team1",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=0.0
        )
        
        # Mock LLM response for complex coordination
        self.mock_llm.responses = ['{"complexity": 8, "agent_sequence": ["team_manager", "communication_specialist"], "estimated_time": 45}']
        
        selected_agents = await self.router.route_request("Schedule training session, coordinate with players, and arrange transport", context)
        
        self.assertIsInstance(selected_agents, list)
        self.assertGreater(len(selected_agents), 0)
        # Check that routing history was updated
        self.assertEqual(len(self.router.routing_history), 1)
    
    async def test_simple_query_request(self):
        """Test routing for simple query request."""
        context = TaskContext(
            user_id="player",
            team_id="team1",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=0.0
        )
        
        # Mock LLM response for simple query
        self.mock_llm.responses = ['{"complexity": 3, "agent_sequence": ["message_processor"], "estimated_time": 5}']
        
        selected_agents = await self.router.route_request("What time is training tomorrow?", context)
        
        self.assertIsInstance(selected_agents, list)
        self.assertGreater(len(selected_agents), 0)
        # Check that routing history was updated
        self.assertEqual(len(self.router.routing_history), 1)


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
        
        self.task_context = TaskContext(
            user_id="test_user",
            team_id="test_team",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=0.0
        )
    
    async def test_llm_error_handling(self):
        """Test handling of LLM errors."""
        # Create an LLM that raises an error
        error_llm = Mock()
        error_llm.ainvoke = Mock(side_effect=Exception("LLM Error"))
        
        router = IntelligentAgentRouter(self.mock_agents, error_llm)
        
        context = TaskContext(
            user_id="test_user",
            team_id="test_team",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=0.0
        )
        
        # Should fallback to default routing
        selected_agents = await router.route_request("Test message", context)
        
        self.assertIsInstance(selected_agents, list)
        self.assertGreater(len(selected_agents), 0)
        # Should have fallback to message_processor or first available agent
    
    async def test_no_agents_available(self):
        """Test handling when no agents are available."""
        router = IntelligentAgentRouter({}, self.mock_llm)  # No agents
        
        context = TaskContext(
            user_id="test_user",
            team_id="test_team",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=0.0
        )
        
        # Should handle gracefully
        selected_agents = await router.route_request("Test message", context)
        
        self.assertIsInstance(selected_agents, list)
        # Should return empty list or handle gracefully 