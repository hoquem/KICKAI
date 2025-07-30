from abc import ABC, abstractmethod
from typing import Any


class DataStoreInterface(ABC):
    @abstractmethod
    async def create_document(
        self, collection: str, data: dict[str, Any], document_id: str | None = None
    ) -> str:
        pass

    @abstractmethod
    async def get_document(self, collection: str, document_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def update_document(
        self, collection: str, document_id: str, data: dict[str, Any]
    ) -> bool:
        pass

    @abstractmethod
    async def delete_document(self, collection: str, document_id: str) -> bool:
        pass

    @abstractmethod
    async def query_documents(
        self,
        collection: str,
        filters: list[dict[str, Any]] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        pass
