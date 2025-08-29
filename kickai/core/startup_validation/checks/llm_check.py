"""
LLM Provider Health Check

This module provides health checks for LLM provider connectivity and configuration.
"""

import asyncio
import os
from typing import Any, Dict

from loguru import logger

from kickai.core.startup_validation.checks.base_check import BaseCheck
from kickai.core.startup_validation.reporting import CheckResult, CheckStatus, CheckCategory
from kickai.core.config import get_settings
from kickai.core.enums import AIProvider


class LLMProviderCheck(BaseCheck):
    """Health check for LLM provider connectivity and configuration."""

    name = "LLM Provider Check"
    category = CheckCategory.LLM
    description = "Validates LLM provider configuration and connectivity"

    async def execute(self, context: Dict[str, Any] = None) -> CheckResult:
        """Execute LLM provider health check."""
        start_time = asyncio.get_event_loop().time()

        try:
            config = get_settings()

            # Validate provider configuration
            provider = config.ai_provider
            logger.info(f"🔧 Validating LLM provider: {provider.value}")

            # Check API key for the configured provider
            api_key = config.get_ai_api_key()
            if not api_key:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"API key not configured for {provider.value}",
                    details={
                        "provider": provider.value,
                        "error": f"API key required for {provider.value} provider"
                    },
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                )

            # Validate model configuration
            if not config.ai_model_simple and not config.ai_model_advanced:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="No AI models configured",
                    details={
                        "provider": provider.value,
                        "error": "AI_MODEL_SIMPLE or AI_MODEL_ADVANCED must be configured"
                    },
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                )

            # Test connectivity based on provider
            connectivity_ok = await self._test_connectivity(provider, config)
            if not connectivity_ok:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"{provider.value} API connectivity test failed",
                    details={
                        "provider": provider.value,
                        "api_key_present": bool(api_key),
                        "error": f"Failed to connect to {provider.value} API"
                    },
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                )

            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message=f"{provider.value} LLM configuration and connectivity validated",
                details={
                    "provider": provider.value,
                    "api_key_present": bool(api_key),
                    "models": {
                        "simple": config.ai_model_simple,
                        "advanced": config.ai_model_advanced,
                        "nlp": config.ai_model_nlp
                    },
                    "connectivity": "OK"
                },
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            )

        except Exception as e:
            logger.error(f"LLM CHECK FAILURE: {e}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Exception during LLM check: {e}",
                error=e,
                details={"error_type": type(e).__name__},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            )

    async def _test_connectivity(self, provider: AIProvider, config) -> bool:
        """Test connectivity for the configured provider."""
        try:
            from kickai.config.llm_config import get_llm_config
            
            # Use the proper LLM configuration system
            llm_config = get_llm_config()
            
            # Create a test LLM with minimal tokens
            test_llm = llm_config._create_llm(
                temperature=0.1,
                max_tokens=10,
                use_case="connectivity_test"
            )
            
            # Test with simple message using CrewAI LLM API
            response = test_llm.call("test")
            return bool(response and len(str(response).strip()) > 0)
            
        except Exception as e:
            logger.error(f"{provider.value} connectivity test failed: {e}")
            return False
