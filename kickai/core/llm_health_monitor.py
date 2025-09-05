"""
LLM Health Monitor with CrewAI Native Rate-Limited Calls

This module provides continuous monitoring of LLM connectivity using
CrewAI's native LLM calls with proper rate limiting. It will stop the
bot if LLM authentication fails during runtime.

Features:
- CrewAI native LLM calls only (no direct litellm)
- Comprehensive rate limiting integration
- Thread-safe health monitoring
- Async/await compatibility
- Production-ready error handling
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime

from kickai.config.llm_config import get_llm_config

logger = logging.getLogger(__name__)


class LLMHealthMonitor:
    """
    Continuous LLM health monitor that stops the bot if LLM fails.

    This monitor runs in the background and checks LLM connectivity
    periodically. If LLM authentication fails, it will trigger a
    shutdown callback to stop the bot gracefully.
    """

    def __init__(self, check_interval_seconds: int = 300):  # Check every 5 minutes
        self.check_interval = check_interval_seconds
        self.is_running = False
        self.shutdown_callback: Callable | None = None
        self.last_check_time: datetime | None = None
        self.consecutive_failures = 0
        self.max_consecutive_failures = 2  # Allow 2 failures before stopping

        logger.info(f"LLM Health Monitor initialized with {check_interval_seconds}s check interval")

    def set_shutdown_callback(self, callback: Callable) -> None:
        """Set the callback function to call when LLM fails."""
        self.shutdown_callback = callback
        logger.info("Shutdown callback set for LLM health monitor")

    async def start_monitoring(self) -> None:
        """Start the LLM health monitoring loop."""
        if self.is_running:
            logger.warning("LLM Health Monitor is already running")
            return

        self.is_running = True
        logger.info("🚀 Starting LLM Health Monitor...")

        try:
            while self.is_running:
                await self._check_llm_health()
                await asyncio.sleep(self.check_interval)
        except asyncio.CancelledError:
            logger.info("LLM Health Monitor cancelled")
        except Exception as e:
            logger.error(f"Error in LLM Health Monitor: {e}")
            # If the monitor itself fails, we should still try to stop the bot
            if self.shutdown_callback:
                await self._trigger_shutdown("LLM Health Monitor error")
        finally:
            self.is_running = False
            logger.info("LLM Health Monitor stopped")

    async def stop_monitoring(self) -> None:
        """Stop the LLM health monitoring loop."""
        self.is_running = False
        logger.info("🛑 LLM Health Monitor stop requested")

    async def _check_llm_health(self) -> None:
        """Perform a single LLM health check using CrewAI native calls."""
        try:
            start_time = datetime.now()
            self.last_check_time = start_time

            logger.debug("🔍 Performing CrewAI native LLM health check...")

            # Use CrewAI LLM configuration for health checks
            llm_config = get_llm_config()

            # Test connection using CrewAI native async method
            connection_success = await llm_config.test_connection_async()

            if not connection_success:
                raise Exception("CrewAI LLM connection test failed")

            # If we get here, the check passed
            if self.consecutive_failures > 0:
                logger.info(
                    f"✅ CrewAI LLM health check passed after {self.consecutive_failures} consecutive failures"
                )
                self.consecutive_failures = 0

            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"✅ CrewAI LLM health check passed in {duration:.2f}s")

        except Exception as e:
            self.consecutive_failures += 1
            logger.error(
                f"❌ CrewAI LLM health check failed (attempt {self.consecutive_failures}/{self.max_consecutive_failures}): {e}"
            )

            if self.consecutive_failures >= self.max_consecutive_failures:
                await self._trigger_shutdown(
                    f"CrewAI LLM authentication failed {self.consecutive_failures} times consecutively"
                )

    async def _test_crewai_connectivity(self, llm_config) -> None:
        """Test CrewAI LLM connectivity with rate limiting."""
        try:
            # Use the main LLM for testing
            test_llm = llm_config.main_llm

            # Simple test prompt
            test_prompt = "Health check - respond with 'OK'"

            # Check rate limiting before making request
            if hasattr(llm_config, "rate_limit_handler"):
                if not llm_config.rate_limit_handler.can_make_request(llm_config.ai_provider):
                    wait_time = llm_config.rate_limit_handler.get_wait_time(llm_config.ai_provider)
                    if wait_time > 0:
                        logger.debug(f"Waiting {wait_time:.2f}s due to rate limiting")
                        await asyncio.sleep(wait_time)

            # Make the request using CrewAI native async method
            if hasattr(test_llm, "ainvoke"):
                response = await test_llm.ainvoke(test_prompt)
            elif hasattr(test_llm, "invoke"):
                # Fallback to sync method in thread pool
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, test_llm.invoke, test_prompt)
            else:
                raise Exception("LLM does not support invoke or ainvoke methods")

            # Record the request for rate limiting
            if hasattr(llm_config, "rate_limit_handler"):
                llm_config.rate_limit_handler.record_request(llm_config.ai_provider)

            if not response or len(str(response).strip()) == 0:
                raise Exception("Empty response from CrewAI LLM")

        except Exception as e:
            raise Exception(f"CrewAI LLM connectivity test failed: {e!s}")

    async def _test_llm_fallback_connectivity(self, llm) -> None:
        """Fallback connectivity test for non-standard LLM types."""
        try:
            if hasattr(llm, "ainvoke"):
                test_prompt = "Health check - respond with 'OK'"
                response = await llm.ainvoke(test_prompt)

                if not response or len(str(response)) == 0:
                    raise Exception("Empty response from LLM")
            elif hasattr(llm, "invoke"):
                # Fallback to sync in thread pool
                test_prompt = "Health check - respond with 'OK'"
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, llm.invoke, test_prompt)

                if not response or len(str(response)) == 0:
                    raise Exception("Empty response from LLM")
            else:
                raise Exception(f"Unknown LLM type: {type(llm).__name__}")

        except Exception as e:
            raise Exception(f"LLM connectivity test failed: {e!s}")

    async def _trigger_shutdown(self, reason: str) -> None:
        """Trigger bot shutdown due to CrewAI LLM failure."""
        logger.error(f"🚫 CRITICAL: Triggering bot shutdown due to CrewAI LLM failure: {reason}")
        logger.error(
            f"📊 Health Monitor Status: consecutive_failures={self.consecutive_failures}, max_allowed={self.max_consecutive_failures}"
        )

        if self.shutdown_callback:
            try:
                logger.info("🔄 Executing shutdown callback...")
                await self.shutdown_callback()
                logger.info("✅ Shutdown callback completed successfully")
            except Exception as e:
                logger.error(f"❌ Error in shutdown callback: {e}")
        else:
            logger.error("❌ No shutdown callback set - cannot stop bot gracefully")
            logger.error("🚨 Forcing system exit due to critical CrewAI LLM failure")
            # Force exit if no callback is available
            import sys

            sys.exit(1)

    def get_status(self) -> dict:
        """Get comprehensive monitor status with CrewAI integration details."""
        try:
            from kickai.config.llm_config import get_llm_config

            llm_config = get_llm_config()
            provider_info = {
                "ai_provider": llm_config.ai_provider.value,
                "model": llm_config.default_model,
                "rate_limiting_enabled": hasattr(llm_config, "rate_limit_handler"),
            }
        except Exception as e:
            provider_info = {
                "ai_provider": "unknown",
                "model": "unknown",
                "rate_limiting_enabled": False,
                "error": str(e),
            }

        return {
            "monitor_status": {
                "is_running": self.is_running,
                "last_check_time": self.last_check_time.isoformat()
                if self.last_check_time
                else None,
                "consecutive_failures": self.consecutive_failures,
                "max_consecutive_failures": self.max_consecutive_failures,
                "check_interval_seconds": self.check_interval,
                "health": "healthy" if self.consecutive_failures == 0 else "unhealthy",
            },
            "llm_provider": provider_info,
            "integration": {
                "uses_crewai_native_calls": True,
                "bypasses_litellm": True,
                "rate_limiting_integrated": True,
            },
        }


# Global instance
_llm_monitor: LLMHealthMonitor | None = None


def get_llm_monitor() -> LLMHealthMonitor:
    """Get the global LLM health monitor instance."""
    global _llm_monitor
    if _llm_monitor is None:
        _llm_monitor = LLMHealthMonitor()
    return _llm_monitor


async def start_llm_monitoring(shutdown_callback: Callable) -> None:
    """Start LLM health monitoring."""
    monitor = get_llm_monitor()
    monitor.set_shutdown_callback(shutdown_callback)
    await monitor.start_monitoring()


async def stop_llm_monitoring() -> None:
    """Stop LLM health monitoring."""
    global _llm_monitor
    if _llm_monitor:
        await _llm_monitor.stop_monitoring()
        _llm_monitor = None
