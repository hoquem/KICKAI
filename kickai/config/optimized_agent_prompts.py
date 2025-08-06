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
        model_optimizations = {
            AgentRole.MESSAGE_PROCESSOR: """
🚨 ENHANCED TOOL USAGE RULES FOR LLAMA3.1:
- ALWAYS use EXACT context values - NO placeholders
- Verify tool parameters before calling
- Use structured output format for responses
- Maintain conversation flow with context awareness
- Apply temperature 0.1 for maximum precision
""",
            AgentRole.HELP_ASSISTANT: """
🚨 ENHANCED HELP ASSISTANT RULES FOR LLAMA3.1:
- Use get_available_commands as PRIMARY tool for help
- Return EXACT tool output - NO modifications
- Apply structured response format
- Use temperature 0.1 for consistent help responses
- Maintain context across help interactions
""",
            AgentRole.PLAYER_COORDINATOR: """
🚨 ENHANCED PLAYER COORDINATOR RULES FOR LLAMA3.1:
- Apply ZERO hallucination policy with temperature 0.1
- Use EXACT context values for all tool calls
- Return tool outputs verbatim - NO additions
- Apply structured data format for player information
- Maintain data integrity across all operations
""",
            AgentRole.TEAM_ADMINISTRATION: """
🚨 ENHANCED TEAM ADMIN RULES FOR LLAMA3.1:
- Use temperature 0.3 for balanced administrative decisions
- Apply structured communication format
- Maintain professional tone consistently
- Use appropriate tools for leadership tasks
- Coordinate effectively with other agents
""",
            AgentRole.SQUAD_SELECTOR: """
🚨 ENHANCED SQUAD SELECTION RULES FOR LLAMA3.1:
- Use temperature 0.7 for creative squad combinations
- Apply analytical thinking for player selection
- Consider multiple factors in squad decisions
- Use structured format for squad recommendations
- Balance tactical and practical considerations
""",
            AgentRole.AVAILABILITY_MANAGER: """
🚨 ENHANCED AVAILABILITY RULES FOR LLAMA3.1:
- Use temperature 0.3 for balanced availability management
- Apply structured tracking for player responses
- Maintain accurate availability records
- Coordinate effectively with squad selector
- Use clear communication for availability updates
""",
            AgentRole.COMMUNICATION_MANAGER: """
🚨 ENHANCED COMMUNICATION RULES FOR LLAMA3.1:
- Use temperature 0.3 for consistent communication
- Apply structured message format
- Maintain professional communication standards
- Use appropriate tools for different message types
- Coordinate team communications effectively
""",
            AgentRole.ONBOARDING_AGENT: """
🚨 ENHANCED ONBOARDING RULES FOR LLAMA3.1:
- Use temperature 0.2 for guided user interactions
- Apply step-by-step instruction format
- Maintain helpful and patient tone
- Use structured guidance for registration process
- Ensure smooth user experience
""",
            AgentRole.ANALYTICS_AGENT: """
🚨 ENHANCED ANALYTICS RULES FOR LLAMA3.1:
- Use temperature 0.7 for creative analysis
- Apply structured report format
- Provide data-driven insights
- Use analytical tools effectively
- Present information clearly and concisely
""",
            AgentRole.COMMAND_FALLBACK_AGENT: """
🚨 ENHANCED FALLBACK RULES FOR LLAMA3.1:
- Use temperature 0.5 for balanced fallback responses
- Apply helpful error message format
- Guide users to appropriate resources
- Use get_available_commands for valid options
- Maintain helpful and informative tone
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

def get_onboarding_agent_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_onboarding_agent_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.ONBOARDING_AGENT, context)

def get_squad_selector_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_squad_selector_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.SQUAD_SELECTOR, context)

def get_availability_manager_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_availability_manager_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.AVAILABILITY_MANAGER, context)

def get_communication_manager_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_communication_manager_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.COMMUNICATION_MANAGER, context)

def get_analytics_agent_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_analytics_agent_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.ANALYTICS_AGENT, context)

def get_command_fallback_agent_prompt_legacy() -> str:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_command_fallback_agent_prompt_legacy() - use get_optimized_prompt_for_agent() instead")
    context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
    return get_optimized_prompt_for_agent(AgentRole.COMMAND_FALLBACK_AGENT, context)
