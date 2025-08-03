#!/usr/bin/env python3
"""
Bot Manager & Telegram API Integration Test Runner

This script runs comprehensive tests for the bot manager and Telegram API integration,
including unit tests, integration tests, and generates detailed reports.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path


def setup_environment():
    """Set up the test environment."""
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Set environment variables for testing
    os.environ.setdefault("PYTHONPATH", "src")
    os.environ.setdefault("ENVIRONMENT", "testing")
    os.environ.setdefault("AI_PROVIDER", "mock")


def run_bot_manager_telegram_api_tests():
    """Run the comprehensive bot manager and Telegram API tests."""
    print("🤖 Running Bot Manager & Telegram API Integration Tests")
    print("=" * 60)
    
    # Test file path
    test_file = "tests/features/bot_manager_telegram_api/test_bot_manager_telegram_api_comprehensive.py"
    
    # Create test directories if they don't exist
    test_dir = Path(test_file).parent
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Coverage directories
    coverage_dir = Path("htmlcov")
    coverage_dir.mkdir(exist_ok=True)
    
    # Run pytest with comprehensive options
    cmd = [
        "python", "-m", "pytest",
        test_file,
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--cov=kickai.features.team_administration.domain.services.multi_bot_manager",
        "--cov=kickai.features.communication.infrastructure.telegram_bot_service",
        "--cov=kickai.agents.agentic_message_router",
        "--cov-report=html:htmlcov/bot_manager_telegram_api",
        "--cov-report=term-missing",
        "--cov-report=json:coverage_bot_manager_telegram_api.json",
        "--junit-xml=test_results_bot_manager_telegram_api.xml",
        "--durations=10",  # Show 10 slowest tests
        "--maxfail=5",  # Stop after 5 failures
        "-x",  # Stop on first failure (for debugging)
    ]
    
    print(f"📋 Running command: {' '.join(cmd)}")
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        end_time = time.time()
        
        print("✅ Tests completed successfully!")
        print(f"⏱️  Total execution time: {end_time - start_time:.2f} seconds")
        print()
        
        # Parse and display results
        if result.stdout:
            print("📊 Test Results:")
            print(result.stdout)
        
        return True, result.stdout, result.stderr
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        
        print("❌ Tests failed!")
        print(f"⏱️  Execution time: {end_time - start_time:.2f} seconds")
        print()
        
        if e.stdout:
            print("📊 Test Output:")
            print(e.stdout)
        
        if e.stderr:
            print("❌ Error Output:")
            print(e.stderr)
        
        return False, e.stdout, e.stderr


def generate_test_report(success: bool, stdout: str, stderr: str):
    """Generate a comprehensive test report."""
    report = {
        "test_suite": "Bot Manager & Telegram API Integration",
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0
        },
        "coverage": {
            "overall_percentage": 0,
            "modules": {}
        },
        "performance": {
            "execution_time": 0,
            "memory_usage": 0
        },
        "issues": []
    }
    
    # Parse test results from stdout
    if stdout:
        lines = stdout.split('\n')
        for line in lines:
            if "passed" in line and "failed" in line:
                # Extract test counts
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        if "passed" in line:
                            report["summary"]["passed"] = int(part)
                        elif "failed" in line:
                            report["summary"]["failed"] = int(part)
                        elif "skipped" in line:
                            report["summary"]["skipped"] = int(part)
                        elif "error" in line:
                            report["summary"]["errors"] = int(part)
    
    # Calculate totals
    report["summary"]["total_tests"] = (
        report["summary"]["passed"] + 
        report["summary"]["failed"] + 
        report["summary"]["skipped"] + 
        report["summary"]["errors"]
    )
    
    # Parse coverage information
    if stdout:
        coverage_lines = [line for line in lines if "TOTAL" in line and "%" in line]
        if coverage_lines:
            coverage_line = coverage_lines[-1]
            try:
                percentage = float(coverage_line.split("%")[0].split()[-1])
                report["coverage"]["overall_percentage"] = percentage
            except (ValueError, IndexError):
                pass
    
    # Add issues if any
    if stderr:
        report["issues"].append({
            "type": "error",
            "message": stderr[:500] + "..." if len(stderr) > 500 else stderr
        })
    
    return report


def save_test_report(report: dict):
    """Save the test report to a JSON file."""
    report_file = "test_report_bot_manager_telegram_api.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Test report saved to: {report_file}")
    return report_file


def display_test_summary(report: dict):
    """Display a summary of test results."""
    print("\n" + "=" * 60)
    print("📊 BOT MANAGER & TELEGRAM API TEST SUMMARY")
    print("=" * 60)
    
    # Overall status
    status = "✅ PASSED" if report["success"] else "❌ FAILED"
    print(f"Status: {status}")
    print(f"Timestamp: {report['timestamp']}")
    print()
    
    # Test counts
    summary = report["summary"]
    print("📈 Test Results:")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Passed: {summary['passed']} ✅")
    print(f"  Failed: {summary['failed']} ❌")
    print(f"  Skipped: {summary['skipped']} ⏭️")
    print(f"  Errors: {summary['errors']} 💥")
    print()
    
    # Coverage
    coverage = report["coverage"]
    print("📊 Coverage:")
    print(f"  Overall Coverage: {coverage['overall_percentage']:.1f}%")
    print()
    
    # Issues
    if report["issues"]:
        print("⚠️  Issues Found:")
        for issue in report["issues"]:
            print(f"  - {issue['type'].upper()}: {issue['message']}")
        print()
    
    # Recommendations
    print("💡 Recommendations:")
    if report["success"]:
        if coverage["overall_percentage"] >= 90:
            print("  ✅ Excellent coverage! Consider adding more edge case tests.")
        elif coverage["overall_percentage"] >= 80:
            print("  ⚠️  Good coverage, but consider adding more tests for better coverage.")
        else:
            print("  ❌ Coverage is below target. Add more tests to improve coverage.")
    else:
        print("  ❌ Fix failing tests before proceeding.")
        print("  🔍 Review error messages and test failures.")
    
    print("=" * 60)


def main():
    """Main test runner function."""
    print("🚀 Starting Bot Manager & Telegram API Integration Test Suite")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Run tests
    success, stdout, stderr = run_bot_manager_telegram_api_tests()
    
    # Generate report
    report = generate_test_report(success, stdout, stderr)
    
    # Save report
    report_file = save_test_report(report)
    
    # Display summary
    display_test_summary(report)
    
    # Return appropriate exit code
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 