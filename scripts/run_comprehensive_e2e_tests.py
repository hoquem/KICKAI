#!/usr/bin/env python3
"""
Comprehensive E2E Test Runner for KICKAI

This script orchestrates the complete end-to-end testing process:
1. Clean up existing test data
2. Set up fresh test data
3. Run comprehensive tests
4. Generate detailed reports
5. Clean up after testing
"""

import os
import sys
import asyncio
import subprocess
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('e2e_test_run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveE2ETestRunner:
    """Comprehensive E2E test runner with full lifecycle management."""
    
    def __init__(self):
        self.start_time = None
        self.test_results = {}
        self.setup_successful = False
        
    async def run_full_test_suite(self):
        """Run the complete E2E test suite."""
        self.start_time = datetime.now()
        logger.info("🚀 Starting Comprehensive E2E Test Suite")
        logger.info(f"📅 Test run started at: {self.start_time}")
        
        try:
            # Step 1: Clean up existing data
            await self.cleanup_existing_data()
            
            # Step 2: Set up fresh test data
            await self.setup_test_data()
            
            # Step 3: Run tests
            await self.run_tests()
            
            # Step 4: Generate reports
            await self.generate_reports()
            
            # Step 5: Final cleanup
            await self.final_cleanup()
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            await self.handle_test_failure(e)
            raise
        finally:
            await self.print_summary()
    
    async def cleanup_existing_data(self):
        """Clean up existing test data."""
        logger.info("🧹 Step 1: Cleaning up existing test data...")
        
        try:
            result = subprocess.run([
                "python", "scripts/cleanup_e2e_test_data.py"
            ], capture_output=True, text=True, check=True)
            
            logger.info("✅ Cleanup completed successfully")
            logger.debug(f"Cleanup output: {result.stdout}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Cleanup failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
    
    async def setup_test_data(self):
        """Set up fresh test data."""
        logger.info("🔧 Step 2: Setting up fresh test data...")
        
        try:
            result = subprocess.run([
                "python", "scripts/setup_e2e_test_data.py"
            ], capture_output=True, text=True, check=True)
            
            logger.info("✅ Test data setup completed successfully")
            logger.debug(f"Setup output: {result.stdout}")
            self.setup_successful = True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Test data setup failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
    
    async def run_tests(self):
        """Run the comprehensive test suite."""
        logger.info("🧪 Step 3: Running comprehensive tests...")
        
        test_suites = [
            {
                "name": "Status Command Tests",
                "file": "tests/e2e_test_status_and_registration.py",
                "markers": ["status"]
            },
            {
                "name": "Player Registration Tests", 
                "file": "tests/e2e_test_status_and_registration.py",
                "markers": ["registration"]
            },
            {
                "name": "Leadership Registration Tests",
                "file": "tests/e2e_test_status_and_registration.py", 
                "markers": ["leadership"]
            },
            {
                "name": "Error Handling Tests",
                "file": "tests/e2e_test_status_and_registration.py",
                "markers": ["error"]
            }
        ]
        
        for suite in test_suites:
            await self.run_test_suite(suite)
    
    async def run_test_suite(self, suite: Dict[str, Any]):
        """Run a specific test suite."""
        logger.info(f"🧪 Running {suite['name']}...")
        
        try:
            # Build pytest command
            cmd = [
                "python", "-m", "pytest",
                suite["file"],
                "-v",
                "--tb=short",
                f"--html=reports/e2e_report_{suite['name'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                "--self-contained-html"
            ]
            
            # Add markers if specified
            if suite.get("markers"):
                for marker in suite["markers"]:
                    cmd.extend(["-m", marker])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse results
            exit_code = result.returncode
            passed = self.parse_test_results(result.stdout)
            
            self.test_results[suite["name"]] = {
                "exit_code": exit_code,
                "passed": passed["passed"],
                "failed": passed["failed"],
                "total": passed["total"],
                "output": result.stdout,
                "error": result.stderr
            }
            
            if exit_code == 0:
                logger.info(f"✅ {suite['name']} completed: {passed['passed']}/{passed['total']} tests passed")
            else:
                logger.warning(f"⚠️  {suite['name']} had issues: {passed['failed']}/{passed['total']} tests failed")
                
        except Exception as e:
            logger.error(f"❌ {suite['name']} failed to run: {e}")
            self.test_results[suite["name"]] = {
                "exit_code": -1,
                "passed": 0,
                "failed": 0,
                "total": 0,
                "output": "",
                "error": str(e)
            }
    
    def parse_test_results(self, output: str) -> Dict[str, int]:
        """Parse pytest output to extract test results."""
        lines = output.split('\n')
        passed = 0
        failed = 0
        
        for line in lines:
            if "PASSED" in line:
                passed += 1
            elif "FAILED" in line:
                failed += 1
        
        total = passed + failed
        return {"passed": passed, "failed": failed, "total": total}
    
    async def generate_reports(self):
        """Generate comprehensive test reports."""
        logger.info("📊 Step 4: Generating comprehensive reports...")
        
        # Create reports directory
        os.makedirs("reports", exist_ok=True)
        
        # Generate summary report
        await self.generate_summary_report()
        
        # Generate detailed report
        await self.generate_detailed_report()
        
        logger.info("✅ Reports generated successfully")
    
    async def generate_summary_report(self):
        """Generate a summary report of all test results."""
        report_file = f"reports/e2e_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w') as f:
            f.write("# KICKAI E2E Test Summary Report\n\n")
            f.write(f"**Test Run Date:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Overall statistics
            total_tests = sum(result["total"] for result in self.test_results.values())
            total_passed = sum(result["passed"] for result in self.test_results.values())
            total_failed = sum(result["failed"] for result in self.test_results.values())
            
            f.write(f"## Overall Statistics\n\n")
            f.write(f"- **Total Test Suites:** {len(self.test_results)}\n")
            f.write(f"- **Total Tests:** {total_tests}\n")
            f.write(f"- **Passed:** {total_passed}\n")
            f.write(f"- **Failed:** {total_failed}\n")
            f.write(f"- **Success Rate:** {(total_passed/total_tests*100):.1f}%\n\n")
            
            # Per-suite results
            f.write("## Test Suite Results\n\n")
            f.write("| Suite | Status | Passed | Failed | Total |\n")
            f.write("|-------|--------|--------|--------|-------|\n")
            
            for suite_name, result in self.test_results.items():
                status = "✅ PASS" if result["exit_code"] == 0 else "❌ FAIL"
                f.write(f"| {suite_name} | {status} | {result['passed']} | {result['failed']} | {result['total']} |\n")
            
            f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            if total_failed == 0:
                f.write("🎉 All tests passed! The system is working correctly.\n")
            else:
                f.write("⚠️  Some tests failed. Please review the detailed reports and fix the issues.\n")
        
        logger.info(f"📄 Summary report generated: {report_file}")
    
    async def generate_detailed_report(self):
        """Generate a detailed report with test outputs."""
        report_file = f"reports/e2e_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w') as f:
            f.write("# KICKAI E2E Detailed Test Report\n\n")
            f.write(f"**Test Run Date:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for suite_name, result in self.test_results.items():
                f.write(f"## {suite_name}\n\n")
                f.write(f"**Status:** {'✅ PASS' if result['exit_code'] == 0 else '❌ FAIL'}\n")
                f.write(f"**Results:** {result['passed']}/{result['total']} tests passed\n\n")
                
                if result["error"]:
                    f.write("### Errors\n\n")
                    f.write(f"```\n{result['error']}\n```\n\n")
                
                if result["output"]:
                    f.write("### Test Output\n\n")
                    f.write(f"```\n{result['output']}\n```\n\n")
                
                f.write("---\n\n")
        
        logger.info(f"📄 Detailed report generated: {report_file}")
    
    async def final_cleanup(self):
        """Perform final cleanup after testing."""
        logger.info("🧹 Step 5: Performing final cleanup...")
        
        try:
            result = subprocess.run([
                "python", "scripts/cleanup_e2e_test_data.py"
            ], capture_output=True, text=True, check=True)
            
            logger.info("✅ Final cleanup completed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Final cleanup had issues: {e}")
            logger.warning(f"stdout: {e.stdout}")
            logger.warning(f"stderr: {e.stderr}")
    
    async def handle_test_failure(self, error: Exception):
        """Handle test suite failures."""
        logger.error(f"❌ Test suite failed with error: {error}")
        
        # Try to clean up even on failure
        try:
            await self.final_cleanup()
        except Exception as cleanup_error:
            logger.error(f"❌ Cleanup also failed: {cleanup_error}")
    
    async def print_summary(self):
        """Print a summary of the test run."""
        end_time = datetime.now()
        duration = end_time - self.start_time if self.start_time else None
        
        logger.info("📊 Test Run Summary")
        logger.info("=" * 50)
        
        if duration:
            logger.info(f"⏱️  Duration: {duration}")
        
        total_tests = sum(result["total"] for result in self.test_results.values())
        total_passed = sum(result["passed"] for result in self.test_results.values())
        total_failed = sum(result["failed"] for result in self.test_results.values())
        
        logger.info(f"📈 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {total_passed}")
        logger.info(f"❌ Failed: {total_failed}")
        
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Per-suite summary
        for suite_name, result in self.test_results.items():
            status = "✅ PASS" if result["exit_code"] == 0 else "❌ FAIL"
            logger.info(f"🧪 {suite_name}: {status} ({result['passed']}/{result['total']})")
        
        logger.info("=" * 50)
        
        if total_failed == 0:
            logger.info("🎉 All tests passed! The system is working correctly.")
        else:
            logger.warning("⚠️  Some tests failed. Please review the detailed reports.")

async def main():
    """Main function to run the comprehensive E2E test suite."""
    runner = ComprehensiveE2ETestRunner()
    await runner.run_full_test_suite()

if __name__ == "__main__":
    # Ensure we're in the right directory
    if not os.path.exists("scripts/setup_e2e_test_data.py"):
        logger.error("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Run the test suite
    asyncio.run(main()) 