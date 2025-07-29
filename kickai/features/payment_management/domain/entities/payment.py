from dataclasses import dataclass

from kickai.core.enums import PaymentStatus, PaymentType


@dataclass
class Payment:
    player_id: str
    amount: float
    type: PaymentType
    status: PaymentStatus
    id: str | None = None
    team_id: str | None = None
    description: str | None = None
    related_entity_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    @staticmethod
    def from_dict(data: dict) -> "Payment":
        return Payment(
            id=data.get("id"),
            player_id=data["player_id"],
            team_id=data.get("team_id"),
            amount=data["amount"],
            type=PaymentType(data["type"]),
            status=PaymentStatus(data["status"]),
            description=data.get("description"),
            related_entity_id=data.get("related_entity_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "player_id": self.player_id,
            "team_id": self.team_id,
            "amount": self.amount,
            "type": self.type.value,
            "status": self.status.value,
            "description": self.description,
            "related_entity_id": self.related_entity_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
