#!/usr/bin/env python3
"""
Pre-commit validation script to ensure proper context field usage.

This script prevents the use of 'username' instead of 'telegram_username' 
in context field access patterns.
"""

import sys
import os
import re
from pathlib import Path


def find_context_field_violations(file_path: Path) -> list[tuple[int, str]]:
    """
    Find lines that use 'username' instead of 'telegram_username' in context access.
    
    Returns:
        List of (line_number, line_content) tuples for violations
    """
    violations = []
    
    # Patterns that should use telegram_username instead of username
    patterns = [
        r"\.get\s*\(\s*['\"]username['\"]",  # .get('username') or .get("username")
        r"context\s*\[\s*['\"]username['\"]",  # context['username']
        r"validated_context\s*\[\s*['\"]username['\"]",  # validated_context['username']
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments and docstrings
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                
                # Check for violations
                for pattern in patterns:
                    if re.search(pattern, line):
                        # Exclude documentation files, examples, and this validation script itself
                        if ('README' not in file_path.name and 
                            'example' not in str(file_path).lower() and
                            'validate_context_fields.py' not in file_path.name):
                            violations.append((line_num, line.strip()))
                        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return violations


def validate_project_context_fields(project_root: Path) -> bool:
    """
    Validate all Python files in the project for proper context field usage.
    
    Returns:
        True if no violations found, False otherwise
    """
    violations_found = False
    
    # Search in key directories
    search_dirs = [
        project_root / 'kickai',
        project_root / 'scripts',
        project_root / 'tests'
    ]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        for py_file in search_dir.rglob('*.py'):
            violations = find_context_field_violations(py_file)
            
            if violations:
                violations_found = True
                print(f"\n❌ CONTEXT FIELD VIOLATIONS in {py_file}:")
                for line_num, line_content in violations:
                    print(f"   Line {line_num}: {line_content}")
                print(f"   → Change 'username' to 'telegram_username'")
    
    return not violations_found


def main():
    """Main validation function."""
    print("🔍 Validating context field usage...")
    
    project_root = Path(__file__).parent.parent
    
    if validate_project_context_fields(project_root):
        print("✅ All context field usage is correct!")
        sys.exit(0)
    else:
        print("\n🚨 CRITICAL: Context field violations found!")
        print("   Fix all violations by changing 'username' to 'telegram_username'")
        print("   This prevents inconsistency bugs in the system.")
        sys.exit(1)


if __name__ == "__main__":
    main()