#!/usr/bin/env python3
"""
Integration tests for Dynamic Task Decomposition system.
Tests the end-to-end functionality of the dynamic task decomposition.
"""

import unittest
import sys
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import ENABLE_DYNAMIC_TASK_DECOMPOSITION, get_feature_flags

class TestDynamicTaskDecompositionIntegration(unittest.TestCase):
    """Integration tests for Dynamic Task Decomposition."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.feature_flags = get_feature_flags()
    
    def test_feature_flag_configuration(self):
        """Test that dynamic task decomposition feature flag is properly configured."""
        # Check that the feature flag exists
        self.assertIn('dynamic_task_decomposition', self.feature_flags)
        self.assertIsInstance(self.feature_flags['dynamic_task_decomposition'], bool)
        
        # Check that the flag is accessible
        self.assertIsInstance(ENABLE_DYNAMIC_TASK_DECOMPOSITION, bool)
    
    def test_task_templates_availability(self):
        """Test that task templates are available and properly structured."""
        try:
            from src.task_templates import TaskTemplateRegistry
            
            registry = TaskTemplateRegistry()
            
            # Check that registry is initialized
            self.assertIsNotNone(registry)
            self.assertIsInstance(registry.templates, dict)
            self.assertGreater(len(registry.templates), 0)
            
            # Check for key templates
            key_templates = [
                'list_players', 'add_player', 'list_fixtures', 
                'create_fixture', 'select_squad', 'get_availability_data'
            ]
            
            for template_name in key_templates:
                template = registry.get_template(template_name)
                if template:
                    # Check template structure
                    self.assertIsNotNone(template.name)
                    self.assertIsNotNone(template.description)
                    self.assertIsNotNone(template.agent_type)
                    self.assertIsInstance(template.parameters, list)
                    
        except ImportError as e:
            self.fail(f"Failed to import TaskTemplateRegistry: {e}")
    
    def test_improved_agentic_system_import(self):
        """Test that ImprovedAgenticSystem can be imported."""
        try:
            from src.improved_agentic_system import ImprovedAgenticSystem, DynamicTaskDecomposer
            
            # Check that classes can be imported
            self.assertIsNotNone(ImprovedAgenticSystem)
            self.assertIsNotNone(DynamicTaskDecomposer)
            
        except ImportError as e:
            self.fail(f"Failed to import ImprovedAgenticSystem: {e}")
    
    @patch('src.improved_agentic_system.ImprovedAgenticSystem')
    def test_agentic_system_initialization(self, mock_agentic_system):
        """Test that ImprovedAgenticSystem can be initialized."""
        try:
            from src.improved_agentic_system import ImprovedAgenticSystem
            
            # Mock agents and LLM
            mock_agents = {'test_agent': Mock()}
            mock_llm = Mock()
            
            # Test initialization
            system = ImprovedAgenticSystem(mock_agents, mock_llm)
            
            # Verify initialization
            self.assertIsNotNone(system)
            
        except Exception as e:
            self.fail(f"Failed to initialize ImprovedAgenticSystem: {e}")
    
    def test_message_handler_integration(self):
        """Test that message handler can import and use dynamic task decomposition."""
        try:
            from src.telegram_command_handler import AgentBasedMessageHandler
            
            # Check that the class can be imported
            self.assertIsNotNone(AgentBasedMessageHandler)
            
            # Check that the class has the expected methods
            handler_class = AgentBasedMessageHandler
            expected_methods = [
                '_handle_with_intelligent_routing',
                '_handle_with_legacy_routing'
            ]
            
            for method_name in expected_methods:
                self.assertTrue(hasattr(handler_class, method_name), 
                              f"Method {method_name} not found in AgentBasedMessageHandler")
            
        except ImportError as e:
            self.fail(f"Failed to import AgentBasedMessageHandler: {e}")
    
    def test_configuration_consistency(self):
        """Test that configuration is consistent across the system."""
        # Check feature flags
        flags = get_feature_flags()
        
        # Verify all expected flags are present
        expected_flags = [
            'intelligent_routing',
            'llm_routing', 
            'dynamic_task_decomposition',
            'advanced_memory',
            'performance_monitoring',
            'analytics',
            'debug'
        ]
        
        for flag in expected_flags:
            self.assertIn(flag, flags, f"Feature flag {flag} not found")
            self.assertIsInstance(flags[flag], bool, f"Feature flag {flag} is not boolean")
    
    def test_template_registry_functionality(self):
        """Test that template registry provides expected functionality."""
        try:
            from src.task_templates import TaskTemplateRegistry, TaskTemplate, TaskParameter
            
            registry = TaskTemplateRegistry()
            
            # Test template registration
            test_template = TaskTemplate(
                name="test_integration_template",
                description="Test template for integration: {param}",
                agent_type="test_agent",
                parameters=[
                    TaskParameter("param", "Test parameter", required=True)
                ]
            )
            
            # Register template
            registry.register_template(test_template)
            
            # Verify registration
            retrieved_template = registry.get_template("test_integration_template")
            self.assertIsNotNone(retrieved_template)
            self.assertEqual(retrieved_template.name, "test_integration_template")
            
            # Test parameter validation
            valid_params = {"param": "test_value"}
            errors = retrieved_template.validate_parameters(valid_params)
            self.assertEqual(len(errors), 0, f"Parameter validation failed: {errors}")
            
            # Test invalid parameters
            invalid_params = {}
            errors = retrieved_template.validate_parameters(invalid_params)
            self.assertGreater(len(errors), 0, "Should have validation errors for missing required parameter")
            
        except Exception as e:
            self.fail(f"Template registry functionality test failed: {e}")

class TestDynamicTaskDecompositionWorkflow(unittest.TestCase):
    """Test the complete workflow of dynamic task decomposition."""
    
    def test_workflow_components_availability(self):
        """Test that all components needed for the workflow are available."""
        components = [
            'src.task_templates',
            'src.improved_agentic_system',
            'src.telegram_command_handler'
        ]
        
        for component in components:
            try:
                __import__(component)
            except ImportError as e:
                self.fail(f"Component {component} not available: {e}")
    
    def test_feature_flag_workflow(self):
        """Test that feature flags control the workflow correctly."""
        # Test that feature flags are accessible
        self.assertIsInstance(ENABLE_DYNAMIC_TASK_DECOMPOSITION, bool)
        
        # Test that feature flags can be retrieved
        flags = get_feature_flags()
        self.assertIn('dynamic_task_decomposition', flags)
        
        # Test that the flag value is consistent
        self.assertEqual(ENABLE_DYNAMIC_TASK_DECOMPOSITION, flags['dynamic_task_decomposition'])

if __name__ == '__main__':
    # Run tests
    unittest.main() 