#!/usr/bin/env python3
"""
Firestore Test Suite Runner

This script runs the comprehensive Firestore database test suite
and displays the results in a user-friendly format.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_banner():
    """Print test suite banner."""
    print("=" * 80)
    print("🔥 FIRESTORE COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing all Firestore operations across all features...")
    print("=" * 80)

def print_summary(report):
    """Print test summary."""
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {report.total_tests}")
    print(f"✅ Passed: {report.passed}")
    print(f"❌ Failed: {report.failed}")
    print(f"⏭️ Skipped: {report.skipped}")
    print(f"💥 Errors: {report.errors}")
    print(f"Success Rate: {report.summary['success_rate']}")
    print(f"Total Duration: {report.total_duration:.2f} seconds")
    print(f"Average Test Duration: {report.summary['average_test_duration']:.3f} seconds")
    
    if report.failed > 0 or report.errors > 0:
        print("\n🔍 FAILED TESTS:")
        for result in report.test_results:
            if result.status.value in ['FAIL', 'ERROR']:
                print(f"  ❌ {result.test_name}")
                if result.error_message:
                    print(f"     Error: {result.error_message}")
    
    print("=" * 80)

async def main():
    """Main execution function."""
    print_banner()
    
    try:
        # Import and run test suite
        from tests.firestore_comprehensive_test_suite import FirestoreComprehensiveTestSuite
        
        # Run tests
        test_suite = FirestoreComprehensiveTestSuite()
        report = await test_suite.run_all_tests()
        
        # Print summary
        print_summary(report)
        
        # Exit with appropriate code
        if report.failed > 0 or report.errors > 0:
            print(f"\n❌ Test suite completed with {report.failed} failures and {report.errors} errors")
            return 1
        else:
            print(f"\n✅ Test suite completed successfully! {report.passed}/{report.total_tests} tests passed")
            return 0
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        return 1
    except Exception as e:
        print(f"💥 Test suite failed to run: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 