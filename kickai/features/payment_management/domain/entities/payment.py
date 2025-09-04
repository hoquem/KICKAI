from dataclasses import dataclass


@dataclass
class Payment:
    id: str | None = None
    amount: float = 0.0
    currency: str = "GBP"
    description: str = ""
    payer_id: str | None = None
    team_id: str | None = None
