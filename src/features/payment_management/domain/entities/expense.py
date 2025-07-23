from dataclasses import dataclass
from enum import Enum


class ExpenseCategory(Enum):
    PITCH_FEES = "pitch_fees"
    REFEREE_FEES = "referee_fees"
    EQUIPMENT = "equipment"
    TEAM_MEAL = "team_meal"
    FA_FEES = "fa_fees"
    OTHER = "other"

@dataclass
class Expense:
    team_id: str
    amount: float
    category: ExpenseCategory
    id: str | None = None
    description: str | None = None
    receipt_url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

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
