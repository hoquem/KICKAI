#!/usr/bin/env python3
"""
Unit tests for StandaloneIntelligentRouter (LLM-powered routing).
"""
import unittest
import sys
import os
import asyncio
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from intelligent_router_standalone import StandaloneIntelligentRouter, RoutingDecision, RequestContext

class MockLLM:
    async def ainvoke(self, prompt):
        print(f"TEST MockLLM received prompt: {prompt[:100]}...")
        
        # Extract the actual request from the prompt
        request = ""
        if '"' in prompt:
            # Find the request in quotes
            start = prompt.find('"') + 1
            end = prompt.find('"', start)
            if end > start:
                request = prompt[start:end]
        
        print(f"TEST: Extracted request: '{request}'")
        
        # For capability determination prompts (contains "Available capabilities:" and "capability names")
        if 'Available capabilities:' in prompt and 'capability names' in prompt:
            print("TEST: Detected capability determination prompt")
            # Check for more specific keywords first
            if 'finance' in request.lower() or 'payment' in request.lower():
                response = '["payment_tracking", "financial_reporting"]'
                print("TEST: Returning finance capabilities")
            elif 'match' in request.lower() or 'fixture' in request.lower():
                response = '["strategic_planning", "coordination", "match_planning"]'
                print("TEST: Returning match capabilities")
            elif 'player' in request.lower():
                response = '["player_management", "operational_tasks"]'
                print("TEST: Returning player capabilities")
            else:
                response = '["intent_analysis"]'
                print("TEST: Returning default capabilities")
            print(f"TEST MockLLM returning: {response}")
            return response
        
        # For analysis prompts (contains "Available agent capabilities:")
        elif 'Available agent capabilities:' in prompt:
            print("TEST: Detected analysis prompt")
            # Check for more specific keywords first to avoid false matches from capability matrix
            if 'finance' in request.lower() or 'payment' in request.lower():
                response = '{"complexity": 5, "intent": "finance", "reasoning": "Finance intent", "entities": [], "urgency": "normal", "estimated_agents_needed": 1}'
                print("TEST: Returning finance analysis")
            elif 'match' in request.lower() or 'fixture' in request.lower():
                response = '{"complexity": 6, "intent": "match_scheduling", "reasoning": "Match scheduling intent", "entities": [], "urgency": "normal", "estimated_agents_needed": 2}'
                print("TEST: Returning match analysis")
            elif 'player' in request.lower():
                response = '{"complexity": 4, "intent": "player_management", "reasoning": "Player management intent", "entities": [], "urgency": "normal", "estimated_agents_needed": 1}'
                print("TEST: Returning player analysis")
            else:
                response = '{"complexity": 3, "intent": "general_query", "reasoning": "Fallback intent", "entities": [], "urgency": "normal", "estimated_agents_needed": 1}'
                print("TEST: Returning default analysis")
            print(f"TEST MockLLM returning: {response}")
            return response
        
        # Fallback for any other prompts
        else:
            print("TEST: Detected unknown prompt type")
            response = '{"complexity": 3, "intent": "general_query", "reasoning": "Fallback intent", "entities": [], "urgency": "normal", "estimated_agents_needed": 1}'
            print(f"TEST MockLLM returning: {response}")
            return response

class MockAgent:
    def __init__(self, name):
        self.name = name

class TestStandaloneIntelligentRouter(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_agents = {
            'message_processor': MockAgent('message_processor'),
            'team_manager': MockAgent('team_manager'),
            'player_coordinator': MockAgent('player_coordinator'),
            'match_analyst': MockAgent('match_analyst'),
            'finance_manager': MockAgent('finance_manager'),
        }
        self.llm = MockLLM()
        self.router = StandaloneIntelligentRouter(self.mock_agents, self.llm)
        self.team_id = 'test_team'
        self.user_id = 'test_user'

    async def test_player_management_routing(self):
        ctx = RequestContext(self.user_id, self.team_id, 'Add a new player', [], {}, {})
        decision = await self.router.route_request('Add a new player', ctx)
        self.assertIn('player_coordinator', decision.selected_agents)
        self.assertGreaterEqual(decision.confidence_score, 0)
        self.assertLessEqual(decision.confidence_score, 1)
        self.assertEqual(decision.reasoning, 'Player management intent')

    async def test_match_scheduling_routing(self):
        ctx = RequestContext(self.user_id, self.team_id, 'Schedule a match against Arsenal', [], {}, {})
        decision = await self.router.route_request('Schedule a match against Arsenal', ctx)
        self.assertTrue(any(agent in decision.selected_agents for agent in ['team_manager', 'match_analyst']))
        self.assertGreaterEqual(decision.complexity_score, 0)
        self.assertLessEqual(decision.complexity_score, 10)

    async def test_finance_routing(self):
        ctx = RequestContext(self.user_id, self.team_id, 'Send a payment reminder', [], {}, {})
        decision = await self.router.route_request('Send a payment reminder', ctx)
        self.assertIn('finance_manager', decision.selected_agents)
        self.assertEqual(decision.reasoning, 'Finance intent')

    async def test_fallback_routing(self):
        ctx = RequestContext(self.user_id, self.team_id, 'What is the weather?', [], {}, {})
        decision = await self.router.route_request('What is the weather?', ctx)
        self.assertIn('message_processor', decision.selected_agents)
        self.assertEqual(decision.reasoning, 'Fallback intent')

    async def test_routing_decision_structure(self):
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

if __name__ == "__main__":
    unittest.main() 