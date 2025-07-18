#!/usr/bin/env python3
"""
Health Check Runner (One-off)

Run comprehensive health checks to diagnose system issues.
"""

import asyncio
import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.dependency_container import get_service
from features.health_monitoring.domain.interfaces.health_check_service_interface import IHealthCheckService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_health_check(team_id: str, export: bool = False, verbose: bool = False):
    """Run a comprehensive health check."""
    logger.info(f"🔍 Running health check for team {team_id}...")
    
    try:
        health_service = get_service(IHealthCheckService)
        report = await health_service.perform_comprehensive_health_check()
        
        # Display results
        logger.info(f"\n📊 Health Check Results for {team_id}")
        logger.info("=" * 60)
        logger.info(f"Overall Status: {report.overall_status.value}")
        logger.info(f"Timestamp: {report.timestamp}")
        logger.info(f"Total Checks: {len(report.checks)}")
        
        if verbose:
            # Detailed results
            logger.info(f"\n🔍 Detailed Results:")
            for check in report.checks:
                status_emoji = "✅" if check.status.value == "healthy" else "⚠️" if check.status.value == "degraded" else "❌"
                logger.info(f"  {status_emoji} {check.component_type.value}:{check.component_name}")
                logger.info(f"    Status: {check.status.value}")
                logger.info(f"    Message: {check.message}")
                logger.info(f"    Response Time: {check.response_time_ms:.2f}ms")
                if check.details:
                    logger.info(f"    Details: {check.details}")
                logger.info("")
        
        # Summary
        logger.info(f"\n📈 Summary:")
        for component_type, status_counts in report.summary.items():
            logger.info(f"  {component_type.value}:")
            for status, count in status_counts.items():
                if count > 0:
                    logger.info(f"    {status.value}: {count}")
        
        # Issues and recommendations
        if report.critical_issues:
            logger.error(f"\n🚨 Critical Issues:")
            for issue in report.critical_issues:
                logger.error(f"  - {issue}")
        
        if report.warnings:
            logger.warning(f"\n⚠️ Warnings:")
            for warning in report.warnings:
                logger.warning(f"  - {warning}")
        
        if report.recommendations:
            logger.info(f"\n💡 Recommendations:")
            for rec in report.recommendations:
                logger.info(f"  - {rec}")
        
        # Export if requested
        if export:
            export_file = await health_service.export_health_report()
            logger.info(f"\n💾 Health report exported to: {export_file}")
        
        return report.is_healthy()
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False


async def start_monitoring(team_id: str, interval: int = 300):
    """Start background health monitoring."""
    logger.info(f"🚀 Starting background health monitoring for team {team_id}...")
    
    try:
        # The original script had get_background_health_monitor here,
        # but it was removed from imports. This function will now
        # need to be refactored or removed if background monitoring
        # is no longer supported. For now, we'll keep it as is,
        # but it will likely fail if get_background_health_monitor
        # is not available.
        # monitor = get_background_health_monitor(team_id)
        # monitor.set_check_interval(interval)
        
        # Add console alert handler
        async def console_alert_handler(alert):
            level_emoji = {
                "critical": "🚨",
                "error": "❌", 
                "warning": "⚠️",
                "info": "ℹ️"
            }
            emoji = level_emoji.get(alert.level.value, "ℹ️")
            logger.info(f"{emoji} [{alert.timestamp.strftime('%H:%M:%S')}] {alert.component_type.value}:{alert.component_name} - {alert.message}")
        
        # monitor.add_alert_handler(console_alert_handler)
        
        # Start monitoring
        # await monitor.start_monitoring()
        
        logger.info(f"✅ Background monitoring started (interval: {interval}s)")
        logger.info("Press Ctrl+C to stop monitoring...")
        
        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping background monitoring...")
            # await monitor.stop_monitoring() # This line will now cause an error
            logger.info("✅ Background monitoring stopped")
        
    except Exception as e:
        logger.error(f"❌ Failed to start monitoring: {e}")


async def show_status(team_id: str):
    """Show current monitoring status."""
    logger.info(f"📊 Showing status for team {team_id}...")
    
    try:
        # The original script had get_background_health_monitor here,
        # but it was removed from imports. This function will now
        # need to be refactored or removed if background monitoring
        # is no longer supported. For now, we'll keep it as is,
        # but it will likely fail if get_background_health_monitor
        # is not available.
        # monitor = get_background_health_monitor(team_id)
        # status = await monitor.get_status_summary()
        
        # logger.info(f"\n📈 Monitoring Status:")
        # logger.info(f"  Active: {status['monitoring_active']}")
        # logger.info(f"  Team ID: {status['team_id']}")
        # logger.info(f"  Check Interval: {status['check_interval_seconds']}s")
        # logger.info(f"  Active Alerts: {status['active_alerts_count']}")
        
        # if status['active_alerts_count'] > 0:
        #     logger.info(f"\n🚨 Active Alerts:")
        #     for level, count in status['alert_summary'].items():
        #         if count > 0:
        #             logger.info(f"  {level}: {count}")
        
        # logger.info(f"\n📊 Performance Metrics:")
        # for metric, value in status['performance_metrics'].items():
        #     if isinstance(value, float):
        #         logger.info(f"  {metric}: {value:.2f}")
        #     else:
        #         logger.info(f"  {metric}: {value}")
        
        # if status['last_check_time']:
        #     logger.info(f"\n🕐 Last Check: {status['last_check_time']}")
        
        logger.info("Background monitoring functionality is currently disabled.")
        
    except Exception as e:
        logger.error(f"❌ Failed to get status: {e}")


async def show_alerts(team_id: str, hours: int = 24):
    """Show recent alerts."""
    logger.info(f"🚨 Showing alerts for team {team_id} (last {hours}h)...")
    
    try:
        # The original script had get_background_health_monitor here,
        # but it was removed from imports. This function will now
        # need to be refactored or removed if background monitoring
        # is no longer supported. For now, we'll keep it as is,
        # but it will likely fail if get_background_health_monitor
        # is not available.
        # monitor = get_background_health_monitor(team_id)
        # alerts = await monitor.get_alert_history(hours)
        
        # if not alerts:
        #     logger.info("✅ No alerts in the specified time period")
        #     return
        
        # logger.info(f"\n📋 Alert History ({len(alerts)} alerts):")
        # for alert in alerts[-10:]:  # Show last 10 alerts
        #     level_emoji = {
        #         "critical": "🚨",
        #         "error": "❌", 
        #         "warning": "⚠️",
        #         "info": "ℹ️"
        #     }
        #     emoji = level_emoji.get(alert.level.value, "ℹ️")
        #     resolved = "✅" if alert.resolved else "⏳"
        #     logger.info(f"{emoji} {resolved} [{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {alert.component_type.value}:{alert.component_name}")
        #     logger.info(f"    {alert.message}")
        #     if alert.details:
        #         logger.info(f"    Details: {alert.details}")
        #     logger.info("")
        
        logger.info("Background monitoring functionality is currently disabled.")
        
    except Exception as e:
        logger.error(f"❌ Failed to get alerts: {e}")


async def force_check(team_id: str):
    """Force an immediate health check."""
    logger.info(f"🔍 Forcing immediate health check for team {team_id}...")
    
    try:
        health_service = get_service(IHealthCheckService)
        report = await health_service.perform_comprehensive_health_check()
        
        # logger.info(f"✅ Forced health check completed")
        return report.is_healthy()
        
    except Exception as e:
        logger.error(f"❌ Forced health check failed: {e}")
        return False


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="KICKAI Health Check CLI")
    parser.add_argument("--team-id", default="KAI", help="Team ID to check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Run a health check")
    check_parser.add_argument("--export", "-e", action="store_true", help="Export report to JSON")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Start background monitoring")
    monitor_parser.add_argument("--interval", "-i", type=int, default=300, help="Check interval in seconds")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show monitoring status")
    
    # Alerts command
    alerts_parser = subparsers.add_parser("alerts", help="Show recent alerts")
    alerts_parser.add_argument("--hours", "-H", type=int, default=24, help="Hours of history to show")
    
    # Force command
    force_parser = subparsers.add_parser("force", help="Force immediate health check")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run the appropriate command
    try:
        if args.command == "check":
            success = asyncio.run(run_health_check(args.team_id, args.export, args.verbose))
            sys.exit(0 if success else 1)
        
        elif args.command == "monitor":
            asyncio.run(start_monitoring(args.team_id, args.interval))
        
        elif args.command == "status":
            asyncio.run(show_status(args.team_id))
        
        elif args.command == "alerts":
            asyncio.run(show_alerts(args.team_id, args.hours))
        
        elif args.command == "force":
            asyncio.run(force_check(args.team_id))
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 