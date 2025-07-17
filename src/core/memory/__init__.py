"""
Advanced Memory System - Modular Architecture

This package provides a modular memory management system that replaces the monolithic
AdvancedMemorySystem with smaller, focused components following the single responsibility principle.
"""

from .system import AdvancedMemorySystem, get_memory_system, initialize_memory_system, cleanup_memory_system
from .storage import MemoryStorage, InMemoryStorage
from .learning import PreferenceLearner, PatternRecognizer
from .context import ConversationContext, ConversationContextManager
from .optimization import MemoryCleanup, PerformanceOptimizer

__all__ = [
    'AdvancedMemorySystem',
    'get_memory_system',
    'initialize_memory_system',
    'cleanup_memory_system',
    'MemoryStorage',
    'InMemoryStorage',
    'PreferenceLearner',
    'PatternRecognizer',
    'ConversationContext',
    'ConversationContextManager',
    'MemoryCleanup',
    'PerformanceOptimizer'
] 