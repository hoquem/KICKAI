"""
Budget Entity for Payment Management.

This module defines the Budget entity with proper validation
and business logic encapsulation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Union

from kickai.features.shared.domain.entities.base_entity import BaseEntity


@dataclass
class Budget(BaseEntity):
    """Budget entity for managing team financial budgets."""
    team_id: Union[str, None] = None
    total_amount: Union[Decimal, None] = None
    allocated_amount: Decimal = Decimal('0')
    spent_amount: Decimal = Decimal('0')
    currency: str = "USD"
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Union[datetime, None] = None
    description: Union[str, None] = None
    status: str = "active"  # active, inactive, exceeded
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        if self.team_id is None:
            raise ValueError("team_id is required")
        if self.total_amount is None:
            raise ValueError("total_amount is required")
        self._validate_budget()

    def _validate_budget(self):
        """Validate budget constraints."""
        if self.total_amount <= 0:
            raise ValueError("Total amount must be positive")

        if self.allocated_amount < 0:
            raise ValueError("Allocated amount cannot be negative")

        if self.spent_amount < 0:
            raise ValueError("Spent amount cannot be negative")

        if self.allocated_amount > self.total_amount:
            raise ValueError("Allocated amount cannot exceed total amount")

        if self.spent_amount > self.allocated_amount:
            raise ValueError("Spent amount cannot exceed allocated amount")

        if self.end_date and self.start_date >= self.end_date:
            raise ValueError("End date must be after start date")

    @property
    def remaining_amount(self) -> Decimal:
        """Calculate remaining budget amount."""
        return self.allocated_amount - self.spent_amount

    @property
    def utilization_percentage(self) -> float:
        """Calculate budget utilization percentage."""
        if self.allocated_amount == 0:
            return 0.0
        return float((self.spent_amount / self.allocated_amount) * 100)

    @property
    def is_exceeded(self) -> bool:
        """Check if budget is exceeded."""
        return self.spent_amount >= self.allocated_amount

    @property
    def is_active(self) -> bool:
        """Check if budget is active."""
        now = datetime.now()
        if self.end_date and now > self.end_date:
            return False
        return self.status == "active"

    def allocate_amount(self, amount: Decimal) -> bool:
        """Allocate additional amount to budget."""
        if amount <= 0:
            raise ValueError("Allocation amount must be positive")

        new_allocated = self.allocated_amount + amount
        if new_allocated > self.total_amount:
            return False

        self.allocated_amount = new_allocated
        return True

    def spend_amount(self, amount: Decimal) -> bool:
        """Record spending against budget."""
        if amount <= 0:
            raise ValueError("Spending amount must be positive")

        if self.spent_amount + amount > self.allocated_amount:
            return False

        self.spent_amount += amount

        # Update status if exceeded
        if self.is_exceeded:
            self.status = "exceeded"

        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert budget to dictionary."""
        return {
            "id": self.id,
            "team_id": self.team_id,
            "total_amount": str(self.total_amount),
            "allocated_amount": str(self.allocated_amount),
            "spent_amount": str(self.spent_amount),
            "currency": self.currency,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "description": self.description,
            "status": self.status,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Budget':
        """Create budget from dictionary."""
        return cls(
            id=data.get("id"),
            team_id=data["team_id"],
            total_amount=Decimal(data["total_amount"]),
            allocated_amount=Decimal(data.get("allocated_amount", "0")),
            spent_amount=Decimal(data.get("spent_amount", "0")),
            currency=data.get("currency", "USD"),
            start_date=datetime.fromisoformat(data["start_date"]),
            end_date=datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None,
            description=data.get("description"),
            status=data.get("status", "active"),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
