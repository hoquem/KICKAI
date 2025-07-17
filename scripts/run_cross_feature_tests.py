#!/usr/bin/env python3
"""
Cross-Feature Test Runner

Runs cross-feature tests including both E2E and integration tests.
Provides options for different test suites and configurations.
"""

import os
import sys
import argparse
import subprocess
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_pytest_tests(test_path: str, markers: str = None, verbose: bool = False) -> bool:
    """Run pytest tests with specified options."""
    cmd = ["python", "-m", "pytest", test_path]
    
    if markers:
        cmd.extend(["-m", markers])
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["--tb=short", "--strict-markers"])
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0

def run_e2e_cross_feature_tests(verbose: bool = False) -> bool:
    """Run E2E cross-feature tests."""
    print("🧪 Running E2E Cross-Feature Tests...")
    test_path = "tests/e2e/features/test_cross_feature_flows.py"
    return run_pytest_tests(test_path, verbose=verbose)

def run_integration_cross_feature_tests(verbose: bool = False) -> bool:
    """Run integration cross-feature tests."""
    print("🔗 Running Integration Cross-Feature Tests...")
    test_path = "tests/integration/features/test_cross_feature_integration.py"
    return run_pytest_tests(test_path, verbose=verbose)

def run_all_cross_feature_tests(verbose: bool = False) -> bool:
    """Run all cross-feature tests."""
    print("🚀 Running All Cross-Feature Tests...")
    
    # Run integration tests first (faster)
    integration_success = run_integration_cross_feature_tests(verbose)
    
    if not integration_success:
        print("❌ Integration tests failed, skipping E2E tests")
        return False
    
    # Run E2E tests
    e2e_success = run_e2e_cross_feature_tests(verbose)
    
    return integration_success and e2e_success

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run cross-feature tests")
    parser.add_argument(
        "--type",
        choices=["e2e", "integration", "all"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--markers",
        help="Pytest markers to filter tests"
    )
    
    args = parser.parse_args()
    
    print("🎯 KICKAI Cross-Feature Test Runner")
    print("=" * 50)
    
    success = False
    
    try:
        if args.type == "e2e":
            success = run_e2e_cross_feature_tests(args.verbose)
        elif args.type == "integration":
            success = run_integration_cross_feature_tests(args.verbose)
        elif args.type == "all":
            success = run_all_cross_feature_tests(args.verbose)
        
        if success:
            print("\n✅ All cross-feature tests passed!")
            return 0
        else:
            print("\n❌ Some cross-feature tests failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Test run interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 