"""
Sequential Test Execution Framework

Provides structured, sequential test execution with:
- Dependency management between test stages
- Detailed progress reporting
- Failure handling and recovery
- Test result aggregation
- Performance profiling
- HTML report generation
"""

import pytest
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TestStage(Enum):
    """Test execution stages."""
    UNIT_TESTS = "unit_tests"
    INTEGRATION_TESTS = "integration_tests"
    PERFORMANCE_TESTS = "performance_tests"
    PROPERTY_TESTS = "property_tests"
    API_TESTS = "api_tests"
    E2E_TESTS = "e2e_tests"


class TestStatus(Enum):
    """Test status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Container for test results."""
    stage: str
    status: str
    duration: float
    passed: int
    failed: int
    skipped: int
    errors: int
    total: int
    details: Dict[str, Any]
    timestamp: str


@dataclass
class TestExecutionPlan:
    """Test execution plan."""
    stages: List[str]
    stop_on_failure: bool
    generate_report: bool
    verbose: bool
    parallel: bool
    coverage: bool


class SequentialTestRunner:
    """Runs tests sequentially with detailed reporting."""
    
    def __init__(self, base_dir: str = None):
        """Initialize test runner."""
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.results: List[TestResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def run_stage(self, stage: TestStage, pytest_args: List[str] = None) -> TestResult:
        """Run a single test stage."""
        print(f"\n{'='*80}")
        print(f"Running {stage.value.upper()}")
        print(f"{'='*80}\n")
        
        # Determine test files for this stage
        test_files = self._get_test_files_for_stage(stage)
        
        if not test_files:
            print(f"No test files found for stage: {stage.value}")
            return TestResult(
                stage=stage.value,
                status=TestStatus.SKIPPED.value,
                duration=0.0,
                passed=0,
                failed=0,
                skipped=0,
                errors=0,
                total=0,
                details={"reason": "No test files found"},
                timestamp=datetime.now().isoformat()
            )
        
        # Build pytest command
        args = [
            "-v",
            "--tb=short",
            "-ra",
            f"--junit-xml=results_{stage.value}.xml",
        ]
        
        if pytest_args:
            args.extend(pytest_args)
        
        args.extend(test_files)
        
        # Run tests
        start_time = time.time()
        exit_code = pytest.main(args)
        duration = time.time() - start_time
        
        # Parse results from pytest
        result = self._parse_pytest_results(stage, exit_code, duration)
        
        self.results.append(result)
        return result
    
    def _get_test_files_for_stage(self, stage: TestStage) -> List[str]:
        """Get test files for a specific stage."""
        stage_mapping = {
            TestStage.UNIT_TESTS: [
                "test_multi_dimensional_models.py",
                "test_compression_algorithms_complete.py"
            ],
            TestStage.INTEGRATION_TESTS: [
                "test_integration_workflows.py",
                "test_meta_learning_service.py"
            ],
            TestStage.PERFORMANCE_TESTS: [
                "test_performance_benchmarks.py"
            ],
            TestStage.PROPERTY_TESTS: [
                "test_property_based.py"
            ],
            TestStage.API_TESTS: [
                "test_api_endpoints.py"
            ]
        }
        
        files = stage_mapping.get(stage, [])
        existing_files = []
        
        for file in files:
            file_path = self.base_dir / file
            if file_path.exists():
                existing_files.append(str(file_path))
        
        return existing_files
    
    def _parse_pytest_results(self, stage: TestStage, exit_code: int, duration: float) -> TestResult:
        """Parse pytest results."""
        # Pytest exit codes:
        # 0: All tests passed
        # 1: Tests were collected and run but some failed
        # 2: Test execution was interrupted
        # 3: Internal error
        # 4: pytest command line usage error
        # 5: No tests collected
        
        if exit_code == 0:
            status = TestStatus.PASSED
        elif exit_code == 5:
            status = TestStatus.SKIPPED
        elif exit_code in [2, 3, 4]:
            status = TestStatus.ERROR
        else:
            status = TestStatus.FAILED
        
        # Try to parse XML results if available
        xml_file = Path(f"results_{stage.value}.xml")
        stats = self._parse_junit_xml(xml_file) if xml_file.exists() else {}
        
        return TestResult(
            stage=stage.value,
            status=status.value,
            duration=duration,
            passed=stats.get('passed', 0),
            failed=stats.get('failed', 0),
            skipped=stats.get('skipped', 0),
            errors=stats.get('errors', 0),
            total=stats.get('total', 0),
            details={
                "exit_code": exit_code,
                "xml_file": str(xml_file) if xml_file.exists() else None
            },
            timestamp=datetime.now().isoformat()
        )
    
    def _parse_junit_xml(self, xml_file: Path) -> Dict[str, int]:
        """Parse JUnit XML results."""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Get testsuite element
            testsuite = root.find('testsuite') if root.tag != 'testsuite' else root
            
            if testsuite is not None:
                return {
                    'total': int(testsuite.get('tests', 0)),
                    'passed': int(testsuite.get('tests', 0)) - int(testsuite.get('failures', 0)) - int(testsuite.get('errors', 0)) - int(testsuite.get('skipped', 0)),
                    'failed': int(testsuite.get('failures', 0)),
                    'errors': int(testsuite.get('errors', 0)),
                    'skipped': int(testsuite.get('skipped', 0))
                }
        except Exception as e:
            print(f"Error parsing XML: {e}")
        
        return {'total': 0, 'passed': 0, 'failed': 0, 'errors': 0, 'skipped': 0}
    
    def run_all(self, plan: TestExecutionPlan) -> bool:
        """Run all test stages according to plan."""
        print(f"\n{'#'*80}")
        print(f"# COMPREHENSIVE TEST SUITE EXECUTION")
        print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*80}\n")
        
        self.start_time = time.time()
        all_passed = True
        
        # Execute stages
        for stage_name in plan.stages:
            try:
                stage = TestStage(stage_name)
            except ValueError:
                print(f"Unknown stage: {stage_name}")
                continue
            
            result = self.run_stage(stage)
            
            # Print stage summary
            self._print_stage_summary(result)
            
            # Check if should stop
            if plan.stop_on_failure and result.status in [TestStatus.FAILED.value, TestStatus.ERROR.value]:
                print(f"\n❌ Stopping due to failure in {stage.value}")
                all_passed = False
                break
            
            if result.status == TestStatus.FAILED.value:
                all_passed = False
        
        self.end_time = time.time()
        
        # Generate final report
        self._print_final_summary()
        
        if plan.generate_report:
            self._generate_html_report()
            self._generate_json_report()
        
        return all_passed
    
    def _print_stage_summary(self, result: TestResult):
        """Print summary for a stage."""
        status_emoji = {
            TestStatus.PASSED.value: "✅",
            TestStatus.FAILED.value: "❌",
            TestStatus.SKIPPED.value: "⏭️",
            TestStatus.ERROR.value: "💥"
        }
        
        emoji = status_emoji.get(result.status, "❓")
        
        print(f"\n{emoji} {result.stage.upper()}: {result.status}")
        print(f"   Duration: {result.duration:.2f}s")
        print(f"   Tests: {result.total} total")
        print(f"   Passed: {result.passed}")
        print(f"   Failed: {result.failed}")
        print(f"   Errors: {result.errors}")
        print(f"   Skipped: {result.skipped}")
    
    def _print_final_summary(self):
        """Print final summary of all stages."""
        total_duration = self.end_time - self.start_time if self.start_time else 0
        
        print(f"\n{'#'*80}")
        print(f"# FINAL SUMMARY")
        print(f"{'#'*80}\n")
        
        # Aggregate statistics
        total_tests = sum(r.total for r in self.results)
        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        total_skipped = sum(r.skipped for r in self.results)
        
        stages_run = len(self.results)
        stages_passed = sum(1 for r in self.results if r.status == TestStatus.PASSED.value)
        stages_failed = sum(1 for r in self.results if r.status == TestStatus.FAILED.value)
        
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Stages: {stages_run} run, {stages_passed} passed, {stages_failed} failed")
        print(f"Tests: {total_tests} total, {total_passed} passed, {total_failed} failed, {total_errors} errors, {total_skipped} skipped")
        
        if total_tests > 0:
            pass_rate = (total_passed / total_tests) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
        
        print(f"\nStage Results:")
        for result in self.results:
            status_symbol = "✅" if result.status == TestStatus.PASSED.value else "❌"
            print(f"  {status_symbol} {result.stage}: {result.status} ({result.duration:.2f}s)")
        
        print(f"\n{'#'*80}\n")
    
    def _generate_html_report(self):
        """Generate HTML report."""
        html_file = Path("test_report.html")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Comprehensive Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .stage {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ background: #d4edda; }}
        .failed {{ background: #f8d7da; }}
        .skipped {{ background: #fff3cd; }}
        .error {{ background: #f8d7da; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #007bff; color: white; }}
        .metric {{ font-size: 24px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Comprehensive Test Suite Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Duration: <span class="metric">{self.end_time - self.start_time if self.start_time else 0:.2f}s</span></p>
        <p>Stages Run: <span class="metric">{len(self.results)}</span></p>
        <p>Total Tests: <span class="metric">{sum(r.total for r in self.results)}</span></p>
    </div>
    
    <h2>Stage Results</h2>
"""
        
        for result in self.results:
            css_class = result.status
            html_content += f"""
    <div class="stage {css_class}">
        <h3>{result.stage.upper()}</h3>
        <p><strong>Status:</strong> {result.status}</p>
        <p><strong>Duration:</strong> {result.duration:.2f}s</p>
        <table>
            <tr><th>Metric</th><th>Count</th></tr>
            <tr><td>Total Tests</td><td>{result.total}</td></tr>
            <tr><td>Passed</td><td>{result.passed}</td></tr>
            <tr><td>Failed</td><td>{result.failed}</td></tr>
            <tr><td>Errors</td><td>{result.errors}</td></tr>
            <tr><td>Skipped</td><td>{result.skipped}</td></tr>
        </table>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        html_file.write_text(html_content)
        print(f"\n📊 HTML report generated: {html_file.absolute()}")
    
    def _generate_json_report(self):
        """Generate JSON report."""
        json_file = Path("test_report.json")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": self.end_time - self.start_time if self.start_time else 0,
            "stages": [asdict(r) for r in self.results],
            "summary": {
                "total_tests": sum(r.total for r in self.results),
                "passed": sum(r.passed for r in self.results),
                "failed": sum(r.failed for r in self.results),
                "errors": sum(r.errors for r in self.results),
                "skipped": sum(r.skipped for r in self.results),
                "stages_run": len(self.results),
                "stages_passed": sum(1 for r in self.results if r.status == TestStatus.PASSED.value)
            }
        }
        
        json_file.write_text(json.dumps(report, indent=2))
        print(f"📄 JSON report generated: {json_file.absolute()}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sequential Test Execution Framework")
    parser.add_argument(
        "--stages",
        nargs="+",
        default=["unit_tests", "integration_tests", "performance_tests", "property_tests", "api_tests"],
        help="Stages to run"
    )
    parser.add_argument("--stop-on-failure", action="store_true", help="Stop on first failure")
    parser.add_argument("--no-report", action="store_true", help="Don't generate reports")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    
    args = parser.parse_args()
    
    plan = TestExecutionPlan(
        stages=args.stages,
        stop_on_failure=args.stop_on_failure,
        generate_report=not args.no_report,
        verbose=args.verbose,
        parallel=args.parallel,
        coverage=args.coverage
    )
    
    runner = SequentialTestRunner()
    success = runner.run_all(plan)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

