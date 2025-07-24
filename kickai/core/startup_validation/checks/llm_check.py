"""
LLM Provider Check

This module provides LLM provider validation health checks.
"""

import asyncio
import logging
import os
from typing import Any

from kickai.core.settings import get_settings
from kickai.utils.llm_factory import LLMFactory

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

            # Test LLM connectivity using LLMFactory
            try:
                # Get provider and model from environment
                provider_str = os.getenv('AI_PROVIDER', 'gemini')
                if provider_str == 'ollama':
                    model_name = os.getenv('OLLAMA_MODEL', 'llama2')
                else:
                    model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

                # Create LLM using the factory
                llm = LLMFactory.create_from_environment()

                # CRITICAL: Test actual authentication with a real API call
                if isinstance(llm, str):
                    # For LiteLLM string-based LLMs, we need to test actual connectivity
                    try:
                        import litellm

                        # Test with a simple prompt to verify API key and connectivity
                        test_prompt = "Hello, this is a connectivity test. Please respond with 'OK' if you can see this message."

                        # Use litellm directly to test the model string
                        response = await litellm.acompletion(
                            model=llm,
                            messages=[{"role": "user", "content": test_prompt}],
                            max_tokens=10,
                            temperature=0
                        )

                        if response and response.choices and len(response.choices) > 0:
                            return CheckResult(
                                name=self.name,
                                category=self.category,
                                status=CheckStatus.PASSED,
                                message=f"LLM authentication successful with {provider_str}",
                                details={
                                    'provider': provider_str,
                                    'model': llm,
                                    'response_length': len(str(response.choices[0].message.content)),
                                    'note': 'Real API authentication test passed'
                                },
                                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                            )
                        else:
                            return CheckResult(
                                name=self.name,
                                category=self.category,
                                status=CheckStatus.FAILED,
                                message="LLM returned empty response - authentication may have failed",
                                details={'provider': provider_str, 'model': llm},
                                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                            )

                    except Exception as auth_error:
                        # This is a CRITICAL failure - API key is invalid or service is down
                        logger.error(f"CRITICAL LLM AUTHENTICATION FAILURE: {auth_error}")
                        return CheckResult(
                            name=self.name,
                            category=self.category,
                            status=CheckStatus.FAILED,
                            message=f"CRITICAL: LLM authentication failed - API key invalid or service unavailable: {auth_error!s}",
                            error=auth_error,
                            details={
                                'provider': provider_str,
                                'model': llm,
                                'error_type': type(auth_error).__name__,
                                'critical': True
                            },
                            duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                        )

                # For other LLM types, try to validate
                if hasattr(llm, 'invoke'):
                    # Test with a simple prompt
                    test_prompt = "Hello, this is a connectivity test. Please respond with 'OK' if you can see this message."
                    try:
                        response = await llm.ainvoke(test_prompt)
                        if response and len(str(response)) > 0:
                            return CheckResult(
                                name=self.name,
                                category=self.category,
                                status=CheckStatus.PASSED,
                                message=f"LLM connectivity successful with {provider_str}",
                                details={
                                    'provider': provider_str,
                                    'model': model_name,
                                    'response_length': len(str(response))
                                },
                                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                            )
                        else:
                            return CheckResult(
                                name=self.name,
                                category=self.category,
                                status=CheckStatus.FAILED,
                                message="LLM returned empty response - authentication may have failed",
                                details={'provider': provider_str, 'model': model_name},
                                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                            )
                    except Exception as e:
                        # This is a CRITICAL failure
                        logger.error(f"CRITICAL LLM AUTHENTICATION FAILURE: {e}")
                        return CheckResult(
                            name=self.name,
                            category=self.category,
                            status=CheckStatus.FAILED,
                            message=f"CRITICAL: LLM authentication failed: {e!s}",
                            error=e,
                            details={
                                'provider': provider_str,
                                'model': model_name,
                                'error_type': type(e).__name__,
                                'critical': True
                            },
                            duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                        )

                # If we get here, we couldn't test the LLM properly
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="Could not perform LLM authentication test - unknown LLM type",
                    details={'provider': provider_str, 'model': model_name, 'llm_type': type(llm).__name__},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )

            except Exception as e:
                logger.error(f"CRITICAL LLM INITIALIZATION FAILURE: {e}")
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"CRITICAL: LLM initialization failed: {e!s}",
                    error=e,
                    details={'error_type': type(e).__name__, 'critical': True},
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )

        except Exception as e:
            logger.error(f"CRITICAL LLM CHECK FAILURE: {e}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"CRITICAL: Exception during LLM check: {e}",
                error=e,
                details={'error_type': type(e).__name__, 'critical': True},
                duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )
