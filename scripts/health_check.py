#!/usr/bin/env python3
"""
KICKAI Health Check Script
Comprehensive health monitoring for all environments
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import aiohttp
import requests
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_check.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    """Health status data class"""
    service: str
    environment: str
    url: str
    status: str
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None
    is_healthy: bool = False

@dataclass
class HealthReport:
    """Health report data class"""
    timestamp: datetime
    total_services: int
    healthy_services: int
    unhealthy_services: int
    services: List[HealthStatus]
    summary: str

class HealthChecker:
    """Comprehensive health checker for KICKAI services"""
    
    def __init__(self):
        self.services = {
            'kickai-testing': {
                'environment': 'testing',
                'url': os.getenv('TESTING_URL', 'https://kickai-testing.railway.app'),
                'timeout': 10,
                'retries': 3
            },
            'kickai-staging': {
                'environment': 'staging',
                'url': os.getenv('STAGING_URL', 'https://kickai-staging.railway.app'),
                'timeout': 15,
                'retries': 3
            },
            'kickai-production': {
                'environment': 'production',
                'url': os.getenv('PRODUCTION_URL', 'https://kickai-production.railway.app'),
                'timeout': 20,
                'retries': 5
            }
        }
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def check_service_health(self, service_name: str, config: dict) -> HealthStatus:
        """Check health of a single service"""
        start_time = time.time()
        url = config['url']
        timeout = config['timeout']
        retries = config['retries']
        
        logger.info(f"Checking health for {service_name} at {url}")
        
        # Try multiple endpoints
        endpoints = ['/health', '/status', '/']
        health_status = None
        
        for endpoint in endpoints:
            full_url = f"{url.rstrip('/')}{endpoint}"
            
            for attempt in range(retries):
                try:
                    async with self.session.get(
                        full_url,
                        timeout=aiohttp.ClientTimeout(total=timeout),
                        headers={'User-Agent': 'KICKAI-HealthChecker/1.0'}
                    ) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            # Try to parse JSON response
                            try:
                                data = await response.json()
                                if isinstance(data, dict) and data.get('status') == 'healthy':
                                    health_status = HealthStatus(
                                        service=service_name,
                                        environment=config['environment'],
                                        url=url,
                                        status='healthy',
                                        response_time=response_time,
                                        last_check=datetime.now(),
                                        is_healthy=True
                                    )
                                    logger.info(f"✅ {service_name} is healthy (endpoint: {endpoint})")
                                    return health_status
                            except:
                                # If not JSON, check if it's a simple OK response
                                text = await response.text()
                                if 'ok' in text.lower() or 'healthy' in text.lower():
                                    health_status = HealthStatus(
                                        service=service_name,
                                        environment=config['environment'],
                                        url=url,
                                        status='healthy',
                                        response_time=response_time,
                                        last_check=datetime.now(),
                                        is_healthy=True
                                    )
                                    logger.info(f"✅ {service_name} is healthy (endpoint: {endpoint})")
                                    return health_status
                        
                        elif response.status == 404 and endpoint != '/':
                            # Endpoint doesn't exist, try next one
                            break
                        else:
                            logger.warning(f"⚠️ {service_name} returned status {response.status} for {endpoint}")
                            
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ {service_name} timeout on attempt {attempt + 1}/{retries} for {endpoint}")
                    if attempt == retries - 1:
                        health_status = HealthStatus(
                            service=service_name,
                            environment=config['environment'],
                            url=url,
                            status='timeout',
                            response_time=time.time() - start_time,
                            last_check=datetime.now(),
                            error_message=f"Timeout after {timeout}s",
                            is_healthy=False
                        )
                except Exception as e:
                    logger.warning(f"❌ {service_name} error on attempt {attempt + 1}/{retries} for {endpoint}: {e}")
                    if attempt == retries - 1:
                        health_status = HealthStatus(
                            service=service_name,
                            environment=config['environment'],
                            url=url,
                            status='error',
                            response_time=time.time() - start_time,
                            last_check=datetime.now(),
                            error_message=str(e),
                            is_healthy=False
                        )
                
                if attempt < retries - 1:
                    await asyncio.sleep(1)  # Brief delay between retries
        
        # If no endpoint worked, return the last error status
        if health_status is None:
            health_status = HealthStatus(
                service=service_name,
                environment=config['environment'],
                url=url,
                status='unreachable',
                response_time=time.time() - start_time,
                last_check=datetime.now(),
                error_message="All endpoints failed",
                is_healthy=False
            )
        
        logger.error(f"❌ {service_name} is unhealthy: {health_status.status}")
        return health_status
    
    async def check_all_services(self) -> List[HealthStatus]:
        """Check health of all services concurrently"""
        tasks = []
        for service_name, config in self.services.items():
            task = self.check_service_health(service_name, config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        health_statuses = []
        for i, result in enumerate(results):
            service_name = list(self.services.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"Exception checking {service_name}: {result}")
                health_statuses.append(HealthStatus(
                    service=service_name,
                    environment=self.services[service_name]['environment'],
                    url=self.services[service_name]['url'],
                    status='exception',
                    response_time=0.0,
                    last_check=datetime.now(),
                    error_message=str(result),
                    is_healthy=False
                ))
            else:
                health_statuses.append(result)
        
        return health_statuses
    
    def generate_report(self, health_statuses: List[HealthStatus]) -> HealthReport:
        """Generate a comprehensive health report"""
        total_services = len(health_statuses)
        healthy_services = sum(1 for status in health_statuses if status.is_healthy)
        unhealthy_services = total_services - healthy_services
        
        # Generate summary
        if unhealthy_services == 0:
            summary = f"🎉 All {total_services} services are healthy!"
        elif healthy_services == 0:
            summary = f"🚨 All {total_services} services are unhealthy!"
        else:
            summary = f"⚠️ {healthy_services}/{total_services} services are healthy"
        
        return HealthReport(
            timestamp=datetime.now(),
            total_services=total_services,
            healthy_services=healthy_services,
            unhealthy_services=unhealthy_services,
            services=health_statuses,
            summary=summary
        )
    
    def save_report(self, report: HealthReport, filename: str = None):
        """Save health report to file"""
        if filename is None:
            timestamp = report.timestamp.strftime('%Y%m%d_%H%M%S')
            filename = f"health_report_{timestamp}.json"
        
        # Convert to JSON-serializable format
        report_dict = asdict(report)
        report_dict['timestamp'] = report.timestamp.isoformat()
        for service in report_dict['services']:
            service['last_check'] = service['last_check'].isoformat()
        
        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        logger.info(f"Health report saved to {filename}")
    
    def print_report(self, report: HealthReport):
        """Print formatted health report"""
        print("\n" + "="*60)
        print("🏥 KICKAI HEALTH CHECK REPORT")
        print("="*60)
        print(f"Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Summary: {report.summary}")
        print(f"Total Services: {report.total_services}")
        print(f"Healthy: {report.healthy_services}")
        print(f"Unhealthy: {report.unhealthy_services}")
        print("\n" + "-"*60)
        
        # Group by environment
        environments = {}
        for status in report.services:
            env = status.environment
            if env not in environments:
                environments[env] = []
            environments[env].append(status)
        
        for environment in ['testing', 'staging', 'production']:
            if environment in environments:
                print(f"\n🌍 {environment.upper()} ENVIRONMENT:")
                print("-" * 40)
                
                for status in environments[environment]:
                    icon = "✅" if status.is_healthy else "❌"
                    print(f"{icon} {status.service}")
                    print(f"   URL: {status.url}")
                    print(f"   Status: {status.status}")
                    print(f"   Response Time: {status.response_time:.2f}s")
                    
                    if status.error_message:
                        print(f"   Error: {status.error_message}")
                    print()
        
        print("="*60)
    
    def check_historical_trends(self, hours: int = 24) -> Dict:
        """Check historical health trends"""
        # This would typically query a database or log files
        # For now, we'll return a simple structure
        return {
            "period_hours": hours,
            "total_checks": 0,
            "average_uptime": 0.0,
            "trend": "stable"
        }

async def main():
    """Main health check function"""
    print("🏥 Starting KICKAI Health Check...")
    
    async with HealthChecker() as checker:
        try:
            # Check all services
            health_statuses = await checker.check_all_services()
            
            # Generate report
            report = checker.generate_report(health_statuses)
            
            # Print report
            checker.print_report(report)
            
            # Save report
            checker.save_report(report)
            
            # Check historical trends
            trends = checker.check_historical_trends()
            print(f"\n📊 Historical Trends (last 24h):")
            print(f"   Average Uptime: {trends['average_uptime']:.1f}%")
            print(f"   Trend: {trends['trend']}")
            
            # Exit with appropriate code
            if report.unhealthy_services > 0:
                print(f"\n⚠️ {report.unhealthy_services} services are unhealthy")
                sys.exit(1)
            else:
                print(f"\n🎉 All services are healthy!")
                sys.exit(0)
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            print(f"❌ Health check failed: {e}")
            sys.exit(1)

def run_sync_health_check():
    """Synchronous health check for simple monitoring"""
    print("🏥 Running synchronous health check...")
    
    services = {
        'kickai-testing': 'https://kickai-testing.railway.app',
        'kickai-staging': 'https://kickai-staging.railway.app',
        'kickai-production': 'https://kickai-production.railway.app'
    }
    
    all_healthy = True
    
    for service_name, url in services.items():
        print(f"\n🔍 Checking {service_name}...")
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{url}/health",
                timeout=10,
                headers={'User-Agent': 'KICKAI-HealthChecker/1.0'}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ {service_name} is healthy ({response_time:.2f}s)")
            else:
                print(f"❌ {service_name} returned status {response.status_code}")
                all_healthy = False
                
        except requests.exceptions.Timeout:
            print(f"⏰ {service_name} timeout")
            all_healthy = False
        except Exception as e:
            print(f"❌ {service_name} error: {e}")
            all_healthy = False
    
    if all_healthy:
        print("\n🎉 All services are healthy!")
        return 0
    else:
        print("\n⚠️ Some services are unhealthy!")
        return 1

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='KICKAI Health Checker')
    parser.add_argument('--sync', action='store_true', help='Run synchronous health check')
    parser.add_argument('--hours', type=int, default=24, help='Hours for historical trends')
    parser.add_argument('--output', type=str, help='Output file for report')
    
    args = parser.parse_args()
    
    if args.sync:
        sys.exit(run_sync_health_check())
    else:
        asyncio.run(main()) 