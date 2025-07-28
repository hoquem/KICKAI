from dataclasses import dataclass
from typing import Optional

from kickai.core.enums import ExpenseCategory


@dataclass
class Expense:
    team_id: str
    amount: float
    category: ExpenseCategory
    id: Optional[str] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "Expense":
        return Expense(
            id=data.get("id"),
            team_id=data["team_id"],
            amount=data["amount"],
            category=ExpenseCategory(data["category"]),
            description=data.get("description"),
            receipt_url=data.get("receipt_url"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "team_id": self.team_id,
            "amount": self.amount,
            "category": self.category.value,
            "description": self.description,
            "receipt_url": self.receipt_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
