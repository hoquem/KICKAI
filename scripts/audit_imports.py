#!/usr/bin/env python3
"""
Import Audit Script - Professional way to find and fix import issues
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

def find_imports_in_file(file_path: Path) -> List[Tuple[str, str, int]]:
    """Find all imports in a Python file."""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, '', node.lineno))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append((module, alias.name, node.lineno))
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return imports

def audit_imports(src_path: str = "kickai") -> Dict[str, List[Tuple[str, str, int]]]:
    """Audit all imports in the codebase."""
    src_dir = Path(src_path)
    all_imports = {}
    
    for py_file in src_dir.rglob("*.py"):
        if "venv" not in str(py_file) and "__pycache__" not in str(py_file):
            imports = find_imports_in_file(py_file)
            if imports:
                all_imports[str(py_file)] = imports
    
    return all_imports

def find_problematic_imports(all_imports: Dict[str, List[Tuple[str, str, int]]]) -> Dict[str, List[str]]:
    """Find imports that might be problematic."""
    problems = {
        "kickai.core.settings": [],
        "kickai.core.interfaces.tool_interfaces": [],
        "EntityType from wrong module": [],
        "missing modules": []
    }
    
    for file_path, imports in all_imports.items():
        for module, name, line in imports:
            # Check for old settings imports
            if "kickai.core.settings" in module:
                problems["kickai.core.settings"].append(f"{file_path}:{line}")
            
            # Check for tool_interfaces imports
            if "kickai.core.interfaces.tool_interfaces" in module:
                problems["kickai.core.interfaces.tool_interfaces"].append(f"{file_path}:{line}")
            
            # Check for EntityType imports from wrong places
            if name == "EntityType" and "entity_specific_agents" in module:
                problems["EntityType from wrong module"].append(f"{file_path}:{line}")
    
    return problems

def main():
    print("🔍 Starting comprehensive import audit...")
    
    # Audit all imports
    all_imports = audit_imports()
    print(f"✅ Audited {len(all_imports)} Python files")
    
    # Find problematic imports
    problems = find_problematic_imports(all_imports)
    
    print("\n📊 Import Issues Found:")
    for issue_type, files in problems.items():
        if files:
            print(f"\n❌ {issue_type}:")
            for file in files:
                print(f"   - {file}")
        else:
            print(f"\n✅ {issue_type}: No issues found")
    
    # Summary
    total_issues = sum(len(files) for files in problems.values())
    print(f"\n🎯 Total issues to fix: {total_issues}")
    
    if total_issues > 0:
        print("\n💡 Recommended fixes:")
        print("1. Replace 'kickai.core.settings' with 'kickai.core.config'")
        print("2. Replace 'kickai.core.interfaces.tool_interfaces' with 'kickai.agents.tool_registry'")
        print("3. Ensure EntityType is imported from 'kickai.core.entity_types'")

if __name__ == "__main__":
    main()
