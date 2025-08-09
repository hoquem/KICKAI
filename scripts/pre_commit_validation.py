#!/usr/bin/env python3
"""
Pre-Commit Validation Script

This script runs validation checks before commits to catch runtime issues early.
It can be integrated into git hooks or run manually during development.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kickai.core.logging_config import logger


def run_ruff_check():
    """Run Ruff linting and formatting checks."""
    logger.info("🔍 Running Ruff checks...")
    
    try:
        # Run Ruff linting
        result = subprocess.run(
            ["ruff", "check", "--fix", "src/"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Ruff check failed:\n{result.stdout}\n{result.stderr}")
            return False
        
        logger.info("✅ Ruff checks passed")
        return True
        
    except FileNotFoundError:
        logger.error("❌ Ruff not found. Please install: pip install ruff")
        return False
    except Exception as e:
        logger.error(f"❌ Ruff check error: {e}")
        return False


def run_agent_validation():
    """Run agent system validation."""
    logger.info("🔍 Running agent validation...")
    
    try:
        result = subprocess.run(
            [sys.executable, "scripts/validate_agent_system.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Agent validation failed:\n{result.stdout}\n{result.stderr}")
            return False
        
        logger.info("✅ Agent validation passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent validation error: {e}")
        return False


def run_unit_tests():
    """Run unit tests."""
    logger.info("🔍 Running unit tests...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/unit/", "-v"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Unit tests failed:\n{result.stdout}\n{result.stderr}")
            return False
        
        logger.info("✅ Unit tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Unit test error: {e}")
        return False


def check_critical_files():
    """Check that critical files exist and are accessible."""
    logger.info("🔍 Checking critical files...")
    
    critical_files = [
        "src/kickai/agents/tool_output_capture.py",
        "src/kickai/agents/configurable_agent.py",
        "src/kickai/agents/crew_agents.py",
        "src/kickai/core/dependency_container.py",
        "src/kickai/core/logging_config.py"
    ]
    
    missing_files = []
    
    for file_path in critical_files:
        full_path = Path(__file__).parent.parent / file_path
        if not full_path.exists():
            missing_files.append(file_path)
            logger.error(f"❌ Missing critical file: {file_path}")
    
    if missing_files:
        logger.error(f"❌ Missing {len(missing_files)} critical files")
        return False
    
    logger.info("✅ All critical files present")
    return True


def main():
    """Run all pre-commit validations."""
    logger.info("🚀 Starting Pre-Commit Validation")
    logger.info("=" * 50)
    
    validation_results = []
    
    # Check critical files
    files_ok = check_critical_files()
    validation_results.append(("Critical Files", files_ok))
    
    # Run Ruff checks
    ruff_ok = run_ruff_check()
    validation_results.append(("Ruff Checks", ruff_ok))
    
    # Run agent validation
    agent_ok = run_agent_validation()
    validation_results.append(("Agent Validation", agent_ok))
    
    # Run unit tests (optional, can be skipped for quick checks)
    if "--skip-tests" not in sys.argv:
        tests_ok = run_unit_tests()
        validation_results.append(("Unit Tests", tests_ok))
    else:
        logger.info("⏭️  Skipping unit tests (--skip-tests flag)")
        validation_results.append(("Unit Tests", True))
    
    # Report results
    logger.info("\n📊 Pre-Commit Validation Results")
    logger.info("=" * 50)
    
    all_passed = True
    for name, passed in validation_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 All pre-commit validations passed!")
        logger.info("✅ Ready to commit")
        return 0
    else:
        logger.error("\n⚠️  Pre-commit validations failed.")
        logger.error("Please fix the issues before committing.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 