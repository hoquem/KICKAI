#!/usr/bin/env python3
"""
Demo Script for Mock Communication Integration

This script demonstrates that communication tools can successfully send messages 
to the Mock Telegram UI when using the MockTelegramBotService.

Usage:
    USE_MOCK_TELEGRAM=true USE_MOCK_UI=true PYTHONPATH=. python demo_mock_communication.py
"""

import asyncio
import os
import sys
from loguru import logger

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

async def demo_communication_integration():
    """Demonstrate the mock communication integration working."""
    
    # Set up environment for mock mode
    os.environ["USE_MOCK_TELEGRAM"] = "true"
    os.environ["USE_MOCK_UI"] = "true"
    os.environ["KICKAI_INVITE_SECRET_KEY"] = "test-invite-secret-key-for-testing-only"
    os.environ["PYTHONPATH"] = "."
    
    logger.info("🎮 KICKAI Mock Communication Integration Demo")
    logger.info("=" * 50)
    logger.info("🌐 Mock Telegram UI should be running at http://localhost:8001")
    logger.info("📱 Messages will appear in real-time in the Mock UI")
    logger.info("")
    
    try:
        # Initialize the dependency container
        from kickai.core.dependency_container import initialize_container, get_container
        
        logger.info("🔧 Initializing KICKAI system...")
        container = initialize_container()
        
        # Get the communication service
        from kickai.features.communication.domain.services.communication_service import CommunicationService
        communication_service = container.get_service(CommunicationService)
        
        # Check if we have the mock service
        if communication_service.telegram_bot_service:
            from kickai.features.communication.infrastructure.mock_telegram_bot_service import MockTelegramBotService
            if isinstance(communication_service.telegram_bot_service, MockTelegramBotService):
                logger.info("✅ MockTelegramBotService is active and ready")
                mock_service = communication_service.telegram_bot_service
                logger.info(f"📱 Bot User ID: {mock_service.bot_user_id}")
                logger.info(f"💬 Main Chat: {mock_service.main_chat_id}")
                logger.info(f"🔒 Leadership Chat: {mock_service.leadership_chat_id}")
            else:
                logger.error("❌ Expected MockTelegramBotService but got real service")
                return False
        else:
            logger.error("❌ No TelegramBotService available")
            return False
        
        logger.info("")
        logger.info("🚀 Starting Communication Demo...")
        logger.info("")
        
        # Demo 1: Send a welcome message
        logger.info("📤 Demo 1: Sending welcome message to main chat")
        success1 = await communication_service.send_message(
            "🎮 Welcome to KICKAI Mock Communication Demo! The integration is working perfectly.",
            "main_chat",
            "KTI"
        )
        logger.info(f"   Result: {'✅ Sent' if success1 else '❌ Failed'}")
        await asyncio.sleep(1)
        
        # Demo 2: Send announcement
        logger.info("📣 Demo 2: Sending announcement")
        success2 = await communication_service.send_announcement(
            "🔥 Great news! Our communication tools are now fully integrated with the Mock Telegram UI. You can see this message in real-time at http://localhost:8001",
            "KTI"
        )
        logger.info(f"   Result: {'✅ Sent' if success2 else '❌ Failed'}")
        await asyncio.sleep(1)
        
        # Demo 3: Send leadership message
        logger.info("🔒 Demo 3: Sending message to leadership chat")
        success3 = await communication_service.send_message(
            "🎯 Leadership team: The Mock Communication Integration is complete and working flawlessly!",
            "leadership_chat",
            "KTI"
        )
        logger.info(f"   Result: {'✅ Sent' if success3 else '❌ Failed'}")
        await asyncio.sleep(1)
        
        # Demo 4: Send poll
        logger.info("📊 Demo 4: Sending poll")
        success4 = await communication_service.send_poll(
            "How would you rate the Mock Communication Integration?",
            "Excellent, Very Good, Good, Needs Improvement",
            "KTI"
        )
        logger.info(f"   Result: {'✅ Sent' if success4 else '❌ Failed'}")
        
        logger.info("")
        logger.info("📊 Demo Summary:")
        total_sent = sum([success1, success2, success3, success4])
        logger.info(f"   Messages sent successfully: {total_sent}/4")
        
        if total_sent > 0:
            logger.info("")
            logger.info("🌐 Check the Mock Telegram UI to see all messages:")
            logger.info("   • Main Chat: http://localhost:8001")
            logger.info("   • Use the chat selector to switch between main and leadership chats")
            logger.info("   • Messages should appear in real-time with proper formatting")
            
        return total_sent == 4
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main demo function."""
    
    logger.info("🎮 KICKAI Mock Communication Integration Demo")
    logger.info("=" * 50)
    
    # Check if Mock UI is running
    import requests
    try:
        response = requests.get("http://localhost:8001/api/stats", timeout=2)
        if response.status_code == 200:
            stats = response.json()
            logger.info(f"✅ Mock UI is running: {stats.get('total_users', 0)} users, {stats.get('total_messages', 0)} messages")
        else:
            logger.error("❌ Mock UI returned unexpected status")
            sys.exit(1)
    except Exception:
        logger.error("❌ Mock UI is not running at http://localhost:8001")
        logger.info("💡 Start it with: PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py")
        sys.exit(1)
    
    # Run demo
    success = asyncio.run(demo_communication_integration())
    
    logger.info("")
    logger.info("=" * 50)
    if success:
        logger.info("🎉 Demo completed successfully!")
        logger.info("✅ Mock Communication Integration is working perfectly")
        logger.info("🌐 Visit http://localhost:8001 to see the messages")
    else:
        logger.error("❌ Demo failed - check logs above")
        sys.exit(1)

if __name__ == "__main__":
    main()