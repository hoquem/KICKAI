#!/usr/bin/env python3
"""
KICKAI Monitoring Dashboard
Real-time monitoring dashboard for all environments
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import queue
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceMetrics:
    """Service metrics data class"""
    service: str
    environment: str
    url: str
    is_healthy: bool
    response_time: float
    status_code: int
    last_check: datetime
    uptime_percentage: float
    error_count: int
    total_checks: int

@dataclass
class DashboardData:
    """Dashboard data class"""
    timestamp: datetime
    services: List[ServiceMetrics]
    overall_health: float
    alerts: List[str]
    recommendations: List[str]

class MonitoringDashboard:
    """Real-time monitoring dashboard for KICKAI services"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.services = {
            'kickai-testing': {
                'environment': 'testing',
                'url': os.getenv('TESTING_URL', 'https://kickai-testing.railway.app'),
                'timeout': 10,
                'critical': False
            },
            'kickai-staging': {
                'environment': 'staging',
                'url': os.getenv('STAGING_URL', 'https://kickai-staging.railway.app'),
                'timeout': 15,
                'critical': False
            },
            'kickai-production': {
                'environment': 'production',
                'url': os.getenv('PRODUCTION_URL', 'https://kickai-production.railway.app'),
                'timeout': 20,
                'critical': True
            }
        }
        
        # Metrics storage
        self.metrics_history = defaultdict(lambda: deque(maxlen=100))
        self.current_metrics = {}
        self.alerts = deque(maxlen=50)
        self.is_running = False
        
        # Threading
        self.metrics_queue = queue.Queue()
        self.stop_event = threading.Event()
    
    async def check_service(self, service_name: str, config: dict) -> ServiceMetrics:
        """Check a single service and return metrics"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{config['url']}/health",
                    timeout=aiohttp.ClientTimeout(total=config['timeout']),
                    headers={'User-Agent': 'KICKAI-Monitor/1.0'}
                ) as response:
                    response_time = time.time() - start_time
                    
                    is_healthy = response.status == 200
                    status_code = response.status
                    
                    # Calculate uptime percentage
                    history = self.metrics_history[service_name]
                    total_checks = len(history) + 1
                    healthy_checks = sum(1 for m in history if m.is_healthy) + (1 if is_healthy else 0)
                    uptime_percentage = (healthy_checks / total_checks) * 100
                    
                    # Calculate error count
                    error_count = sum(1 for m in history if not m.is_healthy)
                    
                    metrics = ServiceMetrics(
                        service=service_name,
                        environment=config['environment'],
                        url=config['url'],
                        is_healthy=is_healthy,
                        response_time=response_time,
                        status_code=status_code,
                        last_check=datetime.now(),
                        uptime_percentage=uptime_percentage,
                        error_count=error_count,
                        total_checks=total_checks
                    )
                    
                    # Store in history
                    self.metrics_history[service_name].append(metrics)
                    self.current_metrics[service_name] = metrics
                    
                    # Check for alerts
                    await self.check_alerts(metrics)
                    
                    return metrics
                    
        except asyncio.TimeoutError:
            return await self.handle_service_error(service_name, config, "Timeout")
        except Exception as e:
            return await self.handle_service_error(service_name, config, str(e))
    
    async def handle_service_error(self, service_name: str, config: dict, error: str) -> ServiceMetrics:
        """Handle service errors and create metrics"""
        history = self.metrics_history[service_name]
        total_checks = len(history) + 1
        healthy_checks = sum(1 for m in history if m.is_healthy)
        uptime_percentage = (healthy_checks / total_checks) * 100
        error_count = sum(1 for m in history if not m.is_healthy) + 1
        
        metrics = ServiceMetrics(
            service=service_name,
            environment=config['environment'],
            url=config['url'],
            is_healthy=False,
            response_time=config['timeout'],
            status_code=0,
            last_check=datetime.now(),
            uptime_percentage=uptime_percentage,
            error_count=error_count,
            total_checks=total_checks
        )
        
        self.metrics_history[service_name].append(metrics)
        self.current_metrics[service_name] = metrics
        
        await self.check_alerts(metrics)
        return metrics
    
    async def check_alerts(self, metrics: ServiceMetrics):
        """Check for alert conditions"""
        alerts = []
        
        # Critical service down
        if not metrics.is_healthy and self.services[metrics.service]['critical']:
            alerts.append(f"🚨 CRITICAL: {metrics.service} is down!")
        
        # High response time
        if metrics.response_time > 5.0:
            alerts.append(f"⚠️ SLOW: {metrics.service} response time {metrics.response_time:.2f}s")
        
        # Low uptime
        if metrics.uptime_percentage < 95.0:
            alerts.append(f"📉 UPTIME: {metrics.service} uptime {metrics.uptime_percentage:.1f}%")
        
        # Multiple consecutive errors
        if metrics.error_count >= 3:
            alerts.append(f"🔴 ERRORS: {metrics.service} has {metrics.error_count} recent errors")
        
        # Add alerts to queue
        for alert in alerts:
            self.alerts.append({
                'timestamp': datetime.now(),
                'service': metrics.service,
                'message': alert,
                'severity': 'critical' if '🚨' in alert else 'warning'
            })
    
    async def monitor_services(self):
        """Continuous monitoring loop"""
        while not self.stop_event.is_set():
            try:
                tasks = []
                for service_name, config in self.services.items():
                    task = self.check_service(service_name, config)
                    tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(5)
    
    def get_dashboard_data(self) -> DashboardData:
        """Get current dashboard data"""
        services = list(self.current_metrics.values())
        
        # Calculate overall health
        if services:
            healthy_services = sum(1 for s in services if s.is_healthy)
            overall_health = (healthy_services / len(services)) * 100
        else:
            overall_health = 0.0
        
        # Get recent alerts
        recent_alerts = []
        for alert in list(self.alerts)[-10:]:  # Last 10 alerts
            recent_alerts.append(f"{alert['timestamp'].strftime('%H:%M:%S')} - {alert['message']}")
        
        # Generate recommendations
        recommendations = self.generate_recommendations(services)
        
        return DashboardData(
            timestamp=datetime.now(),
            services=services,
            overall_health=overall_health,
            alerts=recent_alerts,
            recommendations=recommendations
        )
    
    def generate_recommendations(self, services: List[ServiceMetrics]) -> List[str]:
        """Generate recommendations based on current metrics"""
        recommendations = []
        
        # Check for unhealthy services
        unhealthy_services = [s for s in services if not s.is_healthy]
        if unhealthy_services:
            recommendations.append(f"🔧 Investigate {len(unhealthy_services)} unhealthy services")
        
        # Check for slow services
        slow_services = [s for s in services if s.response_time > 3.0]
        if slow_services:
            recommendations.append(f"⚡ Optimize performance for {len(slow_services)} slow services")
        
        # Check for low uptime
        low_uptime_services = [s for s in services if s.uptime_percentage < 99.0]
        if low_uptime_services:
            recommendations.append(f"📈 Improve reliability for {len(low_uptime_services)} services")
        
        # Check for critical services
        critical_services = [s for s in services if self.services[s.service]['critical'] and not s.is_healthy]
        if critical_services:
            recommendations.append("🚨 IMMEDIATE ACTION: Critical services are down")
        
        if not recommendations:
            recommendations.append("✅ All systems operating normally")
        
        return recommendations
    
    def print_dashboard(self):
        """Print formatted dashboard"""
        data = self.get_dashboard_data()
        
        # Clear screen (works on most terminals)
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("=" * 80)
        print("🏥 KICKAI MONITORING DASHBOARD")
        print("=" * 80)
        print(f"Last Updated: {data.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Overall Health: {data.overall_health:.1f}%")
        print(f"Monitoring {len(data.services)} services")
        print()
        
        # Services status
        print("📊 SERVICES STATUS:")
        print("-" * 80)
        
        # Group by environment
        environments = defaultdict(list)
        for service in data.services:
            environments[service.environment].append(service)
        
        for environment in ['testing', 'staging', 'production']:
            if environment in environments:
                print(f"\n🌍 {environment.upper()} ENVIRONMENT:")
                print("-" * 40)
                
                for service in environments[environment]:
                    icon = "✅" if service.is_healthy else "❌"
                    critical = "🚨" if self.services[service.service]['critical'] else ""
                    
                    print(f"{icon} {critical} {service.service}")
                    print(f"   URL: {service.url}")
                    print(f"   Status: {service.status_code if service.status_code > 0 else 'ERROR'}")
                    print(f"   Response Time: {service.response_time:.2f}s")
                    print(f"   Uptime: {service.uptime_percentage:.1f}%")
                    print(f"   Last Check: {service.last_check.strftime('%H:%M:%S')}")
                    print()
        
        # Alerts
        if data.alerts:
            print("🚨 RECENT ALERTS:")
            print("-" * 80)
            for alert in data.alerts:
                print(f"   {alert}")
            print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print("-" * 80)
        for rec in data.recommendations:
            print(f"   {rec}")
        
        print("\n" + "=" * 80)
        print("Press Ctrl+C to stop monitoring")
    
    def save_metrics(self, filename: str = None):
        """Save current metrics to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"metrics_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'services': [asdict(service) for service in self.current_metrics.values()],
            'overall_health': self.get_dashboard_data().overall_health
        }
        
        # Convert datetime objects
        for service in data['services']:
            service['last_check'] = service['last_check'].isoformat()
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Metrics saved to {filename}")
    
    async def start_monitoring(self):
        """Start the monitoring dashboard"""
        self.is_running = True
        print("🚀 Starting KICKAI Monitoring Dashboard...")
        print(f"📡 Monitoring {len(self.services)} services every {self.check_interval} seconds")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            # Start monitoring in background
            monitor_task = asyncio.create_task(self.monitor_services())
            
            # Main dashboard loop
            while self.is_running:
                self.print_dashboard()
                await asyncio.sleep(5)  # Update dashboard every 5 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitoring...")
            self.is_running = False
            self.stop_event.set()
            monitor_task.cancel()
            
            # Final save
            self.save_metrics()
            print("✅ Monitoring stopped. Final metrics saved.")

def run_simple_monitor():
    """Simple monitoring without async"""
    print("📊 Simple KICKAI Monitor")
    print("=" * 50)
    
    services = {
        'kickai-testing': 'https://kickai-testing.railway.app',
        'kickai-staging': 'https://kickai-staging.railway.app',
        'kickai-production': 'https://kickai-production.railway.app'
    }
    
    while True:
        try:
            print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - Checking services...")
            
            for service_name, url in services.items():
                try:
                    start_time = time.time()
                    response = requests.get(f"{url}/health", timeout=10)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        print(f"✅ {service_name}: {response_time:.2f}s")
                    else:
                        print(f"❌ {service_name}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {service_name}: {str(e)[:50]}")
            
            print("\n" + "-" * 50)
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping simple monitor...")
            break

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KICKAI Monitoring Dashboard')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--simple', action='store_true', help='Run simple monitoring')
    parser.add_argument('--save', type=str, help='Save metrics to file')
    
    args = parser.parse_args()
    
    if args.simple:
        run_simple_monitor()
    else:
        dashboard = MonitoringDashboard(check_interval=args.interval)
        await dashboard.start_monitoring()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        sys.exit(1) 