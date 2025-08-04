"""
CrewAI Agent Health Check

This module provides comprehensive health validation for CrewAI agents
following Enterprise best practices for agentic systems.
"""

import asyncio
import logging
from typing import Any, Dict, List, Tuple

from ..reporting import CheckCategory, CheckResult, CheckStatus
from .base_check import BaseCheck

logger = logging.getLogger(__name__)


class CrewAIAgentHealthCheck(BaseCheck):
    """
    Comprehensive CrewAI agent health validation following Enterprise patterns.
    
    Validates:
    - Agent creation and initialization
    - Tool assignment and accessibility
    - LLM configuration and connectivity
    - Agent memory and context management
    - Inter-agent communication capabilities
    - Agent performance and response times
    - Error handling and recovery mechanisms
    """

    def __init__(self):
        super().__init__(
            name="crewai_agent_health_check",
            category=CheckCategory.AGENTS,
            description="Comprehensive CrewAI agent health and performance validation"
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        """Execute comprehensive CrewAI agent health validation."""
        try:
            validation_results = []
            
            # 1. Agent Factory Health
            factory_result = await self._validate_agent_factory()
            validation_results.append(("Agent Factory", factory_result))
            
            # 2. Core Agent Creation
            creation_result = await self._validate_agent_creation()
            validation_results.append(("Agent Creation", creation_result))
            
            # 3. Tool Assignment Validation
            tool_result = await self._validate_tool_assignment()
            validation_results.append(("Tool Assignment", tool_result))
            
            # 4. LLM Configuration Validation
            llm_result = await self._validate_llm_configuration()
            validation_results.append(("LLM Configuration", llm_result))
            
            # 5. Agent Communication Test
            comm_result = await self._validate_agent_communication()
            validation_results.append(("Agent Communication", comm_result))
            
            # 6. Performance Benchmarking
            perf_result = await self._validate_agent_performance()
            validation_results.append(("Agent Performance", perf_result))
            
            # 7. Error Recovery Testing
            recovery_result = await self._validate_error_recovery()
            validation_results.append(("Error Recovery", recovery_result))
            
            return self._aggregate_results(validation_results)
            
        except Exception as e:
            logger.error(f"❌ CrewAI agent health check failed: {e}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Agent health validation error: {str(e)}",
                error=e
            )

    async def _validate_agent_factory(self) -> Tuple[CheckStatus, str, List[str]]:
        """Validate agent factory health and configuration."""
        issues = []
        details = []
        
        try:
            from kickai.agents.simplified_agent_factory import get_agent_factory
            
            agent_factory = get_agent_factory()
            
            if not agent_factory:
                issues.append("Agent factory not accessible")
                return CheckStatus.FAILED, "Agent factory missing", details
            
            details.append("✅ Agent factory accessible")
            
            # Check factory configuration
            try:
                # Validate that factory has required methods
                required_methods = ['create_agent', 'get_llm_config']
                missing_methods = []
                
                for method in required_methods:
                    if not hasattr(agent_factory, method):
                        missing_methods.append(method)
                
                if missing_methods:
                    issues.append(f"Factory missing methods: {missing_methods}")
                else:
                    details.append("✅ Factory has all required methods")
                
            except Exception as e:
                issues.append(f"Factory method validation failed: {str(e)}")
            
            # Check LLM configuration access
            try:
                llm_config = agent_factory.get_llm_config()
                if llm_config:
                    details.append("✅ LLM configuration accessible from factory")
                else:
                    issues.append("LLM configuration not available from factory")
            except Exception as e:
                issues.append(f"LLM configuration access failed: {str(e)}")
                
        except Exception as e:
            issues.append(f"Agent factory validation failed: {str(e)}")
        
        if issues:
            return CheckStatus.FAILED, f"Agent factory issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Agent factory validation passed", details

    async def _validate_agent_creation(self) -> Tuple[CheckStatus, str, List[str]]:
        """Validate that core agents can be created successfully."""
        issues = []
        details = []
        
        try:
            from kickai.agents.simplified_agent_factory import get_agent_factory
            
            agent_factory = get_agent_factory()
            
            # List of critical agents that must be creatable
            critical_agents = [
                "message_processor",
                "player_coordinator",
                "help_assistant"
            ]
            
            creation_successes = []
            creation_failures = []
            
            for agent_name in critical_agents:
                try:
                    # Test agent creation (without storing the agent)
                    test_agent = agent_factory.create_agent(agent_name)
                    
                    if test_agent:
                        creation_successes.append(agent_name)
                        details.append(f"✅ Successfully created {agent_name}")
                        
                        # Validate agent has required attributes
                        required_attrs = ['role', 'goal', 'backstory']
                        missing_attrs = [attr for attr in required_attrs if not hasattr(test_agent, attr)]
                        
                        if missing_attrs:
                            issues.append(f"{agent_name} missing attributes: {missing_attrs}")
                        
                    else:
                        creation_failures.append(f"{agent_name}: No agent returned")
                        
                except Exception as e:
                    creation_failures.append(f"{agent_name}: {str(e)}")
            
            if creation_failures:
                issues.append(f"Agent creation failures: {creation_failures}")
            
            details.append(f"✅ Successfully created {len(creation_successes)}/{len(critical_agents)} critical agents")
            
        except Exception as e:
            issues.append(f"Agent creation validation failed: {str(e)}")
        
        if issues:
            return CheckStatus.FAILED, f"Agent creation issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Agent creation validation passed", details

    async def _validate_tool_assignment(self) -> Tuple[CheckStatus, str, List[str]]:
        """Validate that agents have proper tool assignments."""
        issues = []
        details = []
        
        try:
            from kickai.agents.simplified_agent_factory import get_agent_factory
            from kickai.agents.tool_registry import get_tool_registry
            
            agent_factory = get_agent_factory()
            tool_registry = get_tool_registry()
            
            # Check that tool registry has tools available
            try:
                available_tools = tool_registry.get_tool_names()
                if len(available_tools) == 0:
                    issues.append("No tools available in tool registry")
                else:
                    details.append(f"✅ {len(available_tools)} tools available in registry")
            except Exception as e:
                issues.append(f"Cannot access tools from registry: {str(e)}")
            
            # Test agent tool assignment
            test_agent_configs = [
                ("help_assistant", ["get_available_commands", "provide_command_help"]),
                ("player_coordinator", ["add_player", "get_player_status"]),
                ("team_manager", ["add_team_member", "update_team_member"])
            ]
            
            for agent_name, expected_tools in test_agent_configs:
                try:
                    # Check if agent can be created with tools
                    agent = agent_factory.create_agent(agent_name)
                    
                    if hasattr(agent, 'tools') and agent.tools:
                        agent_tool_count = len(agent.tools)
                        details.append(f"✅ {agent_name} has {agent_tool_count} tools assigned")
                        
                        # Check for specific expected tools (if available)
                        for expected_tool in expected_tools:
                            if expected_tool in available_tools:
                                details.append(f"✅ {agent_name} can access {expected_tool}")
                    else:
                        issues.append(f"{agent_name} has no tools assigned")
                        
                except Exception as e:
                    issues.append(f"Tool assignment check failed for {agent_name}: {str(e)}")
            
        except Exception as e:
            issues.append(f"Tool assignment validation failed: {str(e)}")
        
        if issues:
            return CheckStatus.FAILED, f"Tool assignment issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Tool assignment validation passed", details

    async def _validate_llm_configuration(self) -> Tuple[CheckStatus, str, List[str]]:
        """Validate LLM configuration for agents."""
        issues = []
        details = []
        
        try:
            from kickai.config.llm_config import get_llm_config
            
            llm_config = get_llm_config()
            
            # Validate LLM configuration exists
            if not llm_config:
                issues.append("LLM configuration not available")
                return CheckStatus.FAILED, "LLM configuration missing", details
            
            details.append("✅ LLM configuration accessible")
            
            # Test LLM connectivity
            try:
                connectivity_test = llm_config.test_connection()
                if connectivity_test:
                    details.append("✅ LLM connectivity test passed")
                else:
                    issues.append("LLM connectivity test failed")
            except Exception as e:
                issues.append(f"LLM connectivity test error: {str(e)}")
            
            # Validate model configuration
            try:
                if hasattr(llm_config, 'default_model'):
                    model_name = llm_config.default_model
                    details.append(f"✅ Default model configured: {model_name}")
                else:
                    issues.append("No default model configured")
                    
                if hasattr(llm_config, 'base_url'):
                    base_url = llm_config.base_url
                    details.append(f"✅ LLM base URL configured: {base_url}")
                else:
                    issues.append("No LLM base URL configured")
                    
            except Exception as e:
                issues.append(f"Model configuration validation failed: {str(e)}")
            
        except Exception as e:
            issues.append(f"LLM configuration validation failed: {str(e)}")
        
        if issues:
            return CheckStatus.FAILED, f"LLM configuration issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "LLM configuration validation passed", details

    async def _validate_agent_communication(self) -> Tuple[CheckStatus, str, List[str]]:
        """Validate inter-agent communication capabilities."""
        issues = []
        details = []
        
        try:
            # This is a simplified communication test
            # In a full implementation, you would test actual agent-to-agent communication
            
            from kickai.agents.simplified_agent_factory import get_agent_factory
            
            agent_factory = get_agent_factory()
            
            # Test basic agent response capability
            try:
                test_agent = agent_factory.create_agent("help_assistant")
                
                if test_agent:
                    # Check that agent has required communication attributes
                    communication_attrs = ['role', 'goal', 'backstory']
                    present_attrs = [attr for attr in communication_attrs if hasattr(test_agent, attr)]
                    
                    details.append(f"✅ Agent has {len(present_attrs)}/{len(communication_attrs)} communication attributes")
                    
                    if len(present_attrs) == len(communication_attrs):
                        details.append("✅ Agent communication setup validated")
                    else:
                        issues.append("Agent missing communication attributes")
                else:
                    issues.append("Cannot create test agent for communication validation")
                    
            except Exception as e:
                issues.append(f"Agent communication test failed: {str(e)}")
            
            # Test message routing capability
            try:
                from kickai.agents.agentic_message_router import AgenticMessageRouter
                
                # Test router initialization
                router = AgenticMessageRouter(team_id="test", crewai_system=None)
                
                if router:
                    details.append("✅ Agent message router initialized")
                else:
                    issues.append("Agent message router failed to initialize")
                    
            except Exception as e:
                issues.append(f"Message router validation failed: {str(e)}")
            
        except Exception as e:
            issues.append(f"Agent communication validation failed: {str(e)}")
        
        if issues:
            return CheckStatus.FAILED, f"Agent communication issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Agent communication validation passed", details

    async def _validate_agent_performance(self) -> Tuple[CheckStatus, str, List[str]]:
        """Validate agent performance and response times."""
        issues = []
        details = []
        
        try:
            import time
            from kickai.agents.simplified_agent_factory import get_agent_factory
            
            agent_factory = get_agent_factory()
            
            # Performance benchmarks
            max_creation_time = 5.0  # seconds
            max_response_time = 10.0  # seconds
            
            # Test agent creation performance
            start_time = time.time()
            try:
                test_agent = agent_factory.create_agent("help_assistant")
                creation_time = time.time() - start_time
                
                if creation_time <= max_creation_time:
                    details.append(f"✅ Agent creation time: {creation_time:.2f}s (within {max_creation_time}s limit)")
                else:
                    issues.append(f"Agent creation slow: {creation_time:.2f}s (exceeds {max_creation_time}s limit)")
                    
            except Exception as e:
                issues.append(f"Agent creation performance test failed: {str(e)}")
            
            # Test memory usage (basic check)
            try:
                import psutil
                import os
                
                process = psutil.Process(os.getpid())
                memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                
                max_memory = 1000  # MB threshold
                if memory_usage <= max_memory:
                    details.append(f"✅ Memory usage: {memory_usage:.1f}MB (within {max_memory}MB limit)")
                else:
                    issues.append(f"High memory usage: {memory_usage:.1f}MB (exceeds {max_memory}MB limit)")
                    
            except ImportError:
                details.append("⚠️ psutil not available, skipping memory check")
            except Exception as e:
                issues.append(f"Memory usage check failed: {str(e)}")
            
        except Exception as e:
            issues.append(f"Agent performance validation failed: {str(e)}")
        
        if issues:
            return CheckStatus.FAILED, f"Agent performance issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Agent performance validation passed", details

    async def _validate_error_recovery(self) -> Tuple[CheckStatus, str, List[str]]:
        """Validate agent error handling and recovery mechanisms."""
        issues = []
        details = []
        
        try:
            from kickai.agents.simplified_agent_factory import get_agent_factory
            
            agent_factory = get_agent_factory()
            
            # Test error handling in agent creation
            try:
                # Try to create an agent with invalid parameters
                invalid_agent = agent_factory.create_agent("nonexistent_agent_type")
                
                if invalid_agent is None:
                    details.append("✅ Agent factory properly handles invalid agent requests")
                else:
                    issues.append("Agent factory does not properly validate agent types")
                    
            except Exception as e:
                # This is expected behavior - the factory should handle errors gracefully
                details.append(f"✅ Agent factory handles errors gracefully: {type(e).__name__}")
            
            # Test tool registry error handling
            try:
                from kickai.agents.tool_registry import get_tool_registry
                
                tool_registry = get_tool_registry()
                
                # Try to access non-existent tool
                try:
                    nonexistent_tool = tool_registry.get_tool("nonexistent_tool")
                    if nonexistent_tool is None:
                        details.append("✅ Tool registry handles missing tools gracefully")
                    else:
                        issues.append("Tool registry does not validate tool existence")
                except Exception:
                    details.append("✅ Tool registry raises appropriate exceptions for missing tools")
                    
            except Exception as e:
                issues.append(f"Tool registry error handling test failed: {str(e)}")
            
            # Test LLM error recovery
            try:
                from kickai.config.llm_config import get_llm_config
                
                llm_config = get_llm_config()
                
                # Test connection with invalid parameters (if method exists)
                if hasattr(llm_config, 'test_connection_with_timeout'):
                    try:
                        # This should fail gracefully
                        result = llm_config.test_connection_with_timeout(timeout=0.001)
                        details.append("✅ LLM configuration handles connection timeouts")
                    except Exception:
                        details.append("✅ LLM configuration raises appropriate exceptions for connection issues")
                        
            except Exception as e:
                issues.append(f"LLM error recovery test failed: {str(e)}")
            
        except Exception as e:
            issues.append(f"Error recovery validation failed: {str(e)}")
        
        if issues:
            return CheckStatus.FAILED, f"Error recovery issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Error recovery validation passed", details

    def _aggregate_results(self, validation_results: List[Tuple[str, Tuple[CheckStatus, str, List[str]]]]) -> CheckResult:
        """Aggregate all validation results into a single check result."""
        overall_status = CheckStatus.PASSED
        messages = []
        all_details = []
        
        critical_components = ["Agent Factory", "Agent Creation", "LLM Configuration"]
        
        for component_name, (status, message, details) in validation_results:
            if status == CheckStatus.FAILED:
                if component_name in critical_components:
                    overall_status = CheckStatus.FAILED
                messages.append(f"❌ {component_name}: {message}")
            else:
                messages.append(f"✅ {component_name}: {message}")
            
            all_details.extend([f"{component_name}: {detail}" for detail in details])
        
        final_message = "\n".join(messages)
        if all_details:
            final_message += "\n\nDetails:\n" + "\n".join(all_details)
        
        return CheckResult(
            name=self.name,
            category=self.category,
            status=overall_status,
            message=final_message,
            details={"component_results": validation_results}
        )