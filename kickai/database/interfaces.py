from abc import ABC, abstractmethod
from typing import Any, Union, Union


class DataStoreInterface(ABC):
    @abstractmethod
    async def create_document(self, collection: str, data: dict[str, Any], document_id: Union[str, None] = None) -> str:
        pass

    @abstractmethod
    async def get_document(self, collection: str, document_id: str) -> Union[dict[str, Any], None]:
        pass

    @abstractmethod
    async def update_document(self, collection: str, document_id: str, data: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_document(self, collection: str, document_id: str) -> bool:
        pass

    @abstractmethod
    async def query_documents(self, collection: str, filters: Union[list[dict[str, Any]], None] = None, order_by: Union[str, None] = None, limit: Union[int, None] = None) -> list[dict[str, Any]]:
        pass
