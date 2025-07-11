#!/usr/bin/env python3
"""
Health Check Runner

Run comprehensive health checks to diagnose system issues.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.startup_validator import run_startup_validation
from services.health_check_service import get_health_check_service
from services.background_health_monitor import get_background_health_monitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('health_checks.log')
    ]
)

async def main():
    """Run health checks and report results."""
    print("🚀 Starting KICKAI System Health Checks...")
    print("=" * 60)
    
    try:
        report = await run_startup_validation(team_id="KAI")
        
        if report.is_healthy():
            print("\n🎉 All health checks passed! System is ready to start.")
            return 0
        else:
            print(f"\n❌ Health checks failed! {len(report.critical_failures)} critical issues found.")
            print("\nPlease fix the critical failures before starting the system.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Health check execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 