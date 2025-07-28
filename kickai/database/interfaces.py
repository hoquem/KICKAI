from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DataStoreInterface(ABC):
    @abstractmethod
    async def create_document(
        self, collection: str, data: Dict[str, Any], document_id: Optional[str] = None
    ) -> str:
        pass

    @abstractmethod
    async def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update_document(
        self, collection: str, document_id: str, data: Dict[str, Any]
    ) -> bool:
        pass

    @abstractmethod
    async def delete_document(self, collection: str, document_id: str) -> bool:
        pass

    @abstractmethod
    async def query_documents(
        self,
        collection: str,
        filters: Optional[List[Dict[str, Any]]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        pass
