#!/usr/bin/env python3
"""
Team Administration Module Test Runner

This script runs comprehensive tests for the team administration module
and generates detailed reports.
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_team_administration_tests():
    """Run comprehensive team administration tests."""
    
    print("🧪 Team Administration Module - Comprehensive Test Suite")
    print("=" * 60)
    
    # Test configuration
    test_file = "tests/features/team_administration/test_team_administration_comprehensive.py"
    
    # Ensure test file exists
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    # Run tests with pytest
    import pytest
    
    start_time = time.time()
    
    try:
        # Run tests with verbose output
        result = pytest.main([
            test_file,
            "-v",
            "--tb=short",
            "--durations=10",
            "--cov=kickai.features.team_administration",
            "--cov-report=html:htmlcov/team_administration",
            "--cov-report=term-missing"
        ])
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Generate test report
        generate_test_report(execution_time, result)
        
        return result == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def generate_test_report(execution_time: float, exit_code: int):
    """Generate a comprehensive test report."""
    
    report = {
        "module": "Team Administration",
        "timestamp": datetime.now().isoformat(),
        "execution_time_seconds": round(execution_time, 2),
        "status": "PASS" if exit_code == 0 else "FAIL",
        "exit_code": exit_code,
        "test_categories": [
            "Entity Tests (Team, TeamMember)",
            "Service Tests (TeamService, TeamMemberService, MultiBotManager)",
            "Tool Tests (Team Management Tools)",
            "Integration Tests (End-to-End Workflows)"
        ],
        "coverage_target": "90%",
        "performance_target": "< 100ms for simple operations"
    }
    
    # Save report to file
    report_file = "test_reports/team_administration_test_report.json"
    os.makedirs("test_reports", exist_ok=True)
    
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Test Report saved to: {report_file}")
    
    # Print summary
    print(f"\n📈 Test Summary:")
    print(f"   • Status: {report['status']}")
    print(f"   • Execution Time: {report['execution_time_seconds']}s")
    print(f"   • Exit Code: {report['exit_code']}")
    
    if exit_code == 0:
        print("   ✅ All tests passed!")
    else:
        print("   ❌ Some tests failed. Check output above for details.")

def main():
    """Main test runner function."""
    
    print("🚀 Starting Team Administration Module Tests...")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("kickai"):
        print("❌ Error: Please run this script from the project root directory")
        return 1
    
    # Run tests
    success = run_team_administration_tests()
    
    if success:
        print("\n🎉 Team Administration tests completed successfully!")
        print("📁 Coverage report available in: htmlcov/team_administration/")
        return 0
    else:
        print("\n❌ Team Administration tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 