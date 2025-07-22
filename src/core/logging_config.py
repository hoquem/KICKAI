#!/usr/bin/env python3
"""
Centralized Logging Configuration for KICKAI

This module provides standardized logging configuration using loguru
for consistent debugging across the entire system.
"""

from loguru import logger
import sys
import os

# Remove all existing handlers and add loguru handlers
logger.remove()

# Add console handler only - this is the primary logging destination
# File logging will be handled by redirecting console output in local development
logger.add(
    sys.stdout, 
    level="INFO", 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    enqueue=True, 
    backtrace=True, 
    diagnose=True,
    colorize=True
)

# Add error handler to stderr for critical errors
logger.add(
    sys.stderr,
    level="ERROR",
    format="<red>{time:YYYY-MM-DD HH:mm:ss}</red> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    enqueue=True,
    colorize=True
)

# Export the logger for use throughout the application
__all__ = ["logger"] 