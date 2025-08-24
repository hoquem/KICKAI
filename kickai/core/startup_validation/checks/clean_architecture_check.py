#!/usr/bin/env python3
"""
Clean Architecture Validation Check

Validates that the system follows Clean Architecture principles:
- All @tool decorators are in application layer (not domain layer)
- Tool registration is using application layer imports
- Domain layer remains pure business logic
"""

import ast
import os
from pathlib import Path
from typing import List, Tuple

from .base_check import BaseCheck
from ..reporting import CheckResult, CheckStatus, CheckCategory


class CleanArchitectureCheck(BaseCheck):
    """Validates Clean Architecture compliance across the codebase."""
    
    name = "Clean Architecture Compliance"
    category = CheckCategory.SYSTEM
    
    def __init__(self):
        super().__init__()
        # Navigate up from /kickai/core/startup_validation/checks/ to /kickai/
        self.kickai_root = Path(__file__).parent.parent.parent.parent.parent
        
    async def execute(self) -> CheckResult:
        """Execute Clean Architecture validation checks."""
        try:
            violations = []
            
            # Check 1: No @tool decorators in domain layer
            domain_violations = await self._check_domain_layer_purity()
            violations.extend(domain_violations)
            
            # Check 2: Tool registry uses application layer imports
            registry_violations = await self._check_tool_registry_imports()
            violations.extend(registry_violations)
            
            # Check 3: Application layer tools are properly structured
            structure_violations = await self._check_application_layer_structure()
            violations.extend(structure_violations)
            
            if violations:
                return CheckResult(
                    status=CheckStatus.FAILED,
                    name=self.name,
                    category=self.category,
                    message=f"Clean Architecture violations found: {'; '.join(violations)}"
                )
            
            return CheckResult(
                status=CheckStatus.SUCCESS,
                name=self.name, 
                category=self.category,
                message="Clean Architecture compliance verified: Domain layer is pure, Application layer handles framework concerns, Tool registry uses correct imports"
            )
            
        except Exception as e:
            return CheckResult(
                status=CheckStatus.FAILED,
                name=self.name,
                category=self.category,
                message=f"Clean Architecture check failed: {str(e)}",
                error=e
            )
    
    async def _check_domain_layer_purity(self) -> List[str]:
        """Check that domain layer has no @tool decorators."""
        violations = []
        
        # Find all domain/tools directories
        domain_dirs = list(self.kickai_root.glob("kickai/features/*/domain/tools"))
        
        for domain_dir in domain_dirs:
            if not domain_dir.exists():
                continue
                
            # Check all Python files in domain/tools
            for py_file in domain_dir.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                    
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    # Check for @tool decorator (quick string check first)
                    if "@tool(" in content or "@tool " in content:
                        # Parse AST for more precise detection
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                for decorator in node.decorator_list:
                                    if (isinstance(decorator, ast.Call) and 
                                        isinstance(decorator.func, ast.Name) and 
                                        decorator.func.id == "tool"):
                                        violations.append(
                                            f"@tool decorator found in domain layer: {py_file.relative_to(self.kickai_root)}"
                                        )
                                        break
                                        
                except (UnicodeDecodeError, SyntaxError) as e:
                    # Skip files that can't be parsed
                    pass
        
        return violations
    
    async def _check_tool_registry_imports(self) -> List[str]:
        """Check that tool registry imports from application layer."""
        violations = []
        
        registry_file = self.kickai_root / "kickai/agents/tool_registry.py"
        if not registry_file.exists():
            violations.append("Tool registry file not found")
            return violations
            
        try:
            content = registry_file.read_text(encoding='utf-8')
            
            # Check for forbidden domain layer imports
            forbidden_patterns = [
                "from kickai.features.*.domain.tools",
                ".domain.tools",
            ]
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Check for domain layer tool imports
                if (".domain.tools" in line_stripped and 
                    "from kickai.features" in line_stripped and
                    not line_stripped.startswith('#')):
                    violations.append(
                        f"Tool registry importing from domain layer (line {i}): {line_stripped[:50]}..."
                    )
        
        except (UnicodeDecodeError, SyntaxError):
            violations.append("Tool registry file could not be parsed")
        
        return violations
    
    async def _check_application_layer_structure(self) -> List[str]:
        """Check that application layer has proper tool structure."""
        violations = []
        
        # Find all application/tools directories
        app_dirs = list(self.kickai_root.glob("kickai/features/*/application/tools"))
        
        if len(app_dirs) == 0:
            violations.append("No application/tools directories found")
            return violations
        
        tools_found = 0
        
        for app_dir in app_dirs:
            if not app_dir.exists():
                continue
                
            # Check for Python files with @tool decorators
            for py_file in app_dir.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                    
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    # Count tools in this file
                    if "@tool(" in content:
                        # Parse AST to count tools
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                for decorator in node.decorator_list:
                                    if (isinstance(decorator, ast.Call) and 
                                        isinstance(decorator.func, ast.Name) and 
                                        decorator.func.id == "tool"):
                                        tools_found += 1
                                        break
                                        
                except (UnicodeDecodeError, SyntaxError):
                    pass
        
        if tools_found < 10:  # Expect at least 10 tools after migration
            violations.append(f"Only {tools_found} tools found in application layer, expected migration of 62+ tools")
        
        return violations