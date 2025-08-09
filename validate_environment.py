#!/usr/bin/env python3
"""
Environment validation script for Claude Code and KICKAI project.
This script validates that all environment requirements are met.
"""

import sys
import os
import subprocess
from pathlib import Path

def validate_python_version():
    """Validate Python version is 3.11+"""
    print("🐍 Validating Python version...")
    
    required_version = (3, 11)
    current_version = sys.version_info[:2]
    
    print(f"   Current version: Python {current_version[0]}.{current_version[1]}")
    print(f"   Required version: Python {required_version[0]}.{required_version[1]}+")
    print(f"   Python executable: {sys.executable}")
    
    if current_version < required_version:
        print("   ❌ FAIL: Python version too old")
        return False
    elif current_version >= (3, 12):
        print("   ⚠️  WARNING: Python version newer than tested (3.11.x recommended)")
        return True
    else:
        print("   ✅ PASS: Python version is compatible")
        return True

def validate_virtual_environment():
    """Validate virtual environment setup"""
    print("\n🔧 Validating virtual environment...")
    
    # Check if we're in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    venv_path = Path("venv311")
    
    print(f"   Virtual environment active: {'Yes' if in_venv else 'No'}")
    print(f"   venv311 directory exists: {'Yes' if venv_path.exists() else 'No'}")
    
    if not venv_path.exists():
        print("   ❌ FAIL: venv311 directory not found")
        return False
    
    if not in_venv:
        print("   ❌ FAIL: Virtual environment not activated")
        return False
    
    if 'venv311' not in sys.executable:
        print("   ⚠️  WARNING: Not using venv311 virtual environment")
        print(f"     Current: {sys.executable}")
        print(f"     Expected: Should contain 'venv311'")
        return True
    
    print("   ✅ PASS: Virtual environment is correctly configured")
    return True

def validate_pythonpath():
    """Validate PYTHONPATH is set correctly"""
    print("\n📁 Validating PYTHONPATH...")
    
    pythonpath = os.environ.get('PYTHONPATH', '')
    current_dir = str(Path.cwd())
    
    print(f"   PYTHONPATH: {pythonpath}")
    print(f"   Current directory: {current_dir}")
    
    if not pythonpath:
        print("   ❌ FAIL: PYTHONPATH not set")
        return False
    
    if current_dir not in pythonpath and '.' not in pythonpath:
        print("   ❌ FAIL: Current directory not in PYTHONPATH")
        return False
    
    print("   ✅ PASS: PYTHONPATH is correctly configured")
    return True

def validate_dependencies():
    """Validate key dependencies are installed"""
    print("\n📦 Validating dependencies...")
    
    required_packages = [
        'crewai',
        'python-telegram-bot',
        'firebase-admin',
        'pydantic',
        'pytest'
    ]
    
    all_good = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}: installed")
        except ImportError:
            print(f"   ❌ {package}: NOT installed")
            all_good = False
    
    if all_good:
        print("   ✅ PASS: All required dependencies are installed")
    else:
        print("   ❌ FAIL: Some dependencies are missing")
        print("   Run: pip install -r requirements.txt && pip install -r requirements-local.txt")
    
    return all_good

def validate_project_files():
    """Validate essential project files exist"""
    print("\n📄 Validating project files...")
    
    required_files = [
        'pyproject.toml',
        'requirements.txt',
        'requirements-local.txt',
        'run_bot_local.py',
        'kickai/__init__.py',
        '.env'
    ]
    
    all_good = True
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}: exists")
        else:
            print(f"   ❌ {file_path}: missing")
            all_good = False
    
    if all_good:
        print("   ✅ PASS: All essential files are present")
    else:
        print("   ❌ FAIL: Some essential files are missing")
    
    return all_good

def main():
    """Run all validation checks"""
    print("🔍 KICKAI Environment Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", validate_python_version),
        ("Virtual Environment", validate_virtual_environment),
        ("PYTHONPATH", validate_pythonpath),
        ("Dependencies", validate_dependencies),
        ("Project Files", validate_project_files)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ ERROR during {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - Environment is ready!")
        print("\n💡 Quick start commands:")
        print("   make dev          # Start development server")
        print("   make test         # Run tests")
        print("   make lint         # Run linting")
    else:
        print("⚠️  SOME CHECKS FAILED - Please fix the issues above")
        print("\n🔧 Common fixes:")
        print("   make setup-dev    # Set up development environment")
        print("   source venv311/bin/activate  # Activate virtual environment")
        print("   export PYTHONPATH=.          # Set PYTHONPATH")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())