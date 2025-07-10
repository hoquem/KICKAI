"""
Configuration module for KICKAI.
"""

import os
from typing import Dict, Any


# Feature flags
ENABLE_DYNAMIC_TASK_DECOMPOSITION = os.getenv('ENABLE_DYNAMIC_TASK_DECOMPOSITION', 'false').lower() == 'true'
ENABLE_PHASE1 = os.getenv('ENABLE_PHASE1', 'false').lower() == 'true'
ENABLE_ADVANCED_MEMORY = os.getenv('ENABLE_ADVANCED_MEMORY', 'false').lower() == 'true'


def get_feature_flags() -> Dict[str, bool]:
    """Get all feature flags."""
    return {
        'ENABLE_DYNAMIC_TASK_DECOMPOSITION': ENABLE_DYNAMIC_TASK_DECOMPOSITION,
        'ENABLE_PHASE1': ENABLE_PHASE1,
        'ENABLE_ADVANCED_MEMORY': ENABLE_ADVANCED_MEMORY,
    }


def is_phase1_enabled() -> bool:
    """Check if phase 1 is enabled."""
    return ENABLE_PHASE1 