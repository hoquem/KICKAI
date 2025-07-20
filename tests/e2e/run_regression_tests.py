#!/usr/bin/env python3
"""
KICKAI Regression Test Runner

This script runs comprehensive regression tests for all KICKAI commands
using both NLP and slash command formats.

Usage:
    python run_regression_tests.py [options]

Options:
    --suite <suite_name>     Run specific test suite (default: all)
    --format <format>        Output format (text, json, html)
    --verbose                Verbose output
    --parallel               Run tests in parallel
    --filter <pattern>       Filter tests by pattern
    --timeout <seconds>      Test timeout in seconds
"""

import os
import sys
import asyncio
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from loguru import logger


class RegressionTestRunner:
    """Runner for KICKAI regression tests."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = []
        self.start_time = None
        self.end_time = None
        
        # Setup logging
        logger.remove()
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO" if not config.get('verbose') else "DEBUG"
        )
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Add file logging
        log_file = f"logs/regression_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days"
        )
    
    async def run_tests(self) -> Dict[str, Any]:
        """Run the regression tests."""
        self.start_time = datetime.now()
        logger.info("🚀 Starting KICKAI Regression Tests")
        
        try:
            # Check environment
            await self._check_environment()
            
            # Run test suites
            test_results = await self._run_test_suites()
            
            # Generate report
            report = await self._generate_report(test_results)
            
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            logger.info(f"✅ Regression tests completed in {duration:.2f} seconds")
            
            return {
                'success': True,
                'duration': duration,
                'results': test_results,
                'report': report,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Regression tests failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': datetime.now().isoformat()
            }
    
    async def _check_environment(self):
        """Check that the test environment is properly set up."""
        logger.info("🔍 Checking test environment...")
        
        # Check if .env.test exists
        if not os.path.exists('.env.test'):
            logger.warning("⚠️  .env.test file not found. Tests may fail.")
        
        # Check if virtual environment is activated
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.warning("⚠️  Virtual environment may not be activated.")
        
        # Check if required directories exist
        required_dirs = ['src', 'tests', 'logs']
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                logger.error(f"❌ Required directory '{dir_name}' not found")
                raise FileNotFoundError(f"Required directory '{dir_name}' not found")
        
        logger.info("✅ Environment check completed")
    
    async def _run_test_suites(self) -> Dict[str, Any]:
        """Run all test suites."""
        test_results = {}
        
        # Define test suites
        test_suites = {
            'regression_commands': {
                'file': 'tests/e2e/features/test_regression_commands.py',
                'description': 'Comprehensive command regression tests (NLP + Slash)',
                'markers': ['asyncio']
            },
            'cross_feature_flows': {
                'file': 'tests/e2e/features/test_cross_feature_flows.py',
                'description': 'Cross-feature integration tests',
                'markers': ['asyncio']
            },
            'status_and_registration': {
                'file': 'tests/e2e/e2e_test_status_and_registration.py',
                'description': 'Status and registration tests',
                'markers': ['asyncio']
            }
        }
        
        # Filter suites if specified
        if self.config.get('suite') and self.config['suite'] != 'all':
            suite_name = self.config['suite']
            if suite_name in test_suites:
                test_suites = {suite_name: test_suites[suite_name]}
            else:
                logger.error(f"❌ Unknown test suite: {suite_name}")
                raise ValueError(f"Unknown test suite: {suite_name}")
        
        # Run each test suite
        for suite_name, suite_config in test_suites.items():
            logger.info(f"🧪 Running test suite: {suite_name}")
            logger.info(f"   Description: {suite_config['description']}")
            
            try:
                result = await self._run_test_suite(suite_name, suite_config)
                test_results[suite_name] = result
                
                if result['success']:
                    logger.info(f"✅ {suite_name} completed successfully")
                else:
                    logger.error(f"❌ {suite_name} failed")
                    
            except Exception as e:
                logger.error(f"❌ Error running {suite_name}: {e}")
                test_results[suite_name] = {
                    'success': False,
                    'error': str(e),
                    'tests_run': 0,
                    'tests_passed': 0,
                    'tests_failed': 0,
                    'duration': 0
                }
        
        return test_results
    
    async def _run_test_suite(self, suite_name: str, suite_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific test suite."""
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            sys.executable, '-m', 'pytest',
            suite_config['file'],
            '-v',
            '--tb=short',
            '--asyncio-mode=auto'
        ]
        
        # Add markers
        for marker in suite_config.get('markers', []):
            cmd.extend(['-m', marker])
        
        # Add filter if specified
        if self.config.get('filter'):
            cmd.extend(['-k', self.config['filter']])
        
        # Add timeout if specified
        if self.config.get('timeout'):
            cmd.extend(['--timeout', str(self.config['timeout'])])
        
        # Add output format
        if self.config.get('format') == 'json':
            cmd.extend(['--json-report', '--json-report-file', f'logs/{suite_name}_results.json'])
        elif self.config.get('format') == 'html':
            cmd.extend(['--html', f'logs/{suite_name}_results.html', '--self-contained-html'])
        
        # Set environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = 'src'
        env['PYTEST_ADDOPTS'] = '--strict-markers'
        
        # Run the tests
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=self.config.get('timeout', 300)
            )
            
            duration = time.time() - start_time
            
            # Parse results
            tests_run = 0
            tests_passed = 0
            tests_failed = 0
            
            if result.returncode == 0:
                # Parse pytest output to count tests
                for line in result.stdout.split('\n'):
                    if '::test_' in line and 'PASSED' in line:
                        tests_passed += 1
                        tests_run += 1
                    elif '::test_' in line and 'FAILED' in line:
                        tests_failed += 1
                        tests_run += 1
                    elif '::test_' in line and 'ERROR' in line:
                        tests_failed += 1
                        tests_run += 1
            
            return {
                'success': result.returncode == 0,
                'tests_run': tests_run,
                'tests_passed': tests_passed,
                'tests_failed': tests_failed,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Test suite {suite_name} timed out")
            return {
                'success': False,
                'error': 'Timeout',
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'duration': self.config.get('timeout', 300)
            }
    
    async def _generate_report(self, test_results: Dict[str, Any]) -> str:
        """Generate a test report."""
        logger.info("📊 Generating test report...")
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_duration = 0
        
        # Calculate totals
        for suite_result in test_results.values():
            total_tests += suite_result.get('tests_run', 0)
            total_passed += suite_result.get('tests_passed', 0)
            total_failed += suite_result.get('tests_failed', 0)
            total_duration += suite_result.get('duration', 0)
        
        # Generate report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("KICKAI REGRESSION TEST REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Duration: {total_duration:.2f} seconds")
        report_lines.append("")
        
        # Summary
        report_lines.append("SUMMARY:")
        report_lines.append(f"  Total Test Suites: {len(test_results)}")
        report_lines.append(f"  Total Tests: {total_tests}")
        report_lines.append(f"  Passed: {total_passed}")
        report_lines.append(f"  Failed: {total_failed}")
        report_lines.append(f"  Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "  Success Rate: N/A")
        report_lines.append("")
        
        # Detailed results
        report_lines.append("DETAILED RESULTS:")
        report_lines.append("-" * 80)
        
        for suite_name, suite_result in test_results.items():
            status = "✅ PASS" if suite_result['success'] else "❌ FAIL"
            report_lines.append(f"{suite_name}: {status}")
            report_lines.append(f"  Tests: {suite_result.get('tests_run', 0)}")
            report_lines.append(f"  Passed: {suite_result.get('tests_passed', 0)}")
            report_lines.append(f"  Failed: {suite_result.get('tests_failed', 0)}")
            report_lines.append(f"  Duration: {suite_result.get('duration', 0):.2f}s")
            
            if not suite_result['success'] and suite_result.get('error'):
                report_lines.append(f"  Error: {suite_result['error']}")
            
            report_lines.append("")
        
        report = "\n".join(report_lines)
        
        # Save report to file
        report_file = f"logs/regression_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"📄 Report saved to: {report_file}")
        
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='KICKAI Regression Test Runner')
    parser.add_argument('--suite', default='all', help='Test suite to run (default: all)')
    parser.add_argument('--format', choices=['text', 'json', 'html'], default='text', help='Output format')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--filter', help='Filter tests by pattern')
    parser.add_argument('--timeout', type=int, default=300, help='Test timeout in seconds')
    
    args = parser.parse_args()
    
    config = {
        'suite': args.suite,
        'format': args.format,
        'verbose': args.verbose,
        'parallel': args.parallel,
        'filter': args.filter,
        'timeout': args.timeout
    }
    
    # Run tests
    runner = RegressionTestRunner(config)
    result = asyncio.run(runner.run_tests())
    
    # Print report
    if result['success']:
        logger.info("\n" + result['report'])
        sys.exit(0)
    else:
        logger.error(f"\n❌ Tests failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main() 