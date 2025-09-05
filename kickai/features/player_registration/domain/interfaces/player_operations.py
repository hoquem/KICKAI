"""
Minimal interfaces and types for player operations (used in tests).
"""

from dataclasses import dataclass


@dataclass
class PlayerInfo:
    id: str | None = None
    name: str | None = None
    phone: str | None = None
    team_id: str | None = None
