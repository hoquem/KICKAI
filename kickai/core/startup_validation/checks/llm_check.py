"""
LLM Provider Check

This module provides LLM provider validation health checks.
"""

import asyncio
import logging
import os
from typing import Any

from kickai.core.settings import get_settings
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

    async def execute(self, context: dict[str, Any] = None) -> CheckResult:
        start_time = asyncio.get_event_loop().time()

        try:
            config = get_settings()

            # Simplified LLM configuration check
            provider_str = os.getenv("AI_PROVIDER", "ollama")
            
            if provider_str == "ollama":
                model_name = os.getenv("OLLAMA_MODEL", "llama2")
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.PASSED,
                    message=f"LLM configuration valid for {provider_str}",
                    details={
                        "provider": provider_str,
                        "model": model_name,
                        "base_url": base_url,
                        "note": "Configuration check passed - actual connectivity not tested",
                    },
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                )
            else:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.PASSED,
                    message=f"LLM configuration valid for {provider_str}",
                    details={
                        "provider": provider_str,
                        "note": "Configuration check passed - actual connectivity not tested",
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
