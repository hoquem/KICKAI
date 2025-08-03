#!/usr/bin/env python3
"""
System Startup Validation Script

This script provides comprehensive validation of the KICKAI system startup process.
It can be used for:
1. Testing validation before deployment
2. Diagnosing startup issues
3. Validating system configuration
4. Ensuring all components are ready

Usage:
    python scripts/validate_system_startup.py [--team-id TEAM_ID] [--exit-on-failure] [--verbose]
"""

import argparse
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

from kickai.core.startup_validation.validator import run_critical_startup_validation


def setup_logging(level: int = logging.INFO) -> None:
    """Setup logging configuration."""
    from loguru import logger
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with specified level
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file handler
    logger.add(
        "logs/kickai.log",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days"
    )


async def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate KICKAI system startup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic validation
    python scripts/validate_system_startup.py
    
    # Validation with specific team
    python scripts/validate_system_startup.py --team-id KAI
    
    # Validation that exits on failure
    python scripts/validate_system_startup.py --exit-on-failure
    
    # Verbose validation with detailed output
    python scripts/validate_system_startup.py --verbose
        """
    )
    
    parser.add_argument(
        "--team-id",
        type=str,
        help="Team ID to validate (default: auto-detect from Firestore)"
    )
    
    parser.add_argument(
        "--exit-on-failure",
        action="store_true",
        help="Exit with error code 1 if validation fails"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = getattr(logging, args.log_level.upper())
    if args.verbose:
        log_level = logging.DEBUG
    
    setup_logging(level=log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 KICKAI System Startup Validation")
    logger.info("=" * 50)
    
    try:
        # Run critical validation
        success = await run_critical_startup_validation(
            team_id=args.team_id,
            exit_on_failure=args.exit_on_failure
        )
        
        if success:
            logger.info("✅ System validation completed successfully!")
            logger.info("🎉 System is ready to start")
            return 0
        else:
            logger.error("❌ System validation failed!")
            logger.error("🔧 Please fix the issues before starting the system")
            return 1
            
    except KeyboardInterrupt:
        logger.info("🛑 Validation interrupted by user")
        return 1
    except Exception as e:
        logger.critical(f"❌ Critical error during validation: {e}")
        logger.critical("🛑 System validation failed due to unexpected error")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1) 