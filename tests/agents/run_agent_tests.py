#!/usr/bin/env python3
"""
Agent Test Runner

This script runs all agent test categories from CREWAI_AGENTS_TEST_SPECIFICATION.md:
- Category 1: Unit Tests
- Category 2: Integration Tests  
- Category 3: Reasoning Validation Tests
- Category 4: End-to-End Tests

Usage:
    python run_agent_tests.py [--category 1-4] [--verbose] [--coverage]
"""

import sys
import os
import asyncio
import argparse
import time
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.agents.conftest import TEST_CONFIG, TEST_DATA


class AgentTestRunner:
    """Runner for agent test categories."""
    
    def __init__(self, verbose: bool = False, coverage: bool = False):
        self.verbose = verbose
        self.coverage = coverage
        self.results = {}
        self.start_time = None
        
    def run_category_1_unit_tests(self) -> Dict[str, Any]:
        """Run Category 1: Unit Tests."""
        print("🧪 Running Category 1: Unit Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/agents/unit/",
            "-v" if self.verbose else "-q",
            "--tb=short"
        ]
        
        if self.coverage:
            cmd.extend(["--cov=kickai.agents", "--cov-report=html", "--cov-report=term"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            "category": "Unit Tests",
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    
    def run_category_2_integration_tests(self) -> Dict[str, Any]:
        """Run Category 2: Integration Tests."""
        print("🔗 Running Category 2: Integration Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/agents/integration/",
            "-v" if self.verbose else "-q",
            "--tb=short"
        ]
        
        if self.coverage:
            cmd.extend(["--cov=kickai.agents", "--cov-report=html", "--cov-report=term"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            "category": "Integration Tests",
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    
    def run_category_3_reasoning_tests(self) -> Dict[str, Any]:
        """Run Category 3: Reasoning Validation Tests."""
        print("🧠 Running Category 3: Reasoning Validation Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/agents/reasoning/",
            "-v" if self.verbose else "-q",
            "--tb=short"
        ]
        
        if self.coverage:
            cmd.extend(["--cov=kickai.agents", "--cov-report=html", "--cov-report=term"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            "category": "Reasoning Validation Tests",
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    
    def run_category_4_e2e_tests(self) -> Dict[str, Any]:
        """Run Category 4: End-to-End Tests."""
        print("🔄 Running Category 4: End-to-End Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/agents/e2e/",
            "-v" if self.verbose else "-q",
            "--tb=short"
        ]
        
        if self.coverage:
            cmd.extend(["--cov=kickai.agents", "--cov-report=html", "--cov-report=term"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            "category": "End-to-End Tests",
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories."""
        print("🚀 Starting Comprehensive Agent Test Suite")
        print(f"Configuration: {json.dumps(TEST_CONFIG, indent=2)}")
        print("-" * 80)
        
        self.start_time = time.time()
        
        # Run all categories
        categories = [
            self.run_category_1_unit_tests,
            self.run_category_2_integration_tests,
            self.run_category_3_reasoning_tests,
            self.run_category_4_e2e_tests
        ]
        
        for category_func in categories:
            try:
                result = category_func()
                self.results[result["category"]] = result
            except Exception as e:
                self.results[f"Error in {category_func.__name__}"] = {
                    "category": category_func.__name__,
                    "success": False,
                    "error": str(e),
                    "return_code": 1
                }
        
        return self.generate_summary()
    
    def run_specific_category(self, category: int) -> Dict[str, Any]:
        """Run a specific test category."""
        category_map = {
            1: self.run_category_1_unit_tests,
            2: self.run_category_2_integration_tests,
            3: self.run_category_3_reasoning_tests,
            4: self.run_category_4_e2e_tests
        }
        
        if category not in category_map:
            raise ValueError(f"Invalid category: {category}. Must be 1-4.")
        
        print(f"🎯 Running Category {category} Tests...")
        self.start_time = time.time()
        
        result = category_map[category]()
        self.results[result["category"]] = result
        
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary."""
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() if result.get("success", False))
        failed_tests = total_tests - successful_tests
        
        summary = {
            "total_categories": total_tests,
            "successful_categories": successful_tests,
            "failed_categories": failed_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "duration_seconds": duration,
            "results": self.results
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("📊 AGENT TEST SUMMARY")
        print("=" * 80)
        
        print(f"Total Categories: {summary['total_categories']}")
        print(f"Successful: {summary['successful_categories']}")
        print(f"Failed: {summary['failed_categories']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Duration: {summary['duration_seconds']:.2f} seconds")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        for category, result in summary["results"].items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"{category}: {status}")
            
            if self.verbose and result.get("error"):
                print(f"  Error: {result['error']}")
        
        print("\n" + "=" * 80)
        
        # Save detailed results to file
        self.save_results(summary)
    
    def save_results(self, summary: Dict[str, Any]):
        """Save test results to file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"agent_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📄 Detailed results saved to: {results_file}")
    
    def check_ollama_availability(self) -> bool:
        """Check if Ollama is available for reasoning tests."""
        try:
            import httpx
            response = httpx.get(f"{TEST_CONFIG['ollama_base_url']}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run CrewAI Agent Tests")
    parser.add_argument("--category", type=int, choices=[1, 2, 3, 4], 
                       help="Run specific test category (1-4)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", 
                       help="Generate coverage report")
    parser.add_argument("--check-ollama", action="store_true", 
                       help="Check Ollama availability before running tests")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = AgentTestRunner(verbose=args.verbose, coverage=args.coverage)
    
    # Check Ollama availability if requested
    if args.check_ollama:
        print("🔍 Checking Ollama availability...")
        if runner.check_ollama_availability():
            print("✅ Ollama is available")
        else:
            print("⚠️  Ollama is not available - reasoning tests may fail")
            print(f"   Expected URL: {TEST_CONFIG['ollama_base_url']}")
    
    try:
        if args.category:
            # Run specific category
            summary = runner.run_specific_category(args.category)
        else:
            # Run all categories
            summary = runner.run_all_tests()
        
        # Print summary
        runner.print_summary(summary)
        
        # Exit with appropriate code
        if summary["failed_categories"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 