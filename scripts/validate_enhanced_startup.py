#!/usr/bin/env python3
"""
Enhanced Startup Validation Script

This script validates the enhanced startup validation system with comprehensive
registry and CrewAI agent health checks following Enterprise best practices.
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

# Add project root to Python path for absolute imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_enhanced_validation():
    """Run the enhanced startup validation system."""
    try:
        logger.info("🚀 Starting Enhanced Startup Validation")
        logger.info("=" * 60)
        
        # Set required environment variables for testing
        os.environ.setdefault('KICKAI_INVITE_SECRET_KEY', 'test_key_for_validation')
        os.environ.setdefault('OLLAMA_BASE_URL', 'http://macmini1.local:11434')
        
        # Import and run the enhanced validation
        from kickai.core.startup_validation import run_startup_validation
        
        start_time = time.time()
        
        # Run validation with enhanced checks
        report = await run_startup_validation()
        
        validation_time = time.time() - start_time
        
        # Display results
        logger.info("📊 ENHANCED VALIDATION RESULTS")
        logger.info("=" * 60)
        logger.info(f"Overall Status: {report.overall_status.value}")
        logger.info(f"Total Checks: {len(report.checks)}")
        logger.info(f"Validation Time: {validation_time:.2f}s")
        logger.info(f"Critical Failures: {len(report.critical_failures)}")
        logger.info(f"Warnings: {len(report.warnings)}")
        
        # Display check results
        logger.info("\n📋 CHECK DETAILS")
        logger.info("-" * 40)
        
        for check in report.checks:
            status_icon = "✅" if check.status.value == "PASSED" else "❌"
            logger.info(f"{status_icon} {check.name}: {check.status.value}")
            
            if check.status.value == "FAILED":
                logger.error(f"   Error: {check.message}")
            elif hasattr(check, 'details') and check.details:
                # Show first few details for passed checks
                if isinstance(check.details, dict) and 'component_results' in check.details:
                    component_count = len(check.details['component_results'])
                    logger.info(f"   Components validated: {component_count}")
                elif isinstance(check.details, str):
                    logger.info(f"   Details: {check.details[:100]}...")
        
        # Show critical failures if any
        if report.critical_failures:
            logger.error("\n🚨 CRITICAL FAILURES")
            logger.error("-" * 40)
            for failure in report.critical_failures:
                logger.error(f"❌ {failure.name}: {failure.message}")
        
        # Show warnings if any
        if report.warnings:
            logger.warning("\n⚠️ WARNINGS")
            logger.warning("-" * 40)
            for warning in report.warnings:
                logger.warning(f"⚠️ {warning.name}: {warning.message}")
        
        # Show recommendations if any
        if hasattr(report, 'recommendations') and report.recommendations:
            logger.info("\n💡 RECOMMENDATIONS")
            logger.info("-" * 40)
            for recommendation in report.recommendations:
                logger.info(f"💡 {recommendation}")
        
        # Performance metrics
        logger.info("\n📈 PERFORMANCE METRICS")
        logger.info("-" * 40)
        logger.info(f"Average check time: {validation_time / len(report.checks):.2f}s")
        
        if validation_time > 60:
            logger.warning(f"⚠️ Validation took {validation_time:.2f}s (consider optimization)")
        else:
            logger.info(f"✅ Validation completed in acceptable time: {validation_time:.2f}s")
        
        # Overall assessment
        logger.info("\n🎯 OVERALL ASSESSMENT")
        logger.info("=" * 60)
        
        if report.overall_status.value == "PASSED":
            logger.info("✅ SYSTEM READY FOR OPERATION")
            logger.info("All critical components validated successfully")
            return True
        else:
            logger.error("❌ SYSTEM NOT READY")
            logger.error("Critical issues must be resolved before operation")
            return False
            
    except Exception as e:
        logger.error(f"❌ Enhanced validation failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


async def test_individual_checks():
    """Test individual enhanced checks."""
    logger.info("\n🔧 TESTING INDIVIDUAL ENHANCED CHECKS")
    logger.info("=" * 60)
    
    try:
        # Test Enhanced Registry Check
        from kickai.core.startup_validation.checks import EnhancedRegistryCheck
        
        logger.info("Testing Enhanced Registry Check...")
        registry_check = EnhancedRegistryCheck()
        registry_result = await registry_check.execute({})
        
        logger.info(f"Enhanced Registry Check: {registry_result.status.value}")
        if registry_result.status.value == "FAILED":
            logger.error(f"Registry issues: {registry_result.message}")
        
        # Test CrewAI Agent Health Check
        from kickai.core.startup_validation.checks import CrewAIAgentHealthCheck
        
        logger.info("Testing CrewAI Agent Health Check...")
        agent_check = CrewAIAgentHealthCheck()
        agent_result = await agent_check.execute({})
        
        logger.info(f"CrewAI Agent Health Check: {agent_result.status.value}")
        if agent_result.status.value == "FAILED":
            logger.error(f"Agent issues: {agent_result.message}")
        
        # Test Initialization Sequence Check
        from kickai.core.startup_validation.checks import InitializationSequenceCheck
        
        logger.info("Testing Initialization Sequence Check...")
        init_check = InitializationSequenceCheck()
        init_result = await init_check.execute({})
        
        logger.info(f"Initialization Sequence Check: {init_result.status.value}")
        if init_result.status.value == "FAILED":
            logger.error(f"Initialization issues: {init_result.message}")
        
        return True
        
    except Exception as e:
        logger.error(f"Individual check testing failed: {e}")
        return False


async def main():
    """Main validation script."""
    logger.info("🔍 Enhanced Startup Validation System")
    logger.info("Following CrewAI Enterprise best practices")
    logger.info("=" * 60)
    
    try:
        # Run individual check tests first
        individual_success = await test_individual_checks()
        
        # Run full enhanced validation
        validation_success = await run_enhanced_validation()
        
        # Final summary
        logger.info("\n🏁 FINAL SUMMARY")
        logger.info("=" * 60)
        
        if individual_success and validation_success:
            logger.info("✅ ALL VALIDATIONS PASSED")
            logger.info("Enhanced startup validation system is working correctly")
            sys.exit(0)
        else:
            logger.error("❌ VALIDATION FAILURES DETECTED")
            logger.error("Review the issues above and fix before proceeding")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Validation script failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())