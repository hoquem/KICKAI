#!/usr/bin/env python3
"""
Test script to verify bot improvements
"""

import time
import logging
from run_telegram_bot import TelegramBotRunner

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bot_improvements():
    """Test the improved bot functionality."""
    print("🧪 Testing Bot Improvements")
    print("=" * 40)
    
    try:
        # Create bot runner
        bot_runner = TelegramBotRunner()
        
        # Test connection
        print("\n🔍 Testing bot connection...")
        if not bot_runner.test_connection():
            print("❌ Bot connection failed")
            return False
        
        # Test webhook deletion
        print("\n🔧 Testing webhook deletion...")
        bot_runner._delete_webhook()
        
        # Test error handling
        print("\n🛡️ Testing error handling...")
        bot_runner.consecutive_errors = 0
        delay = bot_runner._calculate_delay()
        print(f"   Base delay: {delay}s")
        
        bot_runner.consecutive_errors = 2
        delay = bot_runner._calculate_delay()
        print(f"   Delay after 2 errors: {delay:.1f}s")
        
        bot_runner.consecutive_errors = 5
        delay = bot_runner._calculate_delay()
        print(f"   Delay after 5 errors: {delay:.1f}s")
        
        # Test getting updates (should not fail)
        print("\n📡 Testing update retrieval...")
        updates = bot_runner.get_updates(timeout=5)
        if updates is not None:
            print("   ✅ Update retrieval successful")
        else:
            print("   ⚠️ Update retrieval returned None (expected for timeout)")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    test_bot_improvements() 