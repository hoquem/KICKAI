#!/usr/bin/env python3
"""
Integration tests for Phase 1 improvements.
Tests the interaction between different Phase 1 components.
"""

import unittest
import sys
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.agent_capabilities import AgentCapabilityMatrix, CapabilityType
from config import get_feature_flags, is_phase1_enabled

class TestPhase1Integration(unittest.TestCase):
    """Integration tests for Phase 1 features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matrix = AgentCapabilityMatrix()
    
    def test_feature_flags_work_correctly(self):
        """Test that feature flags are properly configured."""
        flags = get_feature_flags()
        
        # Test that all expected flags exist
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
        # Test that all agents have capabilities
        expected_agents = [
            'message_processor', 'team_manager', 'player_coordinator',
            'match_analyst', 'communication_specialist', 'finance_manager',
            'squad_selection_specialist', 'analytics_specialist'
        ]
        
        for agent in expected_agents:
            capabilities = self.matrix.get_agent_capabilities(agent)
            self.assertGreater(len(capabilities), 0)
            
            # Test that each agent has at least one primary capability
            primary_caps = [cap for cap in capabilities if cap.is_primary]
            self.assertGreaterEqual(len(primary_caps), 1)
    
    def test_capability_routing_integration(self):
        """Test that capabilities can be used for routing decisions."""
        # Test routing for different request types
        
        # Performance analysis request
        performance_agents = self.matrix.get_agents_with_capability(
            CapabilityType.PERFORMANCE_ANALYSIS
        )
        self.assertIn('match_analyst', performance_agents)
        self.assertIn('analytics_specialist', performance_agents)
        
        # Coordination request
        coordination_agents = self.matrix.get_agents_with_capability(
            CapabilityType.COORDINATION
        )
        self.assertIn('team_manager', coordination_agents)
        
        # Intent analysis request
        intent_agents = self.matrix.get_agents_with_capability(
            CapabilityType.INTENT_ANALYSIS
        )
        self.assertIn('message_processor', intent_agents)
    
    def test_capability_proficiency_integration(self):
        """Test that proficiency levels are used correctly."""
        # Test that primary capabilities have high proficiency
        for agent in ['message_processor', 'team_manager', 'player_coordinator']:
            primary_caps = self.matrix.get_primary_capabilities(agent)
            
            for cap in primary_caps:
                proficiency = self.matrix.get_agent_proficiency(agent, cap.capability)
                self.assertGreaterEqual(proficiency, 0.8)  # Primary capabilities should be highly proficient
    
    def test_best_agent_selection_integration(self):
        """Test that best agent selection works for different capabilities."""
        # Test performance analysis
        best_performance_agent = self.matrix.get_best_agent_for_capability(
            CapabilityType.PERFORMANCE_ANALYSIS
        )
        self.assertIn(best_performance_agent, ['match_analyst', 'analytics_specialist'])
        
        # Test intent analysis
        best_intent_agent = self.matrix.get_best_agent_for_capability(
            CapabilityType.INTENT_ANALYSIS
        )
        self.assertEqual(best_intent_agent, 'message_processor')
        
        # Test coordination
        best_coordination_agent = self.matrix.get_best_agent_for_capability(
            CapabilityType.COORDINATION
        )
        self.assertEqual(best_coordination_agent, 'team_manager')

class TestPhase1RealWorldScenarios(unittest.TestCase):
    """Test real-world scenarios with Phase 1 features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matrix = AgentCapabilityMatrix()
    
    def test_complex_request_routing(self):
        """Test routing for complex multi-agent requests."""
        # Scenario: "Create a match against Arsenal and notify the team"
        # This should require multiple agents
        
        required_capabilities = [
            CapabilityType.STRATEGIC_PLANNING,  # Team manager for match creation
            CapabilityType.COORDINATION,        # Team manager for coordination
            CapabilityType.MESSAGING,           # Communication specialist for notifications
            CapabilityType.ANNOUNCEMENTS        # Communication specialist for announcements
        ]
        
        selected_agents = set()
        for capability in required_capabilities:
            agents = self.matrix.get_agents_with_capability(capability, min_proficiency=0.7)
            selected_agents.update(agents)
        
        # Should include team_manager and communication_specialist
        self.assertIn('team_manager', selected_agents)
        self.assertIn('communication_specialist', selected_agents)
        self.assertGreaterEqual(len(selected_agents), 2)
    
    def test_performance_analysis_request(self):
        """Test routing for performance analysis requests."""
        # Scenario: "Analyze our team performance and suggest improvements"
        
        required_capabilities = [
            CapabilityType.PERFORMANCE_ANALYSIS,  # Match analyst for analysis
            CapabilityType.TACTICAL_INSIGHTS,     # Match analyst for insights
            CapabilityType.TREND_ANALYSIS,        # Analytics specialist for trends
            CapabilityType.DECISION_MAKING        # Team manager for decisions
        ]
        
        selected_agents = set()
        for capability in required_capabilities:
            agents = self.matrix.get_agents_with_capability(capability, min_proficiency=0.7)
            selected_agents.update(agents)
        
        # Should include match_analyst, analytics_specialist, and team_manager
        self.assertIn('match_analyst', selected_agents)
        self.assertIn('analytics_specialist', selected_agents)
        self.assertIn('team_manager', selected_agents)
    
    def test_player_management_request(self):
        """Test routing for player management requests."""
        # Scenario: "Add player John Doe and track their availability"
        
        required_capabilities = [
            CapabilityType.PLAYER_MANAGEMENT,     # Player coordinator
            CapabilityType.AVAILABILITY_TRACKING, # Player coordinator
            CapabilityType.COORDINATION           # Team manager for coordination
        ]
        
        selected_agents = set()
        for capability in required_capabilities:
            agents = self.matrix.get_agents_with_capability(capability, min_proficiency=0.7)
            selected_agents.update(agents)
        
        # Should include player_coordinator and team_manager
        self.assertIn('player_coordinator', selected_agents)
        self.assertIn('team_manager', selected_agents)
    
    def test_financial_request(self):
        """Test routing for financial requests."""
        # Scenario: "Track payments for the last match and generate a report"
        
        required_capabilities = [
            CapabilityType.PAYMENT_TRACKING,      # Finance manager
            CapabilityType.FINANCIAL_REPORTING,   # Finance manager
            CapabilityType.COORDINATION           # Team manager for coordination
        ]
        
        selected_agents = set()
        for capability in required_capabilities:
            agents = self.matrix.get_agents_with_capability(capability, min_proficiency=0.7)
            selected_agents.update(agents)
        
        # Should include finance_manager and team_manager
        self.assertIn('finance_manager', selected_agents)
        self.assertIn('team_manager', selected_agents)

class TestPhase1Configuration(unittest.TestCase):
    """Test Phase 1 configuration and settings."""
    
    def test_configuration_structure(self):
        """Test that configuration has the expected structure."""
        from config import get_phase1_config
        
        config = get_phase1_config()
        
        # Test that all expected sections exist
        expected_sections = ['feature_flags', 'memory', 'performance', 'routing']
        for section in expected_sections:
            self.assertIn(section, config)
        
        # Test feature flags section
        self.assertIsInstance(config['feature_flags'], dict)
        
        # Test memory section
        memory_config = config['memory']
        self.assertIn('retention_days', memory_config)
        self.assertIn('max_conversation_history', memory_config)
        self.assertIn('max_episodic_memory', memory_config)
        
        # Test performance section
        performance_config = config['performance']
        self.assertIn('monitoring_interval', performance_config)
        self.assertIn('optimization_enabled', performance_config)
        
        # Test routing section
        routing_config = config['routing']
        self.assertIn('complexity_threshold', routing_config)
        self.assertIn('max_negotiation_rounds', routing_config)
    
    def test_configuration_values(self):
        """Test that configuration values are reasonable."""
        from config import get_phase1_config
        
        config = get_phase1_config()
        
        # Test memory configuration
        memory_config = config['memory']
        self.assertGreater(memory_config['retention_days'], 0)
        self.assertLessEqual(memory_config['retention_days'], 365)  # Reasonable range
        self.assertGreater(memory_config['max_conversation_history'], 0)
        self.assertLessEqual(memory_config['max_conversation_history'], 1000)  # Reasonable range
        
        # Test performance configuration
        performance_config = config['performance']
        self.assertGreater(performance_config['monitoring_interval'], 0)
        self.assertLessEqual(performance_config['monitoring_interval'], 3600)  # Reasonable range
        
        # Test routing configuration
        routing_config = config['routing']
        self.assertGreater(routing_config['complexity_threshold'], 0)
        self.assertLessEqual(routing_config['complexity_threshold'], 10)  # Reasonable range
        self.assertGreater(routing_config['max_negotiation_rounds'], 0)
        self.assertLessEqual(routing_config['max_negotiation_rounds'], 10)  # Reasonable range

class TestPhase1ErrorHandling(unittest.TestCase):
    """Test error handling in Phase 1 components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matrix = AgentCapabilityMatrix()
    
    def test_invalid_agent_name(self):
        """Test handling of invalid agent names."""
        # Test getting capabilities for non-existent agent
        capabilities = self.matrix.get_agent_capabilities('non_existent_agent')
        self.assertEqual(capabilities, [])
        
        # Test getting proficiency for non-existent agent
        proficiency = self.matrix.get_agent_proficiency('non_existent_agent', CapabilityType.INTENT_ANALYSIS)
        self.assertEqual(proficiency, 0.0)
        
        # Test validating capability for non-existent agent
        is_valid = self.matrix.validate_capability('non_existent_agent', CapabilityType.INTENT_ANALYSIS)
        self.assertFalse(is_valid)
    
    def test_invalid_capability(self):
        """Test handling of invalid capabilities."""
        # Test getting agents for non-existent capability
        agents = self.matrix.get_agents_with_capability('INVALID_CAPABILITY')  # This will raise an error
        self.assertEqual(agents, [])
        
        # Test getting description for non-existent capability
        description = self.matrix.get_capability_description('INVALID_CAPABILITY')  # This will raise an error
        self.assertEqual(description, "Unknown capability")
    
    def test_edge_case_proficiency_levels(self):
        """Test edge cases for proficiency levels."""
        # Test with minimum proficiency threshold
        agents = self.matrix.get_agents_with_capability(CapabilityType.INTENT_ANALYSIS, min_proficiency=0.0)
        self.assertGreater(len(agents), 0)
        
        # Test with maximum proficiency threshold
        agents = self.matrix.get_agents_with_capability(CapabilityType.INTENT_ANALYSIS, min_proficiency=1.0)
        # Should return agents with perfect proficiency (if any)
        self.assertIsInstance(agents, list)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 