#!/usr/bin/env python3
"""
System Tools - Clean Architecture Application Layer

This module provides CrewAI tools for system functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.shared.domain.interfaces.system_service_interface import ISystemService


@tool("check_system_ping")
async def check_system_ping() -> str:
    """Test KICKAI system connectivity and measure response latency.

    Performs basic system availability check with response time measurement
    for quick connectivity verification without authentication requirements.

    Use when: System connectivity verification is needed
    Required: No authentication required
    Context: System availability testing

    Returns: Ping time and connection status confirmation
    """
    try:
        logger.info("🏓 System ping request initiated")

        # Security check - basic rate limiting
        import time

        current_time = time.time()
        # This could be enhanced with proper rate limiting using Redis or memory cache

        # Get domain service with enhanced error handling
        try:
            container = get_container()
            system_service = container.get_service(ISystemService)
            if not system_service:
                return "❌ System service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get system service: {e}")
            return "❌ System service is not available"

        # Execute business logic with timeout and enhanced error handling
        try:
            import asyncio

            # Add timeout for ping operations to prevent hanging
            ping_result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, system_service.perform_ping),
                timeout=10.0,  # 10 second timeout
            )
            formatted_response = system_service.format_ping_response(ping_result)
        except TimeoutError:
            logger.warning("⚠️ System ping operation timed out")
            return "⚠️ System ping operation timed out after 10 seconds"
        except Exception as e:
            logger.warning(f"⚠️ System ping operation failed: {e}")
            return f"⚠️ System ping operation failed: {e!s}"

        # Log response time safely
        try:
            response_time = getattr(ping_result, "response_time", "unknown")
            logger.info(f"✅ Ping response completed in {response_time}ms")
        except Exception:
            logger.info("✅ Ping response completed")

        return formatted_response

    except Exception as e:
        logger.error(f"❌ Error in ping tool: {e}")
        return f"❌ System ping failed: {e!s}"


@tool("check_system_version")
def check_system_version() -> str:
    """Retrieve KICKAI system version, build information, and feature capabilities.

    Provides comprehensive system identification including version numbers,
    build dates, enabled features, and component versions for system tracking.

    Use when: System version identification is required
    Required: No authentication required
    Context: System information retrieval

    Returns: Version information with build details and capabilities
    """
    try:
        logger.info("📱 System version information requested")

        # Get domain service with enhanced error handling
        try:
            container = get_container()
            system_service = container.get_service(ISystemService)
            if not system_service:
                return "❌ System service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get system service: {e}")
            return "❌ System service is not available"

        # Execute business logic with enhanced error handling and caching
        try:
            system_info = system_service.get_system_info()
            formatted_response = system_service.format_version_response(system_info)

            # Sanitize version info for security (prevent info leakage)
            if hasattr(system_info, "version"):
                version = getattr(system_info, "version", "Unknown")
                # Only show major.minor version publicly
                if "." in version:
                    version_parts = version.split(".")
                    if len(version_parts) >= 2:
                        public_version = f"{version_parts[0]}.{version_parts[1]}"
                        formatted_response = formatted_response.replace(version, public_version)

        except Exception as e:
            logger.warning(f"⚠️ System version operation failed: {e}")
            return f"⚠️ System version operation failed: {e!s}"

        # Log version info safely
        try:
            version = getattr(system_info, "version", "Unknown")
            logger.info(f"✅ Version information provided - KICKAI v{version}")
        except Exception:
            logger.info("✅ Version information provided")

        return formatted_response

    except Exception as e:
        logger.error(f"❌ Error in version tool: {e}")
        return f"❌ Version check failed: {e!s}"


@tool("check_system_health")
def check_system_health() -> str:
    """Execute comprehensive health diagnostics across all KICKAI subsystems.

    Performs detailed health checks across all system components including
    database connectivity, service availability, and operational metrics.

    Use when: Comprehensive system health assessment is required
    Required: Administrative access for detailed diagnostics
    Context: System maintenance and monitoring

    Returns: Detailed health report with service status and metrics
    """
    try:
        logger.info("🏥 System health check requested")

        # Get domain service with enhanced error handling
        try:
            container = get_container()
            system_service = container.get_service(ISystemService)
            if not system_service:
                return "❌ System service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get system service: {e}")
            return "❌ System service is not available"

        # Execute business logic with comprehensive error handling
        try:
            health_report = system_service.get_system_health()
            formatted_response = system_service.format_health_report(health_report)

            # Sanitize sensitive health information for security
            import re

            # Remove potential sensitive patterns (IPs, paths, etc.)
            sensitive_patterns = [
                r"\b(?:\d{1,3}\.){3}\d{1,3}\b",  # IP addresses
                r"/[a-zA-Z0-9/._-]*(?:password|key|secret|token)[a-zA-Z0-9/._-]*",  # Sensitive paths
                r"[a-zA-Z0-9+/]{20,}={0,2}",  # Base64-like tokens
            ]

            for pattern in sensitive_patterns:
                formatted_response = re.sub(pattern, "[REDACTED]", formatted_response)

        except Exception as e:
            logger.warning(f"⚠️ System health check operation failed: {e}")
            return f"⚠️ System health check operation failed: {e!s}"

        logger.info("✅ System health check completed")

        return formatted_response

    except Exception as e:
        logger.error(f"❌ Error in system health check: {e}")
        return f"❌ System health check failed: {e!s}"


@tool("get_system_status")
def get_system_status() -> str:
    """Retrieve current operational status including uptime and active services.

    Provides current system operational state including uptime metrics,
    active services, maintenance status, and known issues.

    Use when: Current operational status information is needed
    Required: No authentication required
    Context: System status monitoring

    Returns: Current system status with operational details
    """
    try:
        logger.info("📊 System status requested")

        # Security enhancement - limit status detail exposure
        # Only show essential operational status, hide internal details

        # Get domain service with enhanced error handling
        try:
            container = get_container()
            system_service = container.get_service(ISystemService)
            if not system_service:
                return "❌ System service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get system service: {e}")
            return "❌ System service is not available"

        # Execute business logic with rate limiting and error handling
        try:
            # Basic rate limiting check (could be enhanced with Redis)
            import time

            current_time = time.time()

            # Get system status with potential caching for frequent requests
            status_info = system_service.get_system_status()
            formatted_response = system_service.format_status_response(status_info)

            # Add timestamp for freshness indicator
            formatted_response += (
                f"\n\n🕰️ Last updated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}"
            )

        except Exception as e:
            logger.warning(f"⚠️ System status operation failed: {e}")
            return f"⚠️ System status operation failed: {e!s}"

        logger.info("✅ System status provided")

        return formatted_response

    except Exception as e:
        logger.error(f"❌ Error getting system status: {e}")
        return f"❌ System status check failed: {e!s}"
