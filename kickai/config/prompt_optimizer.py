#!/usr/bin/env python3
"""
Prompt Optimizer for llama3.1:8b-instruct-q4_k_m Model

This module provides functionality to switch between standard and optimized prompts
based on model capabilities and performance requirements.
"""

import os
from typing import Any

from loguru import logger

from kickai.config.agents import AgentConfig, get_agent_config_manager
from kickai.config.optimized_agent_prompts import (
    get_optimized_backstory_for_agent,
    is_optimized_prompt_available,
)
from kickai.core.enums import AgentRole


class PromptOptimizer:
    """Manages switching between standard and optimized prompts."""

    def __init__(self):
        self.config_manager = get_agent_config_manager()
        self.use_optimized = self._should_use_optimized_prompts()
        self.original_configs: dict[AgentRole, AgentConfig] = {}

    def _should_use_optimized_prompts(self) -> bool:
        """Determine if optimized prompts should be used based on environment."""
        # Check for llama3.1:8b-instruct-q4_k_m model
        model_name = os.getenv("AI_MODEL_NAME", "").lower()
        ollama_model = os.getenv("OLLAMA_MODEL", "").lower()

        is_8b_q4km = (
            "llama3.1:8b-instruct-q4_k_m" in model_name or
            "llama3.1:8b-instruct-q4_k_m" in ollama_model
        )

        # Check for resource constraints (8GB RAM indicator)
        context_length = int(os.getenv("OLLAMA_CONTEXT_LENGTH", "2048"))
        is_resource_constrained = context_length <= 1024

        # Check explicit optimization flag
        explicit_optimize = os.getenv("USE_OPTIMIZED_PROMPTS", "").lower() == "true"

        should_optimize = is_8b_q4km or is_resource_constrained or explicit_optimize

        if should_optimize:
            logger.info("🚀 Using optimized prompts for llama3.1:8b-instruct-q4_k_m")
        else:
            logger.info("📝 Using standard prompts")

        return should_optimize

    def apply_optimizations(self) -> None:
        """Apply optimized prompts to all eligible agents."""
        if not self.use_optimized:
            logger.info("Optimized prompts disabled - using standard prompts")
            return

        logger.info("Applying optimized prompts for llama3.1:8b-instruct-q4_k_m...")
        optimized_count = 0

        for role, config in self.config_manager.get_all_configs().items():
            if is_optimized_prompt_available(role):
                # Store original config
                self.original_configs[role] = config

                # Create optimized config
                optimized_config = self._create_optimized_config(config, role)

                # Update in manager
                self.config_manager.update_agent_config(role, optimized_config)
                optimized_count += 1

                logger.debug(f"✅ Optimized prompt applied for {role.value}")

        logger.info(f"🎯 Applied optimized prompts to {optimized_count} agents")

    def _create_optimized_config(self, original_config: AgentConfig, role: AgentRole) -> AgentConfig:
        """Create optimized version of agent config."""
        try:
            # Use default context for optimization
            context = {
                "team_name": "KICKAI",
                "team_id": "KAI",
                "chat_type": "main",
                "user_role": "public",
                "username": "user"
            }
            optimized_backstory = get_optimized_backstory_for_agent(role, context)

            # Fallback to original backstory if optimization fails
            if not optimized_backstory or len(optimized_backstory.strip()) < 50:
                logger.warning(f"Optimized backstory too short for {role.value}, using original")
                optimized_backstory = original_config.backstory

            # Create new config with optimized settings (only use attributes that exist in AgentConfig)
            optimized_config = AgentConfig(
                role=original_config.role,
                goal=self._get_optimized_goal(original_config.goal),
                backstory=optimized_backstory,
                tools=original_config.tools,
                enabled=original_config.enabled,
                max_iterations=min(original_config.max_iterations, 5),  # Reduce iterations
                allow_delegation=False,  # Disable delegation for performance
                verbose=False,  # Reduce verbosity
                temperature=original_config.temperature,
                max_tokens=original_config.max_tokens,
            )

            return optimized_config

        except Exception as e:
            logger.warning(f"Failed to create optimized config for {role.value}: {e}")
            # Return original config with minimal optimizations
            return AgentConfig(
                role=original_config.role,
                goal=original_config.goal,
                backstory=original_config.backstory,
                tools=original_config.tools,
                enabled=original_config.enabled,
                max_iterations=5,  # Still reduce iterations
                allow_delegation=False,  # Still disable delegation
                verbose=False,  # Still reduce verbosity
                temperature=original_config.temperature,
                max_tokens=original_config.max_tokens,
            )

    def _get_optimized_goal(self, original_goal: str) -> str:
        """Create optimized version of agent goal."""
        # Truncate long goals and make them more direct
        if len(original_goal) > 100:
            # Extract key action words
            words = original_goal.split()
            key_words = []
            for word in words[:15]:  # Take first 15 words maximum
                if word.lower() in ['manage', 'coordinate', 'handle', 'provide', 'ensure', 'track', 'analyze', 'optimize']:
                    key_words.append(word)
                elif len(key_words) < 8:
                    key_words.append(word)

            optimized_goal = ' '.join(key_words)
            if not optimized_goal.endswith('.'):
                optimized_goal += '.'

            return optimized_goal

        return original_goal

    def restore_original_prompts(self) -> None:
        """Restore original prompts (useful for testing)."""
        restored_count = 0

        for role, original_config in self.original_configs.items():
            self.config_manager.update_agent_config(role, original_config)
            restored_count += 1

        logger.info(f"🔄 Restored {restored_count} original prompts")
        self.original_configs.clear()

    def get_optimization_status(self) -> dict[str, Any]:
        """Get current optimization status."""
        return {
            "optimized_prompts_enabled": self.use_optimized,
            "model_name": os.getenv("AI_MODEL_NAME", "unknown"),
            "context_length": os.getenv("OLLAMA_CONTEXT_LENGTH", "unknown"),
            "optimized_agents": len(self.original_configs),
            "available_optimizations": sum(1 for role in AgentRole if is_optimized_prompt_available(role))
        }


# Global instance
_prompt_optimizer = None


def get_prompt_optimizer() -> PromptOptimizer:
    """Get the global prompt optimizer instance."""
    global _prompt_optimizer
    if _prompt_optimizer is None:
        _prompt_optimizer = PromptOptimizer()
    return _prompt_optimizer


def apply_model_optimizations() -> None:
    """Apply model-specific optimizations."""
    optimizer = get_prompt_optimizer()
    optimizer.apply_optimizations()


def get_optimization_status() -> dict[str, Any]:
    """Get current optimization status."""
    optimizer = get_prompt_optimizer()
    return optimizer.get_optimization_status()
