#!/usr/bin/env python3
"""
Tool Consistency Validation Script

This script validates that all tools in the codebase are properly decorated
and follow consistent patterns.
"""

import ast
import importlib.util
import os
import sys
from pathlib import Path
from typing import Dict, List, Set

from loguru import logger


class ToolConsistencyValidator:
    """Validator for tool consistency across the codebase."""

    def __init__(self, src_path: str = "kickai"):
        self.src_path = Path(src_path)
        self.issues = {
            "missing_decorators": [],
            "missing_tool_names": [],
            "inconsistent_patterns": [],
            "undecorated_functions": []
        }
        self.tool_files = []
        self.decorated_functions = set()
        self.undecorated_functions = set()

    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all tools in the codebase."""
        logger.info("🔍 Starting tool consistency validation...")

        # Find all tool files
        self._find_tool_files()
        
        # Validate each tool file
        for file_path in self.tool_files:
            self._validate_tool_file(file_path)

        # Generate report
        return self._generate_report()

    def _find_tool_files(self) -> None:
        """Find all tool files in the codebase."""
        features_path = self.src_path / "features"
        
        if not features_path.exists():
            logger.warning(f"Features path not found: {features_path}")
            return

        # Find tools directories
        for feature_dir in features_path.iterdir():
            if feature_dir.is_dir():
                tools_path = feature_dir / "domain" / "tools"
                if tools_path.exists():
                    for file_path in tools_path.glob("*.py"):
                        if not file_path.name.startswith("__"):
                            self.tool_files.append(file_path)

        # Find shared tools
        shared_tools_path = features_path / "shared" / "domain" / "tools"
        if shared_tools_path.exists():
            for file_path in shared_tools_path.glob("*.py"):
                if not file_path.name.startswith("__"):
                    self.tool_files.append(file_path)

        logger.info(f"Found {len(self.tool_files)} tool files to validate")

    def _validate_tool_file(self, file_path: Path) -> None:
        """Validate a single tool file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            
            # Check for imports
            has_tool_import = self._check_tool_import(tree)
            
            # Check for decorated functions
            self._check_decorated_functions(tree, file_path, has_tool_import)
            
            # Check for undecorated functions that should be tools
            self._check_undecorated_functions(tree, file_path)

        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")

    def _check_tool_import(self, tree: ast.AST) -> bool:
        """Check if the file imports the tool decorator."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if (node.module == "kickai.utils.crewai_tool_decorator" and 
                    any(alias.name == "tool" for alias in node.names)):
                    return True
        return False

    def _check_decorated_functions(self, tree: ast.AST, file_path: Path, has_tool_import: bool) -> None:
        """Check decorated functions for consistency."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.decorator_list:
                    for decorator in node.decorator_list:
                        if self._is_tool_decorator(decorator):
                            self.decorated_functions.add(f"{file_path.name}:{node.name}")
                            
                            # Check if decorator has tool name
                            if not self._has_tool_name(decorator):
                                self.issues["missing_tool_names"].append(
                                    f"{file_path}:{node.name} - Missing tool name in decorator"
                                )
                            
                            # Check for consistent patterns
                            if not self._check_consistent_pattern(node):
                                self.issues["inconsistent_patterns"].append(
                                    f"{file_path}:{node.name} - Inconsistent pattern"
                                )

    def _check_undecorated_functions(self, tree: ast.AST, file_path: Path) -> None:
        """Check for functions that should be tools but aren't decorated."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.decorator_list:  # No decorators
                    # Check if this function should be a tool
                    if self._should_be_tool(node):
                        self.undecorated_functions.add(f"{file_path.name}:{node.name}")
                        self.issues["undecorated_functions"].append(
                            f"{file_path}:{node.name} - Should be decorated as tool"
                        )

    def _is_tool_decorator(self, decorator: ast.expr) -> bool:
        """Check if a decorator is the tool decorator."""
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name) and decorator.func.id == "tool":
                return True
        elif isinstance(decorator, ast.Name) and decorator.id == "tool":
            return True
        return False

    def _has_tool_name(self, decorator: ast.expr) -> bool:
        """Check if the tool decorator has a tool name."""
        if isinstance(decorator, ast.Call):
            if decorator.args:
                return True
        return False

    def _check_consistent_pattern(self, node: ast.FunctionDef) -> bool:
        """Check if the function follows consistent patterns."""
        # Check return type annotation
        if not node.returns:
            return False
        
        # Check if returns str
        if isinstance(node.returns, ast.Name) and node.returns.id == "str":
            return True
        
        return True

    def _should_be_tool(self, node: ast.FunctionDef) -> bool:
        """Check if a function should be decorated as a tool."""
        # Skip private functions (starting with _) - these are internal helpers
        if node.name.startswith("_"):
            return False
        
        # Check if function name suggests it should be a tool
        tool_keywords = [
            "get_", "set_", "update_", "create_", "delete_", "validate_",
            "register_", "approve_", "reject_", "send_", "log_", "format_",
            "check_", "verify_", "process_", "handle_", "manage_"
        ]
        
        function_name = node.name.lower()
        if any(function_name.startswith(keyword) for keyword in tool_keywords):
            return True
        
        # Check if function has string return type
        if node.returns and isinstance(node.returns, ast.Name) and node.returns.id == "str":
            return True
        
        return False

    def _generate_report(self) -> Dict[str, List[str]]:
        """Generate a validation report."""
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        logger.info(f"🔍 Tool validation complete:")
        logger.info(f"  - Tool files checked: {len(self.tool_files)}")
        logger.info(f"  - Decorated functions: {len(self.decorated_functions)}")
        logger.info(f"  - Undecorated functions: {len(self.undecorated_functions)}")
        logger.info(f"  - Total issues found: {total_issues}")
        
        for issue_type, issues in self.issues.items():
            if issues:
                logger.warning(f"  - {issue_type}: {len(issues)} issues")
                for issue in issues:
                    logger.warning(f"    • {issue}")
        
        return self.issues


def main():
    """Main validation function."""
    # Add src to path
    src_path = Path("kickai")
    if not src_path.exists():
        logger.error("kickai directory not found. Run from project root.")
        return 1

    # Run validation
    validator = ToolConsistencyValidator("kickai")
    issues = validator.validate_all()
    
    # Check if there are any issues
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    
    if total_issues == 0:
        logger.success("✅ All tools are consistent!")
        return 0
    else:
        logger.error(f"❌ Found {total_issues} consistency issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())