import logging
from .base_check import BaseCheck
from ..reporting import CheckResult, CheckStatus, CheckCategory
from crewai.tools import BaseTool  # <-- Add this import at the top level

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
            from agents.configurable_agent import ConfigurableAgent, AgentCreationContext
            from config.agents import get_enabled_agent_configs, AgentConfig
            from utils.llm_factory import LLMFactory
            # from crewai.tools import BaseTool  # If tool checks are needed, use this import

            # Simulate agent instantiation for all enabled configs
            configs = get_enabled_agent_configs()
            errors = []
            for role, config in configs.items():
                try:
                    # Create a dummy LLM using environment-based configuration
                    dummy_llm = LLMFactory.create_from_environment()
                    dummy_tools = []  # Could be extended to real tool checks
                    agent_context = AgentCreationContext(
                        team_id="TEST",
                        llm=dummy_llm,
                        tools=dummy_tools,
                        config=config,
                        team_memory=None
                    )
                    agent = ConfigurableAgent(agent_context)
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