"""
Integration tests for Phase 1 improvements.
Tests the interaction between different Phase 1 components.
"""

import pytest
from src.testing.test_base import BaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.testing.test_utils import MockLLM, MockAgent
from src.agents import AgentCapabilityMatrix, CapabilityType
from config import get_feature_flags, is_phase1_enabled

class TestPhase1Integration(BaseTestCase):
    """Integration tests for Phase 1 features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matrix = AgentCapabilityMatrix()
    
    def test_feature_flags_work_correctly(self):
        """Test that feature flags are properly configured."""
        flags = get_feature_flags()
        expected_flags = [
            'intelligent_routing',
            'dynamic_task_decomposition', 
            'advanced_memory',
            'performance_monitoring',
            'analytics',
            'debug'
        ]
        for flag in expected_flags:
            self.assertIn(flag, flags)
            self.assertIsInstance(flags[flag], bool)
    
    def test_phase1_status_detection(self):
        """Test that Phase 1 status is correctly detected."""
        status = is_phase1_enabled()
        self.assertIsInstance(status, bool)
    
    def test_capability_matrix_integration(self):
        """Test that capability matrix integrates with other components."""
        expected_agents = [
            'message_processor', 'team_manager', 'player_coordinator',
            'match_analyst', 'communication_specialist', 'finance_manager',
            'squad_selection_specialist', 'analytics_specialist'
        ]
        for agent in expected_agents:
            capabilities = self.matrix.get_agent_capabilities(agent)
            self.assertGreater(len(capabilities), 0)
            primary_caps = [cap for cap in capabilities if cap.is_primary]
            self.assertGreaterEqual(len(primary_caps), 1)
    
    def test_capability_routing_integration(self):
        """Test that capabilities can be used for routing decisions."""
        performance_agents = self.matrix.get_agents_with_capability(
            CapabilityType.PERFORMANCE_ANALYSIS
        )
        self.assertIn('match_analyst', performance_agents)
        self.assertIn('analytics_specialist', performance_agents)
        coordination_agents = self.matrix.get_agents_with_capability(
            CapabilityType.COORDINATION
        )
        self.assertIn('team_manager', coordination_agents)
        intent_agents = self.matrix.get_agents_with_capability(
            CapabilityType.INTENT_ANALYSIS
        )
        self.assertIn('message_processor', intent_agents)
    
    def test_capability_proficiency_integration(self):
        """Test that proficiency levels are used correctly."""
        for agent in ['message_processor', 'team_manager', 'player_coordinator']:
            primary_caps = self.matrix.get_primary_capabilities(agent)
            for cap in primary_caps:
                proficiency = self.matrix.get_agent_proficiency(agent, cap.capability)
                self.assertGreaterEqual(proficiency, 0.8)
    
    def test_best_agent_selection_integration(self):
        """Test that best agent selection works for different capabilities."""
        best_performance_agent = self.matrix.get_best_agent_for_capability(
            CapabilityType.PERFORMANCE_ANALYSIS
        )
        self.assertIn(best_performance_agent, ['match_analyst', 'analytics_specialist'])
        best_intent_agent = self.matrix.get_best_agent_for_capability(
            CapabilityType.INTENT_ANALYSIS
        )
        self.assertEqual(best_intent_agent, 'message_processor')
        best_coordination_agent = self.matrix.get_best_agent_for_capability(
            CapabilityType.COORDINATION
        )
        self.assertEqual(best_coordination_agent, 'team_manager')

class TestPhase1RealWorldScenarios(BaseTestCase):
    """Test real-world scenarios with Phase 1 features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matrix = AgentCapabilityMatrix()
    
    def test_complex_request_routing(self):
        """Test routing for complex multi-agent requests."""
        required_capabilities = [
            CapabilityType.STRATEGIC_PLANNING,
            CapabilityType.COORDINATION,
            CapabilityType.MESSAGING,
            CapabilityType.ANNOUNCEMENTS
        ]
        selected_agents = set()
        for capability in required_capabilities:
            agents = self.matrix.get_agents_with_capability(capability, min_proficiency=0.7)
            selected_agents.update(agents)
        self.assertIn('team_manager', selected_agents)
        self.assertIn('communication_specialist', selected_agents)
        self.assertGreaterEqual(len(selected_agents), 2)
    
    def test_performance_analysis_request(self):
        """Test routing for performance analysis requests."""
        required_capabilities = [
            CapabilityType.PERFORMANCE_ANALYSIS,
            CapabilityType.TACTICAL_INSIGHTS,
            CapabilityType.TREND_ANALYSIS,
            CapabilityType.DECISION_MAKING
        ]
        selected_agents = set()
        for capability in required_capabilities:
            agents = self.matrix.get_agents_with_capability(capability, min_proficiency=0.7)
            selected_agents.update(agents)
        self.assertIn('match_analyst', selected_agents)
        self.assertIn('analytics_specialist', selected_agents)
        self.assertIn('team_manager', selected_agents)
    
    def test_player_management_request(self):
        """Test routing for player management requests."""
        required_capabilities = [
            CapabilityType.PLAYER_MANAGEMENT,
            CapabilityType.AVAILABILITY_TRACKING,
            CapabilityType.COORDINATION
        ]
        selected_agents = set()
        for capability in required_capabilities:
            agents = self.matrix.get_agents_with_capability(capability, min_proficiency=0.7)
            selected_agents.update(agents)
        self.assertIn('player_coordinator', selected_agents)
        self.assertIn('team_manager', selected_agents)
    
    def test_financial_request(self):
        """Test routing for financial requests."""
        required_capabilities = [
            CapabilityType.PAYMENT_TRACKING,
            CapabilityType.FINANCIAL_REPORTING,
            CapabilityType.COORDINATION
        ]
        selected_agents = set()
        for capability in required_capabilities:
            agents = self.matrix.get_agents_with_capability(capability, min_proficiency=0.7)
            selected_agents.update(agents)
        self.assertIn('finance_manager', selected_agents)
        self.assertIn('team_manager', selected_agents)

class TestPhase1Configuration(BaseTestCase):
    """Test configuration structure and values for Phase 1."""
    def test_configuration_structure(self):
        flags = get_feature_flags()
        self.assertIsInstance(flags, dict)
        self.assertGreater(len(flags), 0)
    def test_configuration_values(self):
        flags = get_feature_flags()
        for value in flags.values():
            self.assertIsInstance(value, bool)

class TestPhase1ErrorHandling(BaseTestCase):
    """Test error handling and edge cases for Phase 1."""
    def setUp(self):
        self.matrix = AgentCapabilityMatrix()
    def test_invalid_agent_name(self):
        capabilities = self.matrix.get_agent_capabilities('nonexistent_agent')
        self.assertEqual(len(capabilities), 0)
    def test_invalid_capability(self):
        # Test with a capability that doesn't exist in the matrix
        # Create a new matrix instance for this test to avoid affecting other tests
        test_matrix = AgentCapabilityMatrix()
        
        # Test with a capability that should not be assigned to any agent
        # We'll use a capability that exists but check with a very high proficiency requirement
        agents = test_matrix.get_agents_with_capability(CapabilityType.INTENT_ANALYSIS, min_proficiency=1.0)
        # With proficiency 1.0, no agents should be returned since no agent has perfect proficiency
        self.assertEqual(len(agents), 0)
    def test_edge_case_proficiency_levels(self):
        for agent in ['message_processor', 'team_manager', 'player_coordinator']:
            for cap in self.matrix.get_agent_capabilities(agent):
                proficiency = self.matrix.get_agent_proficiency(agent, cap.capability)
                self.assertGreaterEqual(proficiency, 0.0)
                self.assertLessEqual(proficiency, 1.0) 