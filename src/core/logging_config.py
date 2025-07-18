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

# Add console handler
logger.add(
    sys.stdout, 
    level="INFO", 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    enqueue=True, 
    backtrace=True, 
    diagnose=True
)

# Add file handler
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger.add(
    "logs/kickai.log", 
    level="DEBUG", 
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB", 
    retention="7 days",
    enqueue=True, 
    backtrace=True, 
    diagnose=True
)

# Configure loguru to intercept standard logging
logger.add(
    sys.stderr,
    level="ERROR",
    format="<red>{time:YYYY-MM-DD HH:mm:ss}</red> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    enqueue=True
)

# Export the logger for use throughout the application
__all__ = ["logger"] 