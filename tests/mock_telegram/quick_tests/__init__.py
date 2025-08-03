"""
Quick Test Scenarios Framework

This module provides automated, one-click testing of core KICKAI bot functionality 
with pre-defined data sets, validation steps, and cleanup procedures.
"""

__version__ = "1.0.0"
__author__ = "KICKAI Testing Team"

from .test_controller import QuickTestController
from .test_data_manager import TestDataManager
from .validation_engine import ValidationEngine
from .cleanup_handler import CleanupHandler
from .base_scenario import BaseScenario

__all__ = [
    "QuickTestController",
    "TestDataManager", 
    "ValidationEngine",
    "CleanupHandler",
    "BaseScenario"
]