"""
Firebase tools for KICKAI system.

This module provides tools for Firebase/Firestore operations.
"""

import logging

from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.database.firebase_client import FirebaseClient
from kickai.utils.crewai_tool_decorator import tool
from kickai.core.enums import ResponseStatus
from kickai.utils.tool_helpers import create_json_response
from typing import Optional

logger = logging.getLogger(__name__)


class GetFirebaseDocumentInput(BaseModel):
    """Input model for get_firebase_document tool."""

    collection: str
    document_id: str
    team_id: Optional[str] = None


@tool("get_firebase_document", result_as_answer=True)
async def get_firebase_document(collection: str, document_id: str, team_id: Optional[str] = None) -> str:
    """
    Get a document from Firebase/Firestore. Requires: collection, document_id

    Args:
        collection: The Firestore collection name
        document_id: The document ID to retrieve
        team_id: Optional team ID for context

    Returns:
        The document data as a JSON string or error message
    """
    try:
        container = get_container()
        firebase_client = container.get_service(FirebaseClient)

        if not firebase_client:
            logger.error("❌ FirebaseClient not available")
            return create_json_response(ResponseStatus.ERROR, message=f"Firebase client not available")

        # Get the document
        document = await firebase_client.get_document(collection, document_id)

        if document:
            logger.info(f"✅ Retrieved document {document_id} from collection {collection}")
            return create_json_response(ResponseStatus.SUCCESS, data=f"Document retrieved: {document}")
        else:
            logger.warning(f"⚠️ Document {document_id} not found in collection {collection}")
            return create_json_response(ResponseStatus.ERROR, message=f"Document {document_id} not found in collection {collection}")

    except Exception as e:
        logger.error(f"❌ Failed to get Firebase document: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get Firebase document: {e!s}")
