"""
LLM Provider Check

This module provides LLM provider validation health checks.
"""

import asyncio
import logging
import os
from typing import Any

from kickai.core.config import get_settings

# Temporarily disabled due to enum mismatch
# from kickai.utils.llm_factory import LLMFactory
from ..reporting import CheckCategory, CheckResult, CheckStatus
from .base_check import BaseCheck

logger = logging.getLogger(__name__)


class LLMProviderCheck(BaseCheck):
    """Check LLM provider configuration and connectivity."""

    name = "LLM Provider"
    category = CheckCategory.LLM
    description = "Validates LLM provider configuration and connectivity"

    async def execute(self, context: dict[str, Any] | None = None) -> CheckResult:
        start_time = asyncio.get_event_loop().time()

        try:
            get_settings()

            # Validate Groq configuration and connectivity
            provider_str = os.getenv("AI_PROVIDER", "groq")

            if provider_str != "groq":
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"AI_PROVIDER must be 'groq', got '{provider_str}'",
                    details={
                        "provider": provider_str,
                        "required": "groq",
                        "error": "System configured for Groq only"
                    },
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                )

            # Check Groq API key
            groq_api_key = os.getenv("GROQ_API_KEY", "")
            if not groq_api_key:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="GROQ_API_KEY not configured",
                    details={
                        "provider": provider_str,
                        "error": "GROQ_API_KEY environment variable is required"
                    },
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                )

            # Test actual Groq connectivity
            connectivity_ok = await self._test_groq_connectivity()
            if not connectivity_ok:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="Groq API connectivity test failed",
                    details={
                        "provider": provider_str,
                        "api_key_present": bool(groq_api_key),
                        "error": "Failed to connect to Groq API"
                    },
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                )

            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message="Groq LLM configuration and connectivity validated",
                details={
                    "provider": provider_str,
                    "api_key_present": bool(groq_api_key),
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

    async def _test_groq_connectivity(self) -> bool:
        """Test actual Groq API connectivity."""
        try:
            from kickai.core.enums import AIProvider
            from kickai.utils.llm_factory import LLMConfig, LLMFactory

            config = LLMConfig(
                provider=AIProvider.GROQ,
                model_name="llama3-8b-instruct",
                api_key=os.getenv("GROQ_API_KEY", ""),
                temperature=0.1,
                timeout_seconds=10,
                max_retries=1
            )

            llm = LLMFactory.create_llm(config)
            # Test with simple message
            response = llm.invoke([{"role": "user", "content": "test"}])
            return bool(response)
        except Exception as e:
            logger.error(f"Groq connectivity test failed: {e}")
            return False
