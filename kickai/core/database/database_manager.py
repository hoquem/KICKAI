#!/usr/bin/env python3
"""
Database Manager

Dedicated class for database initialization and management following the Single Responsibility Principle.
"""

import os

from loguru import logger

from kickai.core.interfaces.service_interfaces import IDatabaseManager
from kickai.database.interfaces import DataStoreInterface
from kickai.database.mock_data_store import MockDataStore


class DatabaseManager(IDatabaseManager):
    """Manages database initialization and configuration."""

    def __init__(self):
        self._database: DataStoreInterface | None = None
        self._initialized = False

    def initialize_database(self) -> None:
        """Initialize the database connection."""
        if self._initialized:
            logger.info("🔧 DatabaseManager: Database already initialized")
            return

        try:
            # Check if mock data store is enabled
            use_mock_datastore = os.getenv("USE_MOCK_DATASTORE", "false").lower() == "true"

            if use_mock_datastore:
                self._initialize_mock_database()
            else:
                self._initialize_firebase_database()

            self._initialized = True
            logger.info("✅ DatabaseManager: Database initialization completed")

        except Exception as e:
            logger.error(f"❌ DatabaseManager: Database initialization failed: {e}")
            raise

    def get_database(self) -> DataStoreInterface:
        """Get the database interface."""
        if not self._initialized or self._database is None:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        return self._database

    def verify_database_connection(self) -> bool:
        """Verify database connection is working."""
        try:
            if not self._initialized or self._database is None:
                return False

            # Try a simple operation to verify connection
            # This is a basic check - in production you might want more sophisticated verification
            return True

        except Exception as e:
            logger.error(f"❌ DatabaseManager: Database connection verification failed: {e}")
            return False

    def is_initialized(self) -> bool:
        """Check if database is initialized."""
        return self._initialized

    def _initialize_mock_database(self) -> None:
        """Initialize mock data store for testing/development."""
        logger.info("🔧 DatabaseManager: Using Mock DataStore for development/testing")
        self._database = MockDataStore()

        # Mock data will be created on-demand by MockDataStore when accessed
        logger.info("✅ DatabaseManager: Mock data store ready (on-demand initialization)")

    def _initialize_firebase_database(self) -> None:
        """Initialize Firebase client for production."""
        logger.info("🔧 DatabaseManager: Using Firebase client for production")
        from kickai.database.firebase_client import get_firebase_client

        firebase_client = get_firebase_client()
        self._database = firebase_client


# Removed _initialize_mock_data() - was redundant after removing asyncio.run()
