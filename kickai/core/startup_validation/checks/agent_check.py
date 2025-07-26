import logging

from ..reporting import CheckCategory, CheckResult, CheckStatus
from .base_check import BaseCheck


class AgentInitializationCheck(BaseCheck):
    """
    Startup check to ensure all CrewAI agent classes/factories can be imported and instantiated.
    Validates agent configuration and dependencies.
    """
    name = "AgentInitializationCheck"
    category = CheckCategory.AGENT
    description = "Validates that all CrewAI agents and dependencies are properly initialized."

    async def execute(self, context=None) -> CheckResult:
        logger = logging.getLogger(__name__)
        try:
            # Attempt to import agent factory and config
            from kickai.agents.configurable_agent import AgentContext, ConfigurableAgent
            from kickai.config.agents import get_enabled_agent_configs
            from kickai.utils.llm_factory import LLMFactory

            # Simulate agent instantiation for all enabled configs
            configs = get_enabled_agent_configs()
            errors = []
            for role, config in configs.items():
                try:
                    # Create a dummy LLM using environment-based configuration
                    dummy_llm = LLMFactory.create_from_environment()

                    # Use the real singleton tool registry
                    from kickai.agents.tool_registry import initialize_tool_registry
                    dummy_tools = initialize_tool_registry()

                    # Create a mock team memory
                    class MockTeamMemory:
                        def get_memory(self):
                            return None
                        def store_conversation(self, *args, **kwargs):
                            pass

                    agent_context = AgentContext(
                        role=role,
                        team_id="TEST",
                        llm=dummy_llm,
                        tool_registry=dummy_tools,
                        config=config,
                        team_memory=MockTeamMemory()
                    )
                    agent = ConfigurableAgent(agent_context)
                    logger.info(f"✅ Agent {role} initialized successfully")
                except Exception as e:
                    logger.error(f"Agent initialization failed for role {role}: {e}")
                    errors.append(f"{role}: {e}")
            if errors:
                return CheckResult(
                    name=self.name,
                    status=CheckStatus.FAILED,
                    category=self.category,
                    message="Some agents failed to initialize.",
                    details={"errors": errors}
                )
            return CheckResult(
                name=self.name,
                status=CheckStatus.PASSED,
                category=self.category,
                message="All agents initialized successfully."
            )
        except Exception as e:
            logger.error(f"AgentInitializationCheck failed: {e}")
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAILED,
                category=self.category,
                message=f"AgentInitializationCheck failed: {e}",
                details={"error": str(e)}
            )
