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
            from kickai.agents.configurable_agent import ConfigurableAgent
            from kickai.config.agents import get_enabled_agent_configs

            # Simulate agent instantiation for all enabled configs
            # Use default context for validation
            context = {
                "team_name": "KICKAI",
                "team_id": "KAI",
                "chat_type": "main",
                "user_role": "public",
                "username": "user",
            }
            configs = get_enabled_agent_configs(context)
            errors = []
            for role, config in configs.items():
                try:
                    # Create agent using the correct constructor
                    agent = ConfigurableAgent(agent_role=role, team_id="TEST")
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
                    details={"errors": errors},
                )
            return CheckResult(
                name=self.name,
                status=CheckStatus.PASSED,
                category=self.category,
                message="All agents initialized successfully.",
            )
        except Exception as e:
            logger.error(f"AgentInitializationCheck failed: {e}")
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAILED,
                category=self.category,
                message=f"AgentInitializationCheck failed: {e}",
                details={"error": str(e)},
            )
