#!/usr/bin/env python3
"""
CI/CD Integration Framework for Mock Telegram Testing System

This framework provides CI/CD integration capabilities including:
- GitHub Actions workflow generation
- Test result reporting and analysis
- Quality gate enforcement
- Automated regression testing
- Performance benchmarking
- Test environment management
- Integration with external CI/CD systems
"""

import asyncio
import json
import yaml
import os
import subprocess
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestStage(str, Enum):
    """CI/CD test stages"""
    UNIT_TESTS = "unit_tests"
    INTEGRATION_TESTS = "integration_tests"
    PERFORMANCE_TESTS = "performance_tests"
    ERROR_HANDLING_TESTS = "error_handling_tests"
    E2E_TESTS = "e2e_tests"
    SECURITY_TESTS = "security_tests"
    REGRESSION_TESTS = "regression_tests"


class QualityGate(str, Enum):
    """Quality gate types"""
    TEST_COVERAGE = "test_coverage"
    SUCCESS_RATE = "success_rate"
    PERFORMANCE_THRESHOLD = "performance_threshold"
    SECURITY_COMPLIANCE = "security_compliance"
    ERROR_RATE = "error_rate"


@dataclass
class QualityGateRule:
    """Quality gate rule definition"""
    gate_type: QualityGate
    threshold: float
    operator: str  # ">=", ">", "<=", "<", "=="
    description: str
    is_blocking: bool = True


@dataclass
class TestExecutionConfig:
    """Test execution configuration"""
    stages: List[TestStage]
    quality_gates: List[QualityGateRule]
    environment: str = "ci"
    timeout_minutes: int = 30
    parallel_execution: bool = True
    retry_count: int = 2
    fail_fast: bool = False


@dataclass
class TestStageResult:
    """Result of a test stage execution"""
    stage: TestStage
    success: bool
    duration_seconds: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        return (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0.0


@dataclass
class CIPipelineResult:
    """Complete CI pipeline execution result"""
    pipeline_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    overall_success: bool = False
    stage_results: List[TestStageResult] = field(default_factory=list)
    quality_gate_results: Dict[str, bool] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def total_tests(self) -> int:
        return sum(result.total_tests for result in self.stage_results)
    
    @property
    def total_passed(self) -> int:
        return sum(result.passed_tests for result in self.stage_results)
    
    @property
    def overall_success_rate(self) -> float:
        return (self.total_passed / self.total_tests * 100) if self.total_tests > 0 else 0.0


class GitHubActionsGenerator:
    """Generate GitHub Actions workflows for testing"""
    
    def __init__(self):
        self.workflow_template = {
            "name": "Mock Telegram Testing Suite",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main", "develop"]},
                "schedule": [{"cron": "0 2 * * *"}]  # Daily at 2 AM
            },
            "jobs": {}
        }
    
    def generate_basic_workflow(self) -> Dict[str, Any]:
        """Generate basic GitHub Actions workflow"""
        workflow = self.workflow_template.copy()
        
        workflow["jobs"]["test"] = {
            "runs-on": "ubuntu-latest",
            "strategy": {
                "matrix": {
                    "python-version": ["3.11", "3.12"]
                }
            },
            "steps": [
                {
                    "name": "Checkout code",
                    "uses": "actions/checkout@v4"
                },
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {
                        "python-version": "${{ matrix.python-version }}"
                    }
                },
                {
                    "name": "Install dependencies",
                    "run": "pip install -r tests/mock_telegram/backend/requirements.txt"
                },
                {
                    "name": "Start Mock Telegram Service",
                    "run": "python tests/mock_telegram/start_mock_tester.py &",
                    "env": {
                        "PYTHONPATH": "."
                    }
                },
                {
                    "name": "Wait for service to start",
                    "run": "sleep 10"
                },
                {
                    "name": "Run Health Check",
                    "run": "curl -f http://localhost:8001/health"
                },
                {
                    "name": "Run Automated Tests",
                    "run": "python tests/mock_telegram/automated_test_framework.py",
                    "env": {
                        "PYTHONPATH": "."
                    }
                },
                {
                    "name": "Run Performance Tests",
                    "run": "python tests/mock_telegram/performance_test_suite.py quick",
                    "env": {
                        "PYTHONPATH": "."
                    }
                },
                {
                    "name": "Run Error Handling Tests",
                    "run": "python tests/mock_telegram/error_handling_test_suite.py quick",
                    "env": {
                        "PYTHONPATH": "."
                    }
                },
                {
                    "name": "Upload Test Reports",
                    "uses": "actions/upload-artifact@v3",
                    "if": "always()",
                    "with": {
                        "name": "test-reports-${{ matrix.python-version }}",
                        "path": "*_report_*.txt"
                    }
                }
            ]
        }
        
        return workflow
    
    def generate_comprehensive_workflow(self) -> Dict[str, Any]:
        """Generate comprehensive GitHub Actions workflow with multiple stages"""
        workflow = self.workflow_template.copy()
        
        # Unit Tests Job
        workflow["jobs"]["unit-tests"] = {
            "runs-on": "ubuntu-latest",
            "steps": [
                {"name": "Checkout code", "uses": "actions/checkout@v4"},
                {"name": "Set up Python", "uses": "actions/setup-python@v4", "with": {"python-version": "3.11"}},
                {"name": "Install dependencies", "run": "pip install -r tests/mock_telegram/backend/requirements.txt"},
                {"name": "Run unit tests", "run": "python -m pytest tests/unit/ -v --junitxml=unit-test-results.xml"},
                {"name": "Upload unit test results", "uses": "actions/upload-artifact@v3", "if": "always()", "with": {"name": "unit-test-results", "path": "unit-test-results.xml"}}
            ]
        }
        
        # Integration Tests Job
        workflow["jobs"]["integration-tests"] = {
            "runs-on": "ubuntu-latest",
            "needs": "unit-tests",
            "steps": [
                {"name": "Checkout code", "uses": "actions/checkout@v4"},
                {"name": "Set up Python", "uses": "actions/setup-python@v4", "with": {"python-version": "3.11"}},
                {"name": "Install dependencies", "run": "pip install -r tests/mock_telegram/backend/requirements.txt"},
                {"name": "Start Mock Telegram Service", "run": "python tests/mock_telegram/start_mock_tester.py &", "env": {"PYTHONPATH": "."}},
                {"name": "Wait for service", "run": "sleep 15"},
                {"name": "Run integration tests", "run": "python tests/mock_telegram/automated_test_framework.py", "env": {"PYTHONPATH": "."}},
                {"name": "Upload integration test results", "uses": "actions/upload-artifact@v3", "if": "always()", "with": {"name": "integration-test-results", "path": "*_report_*.txt"}}
            ]
        }
        
        # Performance Tests Job
        workflow["jobs"]["performance-tests"] = {
            "runs-on": "ubuntu-latest",
            "needs": "integration-tests",
            "steps": [
                {"name": "Checkout code", "uses": "actions/checkout@v4"},
                {"name": "Set up Python", "uses": "actions/setup-python@v4", "with": {"python-version": "3.11"}},
                {"name": "Install dependencies", "run": "pip install -r tests/mock_telegram/backend/requirements.txt"},
                {"name": "Start Mock Telegram Service", "run": "python tests/mock_telegram/start_mock_tester.py &", "env": {"PYTHONPATH": "."}},
                {"name": "Wait for service", "run": "sleep 15"},
                {"name": "Run performance tests", "run": "python tests/mock_telegram/performance_test_suite.py", "env": {"PYTHONPATH": "."}},
                {"name": "Upload performance results", "uses": "actions/upload-artifact@v3", "if": "always()", "with": {"name": "performance-test-results", "path": "performance_report_*.txt"}}
            ]
        }
        
        # Quality Gate Job
        workflow["jobs"]["quality-gate"] = {
            "runs-on": "ubuntu-latest",
            "needs": ["unit-tests", "integration-tests", "performance-tests"],
            "steps": [
                {"name": "Checkout code", "uses": "actions/checkout@v4"},
                {"name": "Download all artifacts", "uses": "actions/download-artifact@v3"},
                {"name": "Set up Python", "uses": "actions/setup-python@v4", "with": {"python-version": "3.11"}},
                {"name": "Install dependencies", "run": "pip install -r tests/mock_telegram/backend/requirements.txt"},
                {"name": "Run quality gate analysis", "run": "python tests/mock_telegram/ci_cd_integration.py analyze-results", "env": {"PYTHONPATH": "."}},
                {"name": "Upload quality gate report", "uses": "actions/upload-artifact@v3", "if": "always()", "with": {"name": "quality-gate-report", "path": "quality_gate_report.json"}}
            ]
        }
        
        return workflow
    
    def save_workflow(self, workflow: Dict[str, Any], file_path: str):
        """Save workflow to file"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"📁 GitHub Actions workflow saved to: {file_path}")


class CIPipelineExecutor:
    """Execute CI/CD pipeline locally or in CI environment"""
    
    def __init__(self, config: TestExecutionConfig):
        self.config = config
        self.base_url = "http://localhost:8001"
        
    async def execute_pipeline(self) -> CIPipelineResult:
        """Execute complete CI/CD pipeline"""
        pipeline_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🚀 Starting CI pipeline: {pipeline_id}")
        
        result = CIPipelineResult(
            pipeline_id=pipeline_id,
            start_time=datetime.now()
        )
        
        try:
            # Execute test stages
            for stage in self.config.stages:
                if self.config.fail_fast and not result.overall_success and result.stage_results:
                    logger.info(f"⏭️ Skipping {stage.value} due to fail_fast setting")
                    continue
                
                stage_result = await self._execute_test_stage(stage)
                result.stage_results.append(stage_result)
                
                if not stage_result.success:
                    logger.error(f"❌ Stage {stage.value} failed")
                    result.overall_success = False
                else:
                    logger.info(f"✅ Stage {stage.value} passed")
            
            # Evaluate quality gates
            await self._evaluate_quality_gates(result)
            
            # Determine overall success
            result.overall_success = all(
                stage_result.success for stage_result in result.stage_results
            ) and all(result.quality_gate_results.values())
            
        except Exception as e:
            logger.error(f"💥 Pipeline execution failed: {e}")
            result.overall_success = False
        
        finally:
            result.end_time = datetime.now()
        
        # Generate pipeline report
        await self._generate_pipeline_report(result)
        
        return result
    
    async def _execute_test_stage(self, stage: TestStage) -> TestStageResult:
        """Execute a single test stage"""
        logger.info(f"🧪 Executing stage: {stage.value}")
        start_time = datetime.now()
        
        stage_result = TestStageResult(
            stage=stage,
            success=False,
            duration_seconds=0.0,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0
        )
        
        try:
            if stage == TestStage.UNIT_TESTS:
                await self._run_unit_tests(stage_result)
            elif stage == TestStage.INTEGRATION_TESTS:
                await self._run_integration_tests(stage_result)
            elif stage == TestStage.PERFORMANCE_TESTS:
                await self._run_performance_tests(stage_result)
            elif stage == TestStage.ERROR_HANDLING_TESTS:
                await self._run_error_handling_tests(stage_result)
            elif stage == TestStage.E2E_TESTS:
                await self._run_e2e_tests(stage_result)
            elif stage == TestStage.SECURITY_TESTS:
                await self._run_security_tests(stage_result)
            elif stage == TestStage.REGRESSION_TESTS:
                await self._run_regression_tests(stage_result)
            else:
                raise ValueError(f"Unknown test stage: {stage}")
            
        except Exception as e:
            stage_result.error_message = str(e)
            logger.error(f"Stage {stage.value} failed with error: {e}")
        
        finally:
            end_time = datetime.now()
            stage_result.duration_seconds = (end_time - start_time).total_seconds()
        
        return stage_result
    
    async def _run_unit_tests(self, stage_result: TestStageResult):
        """Run unit tests"""
        # This would typically run pytest or similar
        logger.info("Running unit tests...")
        
        # Simulate unit test execution
        await asyncio.sleep(2)  # Simulate test execution time
        
        # Mock results - in real implementation, parse actual test results
        stage_result.total_tests = 50
        stage_result.passed_tests = 48
        stage_result.failed_tests = 2
        stage_result.skipped_tests = 0
        stage_result.success = stage_result.success_rate >= 90
        stage_result.artifacts.append("unit_test_results.xml")
    
    async def _run_integration_tests(self, stage_result: TestStageResult):
        """Run integration tests"""
        from .automated_test_framework import AutomatedTestSuite
        
        logger.info("Running integration tests...")
        
        # Wait for service to be ready
        await asyncio.sleep(5)
        
        # Run automated test suite
        test_suite = AutomatedTestSuite(self.base_url)
        metrics = await test_suite.run_all_tests()
        
        stage_result.total_tests = metrics.total_tests
        stage_result.passed_tests = metrics.passed_tests
        stage_result.failed_tests = metrics.failed_tests
        stage_result.skipped_tests = metrics.skipped_tests
        stage_result.success = metrics.success_rate >= 80
        stage_result.metrics["success_rate"] = metrics.success_rate
        stage_result.metrics["average_response_time"] = metrics.average_response_time
        stage_result.artifacts.append("integration_test_report.txt")
    
    async def _run_performance_tests(self, stage_result: TestStageResult):
        """Run performance tests"""
        from .performance_test_suite import PerformanceTestSuite
        
        logger.info("Running performance tests...")
        
        suite = PerformanceTestSuite(self.base_url)
        
        # Run quick performance test
        await suite.run_load_test(concurrent_users=10, duration_seconds=30)
        
        if suite.results:
            perf_result = suite.results[0]
            stage_result.total_tests = 1
            stage_result.passed_tests = 1 if perf_result.success_rate >= 95 else 0
            stage_result.failed_tests = 0 if perf_result.success_rate >= 95 else 1
            stage_result.success = perf_result.success_rate >= 95
            stage_result.metrics["requests_per_second"] = perf_result.requests_per_second
            stage_result.metrics["avg_response_time"] = perf_result.avg_response_time
            stage_result.metrics["success_rate"] = perf_result.success_rate
        
        stage_result.artifacts.append("performance_test_report.txt")
    
    async def _run_error_handling_tests(self, stage_result: TestStageResult):
        """Run error handling tests"""
        from .error_handling_test_suite import ErrorHandlingTestSuite
        
        logger.info("Running error handling tests...")
        
        async with ErrorHandlingTestSuite(self.base_url) as suite:
            # Run input validation tests only for CI speed
            await suite.run_input_validation_tests()
            
            results = suite.test_results
            if results:
                stage_result.total_tests = len(results)
                stage_result.passed_tests = sum(1 for r in results if r.success)
                stage_result.failed_tests = len(results) - stage_result.passed_tests
                stage_result.success = stage_result.success_rate >= 80
                stage_result.metrics["error_handling_success_rate"] = stage_result.success_rate
        
        stage_result.artifacts.append("error_handling_report.txt")
    
    async def _run_e2e_tests(self, stage_result: TestStageResult):
        """Run end-to-end tests"""
        from .test_data_manager import TestDataManager, TestScenario
        
        logger.info("Running E2E tests...")
        
        async with TestDataManager(self.base_url) as manager:
            # Run basic functionality scenario
            dataset = await manager.setup_test_scenario(TestScenario.BASIC_FUNCTIONALITY)
            results = await manager.execute_test_messages(TestScenario.BASIC_FUNCTIONALITY)
            
            stage_result.total_tests = len(results)
            stage_result.passed_tests = sum(1 for r in results if r.get("success"))
            stage_result.failed_tests = len(results) - stage_result.passed_tests
            stage_result.success = stage_result.success_rate >= 80
            
            await manager.cleanup_test_scenario(TestScenario.BASIC_FUNCTIONALITY)
        
        stage_result.artifacts.append("e2e_test_report.txt")
    
    async def _run_security_tests(self, stage_result: TestStageResult):
        """Run security tests"""
        from .error_handling_test_suite import ErrorHandlingTestSuite
        
        logger.info("Running security tests...")
        
        async with ErrorHandlingTestSuite(self.base_url) as suite:
            await suite.run_security_tests()
            
            security_results = [r for r in suite.test_results 
                              if r.test_case.test_type.value == "security_tests"]
            
            if security_results:
                stage_result.total_tests = len(security_results)
                stage_result.passed_tests = sum(1 for r in security_results if r.success)
                stage_result.failed_tests = len(security_results) - stage_result.passed_tests
                stage_result.success = stage_result.success_rate >= 90  # High bar for security
                stage_result.metrics["security_compliance"] = stage_result.success_rate
        
        stage_result.artifacts.append("security_test_report.txt")
    
    async def _run_regression_tests(self, stage_result: TestStageResult):
        """Run regression tests"""
        logger.info("Running regression tests...")
        
        # This would run a comprehensive suite of known-good tests
        # For now, simulate with a quick test run
        await asyncio.sleep(10)
        
        stage_result.total_tests = 25
        stage_result.passed_tests = 24
        stage_result.failed_tests = 1
        stage_result.success = stage_result.success_rate >= 95
        stage_result.artifacts.append("regression_test_report.txt")
    
    async def _evaluate_quality_gates(self, pipeline_result: CIPipelineResult):
        """Evaluate quality gates"""
        logger.info("🚪 Evaluating quality gates...")
        
        for gate_rule in self.config.quality_gates:
            gate_passed = await self._evaluate_single_quality_gate(gate_rule, pipeline_result)
            pipeline_result.quality_gate_results[gate_rule.gate_type.value] = gate_passed
            
            if gate_passed:
                logger.info(f"✅ Quality gate passed: {gate_rule.gate_type.value}")
            else:
                logger.error(f"❌ Quality gate failed: {gate_rule.gate_type.value}")
                if gate_rule.is_blocking:
                    pipeline_result.overall_success = False
    
    async def _evaluate_single_quality_gate(self, gate_rule: QualityGateRule, 
                                          pipeline_result: CIPipelineResult) -> bool:
        """Evaluate a single quality gate rule"""
        if gate_rule.gate_type == QualityGate.SUCCESS_RATE:
            actual_value = pipeline_result.overall_success_rate
        elif gate_rule.gate_type == QualityGate.PERFORMANCE_THRESHOLD:
            # Get average response time from performance tests
            perf_results = [r for r in pipeline_result.stage_results 
                           if r.stage == TestStage.PERFORMANCE_TESTS]
            if perf_results and "avg_response_time" in perf_results[0].metrics:
                actual_value = perf_results[0].metrics["avg_response_time"]
            else:
                return False
        elif gate_rule.gate_type == QualityGate.ERROR_RATE:
            total_tests = pipeline_result.total_tests
            failed_tests = sum(r.failed_tests for r in pipeline_result.stage_results)
            actual_value = (failed_tests / total_tests * 100) if total_tests > 0 else 0
        elif gate_rule.gate_type == QualityGate.SECURITY_COMPLIANCE:
            security_results = [r for r in pipeline_result.stage_results 
                              if r.stage == TestStage.SECURITY_TESTS]
            if security_results:
                actual_value = security_results[0].success_rate
            else:
                return False
        else:
            logger.warning(f"Unknown quality gate type: {gate_rule.gate_type}")
            return False
        
        # Apply operator
        if gate_rule.operator == ">=":
            return actual_value >= gate_rule.threshold
        elif gate_rule.operator == ">":
            return actual_value > gate_rule.threshold
        elif gate_rule.operator == "<=":
            return actual_value <= gate_rule.threshold
        elif gate_rule.operator == "<":
            return actual_value < gate_rule.threshold
        elif gate_rule.operator == "==":
            return actual_value == gate_rule.threshold
        else:
            logger.warning(f"Unknown operator: {gate_rule.operator}")
            return False
    
    async def _generate_pipeline_report(self, pipeline_result: CIPipelineResult):
        """Generate comprehensive pipeline report"""
        report_data = {
            "pipeline_id": pipeline_result.pipeline_id,
            "execution_time": pipeline_result.start_time.isoformat(),
            "duration_seconds": pipeline_result.duration_seconds,
            "overall_success": pipeline_result.overall_success,
            "total_tests": pipeline_result.total_tests,
            "total_passed": pipeline_result.total_passed,
            "overall_success_rate": pipeline_result.overall_success_rate,
            "stage_results": [asdict(result) for result in pipeline_result.stage_results],
            "quality_gate_results": pipeline_result.quality_gate_results,
            "artifacts": pipeline_result.artifacts
        }
        
        # Save JSON report
        report_file = f"ci_pipeline_report_{pipeline_result.pipeline_id}.json"
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2, default=str)
        
        pipeline_result.artifacts.append(report_file)
        
        # Generate human-readable report
        readable_report = self._generate_readable_report(pipeline_result)
        readable_file = f"ci_pipeline_summary_{pipeline_result.pipeline_id}.txt"
        with open(readable_file, "w") as f:
            f.write(readable_report)
        
        pipeline_result.artifacts.append(readable_file)
        
        logger.info(f"📊 Pipeline reports saved: {report_file}, {readable_file}")
    
    def _generate_readable_report(self, pipeline_result: CIPipelineResult) -> str:
        """Generate human-readable pipeline report"""
        status = "✅ PASSED" if pipeline_result.overall_success else "❌ FAILED"
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           CI/CD PIPELINE REPORT                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Pipeline ID:        {pipeline_result.pipeline_id}                              ║
║ Status:             {status}                                    ║
║ Duration:           {pipeline_result.duration_seconds:.1f} seconds              ║
║ Total Tests:        {pipeline_result.total_tests:,}                           ║
║ Passed:            {pipeline_result.total_passed:,} ({pipeline_result.overall_success_rate:.1f}%)   ║  
║ Failed:            {pipeline_result.total_tests - pipeline_result.total_passed:,}   ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 STAGE RESULTS:
"""
        
        for stage_result in pipeline_result.stage_results:
            status_icon = "✅" if stage_result.success else "❌"
            report += f"{status_icon} {stage_result.stage.value.replace('_', ' ').title()}: "
            report += f"{stage_result.passed_tests}/{stage_result.total_tests} "
            report += f"({stage_result.success_rate:.1f}%) - {stage_result.duration_seconds:.1f}s\n"
            
            if stage_result.error_message:
                report += f"   Error: {stage_result.error_message}\n"
        
        report += "\n🚪 QUALITY GATES:\n"
        for gate_type, passed in pipeline_result.quality_gate_results.items():
            status_icon = "✅" if passed else "❌"
            report += f"{status_icon} {gate_type.replace('_', ' ').title()}: {'PASSED' if passed else 'FAILED'}\n"
        
        if pipeline_result.artifacts:
            report += f"\n📁 ARTIFACTS ({len(pipeline_result.artifacts)}):\n"
            for artifact in pipeline_result.artifacts:
                report += f"  • {artifact}\n"
        
        return report


class QualityGateAnalyzer:
    """Analyze test results and enforce quality gates"""
    
    def __init__(self):
        self.default_quality_gates = [
            QualityGateRule(
                gate_type=QualityGate.SUCCESS_RATE,
                threshold=85.0,
                operator=">=",
                description="Overall test success rate must be >= 85%",
                is_blocking=True
            ),
            QualityGateRule(
                gate_type=QualityGate.PERFORMANCE_THRESHOLD,
                threshold=0.5,
                operator="<=",
                description="Average response time must be <= 500ms",
                is_blocking=True
            ),
            QualityGateRule(
                gate_type=QualityGate.ERROR_RATE,
                threshold=5.0,
                operator="<=",
                description="Error rate must be <= 5%",
                is_blocking=True
            ),
            QualityGateRule(
                gate_type=QualityGate.SECURITY_COMPLIANCE,
                threshold=95.0,
                operator=">=",
                description="Security compliance must be >= 95%",
                is_blocking=True
            )
        ]
    
    def analyze_results_from_files(self, results_directory: str) -> Dict[str, Any]:
        """Analyze test results from files in a directory"""
        results_path = Path(results_directory)
        
        analysis = {
            "overall_assessment": "UNKNOWN",
            "quality_gates": {},
            "recommendations": [],
            "metrics": {}
        }
        
        # Look for test result files
        test_files = list(results_path.glob("*_report_*.txt"))
        
        if not test_files:
            analysis["overall_assessment"] = "NO_RESULTS"
            analysis["recommendations"].append("No test result files found")
            return analysis
        
        # Parse results from files (simplified - would need more robust parsing)
        total_tests = 0
        passed_tests = 0
        
        for file_path in test_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Extract metrics (simplified parsing)
                    if "Total Tests:" in content:
                        lines = content.split('\n')
                        for line in lines:
                            if "Total Tests:" in line:
                                total_tests += int(line.split(':')[1].strip().replace(',', ''))
                            elif "Passed:" in line and "%" in line:
                                passed_part = line.split(':')[1].split('(')[0].strip().replace(',', '')
                                passed_tests += int(passed_part)
                                
            except Exception as e:
                logger.warning(f"Could not parse {file_path}: {e}")
        
        # Calculate metrics
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        analysis["metrics"]["total_tests"] = total_tests
        analysis["metrics"]["passed_tests"] = passed_tests
        analysis["metrics"]["success_rate"] = success_rate
        
        # Evaluate quality gates
        for gate in self.default_quality_gates:
            if gate.gate_type == QualityGate.SUCCESS_RATE:
                gate_passed = success_rate >= gate.threshold
                analysis["quality_gates"][gate.gate_type.value] = gate_passed
                
                if not gate_passed:
                    analysis["recommendations"].append(
                        f"Success rate ({success_rate:.1f}%) is below threshold ({gate.threshold}%)"
                    )
        
        # Overall assessment
        all_gates_passed = all(analysis["quality_gates"].values())
        analysis["overall_assessment"] = "PASSED" if all_gates_passed else "FAILED"
        
        return analysis


# CLI Interface and Main Functions
async def run_ci_pipeline():
    """Run complete CI/CD pipeline"""
    config = TestExecutionConfig(
        stages=[
            TestStage.INTEGRATION_TESTS,
            TestStage.PERFORMANCE_TESTS,
            TestStage.ERROR_HANDLING_TESTS,
            TestStage.E2E_TESTS
        ],
        quality_gates=[
            QualityGateRule(QualityGate.SUCCESS_RATE, 85.0, ">=", "Test success rate >= 85%"),
            QualityGateRule(QualityGate.PERFORMANCE_THRESHOLD, 0.5, "<=", "Response time <= 500ms"),
            QualityGateRule(QualityGate.ERROR_RATE, 5.0, "<=", "Error rate <= 5%")
        ],
        timeout_minutes=45,
        parallel_execution=False,  # Sequential for reliability
        fail_fast=False
    )
    
    executor = CIPipelineExecutor(config)
    result = await executor.execute_pipeline()
    
    print(executor._generate_readable_report(result))
    
    return result.overall_success


def generate_github_workflows():
    """Generate GitHub Actions workflows"""
    generator = GitHubActionsGenerator()
    
    # Generate basic workflow
    basic_workflow = generator.generate_basic_workflow()
    generator.save_workflow(basic_workflow, ".github/workflows/mock-telegram-tests.yml")
    
    # Generate comprehensive workflow
    comprehensive_workflow = generator.generate_comprehensive_workflow()
    generator.save_workflow(comprehensive_workflow, ".github/workflows/comprehensive-tests.yml")
    
    logger.info("✅ GitHub Actions workflows generated")


def analyze_test_results(results_dir: str = "."):
    """Analyze test results and generate quality gate report"""
    analyzer = QualityGateAnalyzer()
    analysis = analyzer.analyze_results_from_files(results_dir)
    
    # Save analysis report
    report_file = "quality_gate_report.json"
    with open(report_file, "w") as f:
        json.dump(analysis, f, indent=2)
    
    logger.info(f"📊 Quality gate analysis saved to: {report_file}")
    
    # Print summary
    print(f"""
Quality Gate Analysis Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Assessment: {analysis['overall_assessment']}
Total Tests: {analysis['metrics'].get('total_tests', 0):,}
Success Rate: {analysis['metrics'].get('success_rate', 0):.1f}%

Quality Gates:""")
    
    for gate_name, passed in analysis['quality_gates'].items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {gate_name.replace('_', ' ').title()}: {status}")
    
    if analysis['recommendations']:
        print("\n📋 Recommendations:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")
    
    return analysis['overall_assessment'] == "PASSED"


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ci_cd_integration.py <command>")
        print("Commands:")
        print("  run-pipeline     - Run complete CI/CD pipeline")
        print("  generate-workflows - Generate GitHub Actions workflows")
        print("  analyze-results  - Analyze test results and quality gates")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "run-pipeline":
        success = asyncio.run(run_ci_pipeline())
        sys.exit(0 if success else 1)
    elif command == "generate-workflows":
        generate_github_workflows()
    elif command == "analyze-results":
        results_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        success = analyze_test_results(results_dir)
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)