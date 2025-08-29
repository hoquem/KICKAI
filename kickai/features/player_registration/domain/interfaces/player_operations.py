from _future_ import annotations

"""
Minimal interfaces and types for player operations (used in tests).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PlayerInfo:
    id: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    team_id: Optional[str] = None


