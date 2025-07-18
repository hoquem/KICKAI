"""
Firebase tools for KICKAI (placeholder, not used in production).
"""

from typing import Dict, Type
from loguru import logger
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

TOOL_REGISTRY = {}

def register_tool_instance(tool_instance):
    TOOL_REGISTRY[tool_instance.name] = tool_instance
    return tool_instance

class GetFirebaseDocumentInput(BaseModel):
    collection: str = Field(..., description="Firebase collection name")
    doc_id: str = Field(..., description="Document ID")

class GetFirebaseDocumentTool(BaseTool):
    name: str = "get_firebase_document"
    description: str = "Get a document from Firebase (example tool)."
    args_schema: Type[BaseModel] = GetFirebaseDocumentInput

    def _run(self, collection: str, doc_id: str) -> Dict:
        logger.info(f"[TOOL] Getting document from collection={collection}, doc_id={doc_id}")
        # Placeholder logic
        return {"id": doc_id, "collection": collection, "data": {}}

register_tool_instance(GetFirebaseDocumentTool())

__all__ = ["TOOL_REGISTRY"] 