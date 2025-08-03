#!/usr/bin/env python3
"""
Performance Test Suite for Mock Telegram Testing System

This suite provides comprehensive performance testing including:
- Load testing with multiple concurrent users
- Stress testing to find system limits
- Endurance testing for long-running stability
- WebSocket performance testing
- Bot integration performance testing
- Memory and resource usage monitoring
"""

import asyncio
import aiohttp
import websockets
import psutil
import json
import time
import random
import statistics
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance test metrics"""
    test_name: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Response time metrics
    response_times: List[float] = field(default_factory=list)
    error_count: int = 0
    success_count: int = 0
    
    # Resource usage metrics
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    
    # Throughput metrics
    requests_per_second: float = 0.0
    messages_per_second: float = 0.0
    
    # WebSocket metrics
    websocket_connections: int = 0
    websocket_message_latency: List[float] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def total_requests(self) -> int:
        return self.success_count + self.error_count
    
    @property
    def success_rate(self) -> float:
        total = self.total_requests
        return (self.success_count / total * 100) if total > 0 else 0.0
    
    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0
    
    @property
    def p95_response_time(self) -> float:
        return np.percentile(self.response_times, 95) if self.response_times else 0.0
    
    @property
    def p99_response_time(self) -> float:
        return np.percentile(self.response_times, 99) if self.response_times else 0.0
    
    @property
    def max_response_time(self) -> float:
        return max(self.response_times) if self.response_times else 0.0
    
    @property
    def min_response_time(self) -> float:
        return min(self.response_times) if self.response_times else 0.0


class ResourceMonitor:
    """Monitor system resource usage during tests"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics = []
        
    async def start_monitoring(self, interval: float = 1.0):
        """Start monitoring system resources"""
        self.monitoring = True
        
        while self.monitoring:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            
            self.metrics.append({
                'timestamp': datetime.now(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_info.percent,
                'memory_used': memory_info.used,
                'memory_available': memory_info.available
            })
            
            await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop monitoring resources"""
        self.monitoring = False
    
    def get_summary(self) -> Dict[str, float]:
        """Get resource usage summary"""
        if not self.metrics:
            return {}
        
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        memory_values = [m['memory_percent'] for m in self.metrics]
        
        return {
            'avg_cpu_percent': statistics.mean(cpu_values),
            'max_cpu_percent': max(cpu_values),
            'avg_memory_percent': statistics.mean(memory_values),
            'max_memory_percent': max(memory_values),
            'samples_collected': len(self.metrics)
        }


class PerformanceTestClient:
    """High-performance test client for load testing"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(
            limit=1000,  # Total connection pool size
            limit_per_host=100,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_message_with_timing(self, message_data: Dict[str, Any]) -> Tuple[bool, float]:
        """Send message and return success status with timing"""
        start_time = time.perf_counter()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/send_message",
                json=message_data
            ) as response:
                await response.read()  # Consume response body
                duration = time.perf_counter() - start_time
                return response.status == 200, duration
                
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.debug(f"Request failed: {e}")
            return False, duration
    
    async def create_user_with_timing(self, user_data: Dict[str, Any]) -> Tuple[bool, float]:
        """Create user and return success status with timing"""
        start_time = time.perf_counter()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/users",
                json=user_data
            ) as response:
                await response.read()
                duration = time.perf_counter() - start_time
                return response.status == 200, duration
                
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.debug(f"User creation failed: {e}")
            return False, duration
    
    async def health_check_with_timing(self) -> Tuple[bool, float]:
        """Health check with timing"""
        start_time = time.perf_counter()
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                await response.read()
                duration = time.perf_counter() - start_time
                return response.status == 200, duration
                
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.debug(f"Health check failed: {e}")
            return False, duration


class WebSocketPerformanceTester:
    """WebSocket performance testing"""
    
    def __init__(self, base_url: str = "ws://localhost:8001"):
        self.ws_url = f"{base_url}/ws"
        self.connections = []
        
    async def create_connections(self, count: int) -> int:
        """Create multiple WebSocket connections"""
        successful_connections = 0
        
        for i in range(count):
            try:
                ws = await websockets.connect(self.ws_url)
                self.connections.append(ws)
                successful_connections += 1
                
                # Small delay to avoid overwhelming the server
                if i % 10 == 0:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.debug(f"WebSocket connection {i} failed: {e}")
        
        return successful_connections
    
    async def test_message_latency(self, message_count: int = 10) -> List[float]:
        """Test WebSocket message latency"""
        if not self.connections:
            return []
        
        latencies = []
        
        # Use first connection for testing
        ws = self.connections[0]
        
        for i in range(message_count):
            try:
                # Send a ping and measure response time
                start_time = time.perf_counter()
                await ws.send(json.dumps({"type": "ping", "id": i}))
                
                # Wait for any message (could be echo or bot response)
                await asyncio.wait_for(ws.recv(), timeout=5.0)
                
                duration = time.perf_counter() - start_time
                latencies.append(duration)
                
            except Exception as e:
                logger.debug(f"WebSocket latency test {i} failed: {e}")
        
        return latencies
    
    async def close_connections(self):
        """Close all WebSocket connections"""
        for ws in self.connections:
            try:
                await ws.close()
            except:
                pass
        self.connections.clear()


class PerformanceTestSuite:
    """Main performance test suite"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.results = []
        self.resource_monitor = ResourceMonitor()
        
    async def run_load_test(self, concurrent_users: int = 50, duration_seconds: int = 60) -> PerformanceMetrics:
        """Run load test with specified concurrent users"""
        logger.info(f"🚀 Running load test: {concurrent_users} users for {duration_seconds}s")
        
        metrics = PerformanceMetrics(f"Load Test ({concurrent_users} users)")
        
        # Start resource monitoring
        monitor_task = asyncio.create_task(self.resource_monitor.start_monitoring())
        
        try:
            async with PerformanceTestClient(self.base_url) as client:
                # Create test data
                user_id = 1001  # Use existing test user
                chat_id = 2001  # Main chat
                
                # Create worker tasks
                tasks = []
                for i in range(concurrent_users):
                    task = asyncio.create_task(
                        self._load_test_worker(client, user_id, chat_id, duration_seconds, metrics, i)
                    )
                    tasks.append(task)
                
                # Wait for all workers to complete
                await asyncio.gather(*tasks, return_exceptions=True)
                
        finally:
            # Stop monitoring
            self.resource_monitor.stop_monitoring()
            monitor_task.cancel()
            
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
            
            metrics.end_time = datetime.now()
            
            # Calculate throughput
            if metrics.duration_seconds > 0:
                metrics.requests_per_second = metrics.total_requests / metrics.duration_seconds
        
        # Add resource usage data
        resource_summary = self.resource_monitor.get_summary()
        if resource_summary:
            metrics.cpu_usage = [resource_summary['avg_cpu_percent']]
            metrics.memory_usage = [resource_summary['avg_memory_percent']]
        
        self.results.append(metrics)
        return metrics
    
    async def _load_test_worker(self, client: PerformanceTestClient, user_id: int, 
                               chat_id: int, duration_seconds: int, 
                               metrics: PerformanceMetrics, worker_id: int):
        """Individual worker for load testing"""
        end_time = time.time() + duration_seconds
        request_count = 0
        
        while time.time() < end_time:
            # Send a message
            message_data = {
                "user_id": user_id,
                "chat_id": chat_id,
                "text": f"Load test message from worker {worker_id} - {request_count}",
                "message_type": "text"
            }
            
            success, response_time = await client.send_message_with_timing(message_data)
            
            # Record metrics
            metrics.response_times.append(response_time)
            if success:
                metrics.success_count += 1
            else:
                metrics.error_count += 1
            
            request_count += 1
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.1)
    
    async def run_stress_test(self, max_users: int = 200, ramp_up_time: int = 120) -> PerformanceMetrics:
        """Run stress test to find system limits"""
        logger.info(f"🔥 Running stress test: ramping up to {max_users} users over {ramp_up_time}s")
        
        metrics = PerformanceMetrics(f"Stress Test (up to {max_users} users)")
        
        # Start resource monitoring
        monitor_task = asyncio.create_task(self.resource_monitor.start_monitoring())
        
        try:
            async with PerformanceTestClient(self.base_url) as client:
                user_id = 1001
                chat_id = 2001
                
                # Gradually increase load
                active_tasks = []
                users_per_step = max(1, max_users // 20)  # 20 steps
                step_duration = ramp_up_time / 20
                
                for step in range(20):
                    current_users = min(max_users, (step + 1) * users_per_step)
                    
                    # Add new workers
                    while len(active_tasks) < current_users:
                        worker_id = len(active_tasks)
                        task = asyncio.create_task(
                            self._stress_test_worker(client, user_id, chat_id, metrics, worker_id)
                        )
                        active_tasks.append(task)
                    
                    logger.info(f"📈 Stress test: {current_users} active workers")
                    await asyncio.sleep(step_duration)
                
                # Let test run a bit more
                await asyncio.sleep(30)
                
                # Cancel all workers
                for task in active_tasks:
                    task.cancel()
                
                await asyncio.gather(*active_tasks, return_exceptions=True)
                
        finally:
            self.resource_monitor.stop_monitoring()
            monitor_task.cancel()
            
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
            
            metrics.end_time = datetime.now()
        
        self.results.append(metrics)
        return metrics
    
    async def _stress_test_worker(self, client: PerformanceTestClient, user_id: int,
                                 chat_id: int, metrics: PerformanceMetrics, worker_id: int):
        """Worker for stress testing"""
        request_count = 0
        
        try:
            while True:
                message_data = {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "text": f"Stress test message from worker {worker_id} - {request_count}",
                    "message_type": "text"
                }
                
                success, response_time = await client.send_message_with_timing(message_data)
                
                metrics.response_times.append(response_time)
                if success:
                    metrics.success_count += 1
                else:
                    metrics.error_count += 1
                
                request_count += 1
                await asyncio.sleep(0.05)  # Higher frequency for stress test
                
        except asyncio.CancelledError:
            logger.debug(f"Stress test worker {worker_id} cancelled after {request_count} requests")
    
    async def run_websocket_performance_test(self, connection_count: int = 100) -> PerformanceMetrics:
        """Test WebSocket performance"""
        logger.info(f"🔌 Running WebSocket performance test: {connection_count} connections")
        
        metrics = PerformanceMetrics(f"WebSocket Test ({connection_count} connections)")
        
        ws_tester = WebSocketPerformanceTester("ws://localhost:8001")
        
        try:
            # Create connections
            start_time = time.perf_counter()
            successful_connections = await ws_tester.create_connections(connection_count)
            connection_time = time.perf_counter() - start_time
            
            metrics.websocket_connections = successful_connections
            metrics.response_times.append(connection_time)
            
            logger.info(f"📊 Created {successful_connections}/{connection_count} WebSocket connections in {connection_time:.2f}s")
            
            # Test message latency
            if successful_connections > 0:
                latencies = await ws_tester.test_message_latency(20)
                metrics.websocket_message_latency = latencies
                
                if latencies:
                    avg_latency = statistics.mean(latencies)
                    logger.info(f"📈 Average WebSocket message latency: {avg_latency:.3f}s")
            
            metrics.success_count = successful_connections
            metrics.error_count = connection_count - successful_connections
            
        finally:
            await ws_tester.close_connections()
            metrics.end_time = datetime.now()
        
        self.results.append(metrics)
        return metrics
    
    async def run_endurance_test(self, duration_minutes: int = 30, concurrent_users: int = 20) -> PerformanceMetrics:
        """Run endurance test for system stability"""
        logger.info(f"⏱️ Running endurance test: {concurrent_users} users for {duration_minutes} minutes")
        
        duration_seconds = duration_minutes * 60
        metrics = PerformanceMetrics(f"Endurance Test ({duration_minutes}min)")
        
        # Start resource monitoring
        monitor_task = asyncio.create_task(self.resource_monitor.start_monitoring(interval=5.0))
        
        try:
            async with PerformanceTestClient(self.base_url) as client:
                user_id = 1001
                chat_id = 2001
                
                # Create worker tasks
                tasks = []
                for i in range(concurrent_users):
                    task = asyncio.create_task(
                        self._endurance_test_worker(client, user_id, chat_id, duration_seconds, metrics, i)
                    )
                    tasks.append(task)
                
                # Wait for all workers to complete
                await asyncio.gather(*tasks, return_exceptions=True)
                
        finally:
            self.resource_monitor.stop_monitoring()
            monitor_task.cancel()
            
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
            
            metrics.end_time = datetime.now()
        
        self.results.append(metrics)
        return metrics
    
    async def _endurance_test_worker(self, client: PerformanceTestClient, user_id: int,
                                    chat_id: int, duration_seconds: int,
                                    metrics: PerformanceMetrics, worker_id: int):
        """Worker for endurance testing"""
        end_time = time.time() + duration_seconds
        request_count = 0
        
        while time.time() < end_time:
            # Vary the workload
            if request_count % 100 == 0:
                # Periodic health check
                success, response_time = await client.health_check_with_timing()
            else:
                # Regular message
                message_data = {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "text": f"Endurance test message {request_count} from worker {worker_id}",
                    "message_type": "text"
                }
                success, response_time = await client.send_message_with_timing(message_data)
            
            metrics.response_times.append(response_time)
            if success:
                metrics.success_count += 1
            else:
                metrics.error_count += 1
            
            request_count += 1
            
            # Variable delay to simulate realistic usage
            await asyncio.sleep(random.uniform(0.1, 2.0))
        
        logger.info(f"🏁 Endurance worker {worker_id} completed {request_count} requests")
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        if not self.results:
            return "No performance test results available."
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           PERFORMANCE TEST REPORT                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                             ║
║ Total Test Suites:   {len(self.results)}                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

"""
        
        for result in self.results:
            report += f"""
🧪 {result.test_name}
{'=' * 80}
Duration:           {result.duration_seconds:.1f}s
Total Requests:     {result.total_requests:,}
Success Rate:       {result.success_rate:.1f}%
Requests/Second:    {result.requests_per_second:.1f}

Response Times:
  Average:          {result.avg_response_time:.3f}s
  P95:              {result.p95_response_time:.3f}s  
  P99:              {result.p99_response_time:.3f}s
  Max:              {result.max_response_time:.3f}s
  Min:              {result.min_response_time:.3f}s

"""
            
            if result.websocket_connections > 0:
                report += f"""WebSocket Performance:
  Connections:      {result.websocket_connections}
  Avg Latency:      {statistics.mean(result.websocket_message_latency):.3f}s

"""
            
            if result.cpu_usage or result.memory_usage:
                report += f"""Resource Usage:
  CPU:              {result.cpu_usage[0]:.1f}% (avg)
  Memory:           {result.memory_usage[0]:.1f}% (avg)

"""
        
        # Performance recommendations
        report += """
📊 PERFORMANCE ANALYSIS & RECOMMENDATIONS
════════════════════════════════════════

"""
        
        # Analyze results and provide recommendations
        avg_response_times = [r.avg_response_time for r in self.results]
        avg_success_rates = [r.success_rate for r in self.results]
        
        if avg_response_times:
            overall_avg_response = statistics.mean(avg_response_times)
            report += f"Overall Average Response Time: {overall_avg_response:.3f}s\n"
            
            if overall_avg_response < 0.1:
                report += "✅ Excellent response times - system performing well\n"
            elif overall_avg_response < 0.5:
                report += "✅ Good response times - acceptable performance\n"
            elif overall_avg_response < 1.0:
                report += "⚠️  Moderate response times - consider optimization\n"
            else:
                report += "🚨 High response times - performance optimization needed\n"
        
        if avg_success_rates:
            overall_success_rate = statistics.mean(avg_success_rates)
            report += f"Overall Success Rate: {overall_success_rate:.1f}%\n"
            
            if overall_success_rate >= 99.0:
                report += "✅ Excellent reliability - system very stable\n"
            elif overall_success_rate >= 95.0:
                report += "✅ Good reliability - acceptable stability\n"
            elif overall_success_rate >= 90.0:
                report += "⚠️  Moderate reliability - investigate error causes\n"
            else:
                report += "🚨 Poor reliability - immediate attention required\n"
        
        return report
    
    def save_performance_charts(self, output_dir: str = "."):
        """Generate and save performance charts"""
        try:
            import matplotlib.pyplot as plt
            
            # Response time distribution chart
            plt.figure(figsize=(12, 8))
            
            for i, result in enumerate(self.results):
                if result.response_times:
                    plt.subplot(2, 2, i + 1)
                    plt.hist(result.response_times, bins=50, alpha=0.7, edgecolor='black')
                    plt.title(f'Response Time Distribution - {result.test_name}')
                    plt.xlabel('Response Time (seconds)')
                    plt.ylabel('Frequency')
                    plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/performance_response_times.png", dpi=300, bbox_inches='tight')
            plt.close()
            
            # Throughput comparison chart
            if len(self.results) > 1:
                plt.figure(figsize=(10, 6))
                test_names = [r.test_name for r in self.results]
                throughputs = [r.requests_per_second for r in self.results]
                
                plt.bar(test_names, throughputs, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
                plt.title('Throughput Comparison')
                plt.ylabel('Requests per Second')
                plt.xticks(rotation=45, ha='right')
                plt.grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.savefig(f"{output_dir}/performance_throughput.png", dpi=300, bbox_inches='tight')
                plt.close()
            
            logger.info(f"📊 Performance charts saved to {output_dir}/")
            
        except ImportError:
            logger.warning("matplotlib not available - skipping chart generation")
        except Exception as e:
            logger.error(f"Error generating charts: {e}")


# Main execution functions
async def run_comprehensive_performance_tests():
    """Run all performance tests"""
    suite = PerformanceTestSuite()
    
    logger.info("🚀 Starting Comprehensive Performance Test Suite")
    logger.info("=" * 80)
    
    try:
        # Run different test scenarios
        await suite.run_load_test(concurrent_users=25, duration_seconds=30)
        await asyncio.sleep(5)  # Brief pause between tests
        
        await suite.run_load_test(concurrent_users=50, duration_seconds=30)
        await asyncio.sleep(5)
        
        await suite.run_websocket_performance_test(connection_count=50)
        await asyncio.sleep(5)
        
        await suite.run_stress_test(max_users=100, ramp_up_time=60)
        await asyncio.sleep(10)
        
        # Generate and save report
        report = suite.generate_performance_report()
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"performance_report_{timestamp}.txt"
        with open(report_file, "w") as f:
            f.write(report)
        
        # Save charts
        suite.save_performance_charts()
        
        logger.info(f"📄 Performance report saved to: {report_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Performance test suite failed: {e}")
        return False


async def run_quick_performance_check():
    """Run a quick performance check"""
    suite = PerformanceTestSuite()
    
    logger.info("⚡ Running Quick Performance Check")
    
    # Quick load test
    result = await suite.run_load_test(concurrent_users=10, duration_seconds=15)
    
    print(f"""
Quick Performance Check Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Success Rate:     {result.success_rate:.1f}%
Avg Response:     {result.avg_response_time:.3f}s
Requests/Second:  {result.requests_per_second:.1f}
Total Requests:   {result.total_requests:,}

Status: {'✅ GOOD' if result.success_rate >= 95 and result.avg_response_time < 0.5 else '⚠️  NEEDS ATTENTION'}
""")
    
    return result.success_rate >= 95


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        success = asyncio.run(run_quick_performance_check())
    else:
        success = asyncio.run(run_comprehensive_performance_tests())
    
    sys.exit(0 if success else 1)