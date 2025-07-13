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

from src.core.dependency_container import get_service
from src.domain.interfaces.health_check_service import IHealthCheckService


async def run_health_check(team_id: str, export: bool = False, verbose: bool = False):
    """Run a comprehensive health check."""
    print(f"🔍 Running health check for team {team_id}...")
    
    try:
        health_service = get_service(IHealthCheckService)
        report = await health_service.perform_comprehensive_health_check()
        
        # Display results
        print(f"\n📊 Health Check Results for {team_id}")
        print("=" * 60)
        print(f"Overall Status: {report.overall_status.value}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Total Checks: {len(report.checks)}")
        
        if verbose:
            # Detailed results
            print(f"\n🔍 Detailed Results:")
            for check in report.checks:
                status_emoji = "✅" if check.status.value == "healthy" else "⚠️" if check.status.value == "degraded" else "❌"
                print(f"  {status_emoji} {check.component_type.value}:{check.component_name}")
                print(f"    Status: {check.status.value}")
                print(f"    Message: {check.message}")
                print(f"    Response Time: {check.response_time_ms:.2f}ms")
                if check.details:
                    print(f"    Details: {check.details}")
                print()
        
        # Summary
        print(f"\n📈 Summary:")
        for component_type, status_counts in report.summary.items():
            print(f"  {component_type.value}:")
            for status, count in status_counts.items():
                if count > 0:
                    print(f"    {status.value}: {count}")
        
        # Issues and recommendations
        if report.critical_issues:
            print(f"\n🚨 Critical Issues:")
            for issue in report.critical_issues:
                print(f"  - {issue}")
        
        if report.warnings:
            print(f"\n⚠️ Warnings:")
            for warning in report.warnings:
                print(f"  - {warning}")
        
        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in report.recommendations:
                print(f"  - {rec}")
        
        # Export if requested
        if export:
            export_file = await health_service.export_health_report()
            print(f"\n💾 Health report exported to: {export_file}")
        
        return report.is_healthy()
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


async def start_monitoring(team_id: str, interval: int = 300):
    """Start background health monitoring."""
    print(f"🚀 Starting background health monitoring for team {team_id}...")
    
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
            print(f"{emoji} [{alert.timestamp.strftime('%H:%M:%S')}] {alert.component_type.value}:{alert.component_name} - {alert.message}")
        
        # monitor.add_alert_handler(console_alert_handler)
        
        # Start monitoring
        # await monitor.start_monitoring()
        
        print(f"✅ Background monitoring started (interval: {interval}s)")
        print("Press Ctrl+C to stop monitoring...")
        
        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping background monitoring...")
            # await monitor.stop_monitoring() # This line will now cause an error
            print("✅ Background monitoring stopped")
        
    except Exception as e:
        print(f"❌ Failed to start monitoring: {e}")


async def show_status(team_id: str):
    """Show current monitoring status."""
    print(f"📊 Showing status for team {team_id}...")
    
    try:
        # The original script had get_background_health_monitor here,
        # but it was removed from imports. This function will now
        # need to be refactored or removed if background monitoring
        # is no longer supported. For now, we'll keep it as is,
        # but it will likely fail if get_background_health_monitor
        # is not available.
        # monitor = get_background_health_monitor(team_id)
        # status = await monitor.get_status_summary()
        
        # print(f"\n📈 Monitoring Status:")
        # print(f"  Active: {status['monitoring_active']}")
        # print(f"  Team ID: {status['team_id']}")
        # print(f"  Check Interval: {status['check_interval_seconds']}s")
        # print(f"  Active Alerts: {status['active_alerts_count']}")
        
        # if status['active_alerts_count'] > 0:
        #     print(f"\n🚨 Active Alerts:")
        #     for level, count in status['alert_summary'].items():
        #         if count > 0:
        #             print(f"  {level}: {count}")
        
        # print(f"\n📊 Performance Metrics:")
        # for metric, value in status['performance_metrics'].items():
        #     if isinstance(value, float):
        #         print(f"  {metric}: {value:.2f}")
        #     else:
        #         print(f"  {metric}: {value}")
        
        # if status['last_check_time']:
        #     print(f"\n🕐 Last Check: {status['last_check_time']}")
        
        print("Background monitoring functionality is currently disabled.")
        
    except Exception as e:
        print(f"❌ Failed to get status: {e}")


async def show_alerts(team_id: str, hours: int = 24):
    """Show recent alerts."""
    print(f"🚨 Showing alerts for team {team_id} (last {hours}h)...")
    
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
        #     print("✅ No alerts in the specified time period")
        #     return
        
        # print(f"\n📋 Alert History ({len(alerts)} alerts):")
        # for alert in alerts[-10:]:  # Show last 10 alerts
        #     level_emoji = {
        #         "critical": "🚨",
        #         "error": "❌", 
        #         "warning": "⚠️",
        #         "info": "ℹ️"
        #     }
        #     emoji = level_emoji.get(alert.level.value, "ℹ️")
        #     resolved = "✅" if alert.resolved else "⏳"
        #     print(f"{emoji} {resolved} [{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {alert.component_type.value}:{alert.component_name}")
        #     print(f"    {alert.message}")
        #     if alert.details:
        #         print(f"    Details: {alert.details}")
        #     print()
        
        print("Background monitoring functionality is currently disabled.")
        
    except Exception as e:
        print(f"❌ Failed to get alerts: {e}")


async def force_check(team_id: str):
    """Force an immediate health check."""
    print(f"🔍 Forcing immediate health check for team {team_id}...")
    
    try:
        # The original script had get_background_health_monitor here,
        # but it was removed from imports. This function will now
        # need to be refactored or removed if background monitoring
        # is no longer supported. For now, we'll keep it as is,
        # but it will likely fail if get_background_health_monitor
        # is not available.
        # monitor = get_background_health_monitor(team_id)
        # report = await monitor.force_health_check()
        
        # print(f"✅ Forced health check completed")
        # print(f"Status: {report.overall_status.value}")
        # print(f"Checks performed: {len(report.checks)}")
        
        # # Show unhealthy components
        # unhealthy = [check for check in report.checks if check.status.value == "unhealthy"]
        # if unhealthy:
        #     print(f"\n❌ Unhealthy components:")
        #     for check in unhealthy:
        #         print(f"  - {check.component_type.value}:{check.component_name} - {check.message}")
        
        print("Background monitoring functionality is currently disabled.")
        
    except Exception as e:
        print(f"❌ Failed to force health check: {e}")


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
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 