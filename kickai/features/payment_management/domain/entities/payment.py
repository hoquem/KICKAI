from _future_ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Payment:
    id: Optional[str] = None
    amount: float = 0.0
    currency: str = "GBP"
    description: str = ""
    payer_id: Optional[str] = None
    team_id: Optional[str] = None


