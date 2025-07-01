"""
Test Runner for KICKAI

This module provides a comprehensive test runner with configuration,
reporting, and execution utilities for the KICKAI testing infrastructure.
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import pytest
from dataclasses import dataclass, asdict

from .test_utils import TestContext
from .test_fixtures import create_complete_test_scenario


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    test_type: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    execution_time: float
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class TestSuiteResult:
    """Test suite result data structure."""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    total_execution_time: float
    test_results: List[TestResult]
    metadata: Dict[str, Any] = None


@dataclass
class TestReport:
    """Complete test report data structure."""
    timestamp: str
    total_suites: int
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    total_execution_time: float
    suite_results: List[TestSuiteResult]
    summary: Dict[str, Any]
    metadata: Dict[str, Any] = None


class TestRunner:
    """
    Comprehensive test runner for KICKAI.
    
    Provides test execution, reporting, and analysis capabilities
    for the entire testing infrastructure.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.test_context = TestContext()
        self.results = []
        self.current_suite = None
        
    def _default_config(self) -> Dict[str, Any]:
        """Get default test runner configuration."""
        return {
            'test_directories': ['tests', 'src/testing'],
            'test_patterns': ['test_*.py', '*_test.py'],
            'exclude_patterns': ['__pycache__', '.pytest_cache', 'venv'],
            'parallel_execution': False,
            'max_workers': 4,
            'timeout_seconds': 300,
            'verbose': True,
            'generate_reports': True,
            'report_formats': ['json', 'html', 'xml'],
            'coverage_enabled': True,
            'performance_monitoring': True,
            'security_scanning': True
        }
    
    def run_all_tests(self) -> TestReport:
        """Run all tests and generate a comprehensive report."""
        start_time = time.time()
        
        print("🚀 Starting KICKAI Test Suite...")
        print(f"📅 Test run started at: {datetime.now().isoformat()}")
        print(f"⚙️  Configuration: {json.dumps(self.config, indent=2)}")
        
        # Discover and run test suites
        test_suites = self._discover_test_suites()
        suite_results = []
        
        for suite in test_suites:
            print(f"\n📋 Running test suite: {suite['name']}")
            suite_result = self._run_test_suite(suite)
            suite_results.append(suite_result)
        
        # Generate comprehensive report
        total_execution_time = time.time() - start_time
        report = self._generate_report(suite_results, total_execution_time)
        
        # Save reports
        if self.config['generate_reports']:
            self._save_reports(report)
        
        # Print summary
        self._print_summary(report)
        
        return report
    
    def _discover_test_suites(self) -> List[Dict[str, Any]]:
        """Discover all test suites in the project."""
        test_suites = []
        
        for test_dir in self.config['test_directories']:
            if os.path.exists(test_dir):
                for pattern in self.config['test_patterns']:
                    test_files = Path(test_dir).rglob(pattern)
                    for test_file in test_files:
                        # Skip excluded patterns
                        if any(exclude in str(test_file) for exclude in self.config['exclude_patterns']):
                            continue
                        
                        test_suites.append({
                            'name': test_file.stem,
                            'path': str(test_file),
                            'type': self._determine_test_type(test_file)
                        })
        
        return test_suites
    
    def _determine_test_type(self, test_file: Path) -> str:
        """Determine the type of test suite based on file content."""
        try:
            with open(test_file, 'r') as f:
                content = f.read()
                
            if 'IntegrationTestCase' in content:
                return 'integration'
            elif 'PerformanceTestCase' in content:
                return 'performance'
            elif 'SecurityTestCase' in content:
                return 'security'
            elif 'AsyncBaseTestCase' in content:
                return 'async'
            else:
                return 'unit'
        except Exception:
            return 'unit'
    
    def _run_test_suite(self, suite: Dict[str, Any]) -> TestSuiteResult:
        """Run a single test suite."""
        start_time = time.time()
        
        # Set up test environment
        self._setup_test_environment(suite)
        
        # Run tests using pytest
        pytest_args = [
            suite['path'],
            '-v' if self.config['verbose'] else '-q',
            '--tb=short',
            '--strict-markers',
            '--disable-warnings'
        ]
        
        if self.config['parallel_execution']:
            pytest_args.extend(['-n', str(self.config['max_workers'])])
        
        # Capture pytest output
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exit_code = pytest.main(pytest_args)
        
        # Parse test results
        test_results = self._parse_pytest_results(stdout_capture.getvalue(), stderr_capture.getvalue())
        
        # Calculate suite statistics
        total_execution_time = time.time() - start_time
        suite_result = self._calculate_suite_statistics(suite, test_results, total_execution_time)
        
        # Clean up test environment
        self._cleanup_test_environment(suite)
        
        return suite_result
    
    def _setup_test_environment(self, suite: Dict[str, Any]):
        """Set up the test environment for a suite."""
        # Set environment variables for testing
        os.environ['TESTING'] = 'true'
        os.environ['TEST_SUITE'] = suite['name']
        os.environ['TEST_TYPE'] = suite['type']
        
        # Create test data if needed
        if suite['type'] == 'integration':
            self._setup_integration_test_data()
        elif suite['type'] == 'performance':
            self._setup_performance_test_data()
        elif suite['type'] == 'security':
            self._setup_security_test_data()
    
    def _cleanup_test_environment(self, suite: Dict[str, Any]):
        """Clean up the test environment after a suite."""
        # Clean up test data
        self.test_context.cleanup()
        
        # Remove test environment variables
        os.environ.pop('TESTING', None)
        os.environ.pop('TEST_SUITE', None)
        os.environ.pop('TEST_TYPE', None)
    
    def _setup_integration_test_data(self):
        """Set up test data for integration tests."""
        test_scenario = create_complete_test_scenario()
        self.test_context.set_temp_data('integration_scenario', test_scenario)
    
    def _setup_performance_test_data(self):
        """Set up test data for performance tests."""
        # Performance test data setup
        pass
    
    def _setup_security_test_data(self):
        """Set up test data for security tests."""
        # Security test data setup
        pass
    
    def _parse_pytest_results(self, stdout: str, stderr: str) -> List[TestResult]:
        """Parse pytest output to extract test results."""
        test_results = []
        lines = stdout.split('\n')
        
        current_test = None
        for line in lines:
            if line.startswith('test_') and '::' in line:
                # Parse test name and status
                parts = line.split()
                if len(parts) >= 2:
                    test_name = parts[0]
                    status = 'passed' if 'PASSED' in line else 'failed' if 'FAILED' in line else 'skipped'
                    
                    test_results.append(TestResult(
                        test_name=test_name,
                        test_type='unit',
                        status=status,
                        execution_time=0.0,  # Would need more parsing for actual time
                        metadata={'raw_line': line}
                    ))
        
        return test_results
    
    def _calculate_suite_statistics(self, suite: Dict[str, Any], test_results: List[TestResult], 
                                  execution_time: float) -> TestSuiteResult:
        """Calculate statistics for a test suite."""
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.status == 'passed'])
        failed_tests = len([r for r in test_results if r.status == 'failed'])
        skipped_tests = len([r for r in test_results if r.status == 'skipped'])
        error_tests = len([r for r in test_results if r.status == 'error'])
        
        return TestSuiteResult(
            suite_name=suite['name'],
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            error_tests=error_tests,
            total_execution_time=execution_time,
            test_results=test_results,
            metadata={'suite_type': suite['type']}
        )
    
    def _generate_report(self, suite_results: List[TestSuiteResult], total_execution_time: float) -> TestReport:
        """Generate a comprehensive test report."""
        total_suites = len(suite_results)
        total_tests = sum(s.total_tests for s in suite_results)
        passed_tests = sum(s.passed_tests for s in suite_results)
        failed_tests = sum(s.failed_tests for s in suite_results)
        skipped_tests = sum(s.skipped_tests for s in suite_results)
        error_tests = sum(s.error_tests for s in suite_results)
        
        # Calculate summary statistics
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        failure_rate = (failed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            'success_rate': success_rate,
            'failure_rate': failure_rate,
            'average_execution_time': total_execution_time / total_suites if total_suites > 0 else 0,
            'test_coverage': self._calculate_test_coverage(suite_results),
            'performance_metrics': self._extract_performance_metrics(suite_results),
            'security_findings': self._extract_security_findings(suite_results)
        }
        
        return TestReport(
            timestamp=datetime.now().isoformat(),
            total_suites=total_suites,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            error_tests=error_tests,
            total_execution_time=total_execution_time,
            suite_results=suite_results,
            summary=summary
        )
    
    def _calculate_test_coverage(self, suite_results: List[TestSuiteResult]) -> Dict[str, Any]:
        """Calculate test coverage metrics."""
        # This would integrate with coverage.py for actual coverage data
        return {
            'line_coverage': 0.0,
            'branch_coverage': 0.0,
            'function_coverage': 0.0
        }
    
    def _extract_performance_metrics(self, suite_results: List[TestSuiteResult]) -> Dict[str, Any]:
        """Extract performance metrics from test results."""
        performance_suites = [s for s in suite_results if s.metadata.get('suite_type') == 'performance']
        
        if not performance_suites:
            return {}
        
        metrics = {}
        for suite in performance_suites:
            for test_result in suite.test_results:
                if test_result.metadata and 'performance_metrics' in test_result.metadata:
                    metrics.update(test_result.metadata['performance_metrics'])
        
        return metrics
    
    def _extract_security_findings(self, suite_results: List[TestSuiteResult]) -> Dict[str, Any]:
        """Extract security findings from test results."""
        security_suites = [s for s in suite_results if s.metadata.get('suite_type') == 'security']
        
        if not security_suites:
            return {}
        
        findings = {
            'vulnerabilities': [],
            'total_vulnerabilities': 0,
            'high_severity': 0,
            'medium_severity': 0,
            'low_severity': 0
        }
        
        for suite in security_suites:
            for test_result in suite.test_results:
                if test_result.metadata and 'security_report' in test_result.metadata:
                    report = test_result.metadata['security_report']
                    findings['vulnerabilities'].extend(report.get('vulnerabilities', []))
                    findings['total_vulnerabilities'] += report.get('total_vulnerabilities', 0)
                    findings['high_severity'] += report.get('high_severity', 0)
                    findings['medium_severity'] += report.get('medium_severity', 0)
                    findings['low_severity'] += report.get('low_severity', 0)
        
        return findings
    
    def _save_reports(self, report: TestReport):
        """Save test reports in various formats."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for format_type in self.config['report_formats']:
            if format_type == 'json':
                self._save_json_report(report, timestamp)
            elif format_type == 'html':
                self._save_html_report(report, timestamp)
            elif format_type == 'xml':
                self._save_xml_report(report, timestamp)
    
    def _save_json_report(self, report: TestReport, timestamp: str):
        """Save test report as JSON."""
        report_path = f"test_reports/test_report_{timestamp}.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        print(f"📄 JSON report saved: {report_path}")
    
    def _save_html_report(self, report: TestReport, timestamp: str):
        """Save test report as HTML."""
        report_path = f"test_reports/test_report_{timestamp}.html"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        html_content = self._generate_html_report(report)
        
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        print(f"📄 HTML report saved: {report_path}")
    
    def _save_xml_report(self, report: TestReport, timestamp: str):
        """Save test report as XML."""
        report_path = f"test_reports/test_report_{timestamp}.xml"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        xml_content = self._generate_xml_report(report)
        
        with open(report_path, 'w') as f:
            f.write(xml_content)
        
        print(f"📄 XML report saved: {report_path}")
    
    def _generate_html_report(self, report: TestReport) -> str:
        """Generate HTML report content."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>KICKAI Test Report - {report.timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .suite {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .skipped {{ color: orange; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>KICKAI Test Report</h1>
                <p>Generated: {report.timestamp}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Suites: {report.total_suites}</p>
                <p>Total Tests: {report.total_tests}</p>
                <p class="passed">Passed: {report.passed_tests}</p>
                <p class="failed">Failed: {report.failed_tests}</p>
                <p class="skipped">Skipped: {report.skipped_tests}</p>
                <p>Execution Time: {report.total_execution_time:.2f}s</p>
            </div>
            
            <div class="suites">
                <h2>Test Suites</h2>
                {self._generate_suite_html(report.suite_results)}
            </div>
        </body>
        </html>
        """
    
    def _generate_suite_html(self, suite_results: List[TestSuiteResult]) -> str:
        """Generate HTML for test suites."""
        html = ""
        for suite in suite_results:
            status_class = "passed" if suite.failed_tests == 0 else "failed"
            html += f"""
            <div class="suite">
                <h3 class="{status_class}">{suite.suite_name}</h3>
                <p>Tests: {suite.total_tests} | Passed: {suite.passed_tests} | Failed: {suite.failed_tests} | Skipped: {suite.skipped_tests}</p>
                <p>Execution Time: {suite.total_execution_time:.2f}s</p>
            </div>
            """
        return html
    
    def _generate_xml_report(self, report: TestReport) -> str:
        """Generate XML report content."""
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<testreport timestamp="{report.timestamp}">
    <summary>
        <total_suites>{report.total_suites}</total_suites>
        <total_tests>{report.total_tests}</total_tests>
        <passed_tests>{report.passed_tests}</passed_tests>
        <failed_tests>{report.failed_tests}</failed_tests>
        <skipped_tests>{report.skipped_tests}</skipped_tests>
        <execution_time>{report.total_execution_time}</execution_time>
    </summary>
    <suites>
"""
        
        for suite in report.suite_results:
            xml += f"""        <suite name="{suite.suite_name}">
            <total_tests>{suite.total_tests}</total_tests>
            <passed_tests>{suite.passed_tests}</passed_tests>
            <failed_tests>{suite.failed_tests}</failed_tests>
            <skipped_tests>{suite.skipped_tests}</skipped_tests>
            <execution_time>{suite.total_execution_time}</execution_time>
        </suite>
"""
        
        xml += """    </suites>
</testreport>"""
        
        return xml
    
    def _print_summary(self, report: TestReport):
        """Print a summary of the test results."""
        print("\n" + "="*60)
        print("📊 KICKAI Test Suite Summary")
        print("="*60)
        print(f"📅 Timestamp: {report.timestamp}")
        print(f"📋 Total Suites: {report.total_suites}")
        print(f"🧪 Total Tests: {report.total_tests}")
        print(f"✅ Passed: {report.passed_tests}")
        print(f"❌ Failed: {report.failed_tests}")
        print(f"⏭️  Skipped: {report.skipped_tests}")
        print(f"⏱️  Total Execution Time: {report.total_execution_time:.2f}s")
        
        if report.total_tests > 0:
            success_rate = (report.passed_tests / report.total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("="*60)
        
        if report.failed_tests > 0:
            print("⚠️  Some tests failed. Check the detailed reports for more information.")
        else:
            print("🎉 All tests passed successfully!")


def run_tests(config: Optional[Dict[str, Any]] = None) -> TestReport:
    """Convenience function to run all tests."""
    runner = TestRunner(config)
    return runner.run_all_tests()


if __name__ == "__main__":
    # Run tests when executed directly
    config = {
        'test_directories': ['tests', 'src/testing'],
        'verbose': True,
        'generate_reports': True,
        'report_formats': ['json', 'html']
    }
    
    report = run_tests(config)
    
    # Exit with appropriate code
    sys.exit(0 if report.failed_tests == 0 else 1) 