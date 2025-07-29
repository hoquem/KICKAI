#!/usr/bin/env python3
"""
Full System Validation Runner

This script runs comprehensive system validation to ensure:
1. No stub classes are being used
2. All real implementations are working
3. All systems are properly initialized
4. The system is ready for production use
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env')

from kickai.core.startup_validation import run_startup_validation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('full_system_validation.log')
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Run full system validation and report results."""
    logger.info("🚀 Starting KICKAI Full System Validation...")
    logger.info("=" * 80)
    logger.info("🔍 This validation ensures:")
    logger.info("   • No stub classes are being used")
    logger.info("   • All real implementations are working")
    logger.info("   • All systems are properly initialized")
    logger.info("   • The system is ready for production use")
    logger.info("=" * 80)
    
    try:
        # Run comprehensive validation
        report = await run_startup_validation(team_id="KAI")
        
        # Print detailed results
        logger.info("\n" + "=" * 80)
        logger.info("📊 VALIDATION RESULTS SUMMARY")
        logger.info("=" * 80)
        
        # Overall status
        if report.is_healthy():
            logger.info("🎉 OVERALL STATUS: HEALTHY ✅")
        else:
            logger.error("❌ OVERALL STATUS: UNHEALTHY")
        
        # Check breakdown
        passed_checks = [check for check in report.checks if check.status.value == "PASSED"]
        failed_checks = [check for check in report.checks if check.status.value == "FAILED"]
        warning_checks = [check for check in report.checks if check.status.value == "WARNING"]
        
        logger.info(f"📈 Checks Passed: {len(passed_checks)}")
        logger.info(f"❌ Checks Failed: {len(failed_checks)}")
        logger.info(f"⚠️  Checks with Warnings: {len(warning_checks)}")
        
        # Detailed results
        logger.info("\n" + "-" * 80)
        logger.info("📋 DETAILED CHECK RESULTS")
        logger.info("-" * 80)
        
        for check in report.checks:
            status_emoji = "✅" if check.status.value == "PASSED" else "❌" if check.status.value == "FAILED" else "⚠️"
            logger.info(f"{status_emoji} {check.name}: {check.message}")
            
            # Show details for failed checks
            if check.status.value == "FAILED" and check.details:
                if "stub_detections" in check.details:
                    logger.error("   🔍 Stub Detections:")
                    for detection in check.details["stub_detections"]:
                        logger.error(f"      • {detection}")
                
                if "implementation_validations" in check.details:
                    logger.info("   ✅ Implementation Validations:")
                    for validation in check.details["implementation_validations"]:
                        logger.info(f"      • {validation}")
        
        # Critical failures
        if report.critical_failures:
            logger.error("\n" + "-" * 80)
            logger.error("🚨 CRITICAL FAILURES")
            logger.error("-" * 80)
            for failure in report.critical_failures:
                logger.error(f"❌ {failure}")
        
        # Warnings
        if report.warnings:
            logger.warning("\n" + "-" * 80)
            logger.warning("⚠️  WARNINGS")
            logger.warning("-" * 80)
            for warning in report.warnings:
                logger.warning(f"⚠️  {warning}")
        
        # Recommendations
        if report.recommendations:
            logger.info("\n" + "-" * 80)
            logger.info("💡 RECOMMENDATIONS")
            logger.info("-" * 80)
            for recommendation in report.recommendations:
                logger.info(f"💡 {recommendation}")
        
        # Final verdict
        logger.info("\n" + "=" * 80)
        if report.is_healthy():
            logger.info("🎉 SYSTEM VALIDATION: PASSED ✅")
            logger.info("🚀 The system is ready for production use!")
            logger.info("💡 All real implementations are working correctly.")
            logger.info("🔧 No stub classes detected.")
            return 0
        else:
            logger.error("❌ SYSTEM VALIDATION: FAILED")
            logger.error("🚫 The system is NOT ready for production use.")
            logger.error("🔧 Please fix the critical failures before proceeding.")
            return 1
            
    except Exception as e:
        logger.error(f"\n💥 System validation failed with error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 