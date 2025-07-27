from abc import ABC, abstractmethod

# from kickai.features.payment_management.domain.entities.payment import Payment  # Uncomment and implement Payment entity as needed


class PaymentRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, payment):  # Use Payment type when available
        pass

    @abstractmethod
    async def get_by_id(self, payment_id: str):  # -> Optional[Payment]
        pass

    @abstractmethod
    async def get_by_team(self, team_id: str):  # -> List[Payment]
        pass

    @abstractmethod
    async def update(self, payment):  # -> Payment
        pass

    @abstractmethod
    async def delete(self, payment_id: str) -> None:
        pass
