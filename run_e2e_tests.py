#!/usr/bin/env python3
"""
E2E Test Runner - Root Wrapper

This script is a wrapper for the main E2E test runner in scripts/run_e2e_tests.py.
It ensures proper environment setup and forwards all arguments to the main runner.

Usage:
    python run_e2e_tests.py [options]
    
Examples:
    python run_e2e_tests.py --suite smoke
    python run_e2e_tests.py --suite registration
    python run_e2e_tests.py --suite all
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point for E2E test runner."""
    # Get the script directory
    script_dir = Path(__file__).parent
    e2e_script = script_dir / "scripts" / "run_e2e_tests.py"
    
    # Check if the main E2E script exists
    if not e2e_script.exists():
        print(f"Error: E2E test script not found at {e2e_script}")
        sys.exit(1)
    
    # Set up environment
    os.environ['PYTHONPATH'] = f"{script_dir}/src:{os.environ.get('PYTHONPATH', '')}"
    
    # Forward all arguments to the main script
    args = sys.argv[1:]
    cmd = [sys.executable, str(e2e_script)] + args
    
    try:
        # Run the main E2E test script
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"E2E tests failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nE2E tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error running E2E tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 