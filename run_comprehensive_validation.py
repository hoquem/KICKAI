#!/usr/bin/env python3
"""
Comprehensive Validation Test Runner
Runs synchronous system startup validation
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "kickai"))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not available, using system environment variables")
except Exception as e:
    print(f"⚠️ Failed to load .env file: {e}")

from kickai.core.startup_validation.comprehensive_validator import (
    ComprehensiveStartupValidator,
    validate_system_startup,
    get_startup_validation_report
)

def main():
    """Run comprehensive validation and display results."""
    print("🚀 Starting Comprehensive System Validation...")
    print("=" * 60)
    
    # Run validation
    validator = ComprehensiveStartupValidator()
    result = validator.validate_system_startup()
    
    # Display summary
    print(f"\n📊 VALIDATION SUMMARY")
    print(f"   Success: {'✅ PASS' if result.success else '❌ FAIL'}")
    print(f"   Total Checks: {result.total_checks}")
    print(f"   Passed: {result.passed_checks}")
    print(f"   Failed: {result.failed_checks}")
    print(f"   Duration: {result.total_duration:.2f}s")
    
    # Display individual check results
    if result.check_durations:
        print(f"\n⏱️  CHECK DURATIONS:")
        for check_name, duration in result.check_durations.items():
            status = "✅" if check_name not in ["environment", "database", "registry", "services", "filesystem"] or result.success else "❌"
            print(f"   {status} {check_name}: {duration:.2f}s")
    
    # Display warnings
    if result.warnings:
        print(f"\n⚠️  WARNINGS ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"   - {warning}")
    
    # Display detailed results
    if result.environment_result and not result.environment_result.success:
        print(f"\n🔧 ENVIRONMENT ERRORS:")
        for error in result.environment_result.errors:
            print(f"   ❌ {error}")
    
    if result.database_result and not result.database_result.success:
        print(f"\n🗄️  DATABASE ERRORS:")
        for error in result.database_result.errors:
            print(f"   ❌ {error}")
    
    # Display detailed report
    print(f"\n📋 DETAILED REPORT:")
    print("=" * 60)
    report = validator.get_validation_report(result)
    print(report)
    
    # Exit with appropriate code
    if result.success:
        print(f"\n🎉 System validation PASSED - Bot is ready to start!")
        return 0
    else:
        print(f"\n❌ System validation FAILED - Bot cannot start safely!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 