#!/usr/bin/env python3
"""
Configuration for CrewAI audit scripts.

This module provides centralized configuration for all audit scripts
to ensure consistency and maintainability.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class AuditConfig:
    """Configuration for audit scripts."""
    
    # Paths
    DEFAULT_SRC_PATH: str = "src"
    DEFAULT_KICKAI_PATH: str = "kickai"
    
    # File patterns to exclude
    EXCLUDE_PATTERNS: List[str] = None
    
    # Tool detection patterns
    TOOL_INDICATORS: List[str] = None
    
    # Context extraction patterns
    CONTEXT_PATTERNS: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.EXCLUDE_PATTERNS is None:
            self.EXCLUDE_PATTERNS = [
                "__pycache__",
                ".git",
                ".pytest_cache",
                "venv",
                "venv311",
                "node_modules",
                "*.pyc",
                "*.pyo",
                "*.pyd"
            ]
        
        if self.TOOL_INDICATORS is None:
            self.TOOL_INDICATORS = [
                'tool',
                'player_tool', 
                'team_tool', 
                'help_tool',
                'registration_tool',
                'administration_tool'
            ]
        
        if self.CONTEXT_PATTERNS is None:
            self.CONTEXT_PATTERNS = [
                r'context\.get\([\'"]([^\'"]+)[\'"]\)',
                r'execution_context\.get\([\'"]([^\'"]+)[\'"]\)',
                r'task\.context\.get\([\'"]([^\'"]+)[\'"]\)',
                r'security_context\.get\([\'"]([^\'"]+)[\'"]\)',
                r'extract.*context',
                r'parse.*context',
                r'def.*context.*:',
                r'context.*=.*context'
            ]


class PathManager:
    """Manages paths for audit scripts."""
    
    def __init__(self, config: AuditConfig = None):
        self.config = config or AuditConfig()
        self.project_root = self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = Path.cwd()
        
        # Look for common project root indicators
        while current != current.parent:
            if any((current / indicator).exists() for indicator in [
                'pyproject.toml', 'setup.py', 'requirements.txt', '.git'
            ]):
                return current
            current = current.parent
        
        return Path.cwd()
    
    def get_src_path(self, src_path: str = None) -> Path:
        """Get the source path for auditing."""
        if src_path:
            return Path(src_path)
        
        # Try to find the source directory
        possible_paths = [
            self.project_root / self.config.DEFAULT_SRC_PATH,
            self.project_root / self.config.DEFAULT_KICKAI_PATH,
            self.project_root / "kickai"
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                return path
        
        # Default to src if nothing found
        return self.project_root / self.config.DEFAULT_SRC_PATH
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if a file should be excluded from auditing."""
        file_str = str(file_path)
        
        for pattern in self.config.EXCLUDE_PATTERNS:
            if pattern in file_str:
                return True
        
        return False
    
    def find_python_files(self, src_path: str = None) -> List[Path]:
        """Find all Python files to audit."""
        src_dir = self.get_src_path(src_path)
        python_files = []
        
        if not src_dir.exists():
            return python_files
        
        for file_path in src_dir.rglob("*.py"):
            if not self.should_exclude_file(file_path):
                python_files.append(file_path)
        
        return python_files


# Global configuration instance
DEFAULT_CONFIG = AuditConfig()
DEFAULT_PATH_MANAGER = PathManager(DEFAULT_CONFIG)


def get_config() -> AuditConfig:
    """Get the default audit configuration."""
    return DEFAULT_CONFIG


def get_path_manager() -> PathManager:
    """Get the default path manager."""
    return DEFAULT_PATH_MANAGER


def validate_paths() -> Dict[str, Any]:
    """Validate that all required paths exist."""
    path_manager = get_path_manager()
    src_path = path_manager.get_src_path()
    
    validation = {
        'project_root': str(path_manager.project_root),
        'src_path': str(src_path),
        'src_exists': src_path.exists(),
        'python_files_found': len(path_manager.find_python_files())
    }
    
    return validation 