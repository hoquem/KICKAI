#!/usr/bin/env python3
"""
Wrapper script to run other scripts with proper PYTHONPATH setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    
    # Set PYTHONPATH to include src directory
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path)
    
    # Get the script to run from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_with_src_path.py <script_name> [args...]")
        sys.exit(1)
    
    script_name = sys.argv[1]
    script_args = sys.argv[2:]
    
    # Construct the full path to the script
    script_path = project_root / "scripts" / script_name
    
    if not script_path.exists():
        print(f"Script not found: {script_path}")
        sys.exit(1)
    
    # Run the script with the modified environment
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)] + script_args,
            env=env,
            cwd=project_root
        )
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 