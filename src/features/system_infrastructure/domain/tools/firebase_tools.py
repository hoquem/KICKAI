"""
Firebase tools for KICKAI system.

This module provides tools for Firebase/Firestore operations.
"""

import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel

from crewai.tools import tool
from src.database.firebase_client import FirebaseClient
from src.core.dependency_container import get_container

logger = logging.getLogger(__name__)


class GetFirebaseDocumentInput(BaseModel):
    """Input model for get_firebase_document tool."""
    collection: str
    document_id: str
    team_id: Optional[str] = None


@tool("get_firebase_document")
def get_firebase_document(collection: str, document_id: str, team_id: Optional[str] = None) -> str:
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
            return "❌ Firebase client not available"
        
        # Get the document
        document = firebase_client.get_document(collection, document_id)
        
        if document:
            logger.info(f"✅ Retrieved document {document_id} from collection {collection}")
            return f"✅ Document retrieved: {document}"
        else:
            logger.warning(f"⚠️ Document {document_id} not found in collection {collection}")
            return f"⚠️ Document {document_id} not found in collection {collection}"
        
    except Exception as e:
        logger.error(f"❌ Failed to get Firebase document: {e}")
        return f"❌ Failed to get Firebase document: {str(e)}" 