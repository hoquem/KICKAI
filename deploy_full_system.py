#!/usr/bin/env python3
"""
Full KICKAI System Deployment Script
Deploys the complete system including CrewAI agents to Railway
"""

import os
import sys
import logging
import time
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'GOOGLE_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def test_database_connection():
    """Test database connection and basic functionality."""
    try:
        from src.tools.supabase_tools import get_supabase_client
        supabase = get_supabase_client()
        
        # Test basic query
        response = supabase.table('teams').select('*').limit(1).execute()
        logger.info("✅ Database connection successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_crewai_setup():
    """Test CrewAI setup and agent creation."""
    try:
        from src.agents import create_llm, create_agents_for_team, create_crew_for_team
        
        # Test LLM creation
        logger.info("🧠 Testing LLM creation...")
        llm = create_llm()
        logger.info("✅ LLM created successfully")
        
        # Test agent creation for a team
        logger.info("🤖 Testing agent creation...")
        team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'  # BP Hatters
        agents = create_agents_for_team(llm, team_id)
        logger.info(f"✅ Created {len(agents)} agents for team {team_id}")
        
        # Test crew creation
        logger.info("👥 Testing crew creation...")
        crew = create_crew_for_team(agents)
        logger.info("✅ Crew created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ CrewAI setup failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_telegram_integration():
    """Test Telegram bot integration."""
    try:
        from src.tools.telegram_tools import get_telegram_tools_dual
        
        # Test Telegram tools creation
        team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
        tools = get_telegram_tools_dual(team_id)
        logger.info("✅ Telegram tools created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Telegram integration failed: {e}")
        return False

def start_health_server():
    """Start the health check server for Railway."""
    try:
        from health_check import start_health_server
        health_thread = start_health_server()
        logger.info("✅ Health server started")
        return health_thread
    except Exception as e:
        logger.error(f"❌ Health server failed: {e}")
        return None

def start_telegram_bot():
    """Start the Telegram bot."""
    try:
        from run_telegram_bot import TelegramBotRunner
        
        # Create bot runner
        bot_runner = TelegramBotRunner()
        
        # Test connection
        if not bot_runner.test_connection():
            logger.error("❌ Bot connection failed")
            return False
        
        # Start bot in a separate thread
        def run_bot():
            try:
                bot_runner.run_polling()
            except Exception as e:
                logger.error(f"❌ Bot error: {e}")
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("✅ Telegram bot started")
        return True
        
    except Exception as e:
        logger.error(f"❌ Telegram bot failed: {e}")
        return False

def start_multi_team_manager():
    """Start the multi-team manager."""
    try:
        from src.multi_team_manager import MultiTeamManager
        
        # Create and initialize multi-team manager
        manager = MultiTeamManager()
        manager.initialize()
        
        logger.info(f"✅ Multi-team manager initialized with {len(manager.crews)} teams")
        return manager
        
    except Exception as e:
        logger.error(f"❌ Multi-team manager failed: {e}")
        return None

def main():
    """Main deployment function."""
    print("🚀 KICKAI Full System Deployment")
    print("=" * 40)
    
    # Step 1: Environment check
    print("\n1️⃣ Checking environment...")
    if not check_environment():
        print("❌ Environment check failed")
        return
    
    # Step 2: Database connection test
    print("\n2️⃣ Testing database connection...")
    if not test_database_connection():
        print("❌ Database connection failed")
        return
    
    # Step 3: CrewAI setup test
    print("\n3️⃣ Testing CrewAI setup...")
    if not test_crewai_setup():
        print("❌ CrewAI setup failed")
        return
    
    # Step 4: Telegram integration test
    print("\n4️⃣ Testing Telegram integration...")
    if not test_telegram_integration():
        print("❌ Telegram integration failed")
        return
    
    # Step 5: Start health server
    print("\n5️⃣ Starting health server...")
    health_thread = start_health_server()
    if not health_thread:
        print("❌ Health server failed")
        return
    
    # Step 6: Start multi-team manager
    print("\n6️⃣ Starting multi-team manager...")
    manager = start_multi_team_manager()
    if not manager:
        print("❌ Multi-team manager failed")
        return
    
    # Step 7: Start Telegram bot
    print("\n7️⃣ Starting Telegram bot...")
    if not start_telegram_bot():
        print("❌ Telegram bot failed")
        return
    
    print("\n✅ Full KICKAI system deployed successfully!")
    print("\n📊 System Status:")
    print("   🏥 Health Server: Running")
    print("   🤖 Telegram Bot: Running")
    print("   👥 Multi-Team Manager: Running")
    print("   🧠 CrewAI Agents: Ready")
    print("   🗄️  Database: Connected")
    
    print("\n🔗 Health Check: https://your-app.railway.app/health")
    print("📱 Telegram Bot: @BPHatters_bot")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(60)  # Check every minute
            logger.info("💓 System heartbeat - all services running")
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down KICKAI system...")

if __name__ == "__main__":
    main() 