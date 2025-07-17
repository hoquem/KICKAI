"""
Advanced Memory System - Modular Architecture

This module has been refactored to use a modular architecture with separate
components for storage, learning, context management, and optimization.

The monolithic AdvancedMemorySystem has been split into focused components:
- storage/: Memory storage implementations
- learning/: User preference learning and pattern recognition
- context/: Conversation context management
- optimization/: Memory cleanup and performance optimization
- system.py: Main orchestrator class

This refactoring follows the single responsibility principle and improves
maintainability and testability.
"""

# Import from the new modular structure
from .memory import (
    AdvancedMemorySystem,
    get_memory_system,
    initialize_memory_system,
    cleanup_memory_system,
    MemoryItem,
    MemoryType,
    MemoryPriority,
    UserPreference,
    Pattern
)

from .memory.storage import (
    MemoryStorage,
    InMemoryStorage
)

from .memory.learning import (
    PreferenceLearner,
    PatternRecognizer
)

from .memory.context import (
    ConversationContext,
    ConversationContextManager
)

from .memory.optimization import (
    MemoryCleanup,
    PerformanceOptimizer
)

# Re-export for backward compatibility
__all__ = [
    'AdvancedMemorySystem',
    'get_memory_system',
    'initialize_memory_system',
    'cleanup_memory_system',
    'MemoryItem',
    'MemoryType',
    'MemoryPriority',
    'UserPreference',
    'Pattern',
    'MemoryStorage',
    'InMemoryStorage',
    'PreferenceLearner',
    'PatternRecognizer',
    'ConversationContext',
    'ConversationContextManager',
    'MemoryCleanup',
    'PerformanceOptimizer'
] 