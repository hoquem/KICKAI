"""
Optimized Agent Prompts with YAML Integration

This module provides additional LLM-specific optimizations on top of the base
YAML configurations. It enhances the YAML-based prompts with model-specific
optimizations for llama3.1:8b-instruct-q4_k_m.
"""

from typing import Any

from loguru import logger

from kickai.config.agents import get_agent_config, get_llm_optimizations, get_performance_rules
from kickai.core.enums import AgentRole


class OptimizedAgentPrompts:
    """Enhanced prompts with YAML integration and model-specific optimizations."""

    @staticmethod
    def get_optimized_prompt_for_agent(agent_role: AgentRole, context: dict[str, Any]) -> str:
        """Get optimized prompt for agent with YAML integration and additional optimizations."""
        try:
            # Get the base configuration from YAML with processed templates
            agent_config = get_agent_config(agent_role, context)

            # Apply additional LLM-specific optimizations
            enhanced_backstory = OptimizedAgentPrompts._apply_enhanced_optimizations(
                agent_config.backstory,
                agent_role,
                context
            )

            logger.debug(f"✅ Generated enhanced optimized prompt for {agent_role.value}")
            return enhanced_backstory

        except Exception as e:
            logger.error(f"❌ Failed to generate optimized prompt for {agent_role.value}: {e}")
            # Return a basic fallback prompt
            return f"You are a {agent_role.value} agent. Please help the user with their request."

    @staticmethod
    def _apply_enhanced_optimizations(backstory: str, agent_role: AgentRole, context: dict[str, Any]) -> str:
        """Apply enhanced LLM-specific optimizations to the YAML-based backstory."""

        # Get LLM optimization settings from YAML
        llm_optimizations = get_llm_optimizations()
        performance_rules = get_performance_rules()

        # Model-specific optimizations for llama3.1:8b-instruct-q4_k_m
        # 5-Agent System Optimizations for llama3.1:8b-instruct-q4_k_m
        model_optimizations = {
            AgentRole.MESSAGE_PROCESSOR: """
🚨 ENHANCED MESSAGE PROCESSING RULES FOR LLAMA3.1:
- Use temperature 0.1 for precise routing decisions
- Apply single-step routing - never chain agent calls
- Maintain conversation context throughout interaction
- Use get_active_players for MAIN chat /list commands
- Use get_all_players for LEADERSHIP chat /list commands
- Always validate user context before making tool calls
- Handle communication and analytics functions as absorbed capabilities
- Direct tool calls only - no agent-to-agent communication
""",
            AgentRole.PLAYER_COORDINATOR: """
🚨 ENHANCED PLAYER COORDINATION RULES FOR LLAMA3.1:
- Use temperature 0.1 for precise data handling
- Apply strict anti-hallucination measures
- Never add or modify player data from tool outputs
- Use exact data returned by tools without enhancement
- Validate player existence before status operations
- Handle onboarding guidance as absorbed capability
- Apply structured response format for consistency
- Manage complete player lifecycle from registration to active status
""",
            AgentRole.HELP_ASSISTANT: """
🚨 ENHANCED HELP RULES FOR LLAMA3.1:
- Use temperature 0.1 for accurate help information
- Apply context-aware help responses
- Never hallucinate commands or capabilities
- Use get_available_commands for accurate command lists
- Provide role-specific help based on user context
- Handle command fallback scenarios as absorbed capability
- Use structured help format for clarity
- Guide users through error recovery and alternative actions
""",
            AgentRole.TEAM_ADMINISTRATOR: """
🚨 ENHANCED TEAM ADMIN RULES FOR LLAMA3.1:
- Use temperature 0.3 for balanced administrative decisions
- Apply proper role-based access control
- Validate team member permissions before operations
- Use structured administrative response format
- Maintain team governance standards
- Handle team member lifecycle management
- Coordinate team configuration and settings
""",
            AgentRole.SQUAD_SELECTOR: """
🚨 ENHANCED SQUAD SELECTION RULES FOR LLAMA3.1:
- Use temperature 0.7 for creative squad combinations
- Apply analytical thinking for player selection
- Consider multiple factors in squad decisions
- Use structured format for squad recommendations
- Balance tactical and practical considerations
- Handle availability management as absorbed capability
- Track player responses and coordinate match preparation
- Manage availability conflicts and updates effectively
"""
        }

        # Add model-specific optimization if available
        if agent_role in model_optimizations:
            backstory += model_optimizations[agent_role]

        # Add performance rules from YAML if not already present
        if performance_rules:
            for rule_name, rule_content in performance_rules.items():
                if rule_name not in backstory:
                    backstory += f"\n\n{rule_content}"

        # Add LLM model information
        model_info = llm_optimizations.get("model", "llama3.1:8b-instruct-q4_k_m")
        if model_info not in backstory:
            backstory += f"\n\n**LLM MODEL**: {model_info} - Optimized for performance and accuracy."

        return backstory

    @staticmethod
    def get_optimized_backstory_for_agent(agent_role: AgentRole, context: dict[str, Any]) -> str:
        """Get optimized backstory for agent with YAML integration."""
        return OptimizedAgentPrompts.get_optimized_prompt_for_agent(agent_role, context)

    @staticmethod
    def get_agent_performance_metrics(agent_role: AgentRole) -> dict[str, Any]:
        """Get performance metrics and settings for a specific agent."""
        try:
            # Get base configuration
            agent_config = get_agent_config(agent_role, {})

            # Get LLM optimizations
            llm_optimizations = get_llm_optimizations()

            return {
                "agent_role": agent_role.value,
                "temperature": agent_config.temperature,
                "max_tokens": agent_config.max_tokens,
                "max_iterations": agent_config.max_iterations,
                "model": llm_optimizations.get("model", "llama3.1:8b-instruct-q4_k_m"),
                "optimization_level": "enhanced",
                "features": [
                    "YAML-based configuration",
                    "Template processing",
                    "Model-specific optimizations",
                    "Performance rules integration",
                    "Context-aware processing"
                ]
            }
        except Exception as e:
            logger.error(f"❌ Failed to get performance metrics for {agent_role.value}: {e}")
            return {
                "agent_role": agent_role.value,
                "error": str(e),
                "optimization_level": "fallback"
            }

    @staticmethod
    def get_system_performance_summary() -> dict[str, Any]:
        """Get overall system performance summary."""
        try:
            llm_optimizations = get_llm_optimizations()
            performance_rules = get_performance_rules()

            return {
                "model": llm_optimizations.get("model", "llama3.1:8b-instruct-q4_k_m"),
                "temperature_settings": llm_optimizations.get("temperature_settings", {}),
                "performance_rules_count": len(performance_rules),
                "optimization_features": [
                    "YAML-based configuration",
                    "Template variable processing",
                    "Agent-specific optimizations",
                    "Model-specific enhancements",
                    "Performance rules integration",
                    "Context-aware processing",
                    "Temperature optimization",
                    "Token efficiency",
                    "Anti-hallucination policies"
                ],
                "integration_status": "fully_integrated"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get system performance summary: {e}")
            return {
                "error": str(e),
                "integration_status": "error"
            }


# Public API functions
def get_optimized_prompt_for_agent(agent_role: AgentRole, context: dict[str, Any]) -> str:
    """Get optimized prompt for agent with YAML integration and enhanced optimizations."""
    return OptimizedAgentPrompts.get_optimized_prompt_for_agent(agent_role, context)

def get_optimized_backstory_for_agent(agent_role: AgentRole, context: dict[str, Any]) -> str:
    """Get optimized backstory for agent with YAML integration."""
    return OptimizedAgentPrompts.get_optimized_backstory_for_agent(agent_role, context)

def get_agent_performance_metrics(agent_role: AgentRole) -> dict[str, Any]:
    """Get performance metrics and settings for a specific agent."""
    return OptimizedAgentPrompts.get_agent_performance_metrics(agent_role)

def get_system_performance_summary() -> dict[str, Any]:
    """Get overall system performance summary."""
    return OptimizedAgentPrompts.get_system_performance_summary()

def is_optimized_prompt_available(agent_role: AgentRole) -> bool:
    """Check if optimized prompt is available for agent."""
    return True  # All agents now support optimized prompts with YAML integration

# Legacy functions for backward compatibility
def get_message_processor_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_message_processor_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.MESSAGE_PROCESSOR, context)

def get_player_coordinator_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_player_coordinator_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.PLAYER_COORDINATOR, context)

def get_help_assistant_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_help_assistant_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.HELP_ASSISTANT, context)

def get_team_administrator_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_team_administrator_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.TEAM_ADMINISTRATION, context)

# Legacy functions removed - system now uses only 5 agents
# Use get_optimized_prompt_for_agent() with appropriate AgentRole

def get_squad_selector_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_squad_selector_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.SQUAD_SELECTOR, context)
