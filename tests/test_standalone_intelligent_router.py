"""
Unit tests for StandaloneIntelligentRouter (LLM-powered routing).
"""

import pytest
import asyncio
from datetime import datetime

from src.testing.test_base import AsyncBaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.testing.test_utils import MockLLM, MockAgent
from src.agents import StandaloneIntelligentRouter, RoutingDecision, RequestContext


@pytest.mark.asyncio
class TestStandaloneIntelligentRouter(AsyncBaseTestCase):
    """Test cases for StandaloneIntelligentRouter."""
    
    async def async_setup_method(self):
        """Set up test fixtures."""
        self.mock_agents = {
            'message_processor': self.create_mock_agent('message_processor'),
            'team_manager': self.create_mock_agent('team_manager'),
            'player_coordinator': self.create_mock_agent('player_coordinator'),
            'match_analyst': self.create_mock_agent('match_analyst'),
            'finance_manager': self.create_mock_agent('finance_manager'),
        }
        self.llm = self.create_mock_llm()
        self.router = StandaloneIntelligentRouter(self.mock_agents, self.llm)
        self.team_id = 'test_team'
        self.user_id = 'test_user'
    
    async def test_player_management_routing(self):
        """Test routing for player management requests."""
        ctx = RequestContext(self.user_id, self.team_id, 'Add a new player', [], {}, {})
        decision = await self.router.route_request('Add a new player', ctx)
        
        self.assertIn('player_coordinator', decision.selected_agents)
        self.assertGreaterEqual(decision.confidence_score, 0)
        self.assertLessEqual(decision.confidence_score, 1)
        self.assertEqual(decision.reasoning, 'Player management intent')
    
    async def test_match_scheduling_routing(self):
        """Test routing for match scheduling requests."""
        ctx = RequestContext(self.user_id, self.team_id, 'Schedule a match against Arsenal', [], {}, {})
        decision = await self.router.route_request('Schedule a match against Arsenal', ctx)
        
        self.assertTrue(any(agent in decision.selected_agents for agent in ['team_manager', 'match_analyst']))
        self.assertGreaterEqual(decision.complexity_score, 0)
        self.assertLessEqual(decision.complexity_score, 10)
    
    async def test_finance_routing(self):
        """Test routing for finance requests."""
        ctx = RequestContext(self.user_id, self.team_id, 'Send a payment reminder', [], {}, {})
        decision = await self.router.route_request('Send a payment reminder', ctx)
        
        self.assertIn('finance_manager', decision.selected_agents)
        self.assertEqual(decision.reasoning, 'Finance intent')
    
    async def test_fallback_routing(self):
        """Test fallback routing for unknown requests."""
        ctx = RequestContext(self.user_id, self.team_id, 'What is the weather?', [], {}, {})
        decision = await self.router.route_request('What is the weather?', ctx)
        
        self.assertIn('message_processor', decision.selected_agents)
        self.assertEqual(decision.reasoning, 'Fallback intent')
    
    async def test_routing_decision_structure(self):
        """Test that routing decisions have the correct structure."""
        ctx = RequestContext(self.user_id, self.team_id, 'Add a new player', [], {}, {})
        decision = await self.router.route_request('Add a new player', ctx)
        
        self.assertIsInstance(decision, RoutingDecision)
        self.assertIsInstance(decision.selected_agents, list)
        self.assertIsInstance(decision.complexity_score, float)
        self.assertIsInstance(decision.reasoning, str)
        self.assertIsInstance(decision.estimated_time, int)
        self.assertIsInstance(decision.required_capabilities, list)
        self.assertIsInstance(decision.confidence_score, float)
        self.assertIsInstance(decision.timestamp, datetime) 