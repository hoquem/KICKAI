"""
Factory patterns for dependency assembly in KICKAI.

This package contains factory classes that handle the creation and assembly
of complex objects with their dependencies, following the Factory pattern
and Dependency Injection principles.
"""

from .agent_system_factory import AgentSystemFactory
from .service_factory import ServiceFactory
from .repository_factory import RepositoryFactory

__all__ = [
    "AgentSystemFactory",
    "ServiceFactory",
    "RepositoryFactory",
]