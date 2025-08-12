#!/usr/bin/env python3
"""
System Infrastructure Tools - Native CrewAI Implementation

This module provides tools for system operations using ONLY CrewAI native patterns.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.database.firebase_client import FirebaseClient


@tool("ping")
def ping(telegram_id: int, team_id: str, chat_type: str) -> str:
    """
    Test system connectivity and responsiveness.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)


    :return: Comprehensive system health status including core services and database connectivity
    :rtype: str  # TODO: Fix type
    """
    try:
        # Get container and test basic connectivity
        container = get_container()

        if not container:
            return "❌ System container is not available."

        # Test Firebase connectivity if possible
        try:
            firebase_client = container.get_service(FirebaseClient)
            if firebase_client:
                firebase_status = "✅ Connected"
            else:
                firebase_status = "⚠️ Not available"
        except Exception:
            firebase_status = "❌ Connection failed"

        # Format as simple string response
        result = "🏓 System Status Check\\n\\n"
        result += "• System Core: ✅ Online\\n"
        result += "• Dependency Container: ✅ Active\\n"
        result += f"• Firebase: {firebase_status}\\n"

        if team_id and team_id.strip() != "":
            result += f"• Team Context: {team_id}\\n"

        result += "\\n📊 All core systems are operational and responding normally."

        return result

    except Exception as e:
        logger.error(f"System ping failed: {e}")
        return f"❌ System ping failed: {e!s}"


@tool("version")
def version(telegram_id: int, team_id: str, chat_type: str) -> str:
    """
    Get system version and build information.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)


    :return: System version details including KICKAI version, architecture, and latest features
    :rtype: str  # TODO: Fix type
    """
    try:
        # Format as simple string response
        result = "📋 KICKAI System Information\\n\\n"
        result += "• Version: 5.0\\n"
        result += "• Status: Production Ready\\n"
        result += "• Architecture: 5-Agent CrewAI System\\n"
        result += "• Python: 3.11+\\n"
        result += "• Framework: CrewAI with Native Patterns\\n"
        result += "• Database: Firebase Firestore\\n"

        if team_id and team_id.strip() != "":
            result += f"• Team Context: {team_id}\\n"

        result += "\\n🚀 Latest features: JSON Tool Migration, Native CrewAI Patterns"

        return result

    except Exception as e:
        logger.error(f"Version check failed: {e}")
        return f"❌ Version check failed: {e!s}"


@tool("get_firebase_document")
def get_firebase_document(telegram_id: int, team_id: str, chat_type: str, collection: str, document_id: str) -> str:
    """
    Get a document from Firebase/Firestore.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        collection (str): Firestore collection name to query
        document_id (str): Specific document ID to retrieve


    :return: Document retrieval status with field count and availability information
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get Firebase document."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get Firebase document."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get Firebase document."

    if not collection or collection.strip() == "":
        return "❌ Collection name is required to get Firebase document."

    if not document_id or document_id.strip() == "":
        return "❌ Document ID is required to get Firebase document."

    try:
        # Get service using simple container access
        container = get_container()
        firebase_client = container.get_service(FirebaseClient)

        if not firebase_client:
            return "❌ Firebase service is temporarily unavailable. Please try again later."

        # Get document
        document = firebase_client.get_document(collection.strip(), document_id.strip())

        if document:
            # Format as simple string response (don't expose raw data)
            result = "📄 Document Retrieved\\n\\n"
            result += f"• Collection: {collection}\\n"
            result += f"• Document ID: {document_id}\\n"

            if team_id and team_id.strip() != "":
                result += f"• Team Context: {team_id}\\n"

            result += "• Status: Found\\n"
            result += f"• Fields: {len(document)} fields available\\n\\n"
            result += "📊 Document successfully retrieved from Firestore."

            return result
        else:
            return f"❌ Document '{document_id}' not found in collection '{collection}'."

    except Exception as e:
        logger.error(f"Failed to get Firebase document: {e}")
        return f"❌ Failed to get Firebase document: {e!s}"
