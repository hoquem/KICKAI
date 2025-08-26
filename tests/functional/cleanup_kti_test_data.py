#!/usr/bin/env python3
"""
Cleanup KTI Test Data

Script to safely remove all test data created during functional testing.
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
    """Cleanup KTI test data after functional testing"""
    print("🧹 Cleaning up KTI Test Data")
    print("=" * 40)
    
    try:
        # Initialize test data manager
        manager = KTITestDataManager("KTI")
        await manager.initialize()
        
        # Get summary before cleanup
        print("📊 Checking existing test data...")
        validation_results = await manager.validate_test_data()
        
        if validation_results.get("data_integrity", False):
            summary = await manager.get_test_summary()
            print(f"   • Players to remove: {summary['counts']['players']}")
            print(f"   • Members to remove: {summary['counts']['members']}")
            print(f"   • Markers to remove: {summary['counts']['markers']}")
            
            # Confirm cleanup
            print("\n⚠️  This will permanently delete all test data from Firestore.")
            confirm = input("Proceed with cleanup? (y/N): ")
            
            if confirm.lower() in ['y', 'yes']:
                print("\n🚀 Starting cleanup process...")
                success = await manager.cleanup_test_data()
                
                if success:
                    print("\n✅ KTI Test Data Cleanup Successful!")
                    print("=" * 40)
                    print("🎯 All test data has been removed from Firestore.")
                    print("   • Players removed")
                    print("   • Members removed") 
                    print("   • Test markers removed")
                    print("   • Generated invite links removed")
                    
                else:
                    print("\n⚠️  Cleanup completed with some errors.")
                    print("Check logs for detailed error information.")
                    
            else:
                print("\n🚫 Cleanup cancelled by user.")
                
        else:
            if "error" in validation_results:
                print(f"❌ Error validating test data: {validation_results['message']}")
            else:
                print("ℹ️  No test data found to cleanup.")
                print("Either no test data exists or validation failed.")
            
    except Exception as e:
        print(f"\n💥 Cleanup failed with exception: {e}")
        logger.error(f"Cleanup exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())