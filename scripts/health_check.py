#!/usr/bin/env python3
"""
KICKAI Health Check Script
Monitors the health of deployed KICKAI instances
"""

import os
import sys
import time
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class HealthCheckResult:
    """Health check result data structure."""
    timestamp: datetime
    url: str
    status: str
    response_time: float
    error: Optional[str] = None
    metrics: Optional[Dict] = None

class HealthChecker:
    """Health checker for KICKAI deployments."""
    
    def __init__(self, urls: List[str], timeout: int = 30):
        self.urls = urls
        self.timeout = timeout
        self.results: List[HealthCheckResult] = []
    
    def check_health(self, url: str) -> HealthCheckResult:
        """Check health of a single URL."""
        start_time = time.time()
        
        try:
            # Check health endpoint
            health_response = requests.get(
                f"{url}/health",
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                status = "healthy" if health_data.get('status') == 'healthy' else "unhealthy"
                
                # Get metrics if available
                metrics = None
                try:
                    metrics_response = requests.get(
                        f"{url}/metrics",
                        timeout=self.timeout
                    )
                    if metrics_response.status_code == 200:
                        metrics = metrics_response.json()
                except Exception as e:
                    logger.warning(f"Could not fetch metrics from {url}: {e}")
                
                return HealthCheckResult(
                    timestamp=datetime.now(),
                    url=url,
                    status=status,
                    response_time=response_time,
                    metrics=metrics
                )
            else:
                return HealthCheckResult(
                    timestamp=datetime.now(),
                    url=url,
                    status="error",
                    response_time=response_time,
                    error=f"HTTP {health_response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            return HealthCheckResult(
                timestamp=datetime.now(),
                url=url,
                status="timeout",
                response_time=time.time() - start_time,
                error="Request timeout"
            )
        except requests.exceptions.ConnectionError:
            return HealthCheckResult(
                timestamp=datetime.now(),
                url=url,
                status="connection_error",
                response_time=time.time() - start_time,
                error="Connection error"
            )
        except Exception as e:
            return HealthCheckResult(
                timestamp=datetime.now(),
                url=url,
                status="error",
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def check_all(self) -> List[HealthCheckResult]:
        """Check health of all URLs."""
        results = []
        
        for url in self.urls:
            logger.info(f"Checking health of {url}")
            result = self.check_health(url)
            results.append(result)
            self.results.append(result)
            
            # Print result
            if result.status == "healthy":
                logger.info(f"✅ {url} is healthy (response time: {result.response_time:.2f}s)")
            else:
                logger.error(f"❌ {url} is {result.status}: {result.error}")
        
        return results
    
    def get_summary(self) -> Dict:
        """Get summary of health check results."""
        if not self.results:
            return {"message": "No health checks performed"}
        
        total = len(self.results)
        healthy = len([r for r in self.results if r.status == "healthy"])
        unhealthy = total - healthy
        
        avg_response_time = sum(r.response_time for r in self.results) / total
        
        return {
            "total_checks": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "success_rate": healthy / total if total > 0 else 0,
            "avg_response_time": avg_response_time,
            "last_check": max(r.timestamp for r in self.results).isoformat()
        }
    
    def print_summary(self):
        """Print health check summary."""
        summary = self.get_summary()
        
        print("\n🏥 Health Check Summary")
        print("======================")
        print(f"Total checks: {summary['total_checks']}")
        print(f"Healthy: {summary['healthy']}")
        print(f"Unhealthy: {summary['unhealthy']}")
        print(f"Success rate: {summary['success_rate']:.1%}")
        print(f"Average response time: {summary['avg_response_time']:.2f}s")
        print(f"Last check: {summary['last_check']}")
        
        # Print detailed results
        print("\n📊 Detailed Results:")
        for result in self.results:
            status_icon = "✅" if result.status == "healthy" else "❌"
            print(f"{status_icon} {result.url}")
            print(f"   Status: {result.status}")
            print(f"   Response time: {result.response_time:.2f}s")
            if result.error:
                print(f"   Error: {result.error}")
            if result.metrics:
                print(f"   Bot status: {result.metrics.get('application', {}).get('bot_status', 'unknown')}")
            print()

def load_urls_from_env() -> List[str]:
    """Load URLs from environment variables."""
    urls = []
    
    # Check for testing URL
    if os.getenv('KICKAI_TESTING_URL'):
        urls.append(os.getenv('KICKAI_TESTING_URL'))
    
    # Check for production URL
    if os.getenv('KICKAI_PRODUCTION_URL'):
        urls.append(os.getenv('KICKAI_PRODUCTION_URL'))
    
    # If no URLs found, use default
    if not urls:
        urls.append('http://localhost:5000')
    
    return urls

def main():
    """Main health check function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='KICKAI Health Checker')
    parser.add_argument('--urls', nargs='+', help='URLs to check')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds (for continuous mode)')
    
    args = parser.parse_args()
    
    # Get URLs
    if args.urls:
        urls = args.urls
    else:
        urls = load_urls_from_env()
    
    if not urls:
        logger.error("No URLs specified")
        sys.exit(1)
    
    # Create health checker
    checker = HealthChecker(urls, timeout=args.timeout)
    
    print("🏥 KICKAI Health Checker")
    print("=======================")
    print(f"Checking URLs: {', '.join(urls)}")
    print(f"Timeout: {args.timeout}s")
    
    if args.continuous:
        print(f"Continuous mode: checking every {args.interval}s")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                checker.check_all()
                checker.print_summary()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n🛑 Health checking stopped")
    else:
        # Single check
        checker.check_all()
        checker.print_summary()

if __name__ == "__main__":
    main() 