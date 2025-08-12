#!/usr/bin/env python3
"""
Service Interfaces Package

This package contains service interfaces following the Interface Segregation Principle.
"""

# Import repository interfaces
from .repository_interfaces import *
from .service_interfaces import (
    IContainerLifecycle,
    IContainerStatistics,
    IDatabaseManager,
    IServiceFactory,
    IServiceRegistry,
    IStringServiceLookup,
)

__all__ = [
    "IServiceRegistry",
    "IServiceFactory",
    "IDatabaseManager",
    "IContainerLifecycle",
    "IStringServiceLookup",
    "IContainerStatistics",
    # Repository interfaces
    "IPlayerRepository",
    "ITeamRepository",
    "IUserRepository",
    "IMatchRepository",
]
