"""
Integration tests for Dynamic Task Decomposition system.
Tests the end-to-end functionality of the dynamic task decomposition.
"""

import pytest
from src.testing.test_base import BaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.testing.test_utils import MockLLM, MockAgent
from config import ENABLE_DYNAMIC_TASK_DECOMPOSITION, get_feature_flags

class TestDynamicTaskDecompositionIntegration(BaseTestCase):
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
        from src.task_templates import TaskTemplateRegistry
        registry = TaskTemplateRegistry()
        self.assertIsNotNone(registry)
        self.assertIsInstance(registry.templates, dict)
        self.assertGreater(len(registry.templates), 0)
        key_templates = [
            'list_players', 'add_player', 'list_fixtures', 
            'create_fixture', 'select_squad', 'get_availability_data'
        ]
        for template_name in key_templates:
            template = registry.get_template(template_name)
            if template is not None:
                self.assertIsNotNone(template.name)
                self.assertIsNotNone(template.description)
                self.assertIsNotNone(template.agent_type)
                self.assertIsInstance(template.parameters, list)
    
    def test_improved_agentic_system_import(self):
        """Test that ImprovedAgenticSystem can be imported."""
        from src.improved_agentic_system import ImprovedAgenticSystem, DynamicTaskDecomposer
        self.assertIsNotNone(ImprovedAgenticSystem)
        self.assertIsNotNone(DynamicTaskDecomposer)
    
    def test_agentic_system_initialization(self):
        """Test that ImprovedAgenticSystem can be initialized."""
        from src.improved_agentic_system import ImprovedAgenticSystem
        mock_agents = {'test_agent': MockAgent('test_agent')}
        mock_llm = MockLLM()
        system = ImprovedAgenticSystem(mock_agents, mock_llm)
        self.assertIsNotNone(system)
    
    def test_message_handler_integration(self):
        """Test that message handler can import and use dynamic task decomposition."""
        from src.telegram_command_handler import AgentBasedMessageHandler
        self.assertIsNotNone(AgentBasedMessageHandler)
        handler_class = AgentBasedMessageHandler
        expected_methods = [
            '_handle_with_intelligent_routing',
            '_handle_with_legacy_routing'
        ]
        for method_name in expected_methods:
            self.assertTrue(hasattr(handler_class, method_name), 
                          f"Method {method_name} not found in AgentBasedMessageHandler")
    
    def test_configuration_consistency(self):
        """Test that configuration is consistent across the system."""
        flags = get_feature_flags()
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
        from src.task_templates import TaskTemplateRegistry, TaskTemplate, TaskParameter
        registry = TaskTemplateRegistry()
        test_template = TaskTemplate(
            name="test_integration_template",
            description="Test template for integration: {param}",
            agent_type="test_agent",
            parameters=[
                TaskParameter("param", "Test parameter", required=True)
            ]
        )
        registry.register_template(test_template)
        retrieved_template = registry.get_template("test_integration_template")
        self.assertIsNotNone(retrieved_template)
        if retrieved_template is not None:
            self.assertEqual(retrieved_template.name, "test_integration_template")
            valid_params = {"param": "test_value"}
            errors = retrieved_template.validate_parameters(valid_params)
            self.assertEqual(len(errors), 0, f"Parameter validation failed: {errors}")
            invalid_params = {}
            errors = retrieved_template.validate_parameters(invalid_params)
            self.assertGreater(len(errors), 0, "Should have validation errors for missing required parameter")

class TestDynamicTaskDecompositionWorkflow(BaseTestCase):
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
        self.assertIsInstance(ENABLE_DYNAMIC_TASK_DECOMPOSITION, bool)

if __name__ == '__main__':
    # Run tests
    pytest.main() 