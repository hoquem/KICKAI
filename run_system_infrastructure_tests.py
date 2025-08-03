#!/usr/bin/env python3
"""
System Infrastructure Test Runner

This script runs the comprehensive test suite for the system infrastructure module.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.features.system_infrastructure.test_system_infrastructure_comprehensive import main


if __name__ == "__main__":
    print("🎯 KICKAI System Infrastructure Test Suite")
    print("=" * 50)
    print(f"Started at: {asyncio.run(main())}")
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 