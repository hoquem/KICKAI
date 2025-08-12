"""
Configuration Check

This module provides configuration validation health checks.
"""

import asyncio
import logging
from typing import Any

from kickai.core.config import get_settings

from ..reporting import CheckCategory, CheckResult, CheckStatus
from .base_check import BaseCheck

logger = logging.getLogger(__name__)


class ConfigurationCheck(BaseCheck):
    """Check configuration loading and validation."""

    name = "Configuration Loading"
    category = CheckCategory.CONFIGURATION
    description = "Validates that all required configuration is loaded and accessible"

    async def execute(self, context: dict[str, Any] | None = None) -> CheckResult:
        start_time = asyncio.get_event_loop().time()

        try:
            config = get_settings()

            # Validate essential configuration
            required_fields = ["ai_provider", "ai_max_retries"]
            missing_fields = []
            for field in required_fields:
                if not hasattr(config, field) or getattr(config, field) is None:
                    missing_fields.append(field)

            # Model requirement: either legacy name or simple/advanced pair
            has_legacy = bool(getattr(config, "ai_model_name", None))
            has_pair = bool(getattr(config, "ai_model_simple", None)) and bool(getattr(config, "ai_model_advanced", None))
            if not (has_legacy or has_pair):
                missing_fields.append("AI model configuration (AI_MODEL_SIMPLE & AI_MODEL_ADVANCED or legacy AI_MODEL_NAME)")

            # REMOVED: default_team_id validation - team context should come from execution context

            if missing_fields:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Missing required configuration fields: {missing_fields}",
                    details={"missing_fields": missing_fields},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                )

            # Get actual provider from environment
            import os

            provider_str = os.getenv("AI_PROVIDER", "groq")

            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message="Configuration loaded successfully",
                details={
                    "provider": f"AIProvider.{provider_str.upper()}",
                    "note": "team_id comes from execution context",
                },
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            )
        except Exception as e:
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Exception during configuration check: {e}",
                details={"exception": str(e)},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            )
