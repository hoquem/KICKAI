#!/usr/bin/env python3
"""
Player Registration Test Runner

This script runs the comprehensive player registration test suite.
"""

import asyncio
import sys
from datetime import datetime

# Add kickai to path
sys.path.insert(0, "kickai")

from tests.features.player_registration.test_player_registration_comprehensive import PlayerRegistrationTestSuite


async def main():
    """Main test runner function."""
    print("🎯 KICKAI Player Registration Test Suite")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Create and run test suite
        test_suite = PlayerRegistrationTestSuite()
        report = await test_suite.run_all_tests()
        
        # Print final summary
        print("\n" + "=" * 50)
        print("🏁 TEST EXECUTION COMPLETE")
        print("=" * 50)
        print(report.summary)
        
        # Determine exit code
        if report.failed > 0 or report.errors > 0:
            print("❌ Some tests failed!")
            return 1
        else:
            print("✅ All tests passed!")
            return 0
            
    except Exception as e:
        print(f"💥 Test execution failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 