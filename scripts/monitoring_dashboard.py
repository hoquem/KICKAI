#!/usr/bin/env python3
"""
KICKAI Monitoring Dashboard
Simple local dashboard to monitor deployed KICKAI instances
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import argparse

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^50}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*50}{Colors.END}")

def print_section(text: str):
    """Print a formatted section."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-' * len(text)}{Colors.END}")

def print_status(status: str, message: str):
    """Print a status message with color."""
    if status == "success":
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    elif status == "error":
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    elif status == "info":
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def get_health_data(url: str, timeout: int = 10) -> Optional[Dict]:
    """Get health data from a KICKAI deployment."""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        if response.status_code == 200:
            return response.json()
        else:
            print_status("error", f"Health check failed: HTTP {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        print_status("error", f"Health check timeout for {url}")
        return None
    except requests.exceptions.ConnectionError:
        print_status("error", f"Connection error for {url}")
        return None
    except Exception as e:
        print_status("error", f"Error checking {url}: {e}")
        return None

def get_metrics_data(url: str, timeout: int = 10) -> Optional[Dict]:
    """Get metrics data from a KICKAI deployment."""
    try:
        response = requests.get(f"{url}/metrics", timeout=timeout)
        if response.status_code == 200:
            return response.json()
        else:
            print_status("error", f"Metrics check failed: HTTP {response.status_code}")
            return None
    except Exception as e:
        print_status("error", f"Error getting metrics from {url}: {e}")
        return None

def format_uptime(seconds: float) -> str:
    """Format uptime in human readable format."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"

def display_health_summary(health_data: Dict):
    """Display health summary."""
    print_section("Health Summary")
    
    status = health_data.get('status', 'unknown')
    if status == 'healthy':
        print_status("success", f"Status: {status}")
    else:
        print_status("error", f"Status: {status}")
    
    uptime = health_data.get('uptime', 0)
    print(f"Uptime: {format_uptime(uptime)}")
    
    bot_status = health_data.get('bot_status', 'unknown')
    if bot_status == 'running':
        print_status("success", f"Bot Status: {bot_status}")
    else:
        print_status("warning", f"Bot Status: {bot_status}")
    
    environment = health_data.get('environment', 'unknown')
    print(f"Environment: {environment}")

def display_system_metrics(health_data: Dict):
    """Display system metrics."""
    print_section("System Metrics")
    
    system_metrics = health_data.get('system_metrics', {})
    if not system_metrics:
        print_status("warning", "No system metrics available")
        return
    
    cpu_percent = system_metrics.get('cpu_percent', 0)
    memory_percent = system_metrics.get('memory_percent', 0)
    disk_percent = system_metrics.get('disk_percent', 0)
    
    # CPU
    if cpu_percent < 50:
        print_status("success", f"CPU: {cpu_percent:.1f}%")
    elif cpu_percent < 80:
        print_status("warning", f"CPU: {cpu_percent:.1f}%")
    else:
        print_status("error", f"CPU: {cpu_percent:.1f}%")
    
    # Memory
    if memory_percent < 70:
        print_status("success", f"Memory: {memory_percent:.1f}%")
    elif memory_percent < 90:
        print_status("warning", f"Memory: {memory_percent:.1f}%")
    else:
        print_status("error", f"Memory: {memory_percent:.1f}%")
    
    # Disk
    if disk_percent < 80:
        print_status("success", f"Disk: {disk_percent:.1f}%")
    elif disk_percent < 95:
        print_status("warning", f"Disk: {disk_percent:.1f}%")
    else:
        print_status("error", f"Disk: {disk_percent:.1f}%")
    
    # Process count
    process_count = system_metrics.get('process_count', 0)
    print(f"Processes: {process_count}")

def display_app_metrics(health_data: Dict):
    """Display application metrics."""
    print_section("Application Metrics")
    
    app_metrics = health_data.get('app_metrics', {})
    if not app_metrics:
        print_status("warning", "No application metrics available")
        return
    
    commands_processed = app_metrics.get('commands_processed', 0)
    commands_failed = app_metrics.get('commands_failed', 0)
    avg_response_time = app_metrics.get('avg_response_time', 0)
    
    total_commands = commands_processed + commands_failed
    if total_commands > 0:
        success_rate = commands_processed / total_commands
        if success_rate > 0.95:
            print_status("success", f"Success Rate: {success_rate:.1%}")
        elif success_rate > 0.90:
            print_status("warning", f"Success Rate: {success_rate:.1%}")
        else:
            print_status("error", f"Success Rate: {success_rate:.1%}")
    else:
        print("Success Rate: No commands processed")
    
    print(f"Commands Processed: {commands_processed}")
    print(f"Commands Failed: {commands_failed}")
    
    if avg_response_time > 0:
        if avg_response_time < 2:
            print_status("success", f"Avg Response Time: {avg_response_time:.2f}s")
        elif avg_response_time < 5:
            print_status("warning", f"Avg Response Time: {avg_response_time:.2f}s")
        else:
            print_status("error", f"Avg Response Time: {avg_response_time:.2f}s")
    else:
        print("Avg Response Time: No data")

def display_detailed_metrics(metrics_data: Dict):
    """Display detailed metrics."""
    print_section("Detailed Metrics")
    
    if not metrics_data:
        print_status("warning", "No detailed metrics available")
        return
    
    # System metrics
    system = metrics_data.get('system', {})
    if system:
        print(f"System Metrics Timestamp: {datetime.fromtimestamp(system.get('timestamp', 0))}")
    
    # Application metrics
    application = metrics_data.get('application', {})
    if application:
        print(f"App Metrics Timestamp: {datetime.fromtimestamp(application.get('timestamp', 0))}")
    
    # AI Quality metrics
    ai_quality = metrics_data.get('ai_quality', {})
    if ai_quality:
        avg_quality = ai_quality.get('average_quality', 0)
        if avg_quality > 0:
            if avg_quality > 7:
                print_status("success", f"AI Quality: {avg_quality:.2f}/10")
            elif avg_quality > 5:
                print_status("warning", f"AI Quality: {avg_quality:.2f}/10")
            else:
                print_status("error", f"AI Quality: {avg_quality:.2f}/10")
        
        quality_dist = ai_quality.get('quality_distribution', {})
        if quality_dist:
            print("Quality Distribution:")
            for category, count in quality_dist.items():
                print(f"  {category.title()}: {count}")

def run_dashboard(urls: List[str], continuous: bool = False, interval: int = 60):
    """Run the monitoring dashboard."""
    while True:
        print_header("KICKAI Monitoring Dashboard")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for url in urls:
            print(f"\n{Colors.BOLD}Monitoring: {url}{Colors.END}")
            
            # Get health data
            health_data = get_health_data(url)
            if health_data:
                display_health_summary(health_data)
                display_system_metrics(health_data)
                display_app_metrics(health_data)
                
                # Get detailed metrics
                metrics_data = get_metrics_data(url)
                if metrics_data:
                    display_detailed_metrics(metrics_data)
            else:
                print_status("error", "Could not retrieve health data")
        
        if not continuous:
            break
        
        print(f"\n{Colors.YELLOW}Next update in {interval} seconds... (Press Ctrl+C to stop){Colors.END}")
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n{Colors.BLUE}Dashboard stopped by user{Colors.END}")
            break

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='KICKAI Monitoring Dashboard')
    parser.add_argument('--urls', nargs='+', help='URLs to monitor')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    parser.add_argument('--interval', type=int, default=60, help='Update interval in seconds')
    
    args = parser.parse_args()
    
    # Get URLs
    if args.urls:
        urls = args.urls
    else:
        # Try to get from environment
        urls = []
        if os.getenv('KICKAI_TESTING_URL'):
            urls.append(os.getenv('KICKAI_TESTING_URL'))
        if os.getenv('KICKAI_PRODUCTION_URL'):
            urls.append(os.getenv('KICKAI_PRODUCTION_URL'))
        
        if not urls:
            print_status("error", "No URLs specified. Use --urls or set environment variables.")
            sys.exit(1)
    
    print(f"Monitoring URLs: {', '.join(urls)}")
    
    try:
        run_dashboard(urls, args.continuous, args.interval)
    except KeyboardInterrupt:
        print(f"\n{Colors.BLUE}Dashboard stopped{Colors.END}")

if __name__ == "__main__":
    main() 