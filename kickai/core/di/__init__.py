"""
Dependency Injection module for KICKAI system.

This module provides modern dependency injection capabilities
with scoping and lifecycle management.
"""

from .modern_container import ModernDIContainer, ServiceRegistration, ServiceScope

__all__ = ["ModernDIContainer", "ServiceScope", "ServiceRegistration"]
