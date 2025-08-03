#!/usr/bin/env python3
"""
Validation Failure Diagnostic Script

This script provides detailed diagnostics for validation failures,
showing exactly which components are missing and why.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set PYTHONPATH for proper imports
os.environ["PYTHONPATH"] = str(project_root)

from kickai.core.startup_validation.validator import run_startup_validation
from kickai.core.startup_validation.checks.system_readiness_check import SystemReadinessCheck


def setup_logging():
    """Setup logging configuration."""
    from loguru import logger
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with INFO level
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )


async def diagnose_system_readiness():
    """Run detailed system readiness diagnostics."""
    logger = logging.getLogger(__name__)
    
    print("🔍 Running detailed System Readiness diagnostics...")
    print("=" * 60)
    
    # Create the check
    check = SystemReadinessCheck()
    
    # Run the check with empty context
    context = {}
    result = await check.execute(context)
    
    print(f"📊 System Readiness Check Results:")
    print(f"   Status: {result.status.value}")
    print(f"   Message: {result.message}")
    
    if result.details:
        print(f"   Total Checks: {result.details.get('total_checks', 'N/A')}")
        print(f"   Passed: {result.details.get('success_count', 'N/A')}")
        print(f"   Failed: {result.details.get('failure_count', 'N/A')}")
        
        if 'failed_checks' in result.details:
            print(f"\n❌ Failed Components:")
            for i, failure in enumerate(result.details['failed_checks'], 1):
                print(f"   {i}. {failure}")
        
        if 'passed_checks' in result.details:
            print(f"\n✅ Passed Components:")
            for i, success in enumerate(result.details['passed_checks'], 1):
                print(f"   {i}. {success}")
    
    print("=" * 60)
    
    # Provide recommendations
    print("💡 Recommendations:")
    if result.status.value == "FAILED":
        print("   • Review the failed components above")
        print("   • Ensure all required services are running")
        print("   • Check configuration files and environment variables")
        print("   • Verify database connectivity")
        print("   • Ensure all registries are properly initialized")
    else:
        print("   • System is ready for operation")
    
    return result


async def main():
    """Main diagnostic function."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 KICKAI Validation Failure Diagnostics")
    logger.info("=" * 60)
    
    try:
        # Run detailed system readiness diagnostics
        result = await diagnose_system_readiness()
        
        if result.status.value == "FAILED":
            logger.error("❌ System readiness check failed")
            logger.error("🔧 Please address the issues above before starting the system")
            return 1
        else:
            logger.info("✅ System readiness check passed")
            return 0
            
    except Exception as e:
        logger.critical(f"❌ Diagnostic failed with error: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Diagnostics interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1) 