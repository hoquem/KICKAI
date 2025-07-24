"""
LLM Health Monitor

This module provides continuous monitoring of LLM connectivity and will
stop the bot if LLM authentication fails during runtime.
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime

from kickai.utils.llm_factory import LLMFactory

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
        """Perform a single LLM health check."""
        try:
            start_time = datetime.now()
            self.last_check_time = start_time

            logger.debug("🔍 Performing LLM health check...")

            # Create LLM using the factory
            llm = LLMFactory.create_from_environment()

            # Test actual authentication
            if isinstance(llm, str):
                await self._test_litellm_connectivity(llm)
            else:
                await self._test_llm_connectivity(llm)

            # If we get here, the check passed
            if self.consecutive_failures > 0:
                logger.info(f"✅ LLM health check passed after {self.consecutive_failures} consecutive failures")
                self.consecutive_failures = 0

            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"✅ LLM health check passed in {duration:.2f}s")

        except Exception as e:
            self.consecutive_failures += 1
            logger.error(f"❌ LLM health check failed (attempt {self.consecutive_failures}/{self.max_consecutive_failures}): {e}")

            if self.consecutive_failures >= self.max_consecutive_failures:
                await self._trigger_shutdown(f"LLM authentication failed {self.consecutive_failures} times consecutively")

    async def _test_litellm_connectivity(self, llm_string: str) -> None:
        """Test LiteLLM connectivity with actual API call."""
        try:
            import litellm

            # Simple test prompt
            test_prompt = "Health check - respond with 'OK'"

            response = await litellm.acompletion(
                model=llm_string,
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=5,
                temperature=0
            )

            if not response or not response.choices or len(response.choices) == 0:
                raise Exception("Empty response from LLM")

            content = response.choices[0].message.content
            if not content or len(content.strip()) == 0:
                raise Exception("Empty content in LLM response")

        except Exception as e:
            raise Exception(f"LiteLLM connectivity test failed: {e!s}")

    async def _test_llm_connectivity(self, llm) -> None:
        """Test other LLM types connectivity."""
        try:
            if hasattr(llm, 'ainvoke'):
                test_prompt = "Health check - respond with 'OK'"
                response = await llm.ainvoke(test_prompt)

                if not response or len(str(response)) == 0:
                    raise Exception("Empty response from LLM")
            else:
                raise Exception(f"Unknown LLM type: {type(llm).__name__}")

        except Exception as e:
            raise Exception(f"LLM connectivity test failed: {e!s}")

    async def _trigger_shutdown(self, reason: str) -> None:
        """Trigger bot shutdown due to LLM failure."""
        logger.error(f"🚫 CRITICAL: Triggering bot shutdown due to LLM failure: {reason}")

        if self.shutdown_callback:
            try:
                await self.shutdown_callback()
            except Exception as e:
                logger.error(f"Error in shutdown callback: {e}")
        else:
            logger.error("No shutdown callback set - cannot stop bot gracefully")
            # Force exit if no callback is available
            import sys
            sys.exit(1)

    def get_status(self) -> dict:
        """Get current monitor status."""
        return {
            'is_running': self.is_running,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'consecutive_failures': self.consecutive_failures,
            'max_consecutive_failures': self.max_consecutive_failures,
            'check_interval_seconds': self.check_interval
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
