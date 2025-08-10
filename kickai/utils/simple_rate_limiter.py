"""
Simple Universal Rate Limiter for KICKAI

A straightforward, easy-to-understand rate limiter that works with any LLM provider.
Designed for simplicity, reliability, and ease of debugging.
"""

import logging
import threading
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SimpleUniversalRateLimiter:
    """
    Simple, thread-safe rate limiter that works with any LLM provider.
    
    Uses conservative limits with safety margins to prevent rate limit errors.
    Easy to understand, debug, and configure.
    """
    
    # Provider-specific limits with 20% safety margins
    PROVIDER_LIMITS = {
        "groq": {
            "max_rpm": 800,      # 20% safety margin from 1000 RPM
            "max_tpm": 200000,   # Conservative for 8b-instant (250K actual)
            "max_tpm_70b": 240000, # Conservative for 70b-versatile (300K actual)
            "wait_time": 1.0,
            "avg_tokens": 100    # Average tokens per request estimate
        },
        "openai": {
            "max_rpm": 500,      # Conservative estimate
            "max_tpm": 80000,    # Conservative estimate
            "wait_time": 1.0,
            "avg_tokens": 100
        },
        "gemini": {
            "max_rpm": 300,      # Conservative estimate
            "max_tpm": 60000,    # Conservative estimate
            "wait_time": 1.0,
            "avg_tokens": 100
        },
        "ollama": {
            "max_rpm": 1000,     # Local - no external limits
            "max_tpm": 999999,   # Local - no external limits
            "wait_time": 0.1,    # Minimal wait for local
            "avg_tokens": 100
        }
    }
    
    def __init__(self):
        """Initialize the rate limiter with thread-safe tracking."""
        self._lock = threading.Lock()
        self._request_counts = {}  # provider -> count
        self._token_counts = {}    # provider -> token count
        self._reset_times = {}     # provider -> reset time
        self._last_requests = {}   # provider -> last request time
        
        logger.info("🚀 SimpleUniversalRateLimiter initialized")
    
    def detect_provider(self, model_name: str = None, ai_provider_config: str = None) -> str:
        """
        Simple provider detection from model name or config.
        
        Args:
            model_name: The model name (e.g., "groq/llama-3.1-8b-instant")
            ai_provider_config: Explicit provider config
            
        Returns:
            str: Provider name (groq, openai, gemini, ollama, unknown)
        """
        # Use explicit config first
        if ai_provider_config:
            provider = ai_provider_config.lower().strip()
            if provider in self.PROVIDER_LIMITS:
                return provider
        
        # Auto-detect from model name
        if model_name:
            model_lower = model_name.lower()
            if "groq/" in model_lower:
                return "groq"
            elif "gpt-" in model_lower or "openai/" in model_lower:
                return "openai"
            elif "gemini" in model_lower:
                return "gemini"
            elif "ollama/" in model_lower:
                return "ollama"
            elif "llama" in model_lower:
                return "groq"  # Default llama models to groq
        
        raise ValueError(f"Unknown provider for model: {model_name}. Supported providers: groq, openai, gemini, ollama")
    
    def get_provider_limits(self, provider: str, model_name: str = None) -> Dict[str, Any]:
        """
        Get rate limits for a specific provider and model.
        
        Args:
            provider: Provider name
            model_name: Optional model name for provider-specific adjustments
            
        Returns:
            Dict with max_rpm, max_tpm, wait_time, avg_tokens
        """
        if provider not in self.PROVIDER_LIMITS:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: {list(self.PROVIDER_LIMITS.keys())}")
        
        limits = self.PROVIDER_LIMITS[provider].copy()
        
        # Groq model-specific TPM limits
        if provider == "groq" and model_name:
            if "70b" in model_name.lower():
                limits["max_tpm"] = limits["max_tpm_70b"]
                logger.debug(f"Using 70B model TPM limit: {limits['max_tpm']}")
        
        return limits
    
    def _reset_counters_if_needed(self, provider: str) -> None:
        """Reset counters if the time window has passed."""
        current_time = time.time()
        
        # Initialize if first time
        if provider not in self._reset_times:
            self._reset_times[provider] = current_time + 60  # 1 minute window
            self._request_counts[provider] = 0
            self._token_counts[provider] = 0
        
        # Reset if minute has passed
        if current_time >= self._reset_times[provider]:
            self._request_counts[provider] = 0
            self._token_counts[provider] = 0
            self._reset_times[provider] = current_time + 60
            logger.debug(f"Reset counters for {provider}")
    
    def can_make_request(self, provider: str, model_name: str = None, estimated_tokens: int = None) -> tuple[bool, str]:
        """
        Check if a request can be made without hitting rate limits.
        
        Args:
            provider: Provider name
            model_name: Optional model name
            estimated_tokens: Optional token estimate for this request
            
        Returns:
            tuple: (can_make_request: bool, reason: str)
        """
        with self._lock:
            self._reset_counters_if_needed(provider)
            
            limits = self.get_provider_limits(provider, model_name)
            current_requests = self._request_counts.get(provider, 0)
            current_tokens = self._token_counts.get(provider, 0)
            
            # Use provided token estimate or default
            tokens_for_request = estimated_tokens or limits["avg_tokens"]
            
            # Check RPM limit
            if current_requests >= limits["max_rpm"]:
                return False, f"RPM limit reached: {current_requests}/{limits['max_rpm']}"
            
            # Check TPM limit
            if current_tokens + tokens_for_request > limits["max_tpm"]:
                return False, f"TPM limit would be exceeded: {current_tokens + tokens_for_request}/{limits['max_tpm']}"
            
            return True, "OK"
    
    def record_request(self, provider: str, model_name: str = None, actual_tokens: int = None) -> None:
        """
        Record that a request was made.
        
        Args:
            provider: Provider name
            model_name: Optional model name
            actual_tokens: Actual tokens used (or estimated if not known)
        """
        with self._lock:
            self._reset_counters_if_needed(provider)
            
            limits = self.get_provider_limits(provider, model_name)
            tokens_used = actual_tokens or limits["avg_tokens"]
            
            # Update counters
            self._request_counts[provider] = self._request_counts.get(provider, 0) + 1
            self._token_counts[provider] = self._token_counts.get(provider, 0) + tokens_used
            self._last_requests[provider] = time.time()
            
            logger.debug(f"Recorded request for {provider}: "
                        f"requests={self._request_counts[provider]}/{limits['max_rpm']}, "
                        f"tokens={self._token_counts[provider]}/{limits['max_tpm']}")
    
    def wait_if_needed(self, provider: str, model_name: str = None, estimated_tokens: int = None) -> None:
        """
        Wait if necessary to avoid hitting rate limits, then record the request.
        
        This is the main method that should be called before making LLM requests.
        
        Args:
            provider: Provider name
            model_name: Optional model name
            estimated_tokens: Optional token estimate for this request
        """
        can_proceed, reason = self.can_make_request(provider, model_name, estimated_tokens)
        
        if not can_proceed:
            limits = self.get_provider_limits(provider, model_name)
            wait_time = limits["wait_time"]
            
            logger.info(f"⏳ Rate limit approached for {provider}: {reason}. Waiting {wait_time}s...")
            time.sleep(wait_time)
        
        # Record the request
        self.record_request(provider, model_name, estimated_tokens)
    
    def get_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current rate limiting status for all providers.
        
        Returns:
            Dict with provider status information
        """
        status = {}
        
        with self._lock:
            for provider in self._request_counts:
                self._reset_counters_if_needed(provider)
                limits = self.get_provider_limits(provider)
                
                status[provider] = {
                    "requests": self._request_counts.get(provider, 0),
                    "max_requests": limits["max_rpm"],
                    "tokens": self._token_counts.get(provider, 0),
                    "max_tokens": limits["max_tpm"],
                    "last_request": self._last_requests.get(provider, 0),
                    "next_reset": self._reset_times.get(provider, 0)
                }
        
        return status


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter() -> SimpleUniversalRateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = SimpleUniversalRateLimiter()
    return _rate_limiter