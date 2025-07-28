#!/usr/bin/env python3
"""
Centralized Logging Configuration for KICKAI

This module provides standardized logging configuration using loguru
for console-only logging. File logging is handled through redirection
in the startup scripts.
"""

import os
import sys

from loguru import logger

# Remove all existing handlers to prevent double logging
logger.remove()

# Check if we're in a test environment
is_test = os.getenv("TESTING", "false").lower() == "true"

# Add console handler only - this is the primary logging destination
# File logging will be handled by redirecting console output in startup scripts
# Using only stdout to prevent double logging when redirecting with 2>&1
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    colorize=True,
    filter=lambda record: not is_test or record["level"].name in ["ERROR", "CRITICAL"],
)

# Export the logger for use throughout the application
__all__ = ["logger"]
