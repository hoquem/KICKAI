"""
Import Helper for KICKAI

This module provides consistent import resolution regardless of where the code is executed from.
It ensures that absolute imports work correctly whether running from:
- Project root (bot startup)
- Scripts directory (utility scripts)
- Tests directory (test files)
- Any other location

Usage:
    from src.utils.import_helper import ensure_src_in_path
    ensure_src_in_path()
    
    # Now all absolute imports will work
    from core.settings import get_settings
    from features.player_registration.domain.services import PlayerRegistrationService
"""

import os
import sys
from pathlib import Path
from typing import Optional


def find_project_root() -> Optional[Path]:
    """
    Find the project root directory by looking for key files.
    
    Returns:
        Path to project root, or None if not found
    """
    current = Path.cwd()
    
    # Look for project root indicators
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    
    return None


def ensure_src_in_path() -> None:
    """
    Ensure that the src directory is in the Python path.
    
    This function:
    1. Finds the project root directory
    2. Adds the src directory to sys.path if not already present
    3. Ensures absolute imports work consistently
    
    This should be called at the top of any script or module that needs
    to import from the src package.
    """
    project_root = find_project_root()
    
    if project_root is None:
        raise RuntimeError(
            "Could not find project root. Make sure you're running from within "
            "the KICKAI project directory or a subdirectory."
        )
    
    src_path = project_root / "src"
    
    if not src_path.exists():
        raise RuntimeError(f"Source directory not found at {src_path}")
    
    # Convert to string and normalize
    src_path_str = str(src_path.absolute())
    
    # Add to sys.path if not already present
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to project root
        
    Raises:
        RuntimeError: If project root cannot be found
    """
    project_root = find_project_root()
    
    if project_root is None:
        raise RuntimeError(
            "Could not find project root. Make sure you're running from within "
            "the KICKAI project directory or a subdirectory."
        )
    
    return project_root


def get_src_path() -> Path:
    """
    Get the src directory path.
    
    Returns:
        Path to src directory
        
    Raises:
        RuntimeError: If src directory cannot be found
    """
    return get_project_root() / "src"


# Auto-ensure src is in path when this module is imported
ensure_src_in_path() 