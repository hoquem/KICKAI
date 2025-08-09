"""
Initialization Sequence Check

This module validates the proper initialization sequence and startup order
following fail-fast principles and CrewAI Enterprise patterns.
"""

import logging
import time
from typing import Any

from ..reporting import CheckCategory, CheckResult, CheckStatus
from .base_check import BaseCheck

logger = logging.getLogger(__name__)


class InitializationSequenceCheck(BaseCheck):
    """
    Validates the proper initialization sequence and startup order.

    Ensures:
    - Correct dependency initialization order
    - Fail-fast validation at each step
    - Rollback capabilities for failed initialization
    - Performance monitoring of startup sequence
    - Resource cleanup on failure
    - Configuration validation before service creation
    """

    def __init__(self):
        super().__init__(
            name="initialization_sequence_check",
            category=CheckCategory.SYSTEM,
            description="Validates proper initialization sequence and startup order"
        )

    async def execute(self, context: dict[str, Any]) -> CheckResult:
        """Execute initialization sequence validation."""
        try:
            validation_results = []

            # 1. Pre-initialization Validation
            pre_init_result = await self._validate_pre_initialization()
            validation_results.append(("Pre-initialization", pre_init_result))

            if pre_init_result[0] == CheckStatus.FAILED:
                # Fail fast if pre-initialization fails
                return self._create_fail_fast_result("Pre-initialization failed", validation_results)

            # 2. Configuration Loading Sequence
            config_result = await self._validate_configuration_sequence()
            validation_results.append(("Configuration Sequence", config_result))

            if config_result[0] == CheckStatus.FAILED:
                return self._create_fail_fast_result("Configuration loading failed", validation_results)

            # 3. Core Dependencies Initialization
            core_deps_result = await self._validate_core_dependencies()
            validation_results.append(("Core Dependencies", core_deps_result))

            if core_deps_result[0] == CheckStatus.FAILED:
                return self._create_fail_fast_result("Core dependencies failed", validation_results)

            # 4. Registry Initialization Sequence
            registry_result = await self._validate_registry_sequence()
            validation_results.append(("Registry Sequence", registry_result))

            if registry_result[0] == CheckStatus.FAILED:
                return self._create_fail_fast_result("Registry initialization failed", validation_results)

            # 5. Service Layer Initialization
            service_result = await self._validate_service_sequence()
            validation_results.append(("Service Sequence", service_result))

            if service_result[0] == CheckStatus.FAILED:
                return self._create_fail_fast_result("Service initialization failed", validation_results)

            # 6. Agent System Initialization
            agent_result = await self._validate_agent_sequence()
            validation_results.append(("Agent Sequence", agent_result))

            # 7. Post-initialization Validation
            post_init_result = await self._validate_post_initialization()
            validation_results.append(("Post-initialization", post_init_result))

            return self._aggregate_results(validation_results)

        except Exception as e:
            logger.error(f"❌ Initialization sequence check failed: {e}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Initialization sequence validation error: {e!s}",
                error=e
            )

    async def _validate_pre_initialization(self) -> tuple[CheckStatus, str, list[str]]:
        """Validate pre-initialization requirements."""
        issues = []
        details = []

        try:
            # 1. Environment Variable Validation
            import os

            required_env_vars = [
                'KICKAI_INVITE_SECRET_KEY',
                'OLLAMA_BASE_URL'
            ]

            missing_env_vars = []
            for env_var in required_env_vars:
                if not os.getenv(env_var):
                    missing_env_vars.append(env_var)
                else:
                    details.append(f"✅ Environment variable {env_var} is set")

            if missing_env_vars:
                issues.append(f"Missing required environment variables: {missing_env_vars}")

            # 2. Python Path Validation
            import sys
            current_path = os.getcwd()

            if current_path not in sys.path and '.' not in sys.path:
                issues.append("Current directory not in Python path - may cause import issues")
            else:
                details.append("✅ Python path configured for absolute imports")

            # 3. Critical Module Availability
            critical_modules = [
                'crewai',
                'firebase_admin',
                'telegram',
                'loguru'
            ]

            unavailable_modules = []
            for module in critical_modules:
                try:
                    __import__(module)
                    details.append(f"✅ Critical module {module} available")
                except ImportError:
                    unavailable_modules.append(module)

            if unavailable_modules:
                issues.append(f"Critical modules not available: {unavailable_modules}")

            # 4. File System Permissions
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=True) as tmp:
                    tmp.write(b"test")
                details.append("✅ File system write permissions available")
            except Exception as e:
                issues.append(f"File system permission issues: {e!s}")

        except Exception as e:
            issues.append(f"Pre-initialization validation failed: {e!s}")

        if issues:
            return CheckStatus.FAILED, f"Pre-initialization issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Pre-initialization validation passed", details

    async def _validate_configuration_sequence(self) -> tuple[CheckStatus, str, list[str]]:
        """Validate configuration loading sequence."""
        issues = []
        details = []

        try:
            start_time = time.time()

            # 1. Settings Configuration
            try:
                from kickai.core.config import get_settings
                settings = get_settings()

                if settings:
                    details.append("✅ Core settings loaded successfully")
                else:
                    issues.append("Core settings not loaded")
            except Exception as e:
                issues.append(f"Settings loading failed: {e!s}")

            # 2. LLM Configuration
            try:
                from kickai.config.llm_config import get_llm_config
                llm_config = get_llm_config()

                if llm_config:
                    details.append("✅ LLM configuration loaded successfully")

                    # Validate LLM configuration
                    config_errors = llm_config.validate_configuration()
                    if config_errors:
                        issues.append(f"LLM configuration errors: {config_errors}")
                    else:
                        details.append("✅ LLM configuration validated")
                else:
                    issues.append("LLM configuration not loaded")
            except Exception as e:
                issues.append(f"LLM configuration loading failed: {e!s}")

            # 3. Logging Configuration
            try:
                from kickai.core.logging_config import logger as app_logger
                if app_logger:
                    details.append("✅ Logging configuration loaded successfully")
                    app_logger.info("Logging system validation test")
                else:
                    issues.append("Logging configuration not loaded")
            except Exception as e:
                issues.append(f"Logging configuration failed: {e!s}")

            # 4. Constants Validation
            try:
                from kickai.core.constants import validate_constants
                validate_constants()
                details.append("✅ Constants validated successfully")
            except Exception as e:
                issues.append(f"Constants validation failed: {e!s}")

            load_time = time.time() - start_time
            details.append(f"✅ Configuration loading completed in {load_time:.2f}s")

            if load_time > 10.0:  # 10 second threshold
                issues.append(f"Configuration loading too slow: {load_time:.2f}s")

        except Exception as e:
            issues.append(f"Configuration sequence validation failed: {e!s}")

        if issues:
            return CheckStatus.FAILED, f"Configuration sequence issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Configuration sequence validation passed", details

    async def _validate_core_dependencies(self) -> tuple[CheckStatus, str, list[str]]:
        """Validate core dependency initialization."""
        issues = []
        details = []

        try:
            start_time = time.time()

            # 1. Database Connection
            try:
                from kickai.database.firebase_client import get_firebase_client
                firebase_client = get_firebase_client()

                if firebase_client:
                    details.append("✅ Firebase client initialized successfully")
                else:
                    issues.append("Firebase client not initialized")
            except Exception as e:
                issues.append(f"Firebase client initialization failed: {e!s}")

            # 2. Dependency Container
            try:
                from kickai.core.dependency_container import get_container, initialize_container

                container = get_container()
                if not container._initialized:
                    container = initialize_container()

                if container and container._initialized:
                    details.append("✅ Dependency container initialized successfully")
                else:
                    issues.append("Dependency container not properly initialized")
            except Exception as e:
                issues.append(f"Dependency container initialization failed: {e!s}")

            # 3. Service Factory
            try:
                from kickai.core.dependency_container import get_container
                from kickai.features.registry import create_service_factory

                container = get_container()
                database = container.get_database()

                service_factory = create_service_factory(container, database)

                if service_factory:
                    details.append("✅ Service factory created successfully")
                else:
                    issues.append("Service factory not created")
            except Exception as e:
                issues.append(f"Service factory creation failed: {e!s}")

            init_time = time.time() - start_time
            details.append(f"✅ Core dependencies initialized in {init_time:.2f}s")

            if init_time > 15.0:  # 15 second threshold
                issues.append(f"Core dependency initialization too slow: {init_time:.2f}s")

        except Exception as e:
            issues.append(f"Core dependencies validation failed: {e!s}")

        if issues:
            return CheckStatus.FAILED, f"Core dependencies issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Core dependencies validation passed", details

    async def _validate_registry_sequence(self) -> tuple[CheckStatus, str, list[str]]:
        """Validate registry initialization sequence."""
        issues = []
        details = []

        try:
            start_time = time.time()

            # 1. Command Registry Initialization
            try:
                from kickai.core.command_registry_initializer import initialize_command_registry

                command_registry = initialize_command_registry()

                if command_registry:
                    commands = command_registry.list_all_commands()
                    details.append(f"✅ Command registry initialized with {len(commands)} commands")
                else:
                    issues.append("Command registry not initialized")
            except Exception as e:
                issues.append(f"Command registry initialization failed: {e!s}")

            # 2. Tool Registry Initialization
            try:
                from kickai.agents.tool_registry import get_tool_registry

                tool_registry = get_tool_registry()
                tool_registry.auto_discover_tools()

                tool_names = tool_registry.get_tool_names()
                details.append(f"✅ Tool registry initialized with {len(tool_names)} tools")

            except Exception as e:
                issues.append(f"Tool registry initialization failed: {e!s}")

            # 3. Agent Factory Initialization
            try:
                from kickai.agents.simplified_agent_factory import get_agent_factory

                agent_factory = get_agent_factory()

                if agent_factory:
                    details.append("✅ Agent factory initialized successfully")
                else:
                    issues.append("Agent factory not initialized")
            except Exception as e:
                issues.append(f"Agent factory initialization failed: {e!s}")

            registry_time = time.time() - start_time
            details.append(f"✅ Registries initialized in {registry_time:.2f}s")

            if registry_time > 20.0:  # 20 second threshold
                issues.append(f"Registry initialization too slow: {registry_time:.2f}s")

        except Exception as e:
            issues.append(f"Registry sequence validation failed: {e!s}")

        if issues:
            return CheckStatus.FAILED, f"Registry sequence issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Registry sequence validation passed", details

    async def _validate_service_sequence(self) -> tuple[CheckStatus, str, list[str]]:
        """Validate service layer initialization sequence using dynamic service discovery."""
        issues = []
        details = []

        try:
            start_time = time.time()

            # 1. Service Factory Initialization
            try:
                from kickai.core.dependency_container import get_container

                container = get_container()
                factory = container.get_factory()

                if factory:
                    details.append("✅ Service factory accessible from container")
                else:
                    issues.append("Service factory not accessible from container")
            except Exception as e:
                issues.append(f"Service factory access failed: {e!s}")

            # 2. Dynamic Service Discovery and Validation
            try:
                from kickai.core.service_discovery.discovery import get_service_discovery
                from kickai.core.service_discovery.health_checkers import (
                    register_default_health_checkers,
                )
                from kickai.core.service_discovery.interfaces import ServiceType
                from kickai.core.service_discovery.registry import get_service_registry

                # Initialize service registry and discovery
                registry = get_service_registry()
                discovery = get_service_discovery()

                # Register health checkers
                register_default_health_checkers(registry)

                # Auto-discover and register services
                discovery.auto_register_services(registry)

                # Get core services that should be available
                core_services = registry.list_services(ServiceType.CORE)
                feature_services = registry.list_services(ServiceType.FEATURE)

                details.append(f"✅ Discovered {len(core_services)} core services")
                details.append(f"✅ Discovered {len(feature_services)} feature services")

                # Validate core services health
                core_service_health = await registry.check_all_services_health()

                healthy_services = []
                unhealthy_services = []

                for service_name, health in core_service_health.items():
                    service_def = registry.get_service_definition(service_name)
                    if service_def and service_def.service_type == ServiceType.CORE:
                        if health.status.value == "healthy":
                            healthy_services.append(service_name)
                            details.append(f"✅ Core service {service_name} is healthy")
                        else:
                            unhealthy_services.append(service_name)
                            details.append(f"❌ Core service {service_name} is unhealthy: {health.error_message}")

                # Report validation results
                if unhealthy_services:
                    issues.append(f"Unhealthy core services: {unhealthy_services}")

                details.append(f"✅ Service health check completed: {len(healthy_services)} healthy, {len(unhealthy_services)} unhealthy")

                # Get service statistics
                stats = registry.get_service_statistics()
                details.append(f"✅ Service registry statistics: {stats}")

            except Exception as e:
                issues.append(f"Dynamic service discovery failed: {e!s}")

                # Fallback to legacy validation
                try:
                    from kickai.core.dependency_container import get_container

                    container = get_container()

                    # Check minimal critical services as fallback
                    critical_services = ['DataStoreInterface']

                    missing_services = []
                    for service_name in critical_services:
                        try:
                            service = container.get_service(service_name)
                            if service:
                                details.append(f"✅ Fallback: Service {service_name} available")
                            else:
                                missing_services.append(service_name)
                        except Exception:
                            missing_services.append(service_name)

                    if missing_services:
                        issues.append(f"Missing critical services (fallback check): {missing_services}")

                except Exception as fallback_error:
                    issues.append(f"Both dynamic discovery and fallback validation failed: {fallback_error}")

            service_time = time.time() - start_time
            details.append(f"✅ Service layer validation completed in {service_time:.2f}s")

            if service_time > 30.0:  # 30 second threshold
                issues.append(f"Service validation too slow: {service_time:.2f}s")

        except Exception as e:
            issues.append(f"Service sequence validation failed: {e!s}")

        if issues:
            return CheckStatus.FAILED, f"Service sequence issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Service sequence validation passed", details

    async def _validate_agent_sequence(self) -> tuple[CheckStatus, str, list[str]]:
        """Validate agent system initialization sequence."""
        issues = []
        details = []

        try:
            start_time = time.time()

            # 1. Agent Factory Readiness
            try:
                from kickai.agents.simplified_agent_factory import get_agent_factory

                agent_factory = get_agent_factory()

                if agent_factory:
                    details.append("✅ Agent factory ready for agent creation")
                else:
                    issues.append("Agent factory not ready")
            except Exception as e:
                issues.append(f"Agent factory readiness check failed: {e!s}")

            # 2. Sample Agent Creation
            try:
                from kickai.agents.simplified_agent_factory import get_agent_factory

                agent_factory = get_agent_factory()
                test_agent = agent_factory.create_agent("help_assistant")

                if test_agent:
                    details.append("✅ Sample agent created successfully")
                else:
                    issues.append("Sample agent creation failed")
            except Exception as e:
                issues.append(f"Sample agent creation failed: {e!s}")

            # 3. Agent Communication Setup
            try:
                from kickai.agents.agentic_message_router import AgenticMessageRouter

                router = AgenticMessageRouter(team_id="test", crewai_system=None)

                if router:
                    details.append("✅ Agent message router initialized")
                else:
                    issues.append("Agent message router initialization failed")
            except Exception as e:
                issues.append(f"Agent communication setup failed: {e!s}")

            agent_time = time.time() - start_time
            details.append(f"✅ Agent system initialized in {agent_time:.2f}s")

            if agent_time > 25.0:  # 25 second threshold
                issues.append(f"Agent initialization too slow: {agent_time:.2f}s")

        except Exception as e:
            issues.append(f"Agent sequence validation failed: {e!s}")

        if issues:
            return CheckStatus.FAILED, f"Agent sequence issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Agent sequence validation passed", details

    async def _validate_post_initialization(self) -> tuple[CheckStatus, str, list[str]]:
        """Validate post-initialization system health."""
        issues = []
        details = []

        try:
            # 1. System Readiness Check
            try:
                from kickai.core.dependency_container import get_container

                container = get_container()
                readiness = container.verify_services_ready()

                if readiness:
                    details.append("✅ System services ready")
                else:
                    issues.append("System services not ready")
            except Exception as e:
                issues.append(f"System readiness check failed: {e!s}")

            # 2. Health Check Endpoint
            try:
                # Basic health indicators
                import os

                import psutil

                process = psutil.Process(os.getpid())
                cpu_percent = process.cpu_percent()
                memory_mb = process.memory_info().rss / 1024 / 1024

                details.append(f"✅ System health - CPU: {cpu_percent}%, Memory: {memory_mb:.1f}MB")

                if memory_mb > 2000:  # 2GB threshold
                    issues.append(f"High memory usage after initialization: {memory_mb:.1f}MB")

            except ImportError:
                details.append("⚠️ psutil not available, skipping resource monitoring")
            except Exception as e:
                issues.append(f"Health check failed: {e!s}")

            # 3. Integration Test
            try:
                # Test that the system can process a simple request
                from kickai.core.command_registry_initializer import (
                    get_initialized_command_registry,
                )

                registry = get_initialized_command_registry()
                help_command = registry.get_command("/help")

                if help_command:
                    details.append("✅ Integration test passed - help command accessible")
                else:
                    issues.append("Integration test failed - help command not found")

            except Exception as e:
                issues.append(f"Integration test failed: {e!s}")

        except Exception as e:
            issues.append(f"Post-initialization validation failed: {e!s}")

        if issues:
            return CheckStatus.FAILED, f"Post-initialization issues: {'; '.join(issues)}", details
        return CheckStatus.PASSED, "Post-initialization validation passed", details

    def _create_fail_fast_result(self, failure_reason: str, validation_results: list) -> CheckResult:
        """Create a fail-fast result when critical initialization fails."""
        messages = [f"❌ FAIL-FAST: {failure_reason}"]
        all_details = []

        for component_name, (status, message, details) in validation_results:
            if status == CheckStatus.FAILED:
                messages.append(f"❌ {component_name}: {message}")
            else:
                messages.append(f"✅ {component_name}: {message}")

            all_details.extend([f"{component_name}: {detail}" for detail in details])

        final_message = "\n".join(messages)
        final_message += "\n\n🚨 SYSTEM INITIALIZATION HALTED - FIX CRITICAL ISSUES BEFORE PROCEEDING"

        if all_details:
            final_message += "\n\nDetails:\n" + "\n".join(all_details)

        return CheckResult(
            name=self.name,
            category=self.category,
            status=CheckStatus.FAILED,
            message=final_message,
            details={"fail_fast": True, "validation_results": validation_results}
        )

    def _aggregate_results(self, validation_results: list[tuple[str, tuple[CheckStatus, str, list[str]]]]) -> CheckResult:
        """Aggregate all validation results into a single check result."""
        overall_status = CheckStatus.PASSED
        messages = []
        all_details = []

        for component_name, (status, message, details) in validation_results:
            if status == CheckStatus.FAILED:
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
