#!/usr/bin/env python3
"""
Unit tests for Dynamic Task Decomposition system.
Tests the DynamicTaskDecomposer class and related functionality.
"""

import unittest
import sys
import os
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.improved_agentic_system import DynamicTaskDecomposer, ImprovedAgenticSystem
from src.task_templates import TaskTemplateRegistry, TaskTemplate, TaskParameter, Task, TaskStatus
from config import ENABLE_DYNAMIC_TASK_DECOMPOSITION

class TestDynamicTaskDecomposer(unittest.TestCase):
    """Test cases for DynamicTaskDecomposer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        self.mock_llm.ainvoke = AsyncMock()
        self.decomposer = DynamicTaskDecomposer(self.mock_llm)
        
        # Mock agents
        self.mock_agents = [
            Mock(role="message_processor"),
            Mock(role="player_coordinator"),
            Mock(role="team_manager"),
            Mock(role="communication_specialist"),
            Mock(role="match_analyst")
        ]
    
    def test_initialization(self):
        """Test that DynamicTaskDecomposer initializes correctly."""
        self.assertIsNotNone(self.decomposer)
        self.assertIsNotNone(self.decomposer.task_templates)
        self.assertIsInstance(self.decomposer.task_templates, dict)
        
        # Check that expected templates are loaded
        expected_templates = [
            'intent_analysis', 'player_management', 'fixture_management',
            'communication', 'analysis', 'coordination'
        ]
        for template in expected_templates:
            self.assertIn(template, self.decomposer.task_templates)
    
    def test_load_task_templates(self):
        """Test that task templates are loaded correctly."""
        templates = self.decomposer._load_task_templates()
        
        # Check template structure
        for template_name, template_data in templates.items():
            self.assertIn('description', template_data)
            self.assertIn('expected_output', template_data)
            self.assertIn('agent_type', template_data)
            
            # Check that description contains placeholders
            self.assertIn('{', template_data['description'])
    
    @patch('src.improved_agentic_system.Task')
    async def test_decompose_request_success(self, mock_task_class):
        """Test successful request decomposition."""
        # Mock LLM response
        mock_response = {
            "tasks": [
                {
                    "template": "intent_analysis",
                    "parameters": {"request": "test request"},
                    "dependencies": []
                },
                {
                    "template": "player_management",
                    "parameters": {"operation": "add", "player_info": "test player"},
                    "dependencies": ["intent_analysis"]
                }
            ]
        }
        self.mock_llm.ainvoke.return_value = json.dumps(mock_response)
        
        # Mock Task class
        mock_task = Mock()
        mock_task_class.return_value = mock_task
        
        # Test decomposition
        context = Mock()
        context.__dict__ = {"user_id": "test_user", "team_id": "test_team"}
        
        tasks = await self.decomposer.decompose_request(
            "test request", self.mock_agents, context
        )
        
        # Verify results
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 2)
        self.mock_llm.ainvoke.assert_called_once()
        
        # Verify Task creation
        self.assertEqual(mock_task_class.call_count, 2)
    
    @patch('src.improved_agentic_system.Task')
    async def test_decompose_request_fallback(self, mock_task_class):
        """Test fallback behavior when decomposition fails."""
        # Mock LLM to raise exception
        self.mock_llm.ainvoke.side_effect = Exception("LLM error")
        
        # Mock Task class
        mock_task = Mock()
        mock_task_class.return_value = mock_task
        
        # Test decomposition
        context = Mock()
        context.__dict__ = {"user_id": "test_user", "team_id": "test_team"}
        
        tasks = await self.decomposer.decompose_request(
            "test request", self.mock_agents, context
        )
        
        # Verify fallback behavior
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 1)  # Should create one fallback task
        mock_task_class.assert_called_once()
    
    def test_find_agent_by_type(self):
        """Test agent finding by type."""
        # Test exact match
        agent = self.decomposer._find_agent_by_type(self.mock_agents, "message_processor")
        self.assertEqual(agent.role, "message_processor")
        
        # Test partial match
        agent = self.decomposer._find_agent_by_type(self.mock_agents, "player")
        self.assertEqual(agent.role, "player_coordinator")
        
        # Test no match (should return first agent)
        agent = self.decomposer._find_agent_by_type(self.mock_agents, "nonexistent")
        self.assertEqual(agent.role, "message_processor")
        
        # Test empty agents list
        agent = self.decomposer._find_agent_by_type([], "message_processor")
        self.assertIsNone(agent)

class TestTaskTemplateRegistry(unittest.TestCase):
    """Test cases for TaskTemplateRegistry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = TaskTemplateRegistry()
    
    def test_initialization(self):
        """Test that TaskTemplateRegistry initializes correctly."""
        self.assertIsNotNone(self.registry)
        self.assertIsInstance(self.registry.templates, dict)
        self.assertGreater(len(self.registry.templates), 0)
    
    def test_register_template(self):
        """Test template registration."""
        template = TaskTemplate(
            name="test_template",
            description="Test template: {param}",
            agent_type="test_agent",
            parameters=[
                TaskParameter("param", "Test parameter", required=True)
            ]
        )
        
        self.registry.register_template(template)
        self.assertIn("test_template", self.registry.templates)
        self.assertEqual(self.registry.templates["test_template"], template)
    
    def test_get_template(self):
        """Test template retrieval."""
        # Register a test template to ensure it exists
        template = TaskTemplate(
            name="test_template_get",
            description="Test template: {param}",
            agent_type="test_agent",
            parameters=[
                TaskParameter("param", "Test parameter", required=True)
            ]
        )
        self.registry.register_template(template)
        # Test existing template
        template = self.registry.get_template("test_template_get")
        self.assertIsNotNone(template)
        self.assertEqual(template.name, "test_template_get")
        # Test non-existing template
        template = self.registry.get_template("nonexistent")
        self.assertIsNone(template)
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        # Register a test template to ensure it exists
        template = TaskTemplate(
            name="test_template_validate",
            description="Test template: {param}",
            agent_type="test_agent",
            parameters=[
                TaskParameter("param", "Test parameter", required=True)
            ]
        )
        self.registry.register_template(template)
        template = self.registry.get_template("test_template_validate")
        # Test valid parameters
        valid_params = {"param": "test_value"}
        errors = template.validate_parameters(valid_params)
        self.assertEqual(len(errors), 0)
        # Test missing required parameter
        invalid_params = {}
        errors = template.validate_parameters(invalid_params)
        self.assertGreater(len(errors), 0)
        self.assertIn("param", errors)
    
    def test_instantiate_task(self):
        """Test task instantiation from template."""
        # Register a test template to ensure it exists
        template = TaskTemplate(
            name="test_template_instantiate",
            description="Test template: {param}",
            agent_type="test_agent",
            parameters=[
                TaskParameter("param", "Test parameter", required=True)
            ]
        )
        self.registry.register_template(template)
        template = self.registry.get_template("test_template_instantiate")
        params = {"param": "test_value"}
        task = template.instantiate(params, "test_task_id")
        self.assertIsInstance(task, Task)
        self.assertEqual(task.task_id, "test_task_id")
        self.assertEqual(task.template_name, "test_template_instantiate")
        self.assertEqual(task.parameters, params)
        self.assertEqual(task.status, TaskStatus.PENDING)

class TestTaskDependencyManagement(unittest.TestCase):
    """Test cases for task dependency management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        self.mock_llm.ainvoke = AsyncMock()
        self.decomposer = DynamicTaskDecomposer(self.mock_llm)
    
    @patch('src.improved_agentic_system.Task')
    async def test_dependency_resolution(self, mock_task_class):
        """Test that task dependencies are properly resolved."""
        # Mock LLM response with dependencies
        mock_response = {
            "tasks": [
                {
                    "template": "intent_analysis",
                    "parameters": {"request": "test request"},
                    "dependencies": []
                },
                {
                    "template": "player_management",
                    "parameters": {"operation": "add", "player_info": "test player"},
                    "dependencies": ["intent_analysis"]
                },
                {
                    "template": "communication",
                    "parameters": {"message_type": "notification", "content": "test"},
                    "dependencies": ["player_management"]
                }
            ]
        }
        self.mock_llm.ainvoke.return_value = json.dumps(mock_response)
        
        # Mock Task class
        mock_task = Mock()
        mock_task_class.return_value = mock_task
        
        # Test decomposition
        context = Mock()
        context.__dict__ = {"user_id": "test_user", "team_id": "test_team"}
        
        tasks = await self.decomposer.decompose_request(
            "test request", [Mock(role="test_agent")], context
        )
        
        # Verify tasks are created with dependencies
        self.assertEqual(len(tasks), 3)
        
        # Verify Task creation calls include dependency information
        calls = mock_task_class.call_args_list
        self.assertEqual(len(calls), 3)
        
        # Check that context includes dependency information
        for call in calls:
            kwargs = call[1]  # Get keyword arguments
            if 'context' in kwargs:
                context_data = kwargs['context']
                self.assertIn('dependencies', context_data)

class TestPerformanceAndErrorHandling(unittest.TestCase):
    """Test cases for performance and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        self.mock_llm.ainvoke = AsyncMock()
        self.decomposer = DynamicTaskDecomposer(self.mock_llm)
    
    @patch('src.improved_agentic_system.Task')
    async def test_performance_with_complex_request(self, mock_task_class):
        """Test performance with complex requests."""
        # Mock complex LLM response
        mock_response = {
            "tasks": [
                {
                    "template": "intent_analysis",
                    "parameters": {"request": "complex request"},
                    "dependencies": []
                }
            ] * 5  # Create 5 tasks
        }
        self.mock_llm.ainvoke.return_value = json.dumps(mock_response)
        
        # Mock Task class
        mock_task = Mock()
        mock_task_class.return_value = mock_task
        
        # Test decomposition timing
        import time
        start_time = time.time()
        
        context = Mock()
        context.__dict__ = {"user_id": "test_user", "team_id": "test_team"}
        
        tasks = await self.decomposer.decompose_request(
            "complex request", [Mock(role="test_agent")], context
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance is acceptable (should complete in under 5 seconds)
        self.assertLess(execution_time, 5.0)
        self.assertEqual(len(tasks), 5)
    
    async def test_error_handling_with_invalid_json(self):
        """Test error handling when LLM returns invalid JSON."""
        # Mock LLM to return invalid JSON
        self.mock_llm.ainvoke.return_value = "invalid json"
        
        context = Mock()
        context.__dict__ = {"user_id": "test_user", "team_id": "test_team"}
        
        # Should not raise exception, should fall back to simple task
        tasks = await self.decomposer.decompose_request(
            "test request", [Mock(role="test_agent")], context
        )
        
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 1)  # Should create fallback task

class TestDependencyExecution(unittest.IsolatedAsyncioTestCase):
    async def test_dependency_execution_order(self):
        """Test that tasks are executed in dependency order with parallelism."""
        # Create mock agents and llm
        mock_agents = {'a': Mock(role='a'), 'b': Mock(role='b'), 'c': Mock(role='c')}
        mock_llm = Mock()
        system = ImprovedAgenticSystem(mock_agents, mock_llm)
        # Create mock tasks with dependencies: a -> b -> c
        class DummyTask:
            def __init__(self, name, dependencies=None):
                self.context = {'template': name, 'dependencies': dependencies or []}
                self.name = name
                self.executed = False
            async def execute(self):
                await asyncio.sleep(0.01)
                self.executed = True
                return f"done-{self.name}"
        task_a = DummyTask('a')
        task_b = DummyTask('b', dependencies=['a'])
        task_c = DummyTask('c', dependencies=['b'])
        tasks = [task_a, task_b, task_c]
        # Run dependency-based execution
        result = await system._execute_tasks_with_dependencies(tasks, context=Mock())
        # Check that all tasks executed
        self.assertTrue(task_a.executed)
        self.assertTrue(task_b.executed)
        self.assertTrue(task_c.executed)
        # Check result order
        self.assertIn('a: done-a', result)
        self.assertIn('b: done-b', result)
        self.assertIn('c: done-c', result)

    async def test_parallel_execution(self):
        """Test that independent tasks are executed in parallel."""
        mock_agents = {'x': Mock(role='x'), 'y': Mock(role='y')}
        mock_llm = Mock()
        system = ImprovedAgenticSystem(mock_agents, mock_llm)
        # Two independent tasks
        class DummyTask:
            def __init__(self, name):
                self.context = {'template': name, 'dependencies': []}
                self.name = name
                self.executed = False
            async def execute(self):
                await asyncio.sleep(0.05)
                self.executed = True
                return f"done-{self.name}"
        task_x = DummyTask('x')
        task_y = DummyTask('y')
        tasks = [task_x, task_y]
        # Run and time execution
        start = asyncio.get_event_loop().time()
        result = await system._execute_tasks_with_dependencies(tasks, context=Mock())
        elapsed = asyncio.get_event_loop().time() - start
        # Should be less than sum of both sleeps if run in parallel
        self.assertLess(elapsed, 0.09)
        self.assertTrue(task_x.executed)
        self.assertTrue(task_y.executed)
        self.assertIn('x: done-x', result)
        self.assertIn('y: done-y', result)

if __name__ == '__main__':
    # Run tests
    unittest.main() 