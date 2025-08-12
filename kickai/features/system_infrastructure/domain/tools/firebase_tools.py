"""
Firebase tools for KICKAI system.

This module provides tools for Firebase/Firestore operations.
"""

import logging

from crewai.tools import tool
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.database.firebase_client import FirebaseClient
from kickai.utils.json_helper import json_error, json_response

logger = logging.getLogger(__name__)

class GetFirebaseDocumentInput(BaseModel):
    """Input model for get_firebase_document tool."""

    collection: str
    document_id: str
    team_id: str | None = None

@tool("get_firebase_document")
def get_firebase_document(collection: str, document_id: str, team_id: str | None = None) -> str:
    """
    Get a document from Firebase/Firestore. Requires: collection, document_id


        collection: The Firestore collection name
        document_id: The document ID to retrieve
        team_id: Optional team ID for context


    :return: JSON response with document data
    :rtype: str  # TODO: Fix type
    """
    try:
        container = get_container()
        firebase_client = container.get_service(FirebaseClient)

        if not firebase_client:
            logger.error("❌ FirebaseClient not available")
            return json_error("Firebase client not available", "Service unavailable")

        # Get the document
        document = firebase_client.get_document(collection, document_id)

        if document:
            logger.info(f"✅ Retrieved document {document_id} from collection {collection}")
            data = {
                'collection': collection,
                'document_id': document_id,
                'team_id': team_id,
                'document': document,
                'status': 'retrieved'
            }
            ui_format = f"✅ Document retrieved: {document}"
            return json_response(data, ui_format=ui_format)
        else:
            logger.warning(f"⚠️ Document {document_id} not found in collection {collection}")
            data = {
                'collection': collection,
                'document_id': document_id,
                'team_id': team_id,
                'document': None,
                'status': 'not_found'
            }
            ui_format = f"⚠️ Document {document_id} not found in collection {collection}"
            return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"❌ Failed to get Firebase document: {e}")
        return json_error(f"Failed to get Firebase document: {e!s}", "Operation failed")
