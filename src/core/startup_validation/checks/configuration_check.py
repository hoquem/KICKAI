"""
Configuration Check

This module provides configuration validation health checks.
"""

import asyncio
import logging
from typing import Dict, Any

from .base_check import BaseCheck
from ..reporting import CheckResult, CheckCategory, CheckStatus
from core.settings import get_settings

logger = logging.getLogger(__name__)


class ConfigurationCheck(BaseCheck):
    """Check configuration loading and validation."""
    
    name = "Configuration Loading"
    category = CheckCategory.CONFIGURATION
    description = "Validates that all required configuration is loaded and accessible"
    
    async def execute(self, context: Dict[str, Any] = None) -> CheckResult:
        start_time = asyncio.get_event_loop().time()
        
        try:
            config = get_settings()
            
            # Validate essential configuration
            required_fields = [
                'ai_provider', 'google_api_key', 'ai_model_name', 'ai_max_retries'
            ]
            missing_fields = []
            for field in required_fields:
                if not hasattr(config, field) or getattr(config, field) is None:
                    missing_fields.append(field)
            
            if not config.default_team_id:
                missing_fields.append('default_team_id')
            
            if missing_fields:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Missing required configuration fields: {missing_fields}",
                    details={'missing_fields': missing_fields},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            
            # Get actual provider from environment
            import os
            provider_str = os.getenv('AI_PROVIDER', 'gemini')
            
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message="Configuration loaded successfully",
                details={'provider': f'AIProvider.{provider_str.upper()}', 'team_id': config.default_team_id},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )
        except Exception as e:
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Exception during configuration check: {e}",
                details={'exception': str(e)},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            ) 