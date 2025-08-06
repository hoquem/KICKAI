"""
Centralized Ollama API Client

This module provides a robust, production-ready client for interacting with Ollama servers
with proper error handling, resource management, and observability.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any
from urllib.parse import urljoin

import httpx
import structlog
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

try:
    from prometheus_client import Counter, Gauge, Histogram
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


class ConnectionState(Enum):
    """Ollama connection states for circuit breaker"""
    CLOSED = "closed"      # Healthy - requests allowed
    OPEN = "open"          # Unhealthy - requests blocked
    HALF_OPEN = "half_open"  # Testing - limited requests allowed


@dataclass
class OllamaConfig:
    """Configuration for Ollama client"""
    base_url: str
    connection_timeout: float = 30.0
    request_timeout: float = 120.0
    retry_attempts: int = 3
    retry_min_wait: float = 1.0
    retry_max_wait: float = 10.0
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: float = 60.0
    circuit_breaker_half_open_max_calls: int = 3

    def __post_init__(self):
        """Validate configuration"""
        if not self.base_url:
            raise ValueError("base_url is required")
        if not self.base_url.startswith(('http://', 'https://')):
            raise ValueError("base_url must start with http:// or https://")
        self.base_url = self.base_url.rstrip('/')


class CircuitBreaker:
    """Simple circuit breaker implementation for Ollama client"""

    def __init__(self, failure_threshold: int, recovery_timeout: float, half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.failure_count = 0
        self.last_failure_time = 0
        self.state = ConnectionState.CLOSED
        self.half_open_calls = 0

        self.logger = structlog.get_logger(__name__)

    def can_execute(self) -> bool:
        """Check if request can be executed based on circuit breaker state"""
        current_time = time.time()

        if self.state == ConnectionState.CLOSED:
            return True
        elif self.state == ConnectionState.OPEN:
            if current_time - self.last_failure_time > self.recovery_timeout:
                self.state = ConnectionState.HALF_OPEN
                self.half_open_calls = 0
                self.logger.info("circuit_breaker_half_open",
                               failure_count=self.failure_count)
                return True
            return False
        elif self.state == ConnectionState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls

        return False

    def record_success(self):
        """Record successful request"""
        if self.state == ConnectionState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                self.state = ConnectionState.CLOSED
                self.failure_count = 0
                self.logger.info("circuit_breaker_closed", message="Recovery successful")
        elif self.state == ConnectionState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == ConnectionState.HALF_OPEN:
            self.state = ConnectionState.OPEN
            self.logger.warning("circuit_breaker_open",
                              message="Half-open test failed")
        elif self.failure_count >= self.failure_threshold:
            self.state = ConnectionState.OPEN
            self.logger.error("circuit_breaker_open",
                            failure_count=self.failure_count,
                            threshold=self.failure_threshold)


class OllamaClientError(Exception):
    """Base exception for Ollama client errors"""
    pass


class OllamaConnectionError(OllamaClientError):
    """Connection-related errors"""
    pass


class OllamaTimeoutError(OllamaClientError):
    """Timeout-related errors"""
    pass


class OllamaCircuitBreakerError(OllamaClientError):
    """Circuit breaker is open"""
    pass


class OllamaClient:
    """
    Production-ready Ollama API client with circuit breaker, retries, and observability.

    Features:
    - Async/await support with proper resource management
    - Circuit breaker pattern for resilience
    - Exponential backoff retry logic
    - Structured logging and optional Prometheus metrics
    - Comprehensive error handling and sanitization
    - URL validation and security hardening
    """

    def __init__(self, config: OllamaConfig):
        self.config = config
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_failure_threshold,
            recovery_timeout=config.circuit_breaker_recovery_timeout,
            half_open_max_calls=config.circuit_breaker_half_open_max_calls
        )

        # Structured logging
        self.logger = structlog.get_logger(__name__).bind(
            ollama_base_url=config.base_url
        )

        # Optional Prometheus metrics
        if METRICS_AVAILABLE:
            self._init_metrics()
        else:
            self.logger.warning("prometheus_client not available - metrics disabled")

    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        try:
            self.connection_attempts = Counter(
                'ollama_connection_attempts_total',
                'Total Ollama connection attempts',
                ['result', 'operation']
            )
            self.connection_duration = Histogram(
                'ollama_connection_duration_seconds',
                'Ollama connection duration',
                ['operation']
            )
            self.circuit_breaker_state = Gauge(
                'ollama_circuit_breaker_state',
                'Circuit breaker state (0=closed, 1=half_open, 2=open)'
            )
            self.active_connections = Gauge(
                'ollama_active_connections',
                'Number of active Ollama connections'
            )
        except ValueError as e:
            # Metrics already registered, use existing ones
            if "Duplicated timeseries" in str(e):
                self.logger.warning("Metrics already registered, using existing ones")
                # Disable metrics to avoid conflicts
                self.connection_attempts = None
                self.connection_duration = None
                self.circuit_breaker_state = None
                self.active_connections = None
            else:
                raise

    def _update_circuit_breaker_metric(self):
        """Update circuit breaker state metric"""
        if METRICS_AVAILABLE:
            state_map = {
                ConnectionState.CLOSED: 0,
                ConnectionState.HALF_OPEN: 1,
                ConnectionState.OPEN: 2
            }
            self.circuit_breaker_state.set(state_map[self.circuit_breaker.state])

    def _sanitize_error(self, error: Exception) -> dict[str, Any]:
        """Sanitize error information for logging"""
        if isinstance(error, httpx.ConnectError):
            return {
                "error_type": "connection_error",
                "message": "Unable to connect to Ollama server",
                "category": "network"
            }
        elif isinstance(error, httpx.TimeoutException):
            return {
                "error_type": "timeout_error",
                "message": "Request to Ollama server timed out",
                "category": "timeout"
            }
        elif isinstance(error, httpx.HTTPStatusError):
            return {
                "error_type": "http_error",
                "message": f"HTTP {error.response.status_code} from Ollama server",
                "status_code": error.response.status_code,
                "category": "http"
            }
        else:
            return {
                "error_type": "unknown_error",
                "message": "Unknown error occurred",
                "category": "unknown"
            }

    def _safe_url(self, path: str) -> str:
        """Safely construct URL with validation"""
        if not path.startswith('/'):
            path = '/' + path
        return urljoin(self.config.base_url, path)

    async def _execute_with_circuit_breaker(self, operation_name: str, coro):
        """Execute operation with circuit breaker protection"""
        if not self.circuit_breaker.can_execute():
            self._update_circuit_breaker_metric()
            if METRICS_AVAILABLE:
                self.connection_attempts.labels(
                    result='circuit_breaker_open',
                    operation=operation_name
                ).inc()

            self.logger.warning("circuit_breaker_blocked",
                              operation=operation_name,
                              state=self.circuit_breaker.state.value)
            raise OllamaCircuitBreakerError(
                f"Circuit breaker is {self.circuit_breaker.state.value} for operation: {operation_name}"
            )

        start_time = time.time()
        try:
            if METRICS_AVAILABLE:
                self.active_connections.inc()

            result = await coro

            # Success
            duration = time.time() - start_time
            self.circuit_breaker.record_success()
            self._update_circuit_breaker_metric()

            if METRICS_AVAILABLE:
                self.connection_attempts.labels(
                    result='success',
                    operation=operation_name
                ).inc()
                self.connection_duration.labels(operation=operation_name).observe(duration)

            self.logger.info("ollama_operation_success",
                           operation=operation_name,
                           duration_ms=duration * 1000,
                           circuit_breaker_state=self.circuit_breaker.state.value)

            return result

        except Exception as e:
            # Failure
            duration = time.time() - start_time
            self.circuit_breaker.record_failure()
            self._update_circuit_breaker_metric()

            error_info = self._sanitize_error(e)

            if METRICS_AVAILABLE:
                self.connection_attempts.labels(
                    result='failure',
                    operation=operation_name
                ).inc()
                self.connection_duration.labels(operation=operation_name).observe(duration)

            self.logger.error("ollama_operation_failed",
                            operation=operation_name,
                            duration_ms=duration * 1000,
                            circuit_breaker_state=self.circuit_breaker.state.value,
                            **error_info)

            # Re-raise with proper exception type
            if isinstance(e, httpx.ConnectError):
                raise OllamaConnectionError(f"Connection failed: {error_info['message']}") from e
            elif isinstance(e, httpx.TimeoutException):
                raise OllamaTimeoutError(f"Timeout: {error_info['message']}") from e
            else:
                raise OllamaClientError(f"Operation failed: {error_info['message']}") from e

        finally:
            if METRICS_AVAILABLE:
                self.active_connections.dec()

    @retry(
        stop=stop_after_attempt(3),  # Will be overridden by config
        wait=wait_exponential(multiplier=1, min=1, max=10),  # Will be overridden by config
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))
    )
    async def _http_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic"""
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=self.config.connection_timeout,
                read=self.config.request_timeout,
                write=self.config.request_timeout,
                pool=self.config.connection_timeout
            )
        ) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response

    async def health_check(self) -> bool:
        """
        Check if Ollama server is healthy and responsive.

        Returns:
            bool: True if server is healthy, False otherwise

        Raises:
            OllamaCircuitBreakerError: If circuit breaker is open
            OllamaConnectionError: If connection fails
            OllamaTimeoutError: If request times out
        """
        async def _health_check():
            url = self._safe_url('/api/tags')
            response = await self._http_request('GET', url)
            return response.status_code == 200

        # Configure retry for this specific call
        retry_decorator = retry(
            stop=stop_after_attempt(self.config.retry_attempts),
            wait=wait_exponential(
                multiplier=1,
                min=self.config.retry_min_wait,
                max=self.config.retry_max_wait
            ),
            retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))
        )

        try:
            return await self._execute_with_circuit_breaker(
                'health_check',
                retry_decorator(_health_check)()
            )
        except RetryError as e:
            # Convert retry error to our exception type
            if e.last_attempt.failed:
                original_error = e.last_attempt.exception()
                if isinstance(original_error, httpx.ConnectError):
                    raise OllamaConnectionError("Health check failed after retries") from original_error
                elif isinstance(original_error, httpx.TimeoutException):
                    raise OllamaTimeoutError("Health check timed out after retries") from original_error
            raise OllamaClientError("Health check failed after retries") from e

    async def get_models(self) -> list[str]:
        """
        Get list of available models from Ollama server.

        Returns:
            List[str]: List of available model names

        Raises:
            OllamaCircuitBreakerError: If circuit breaker is open
            OllamaConnectionError: If connection fails
            OllamaTimeoutError: If request times out
        """
        async def _get_models():
            url = self._safe_url('/api/tags')
            response = await self._http_request('GET', url)
            data = response.json()
            return [model["name"] for model in data.get("models", [])]

        retry_decorator = retry(
            stop=stop_after_attempt(self.config.retry_attempts),
            wait=wait_exponential(
                multiplier=1,
                min=self.config.retry_min_wait,
                max=self.config.retry_max_wait
            ),
            retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))
        )

        try:
            return await self._execute_with_circuit_breaker(
                'get_models',
                retry_decorator(_get_models)()
            )
        except RetryError as e:
            if e.last_attempt.failed:
                original_error = e.last_attempt.exception()
                if isinstance(original_error, httpx.ConnectError):
                    raise OllamaConnectionError("Get models failed after retries") from original_error
                elif isinstance(original_error, httpx.TimeoutException):
                    raise OllamaTimeoutError("Get models timed out after retries") from original_error
            raise OllamaClientError("Get models failed after retries") from e

    async def generate(self, model: str, prompt: str, **kwargs) -> dict[str, Any]:
        """
        Generate response from Ollama model.

        Args:
            model: Model name to use
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Dict[str, Any]: Generation response

        Raises:
            OllamaCircuitBreakerError: If circuit breaker is open
            OllamaConnectionError: If connection fails
            OllamaTimeoutError: If request times out
        """
        async def _generate():
            url = self._safe_url('/api/generate')
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            response = await self._http_request('POST', url, json=payload)
            return response.json()

        retry_decorator = retry(
            stop=stop_after_attempt(self.config.retry_attempts),
            wait=wait_exponential(
                multiplier=1,
                min=self.config.retry_min_wait,
                max=self.config.retry_max_wait
            ),
            retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))
        )

        try:
            return await self._execute_with_circuit_breaker(
                'generate',
                retry_decorator(_generate)()
            )
        except RetryError as e:
            if e.last_attempt.failed:
                original_error = e.last_attempt.exception()
                if isinstance(original_error, httpx.ConnectError):
                    raise OllamaConnectionError("Generate failed after retries") from original_error
                elif isinstance(original_error, httpx.TimeoutException):
                    raise OllamaTimeoutError("Generate timed out after retries") from original_error
            raise OllamaClientError("Generate failed after retries") from e

    async def close(self):
        """Clean up resources"""
        self.logger.info("ollama_client_closed")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    def get_circuit_breaker_state(self) -> dict[str, Any]:
        """Get current circuit breaker state for monitoring"""
        return {
            "state": self.circuit_breaker.state.value,
            "failure_count": self.circuit_breaker.failure_count,
            "last_failure_time": self.circuit_breaker.last_failure_time,
            "half_open_calls": self.circuit_breaker.half_open_calls,
            "can_execute": self.circuit_breaker.can_execute()
        }
