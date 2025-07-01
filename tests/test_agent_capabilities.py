#!/usr/bin/env python3
"""
Unit tests for agent capabilities system.
"""

import pytest
from typing import List

from src.testing.test_base import BaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.testing.test_utils import MockLLM, MockAgent
from src.agent_capabilities import (
    AgentCapabilityMatrix, 
    AgentCapability, 
    CapabilityType,
    get_agent_capabilities,
    get_agents_with_capability,
    get_capability_matrix_summary,
    get_best_agent_for_capability
)


class TestAgentCapabilities(BaseTestCase):
    """Test cases for agent capabilities system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matrix = AgentCapabilityMatrix()
    
    def test_agent_capabilities_initialization(self):
        """Test that agent capabilities are properly initialized."""
        # Test that all expected agents exist
        expected_agents = [
            'message_processor', 'team_manager', 'player_coordinator',
            'match_analyst', 'communication_specialist', 'finance_manager',
            'squad_selection_specialist', 'analytics_specialist'
        ]
        
        for agent in expected_agents:
            capabilities = self.matrix.get_agent_capabilities(agent)
            self.assertIsInstance(capabilities, list)
            self.assertGreater(len(capabilities), 0)
            self.assertTrue(all(isinstance(cap, AgentCapability) for cap in capabilities))
    
    def test_capability_types(self):
        """Test that all capability types are properly defined."""
        # Test that capability types are enums
        self.assertTrue(hasattr(CapabilityType, 'INTENT_ANALYSIS'))
        self.assertTrue(hasattr(CapabilityType, 'PLAYER_MANAGEMENT'))
        self.assertTrue(hasattr(CapabilityType, 'PERFORMANCE_ANALYSIS'))
    
    def test_agent_capability_structure(self):
        """Test that agent capabilities have the correct structure."""
        capabilities = self.matrix.get_agent_capabilities('message_processor')
        
        for capability in capabilities:
            self.assertIsInstance(capability.capability, CapabilityType)
            self.assertIsInstance(capability.proficiency_level, float)
            self.assertIsInstance(capability.description, str)
            self.assertIsInstance(capability.is_primary, bool)
            
            # Test proficiency level bounds
            self.assertGreaterEqual(capability.proficiency_level, 0.0)
            self.assertLessEqual(capability.proficiency_level, 1.0)
    
    def test_get_agents_with_capability(self):
        """Test getting agents with specific capabilities."""
        # Test coordination capability (should have multiple agents)
        coordination_agents = self.matrix.get_agents_with_capability(CapabilityType.COORDINATION)
        self.assertIsInstance(coordination_agents, list)
        self.assertGreater(len(coordination_agents), 0)
        
        # Test that returned agents actually have the capability
        for agent in coordination_agents:
            proficiency = self.matrix.get_agent_proficiency(agent, CapabilityType.COORDINATION)
            self.assertGreater(proficiency, 0.0)
    
    def test_get_agents_with_capability_min_proficiency(self):
        """Test getting agents with minimum proficiency threshold."""
        # Test with high proficiency threshold
        high_proficiency_agents = self.matrix.get_agents_with_capability(
            CapabilityType.INTENT_ANALYSIS, min_proficiency=0.9
        )
        
        # Test with low proficiency threshold
        low_proficiency_agents = self.matrix.get_agents_with_capability(
            CapabilityType.INTENT_ANALYSIS, min_proficiency=0.1
        )
        
        # High threshold should return fewer or equal agents
        self.assertLessEqual(len(high_proficiency_agents), len(low_proficiency_agents))
    
    def test_get_primary_capabilities(self):
        """Test getting primary capabilities for agents."""
        for agent in ['message_processor', 'team_manager', 'player_coordinator']:
            primary_caps = self.matrix.get_primary_capabilities(agent)
            self.assertIsInstance(primary_caps, list)
            
            # All primary capabilities should have is_primary=True
            for cap in primary_caps:
                self.assertTrue(cap.is_primary)
    
    def test_get_capability_description(self):
        """Test getting descriptions for capabilities."""
        description = self.matrix.get_capability_description(CapabilityType.INTENT_ANALYSIS)
        self.assertIsInstance(description, str)
        self.assertGreater(len(description), 0)
        
        # Test unknown capability
        unknown_description = self.matrix.get_capability_description(CapabilityType.INTENT_ANALYSIS)
        self.assertIsInstance(unknown_description, str)
    
    def test_get_agent_proficiency(self):
        """Test getting proficiency levels for agent-capability pairs."""
        # Test existing capability
        proficiency = self.matrix.get_agent_proficiency('message_processor', CapabilityType.INTENT_ANALYSIS)
        self.assertIsInstance(proficiency, float)
        self.assertGreater(proficiency, 0.0)
        self.assertLessEqual(proficiency, 1.0)
        
        # Test non-existing capability
        proficiency = self.matrix.get_agent_proficiency('message_processor', CapabilityType.PLAYER_MANAGEMENT)
        self.assertEqual(proficiency, 0.0)
    
    def test_get_all_capabilities(self):
        """Test getting all available capability types."""
        all_capabilities = self.matrix.get_all_capabilities()
        self.assertIsInstance(all_capabilities, set)
        self.assertGreater(len(all_capabilities), 0)
        
        # Test that all capabilities are CapabilityType enums
        for capability in all_capabilities:
            self.assertIsInstance(capability, CapabilityType)
    
    def test_get_capability_matrix_summary(self):
        """Test getting capability matrix summary."""
        summary = self.matrix.get_capability_matrix_summary()
        self.assertIsInstance(summary, dict)
        
        # Test that all agents are present
        expected_agents = [
            'message_processor', 'team_manager', 'player_coordinator',
            'match_analyst', 'communication_specialist', 'finance_manager',
            'squad_selection_specialist', 'analytics_specialist'
        ]
        
        for agent in expected_agents:
            self.assertIn(agent, summary)
            self.assertIsInstance(summary[agent], list)
    
    def test_validate_capability(self):
        """Test capability validation."""
        # Test valid capability
        is_valid = self.matrix.validate_capability('message_processor', CapabilityType.INTENT_ANALYSIS)
        self.assertTrue(is_valid)
        
        # Test invalid capability
        is_valid = self.matrix.validate_capability('message_processor', CapabilityType.PLAYER_MANAGEMENT)
        self.assertFalse(is_valid)
    
    def test_get_best_agent_for_capability(self):
        """Test getting the best agent for a capability."""
        # Test with a capability that should have a clear best agent
        best_agent = self.matrix.get_best_agent_for_capability(CapabilityType.PERFORMANCE_ANALYSIS)
        self.assertIsInstance(best_agent, str)
        self.assertIn(best_agent, ['match_analyst', 'analytics_specialist'])
        
        # Test that the returned agent has the capability
        if best_agent is not None:
            proficiency = self.matrix.get_agent_proficiency(best_agent, CapabilityType.PERFORMANCE_ANALYSIS)
            self.assertGreater(proficiency, 0.0)
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        # Test get_agent_capabilities
        capabilities = get_agent_capabilities('message_processor')
        self.assertIsInstance(capabilities, list)
        self.assertGreater(len(capabilities), 0)
        
        # Test get_agents_with_capability
        agents = get_agents_with_capability(CapabilityType.COORDINATION)
        self.assertIsInstance(agents, list)
        
        # Test get_capability_matrix_summary
        summary = get_capability_matrix_summary()
        self.assertIsInstance(summary, dict)
        
        # Test get_best_agent_for_capability
        best_agent = get_best_agent_for_capability(CapabilityType.INTENT_ANALYSIS)
        self.assertIsInstance(best_agent, str)
    
    def test_capability_coverage(self):
        """Test that all agents have reasonable capability coverage."""
        for agent in ['message_processor', 'team_manager', 'player_coordinator']:
            capabilities = self.matrix.get_agent_capabilities(agent)
            
            # Each agent should have at least one capability
            self.assertGreater(len(capabilities), 0)
            
            # Each agent should have at least one primary capability
            primary_caps = [cap for cap in capabilities if cap.is_primary]
            self.assertGreater(len(primary_caps), 0)
    
    def test_proficiency_distribution(self):
        """Test that proficiency levels are reasonably distributed."""
        for agent in ['message_processor', 'team_manager', 'player_coordinator']:
            capabilities = self.matrix.get_agent_capabilities(agent)
            
            # Should have at least one high proficiency capability
            high_proficiency = [cap for cap in capabilities if cap.proficiency_level >= 0.8]
            self.assertGreater(len(high_proficiency), 0)
            
            # Should have reasonable number of medium proficiency capabilities
            medium_proficiency = [cap for cap in capabilities if 0.4 <= cap.proficiency_level < 0.8]
            self.assertGreaterEqual(len(medium_proficiency), 0)


class TestAgentCapabilityIntegration(BaseTestCase):
    """Integration tests for agent capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matrix = AgentCapabilityMatrix()
    
    def test_real_world_scenarios(self):
        """Test capabilities in real-world scenarios."""
        # Scenario: Player management request
        player_management_agents = self.matrix.get_agents_with_capability(CapabilityType.PLAYER_MANAGEMENT)
        self.assertIn('player_coordinator', player_management_agents)
        
        # Scenario: Team coordination request
        coordination_agents = self.matrix.get_agents_with_capability(CapabilityType.COORDINATION)
        self.assertIn('team_manager', coordination_agents)
        
        # Scenario: Performance analysis request
        analysis_agents = self.matrix.get_agents_with_capability(CapabilityType.PERFORMANCE_ANALYSIS)
        self.assertIn('match_analyst', analysis_agents)
    
    def test_capability_hierarchy(self):
        """Test that capability hierarchy is logical."""
        # Team manager should have coordination as primary capability
        team_manager_caps = self.matrix.get_agent_capabilities('team_manager')
        coordination_cap = next((cap for cap in team_manager_caps if cap.capability == CapabilityType.COORDINATION), None)
        self.assertIsNotNone(coordination_cap)
        if coordination_cap is not None:
            self.assertTrue(coordination_cap.is_primary)
        
        # Message processor should have intent analysis as primary capability
        message_processor_caps = self.matrix.get_agent_capabilities('message_processor')
        intent_cap = next((cap for cap in message_processor_caps if cap.capability == CapabilityType.INTENT_ANALYSIS), None)
        self.assertIsNotNone(intent_cap)
        if intent_cap is not None:
            self.assertTrue(intent_cap.is_primary)

if __name__ == '__main__':
    # Run tests
    pytest.main() 