#!/usr/bin/env python3
"""
Setup KTI Test Data

Simple script to initialize test data for KTI team functional testing.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.functional.kti_test_data_manager import KTITestDataManager
from loguru import logger

async def main():
    """Setup KTI test data for functional testing"""
    print("🚀 Setting up KTI Test Data for Functional Testing")
    print("=" * 60)
    
    try:
        # Initialize test data manager
        manager = KTITestDataManager("KTI")
        await manager.initialize()
        
        # Setup test data
        logger.info("Creating comprehensive test data set...")
        success = await manager.setup_test_data()
        
        if success:
            # Validate the created data
            validation_results = await manager.validate_test_data()
            
            if validation_results.get("data_integrity", False):
                print("\n✅ KTI Test Data Setup Successful!")
                print("=" * 60)
                
                # Print summary
                summary = await manager.get_test_summary()
                print(f"📊 Test Data Summary:")
                print(f"   • Team ID: {summary['team_id']}")
                print(f"   • Players created: {summary['counts']['players']}")
                print(f"   • Members created: {summary['counts']['members']}")
                print(f"   • Test markers: {summary['counts']['markers']}")
                
                print("\n🎯 Ready for functional testing!")
                print("   • Mock Telegram UI: PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py")
                print("   • Start KICKAI Bot: PYTHONPATH=. python run_bot_local.py")
                print("   • Run tests: PYTHONPATH=. python tests/functional/functional_test_runner.py")
                
            else:
                print("\n❌ Test data validation failed!")
                print(f"Validation results: {validation_results}")
                
                # Cleanup on validation failure
                print("🧹 Cleaning up invalid test data...")
                await manager.cleanup_test_data()
                
        else:
            print("\n❌ KTI Test Data Setup Failed!")
            print("Check logs for detailed error information.")
            
    except Exception as e:
        print(f"\n💥 Setup failed with exception: {e}")
        logger.error(f"Setup exception: {e}")
        
        # Attempt cleanup on exception
        try:
            if 'manager' in locals():
                await manager.cleanup_test_data()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())