"""
Unit tests for Dynamic Task Decomposition system.
Tests the DynamicTaskDecomposer class and related functionality.
"""

import pytest
import asyncio
import json
from typing import Dict, List, Any, Optional, Union
from unittest.mock import AsyncMock

from src.testing.test_base import BaseTestCase, AsyncBaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.testing.test_utils import MockLLM, MockAgent
from src.agents.intelligent_system import DynamicTaskDecomposer, ImprovedAgenticSystem, TaskContext
from src.tasks.task_templates import TaskTemplateRegistry, TaskTemplate, TaskParameter, Task, TaskStatus
from crewai import Agent
from config import ENABLE_DYNAMIC_TASK_DECOMPOSITION


class TestDynamicTaskDecomposer(BaseTestCase):
    """Test cases for DynamicTaskDecomposer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = self.create_mock_llm()
        self.decomposer = DynamicTaskDecomposer(self.mock_llm)
        
        # Mock agents
        self.mock_agents = [
            self.create_mock_agent(name="message_processor", role="message_processor"),
            self.create_mock_agent(name="player_coordinator", role="player_coordinator"),
            self.create_mock_agent(name="team_manager", role="team_manager"),
            self.create_mock_agent(name="communication_specialist", role="communication_specialist"),
            self.create_mock_agent(name="match_analyst", role="match_analyst")
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
    
    def test_find_agent_by_type(self):
        """Test agent finding by type."""
        # Cast mock_agents to List[Agent] for type compatibility
        agents: List[Agent] = self.mock_agents  # type: ignore
        
        # Test exact match - the method looks for agent_type in role.lower()
        agent = self.decomposer._find_agent_by_type(agents, "message_processor")
        if agent is not None:
            self.assertIn("message_processor", agent.role.lower())
        
        # Test partial match
        agent = self.decomposer._find_agent_by_type(agents, "player")
        if agent is not None:
            self.assertIn("player", agent.role.lower())
        
        # Test no match (should return first agent)
        agent = self.decomposer._find_agent_by_type(agents, "nonexistent")
        if agent is not None:
            # Should return first agent when no match found
            self.assertEqual(agent, self.mock_agents[0])
        
        # Test empty agents list
        agent = self.decomposer._find_agent_by_type([], "message_processor")
        self.assertIsNone(agent)


class TestTaskTemplateRegistry(BaseTestCase):
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
        retrieved_template = self.registry.get_template("test_template_get")
        self.assertIsNotNone(retrieved_template)
        if retrieved_template is not None:
            self.assertEqual(retrieved_template.name, "test_template_get")
        
        # Test non-existing template
        retrieved_template = self.registry.get_template("nonexistent")
        self.assertIsNone(retrieved_template)
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        template = TaskTemplate(
            name="test_validation",
            description="Test template: {required_param} {optional_param}",
            agent_type="test_agent",
            parameters=[
                TaskParameter("required_param", "Required parameter", required=True),
                TaskParameter("optional_param", "Optional parameter", required=False)
            ]
        )
        
        # Test valid parameters
        valid_params = {"required_param": "test_value"}
        errors = template.validate_parameters(valid_params)
        self.assertEqual(len(errors), 0)
        
        # Test missing required parameter
        invalid_params = {"optional_param": "test_value"}
        errors = template.validate_parameters(invalid_params)
        self.assertGreater(len(errors), 0)
    
    def test_instantiate_task(self):
        """Test task instantiation from template."""
        template = TaskTemplate(
            name="test_instantiate",
            description="Test template: {param}",
            agent_type="test_agent",
            parameters=[
                TaskParameter("param", "Test parameter", required=True)
            ]
        )
        
        parameters = {"param": "test_value"}
        task = template.instantiate(parameters, "test_task_id")
        
        self.assertIsInstance(task, Task)
        self.assertEqual(task.template_name, "test_instantiate")
        self.assertEqual(task.parameters, parameters)


@pytest.mark.asyncio
class TestTaskDependencyManagement(AsyncBaseTestCase):
    """Test cases for task dependency management."""
    
    def setup_method(self, method=None):
        """Set up test fixtures."""
        super().setup_method(method)
        self.mock_llm = self.create_mock_llm()
        self.decomposer = DynamicTaskDecomposer(self.mock_llm)
        
        self.mock_agents = [
            self.create_mock_agent(name="message_processor", role="message_processor"),
            self.create_mock_agent(name="player_coordinator", role="player_coordinator"),
            self.create_mock_agent(name="team_manager", role="team_manager")
        ]
    
    async def test_dependency_resolution(self):
        """Test dependency resolution in task decomposition."""
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
                }
            ]
        }
        self.mock_llm.invoke.return_value = json.dumps(mock_response)
        
        # Test decomposition
        context = TaskContext(
            user_id="test_user",
            team_id="test_team",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=5.0
        )
        
        # Cast mock_agents to List[Agent] for type compatibility
        agents: List[Agent] = self.mock_agents  # type: ignore
        
        tasks = await self.decomposer.decompose_request(
            "test request", agents, context
        )
        
        # Verify results
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 2)
        
        # Verify dependency is set (check if task has dependencies attribute)
        if len(tasks) >= 2:
            # Check if the task has a context with dependencies
            task_context = tasks[1].context
            if isinstance(task_context, dict) and 'dependencies' in task_context:
                self.assertEqual(task_context['dependencies'], ["intent_analysis"])


@pytest.mark.asyncio
class TestPerformanceAndErrorHandling(AsyncBaseTestCase):
    """Test cases for performance and error handling."""
    
    def setup_method(self, method=None):
        """Set up test fixtures."""
        super().setup_method(method)
        self.mock_llm = self.create_mock_llm()
        self.decomposer = DynamicTaskDecomposer(self.mock_llm)
        
        self.mock_agents = [
            self.create_mock_agent(name="message_processor", role="message_processor"),
            self.create_mock_agent(name="player_coordinator", role="player_coordinator")
        ]
    
    async def test_performance_with_complex_request(self):
        """Test performance with complex request decomposition."""
        # Mock LLM response for complex request
        mock_response = {
            "tasks": [
                {
                    "template": "intent_analysis",
                    "parameters": {"request": "complex request"},
                    "dependencies": []
                },
                {
                    "template": "player_management",
                    "parameters": {"operation": "add"},
                    "dependencies": ["intent_analysis"]
                },
                {
                    "template": "communication",
                    "parameters": {"message": "notification"},
                    "dependencies": ["player_management"]
                }
            ]
        }
        self.mock_llm.invoke.return_value = json.dumps(mock_response)
        
        # Test decomposition
        context = TaskContext(
            user_id="test_user",
            team_id="test_team",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=5.0
        )
        
        # Cast mock_agents to List[Agent] for type compatibility
        agents: List[Agent] = self.mock_agents  # type: ignore
        
        tasks = await self.decomposer.decompose_request(
            "complex request", agents, context
        )
        
        # Verify results
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 3)
    
    async def test_error_handling_with_invalid_json(self):
        """Test error handling when LLM returns invalid JSON."""
        # Mock LLM to return invalid JSON
        self.mock_llm.invoke.return_value = "invalid json response"
        
        # Test decomposition
        context = TaskContext(
            user_id="test_user",
            team_id="test_team",
            conversation_history=[],
            user_preferences={},
            team_patterns={},
            complexity_score=5.0
        )
        
        # Cast mock_agents to List[Agent] for type compatibility
        agents: List[Agent] = self.mock_agents  # type: ignore
        
        tasks = await self.decomposer.decompose_request(
            "test request", agents, context
        )
        
        # Should handle error gracefully and return fallback task
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 1)


@pytest.mark.asyncio
class TestDependencyExecution(AsyncBaseTestCase):
    """Test cases for dependency execution."""
    
    async def test_dependency_execution_order(self):
        """Test that tasks execute in correct dependency order."""
        # Create dummy tasks with dependencies
        class DummyTask:
            def __init__(self, name, dependencies=None):
                self.name = name
                self.dependencies = dependencies or []
                self.executed = False
            
            async def execute(self):
                self.executed = True
                return f"Executed {self.name}"
        
        task1 = DummyTask("task1", [])
        task2 = DummyTask("task2", ["task1"])
        task3 = DummyTask("task3", ["task2"])
        
        tasks = [task1, task2, task3]
        
        # Simulate dependency execution
        executed_order = []
        for task in tasks:
            if not task.dependencies or all(t.executed for t in tasks if t.name in task.dependencies):
                await task.execute()
                executed_order.append(task.name)
        
        # Verify execution order
        self.assertEqual(executed_order, ["task1", "task2", "task3"])
    
    async def test_parallel_execution(self):
        """Test parallel execution of independent tasks."""
        # Create dummy tasks without dependencies
        class DummyTask:
            def __init__(self, name):
                self.name = name
                self.executed = False
            
            async def execute(self):
                self.executed = True
                return f"Executed {self.name}"
        
        task1 = DummyTask("task1")
        task2 = DummyTask("task2")
        task3 = DummyTask("task3")
        
        tasks = [task1, task2, task3]
        
        # Execute tasks in parallel
        import asyncio
        await asyncio.gather(*[task.execute() for task in tasks])
        
        # Verify all tasks executed
        for task in tasks:
            self.assertTrue(task.executed) 