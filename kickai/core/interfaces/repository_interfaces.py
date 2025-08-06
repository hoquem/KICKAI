"""
Repository interfaces for data layer abstraction.

This module re-exports split repository interfaces that follow the Interface
Segregation Principle, allowing components to depend only on the methods they need.

For backward compatibility, complete repository interfaces are provided.
For new code, use the specific split interfaces for better dependency isolation.
"""

from __future__ import annotations

# Match repository interfaces (split)
from .match_repositories import (
    IMatchAvailabilityRepository,
    IMatchReadRepository,
    IMatchRepository,
    IMatchWriteRepository,
)

# Player repository interfaces (split)
from .player_repositories import (
    IPlayerApprovalRepository,
    IPlayerReadRepository,
    IPlayerRepository,
    IPlayerWriteRepository,
)

# Base repository interfaces
from .repository_base import IBulkRepository, IQueryRepository, IRepository

# Team repository interfaces (split)
from .team_repositories import (
    ITeamConfigRepository,
    ITeamMemberReadRepository,
    ITeamMemberWriteRepository,
    ITeamRepository,
)

# User repository interfaces (split)
from .user_repositories import (
    IUserPermissionRepository,
    IUserRegistrationRepository,
    IUserRepository,
)

# Export all interfaces for backward compatibility and new focused dependencies
__all__ = [
    # Base interfaces
    "IRepository",
    "IQueryRepository",
    "IBulkRepository",

    # Player interfaces
    "IPlayerReadRepository",
    "IPlayerWriteRepository",
    "IPlayerApprovalRepository",
    "IPlayerRepository",

    # Team interfaces
    "ITeamConfigRepository",
    "ITeamMemberReadRepository",
    "ITeamMemberWriteRepository",
    "ITeamRepository",

    # User interfaces
    "IUserRegistrationRepository",
    "IUserPermissionRepository",
    "IUserRepository",

    # Match interfaces
    "IMatchReadRepository",
    "IMatchWriteRepository",
    "IMatchAvailabilityRepository",
    "IMatchRepository"
]
