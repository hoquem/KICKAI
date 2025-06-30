#!/usr/bin/env python3
"""
Test runner for Phase 1 improvements.
Runs all Phase 1 related tests and provides a summary report.
"""

import unittest
import sys
import os
import time
from typing import List, Dict

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_phase1_tests():
    """Run all Phase 1 tests and return results."""
    print("🧪 Running Phase 1 Tests")
    print("=" * 50)
    
    # Test modules to run
    test_modules = [
        'test_agent_capabilities',
        'test_phase1_integration'
    ]
    
    # Load test suites
    loader = unittest.TestLoader()
    suites = []
    
    for module_name in test_modules:
        try:
            # Import the module directly
            module = __import__(f'tests.{module_name}', fromlist=['*'])
            suite = loader.loadTestsFromModule(module)
            suites.append(suite)
            print(f"✅ Loaded test suite: {module_name}")
        except Exception as e:
            print(f"❌ Failed to load test suite {module_name}: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    results = []
    
    start_time = time.time()
    
    for suite in suites:
        result = runner.run(suite)
        results.append(result)
    
    end_time = time.time()
    
    # Generate summary
    print("\n" + "=" * 50)
    print("📊 Phase 1 Test Summary")
    print("=" * 50)
    
    total_tests = sum(result.testsRun for result in results)
    total_failures = sum(len(result.failures) for result in results)
    total_errors = sum(len(result.errors) for result in results)
    total_skipped = sum(len(result.skipped) for result in results)
    total_passed = total_tests - total_failures - total_errors - total_skipped
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed} ✅")
    print(f"Failed: {total_failures} ❌")
    print(f"Errors: {total_errors} 💥")
    print(f"Skipped: {total_skipped} ⏭️")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
    print(f"Execution Time: {end_time - start_time:.2f} seconds")
    
    # Detailed failure report
    if total_failures > 0 or total_errors > 0:
        print("\n🔍 Detailed Failure Report")
        print("-" * 30)
        
        for i, result in enumerate(results):
            if result.failures:
                print(f"\nFailures in suite {i+1}:")
                for test, traceback in result.failures:
                    print(f"  ❌ {test}: {traceback.split('AssertionError:')[-1].strip()}")
            
            if result.errors:
                print(f"\nErrors in suite {i+1}:")
                for test, traceback in result.errors:
                    print(f"  💥 {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Phase 1 readiness assessment
    print("\n🚀 Phase 1 Readiness Assessment")
    print("-" * 30)
    
    if total_passed == total_tests and total_tests > 0:
        print("✅ All tests passed! Phase 1 foundation is ready.")
        print("📋 Next steps:")
        print("  1. Deploy capability matrix to staging")
        print("  2. Test with real agent interactions")
        print("  3. Enable intelligent routing feature flag")
    elif total_passed / total_tests >= 0.8:
        print("⚠️  Most tests passed. Review failures before proceeding.")
        print("📋 Next steps:")
        print("  1. Fix failing tests")
        print("  2. Re-run test suite")
        print("  3. Deploy to staging after fixes")
    else:
        print("❌ Too many test failures. Fix issues before proceeding.")
        print("📋 Next steps:")
        print("  1. Review and fix all failing tests")
        print("  2. Address any configuration issues")
        print("  3. Re-run test suite")
    
    return {
        'total_tests': total_tests,
        'passed': total_passed,
        'failed': total_failures,
        'errors': total_errors,
        'skipped': total_skipped,
        'success_rate': (total_passed/total_tests*100) if total_tests > 0 else 0,
        'execution_time': end_time - start_time,
        'ready_for_deployment': total_passed == total_tests and total_tests > 0
    }

def run_specific_test(test_name: str):
    """Run a specific test by name."""
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

def run_capability_tests():
    """Run only capability matrix tests."""
    print("🧪 Running Capability Matrix Tests")
    print("=" * 50)
    
    try:
        import tests.test_agent_capabilities as test_module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result
    except Exception as e:
        print(f"❌ Failed to run capability tests: {e}")
        return None

def run_integration_tests():
    """Run only integration tests."""
    print("🧪 Running Integration Tests")
    print("=" * 50)
    
    try:
        import tests.test_phase1_integration as test_module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result
    except Exception as e:
        print(f"❌ Failed to run integration tests: {e}")
        return None

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Phase 1 tests')
    parser.add_argument('--test', help='Run specific test')
    parser.add_argument('--capabilities', action='store_true', help='Run only capability tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    
    args = parser.parse_args()
    
    if args.test:
        run_specific_test(args.test)
    elif args.capabilities:
        run_capability_tests()
    elif args.integration:
        run_integration_tests()
    else:
        results = run_phase1_tests()
        
        # Exit with appropriate code
        if results['ready_for_deployment']:
            sys.exit(0)
        else:
            sys.exit(1) 