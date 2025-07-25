#!/usr/bin/env python3
"""
Quick Validation Script

A lightweight validation script that can be run during development to catch
common runtime issues before they occur in production.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kickai.core.validation.agent_validation import run_agent_validation
from kickai.core.logging_config import logger


def main():
    """Run quick validation checks."""
    logger.info("🔍 Quick Agent System Validation")
    logger.info("=" * 40)
    
    # Run the comprehensive agent validation
    result = run_agent_validation()
    
    if result.passed:
        logger.info("✅ All validations passed! Ready for development.")
        return 0
    else:
        logger.error(f"❌ Validation failed with {len(result.errors)} errors:")
        for error in result.errors:
            logger.error(f"   - {error}")
        logger.error("Please fix these issues before running the bot.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 