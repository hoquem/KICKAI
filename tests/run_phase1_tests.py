#!/usr/bin/env python3
"""
Test runner for Phase 1 improvements.
Runs all Phase 1 related tests and provides a summary report.
"""

import pytest
import sys
import time
from typing import List, Dict

def run_phase1_tests():
    """Run all Phase 1 tests and return results."""
    print("🧪 Running Phase 1 Tests")
    print("=" * 50)
    
    # Test modules to run
    test_modules = [
        'tests.test_agent_capabilities',
        'tests.test_phase1_integration'
    ]
    
    # Run tests with pytest
    start_time = time.time()
    
    try:
        # Run pytest on the test modules
        exit_code = pytest.main([
            '--tb=short',
            '--quiet',
            '--disable-warnings',
            *test_modules
        ])
        
        end_time = time.time()
        
        # Generate summary
        print("\n" + "=" * 50)
        print("📊 Phase 1 Test Summary")
        print("=" * 50)
        
        success = exit_code == 0
        execution_time = end_time - start_time
        
        if success:
            print("✅ All tests passed! Phase 1 foundation is ready.")
            print("📋 Next steps:")
            print("  1. Deploy capability matrix to staging")
            print("  2. Test with real agent interactions")
            print("  3. Enable intelligent routing feature flag")
        else:
            print("❌ Some tests failed. Review failures before proceeding.")
            print("📋 Next steps:")
            print("  1. Fix failing tests")
            print("  2. Re-run test suite")
            print("  3. Deploy to staging after fixes")
        
        print(f"Execution Time: {execution_time:.2f} seconds")
        
        return {
            'success': success,
            'execution_time': execution_time,
            'ready_for_deployment': success
        }
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return {
            'success': False,
            'execution_time': 0,
            'ready_for_deployment': False
        }

def run_specific_test(test_name: str):
    """Run a specific test by name."""
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 50)
    
    try:
        exit_code = pytest.main([
            '--tb=short',
            '--quiet',
            test_name
        ])
        
        return exit_code == 0
    except Exception as e:
        print(f"❌ Failed to run test: {e}")
        return False

def run_capability_tests():
    """Run only capability matrix tests."""
    print("🧪 Running Capability Matrix Tests")
    print("=" * 50)
    
    try:
        exit_code = pytest.main([
            '--tb=short',
            '--quiet',
            'tests.test_agent_capabilities'
        ])
        
        return exit_code == 0
    except Exception as e:
        print(f"❌ Failed to run capability tests: {e}")
        return False

def run_integration_tests():
    """Run only integration tests."""
    print("🧪 Running Integration Tests")
    print("=" * 50)
    
    try:
        exit_code = pytest.main([
            '--tb=short',
            '--quiet',
            'tests.test_phase1_integration'
        ])
        
        return exit_code == 0
    except Exception as e:
        print(f"❌ Failed to run integration tests: {e}")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Phase 1 tests')
    parser.add_argument('--test', help='Run specific test')
    parser.add_argument('--capabilities', action='store_true', help='Run only capability tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    
    args = parser.parse_args()
    
    if args.test:
        success = run_specific_test(args.test)
        sys.exit(0 if success else 1)
    elif args.capabilities:
        success = run_capability_tests()
        sys.exit(0 if success else 1)
    elif args.integration:
        success = run_integration_tests()
        sys.exit(0 if success else 1)
    else:
        results = run_phase1_tests()
        
        # Exit with appropriate code
        sys.exit(0 if results['ready_for_deployment'] else 1) 