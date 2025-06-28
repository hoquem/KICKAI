#!/usr/bin/env python3
"""
KICKAI Monitoring System
Handles system metrics, application metrics, and AI response quality monitoring
"""

import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System metrics data structure."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    process_count: int
    uptime: float

@dataclass
class AppMetrics:
    """Application metrics data structure."""
    timestamp: float
    commands_processed: int
    commands_failed: int
    avg_response_time: float
    bot_status: str
    uptime: float

@dataclass
class AIResponseQuality:
    """AI response quality metrics."""
    timestamp: float
    user_input: str
    ai_response: str
    quality_score: float
    response_time: float
    context: Dict

class SystemMonitor:
    """System-level monitoring."""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 1000  # Keep last 1000 metrics
    
    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            import psutil
            
            metrics = SystemMetrics(
                timestamp=time.time(),
                cpu_percent=psutil.cpu_percent(),
                memory_percent=psutil.virtual_memory().percent,
                disk_percent=psutil.disk_usage('/').percent,
                process_count=len(psutil.pids()),
                uptime=time.time() - self.start_time
            )
            
            # Store in history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)
            
            return metrics
            
        except ImportError:
            logger.warning("psutil not available, returning basic metrics")
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                process_count=0,
                uptime=time.time() - self.start_time
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                process_count=0,
                uptime=time.time() - self.start_time
            )
    
    def get_metrics_history(self, hours: int = 24) -> List[SystemMetrics]:
        """Get metrics history for the last N hours."""
        cutoff_time = time.time() - (hours * 3600)
        return [m for m in self.metrics_history if m.timestamp > cutoff_time]
    
    def get_average_metrics(self, hours: int = 1) -> Dict:
        """Get average metrics for the last N hours."""
        recent_metrics = self.get_metrics_history(hours)
        if not recent_metrics:
            return {}
        
        return {
            'avg_cpu': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'avg_memory': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            'avg_disk': sum(m.disk_percent for m in recent_metrics) / len(recent_metrics),
            'sample_count': len(recent_metrics)
        }

class AppMonitor:
    """Application-level monitoring."""
    
    def __init__(self):
        self.start_time = time.time()
        self.commands_processed = 0
        self.commands_failed = 0
        self.response_times: List[float] = []
        self.bot_status = 'stopped'
        self.metrics_history: List[AppMetrics] = []
        self.max_history_size = 1000
    
    def record_command(self, success: bool, response_time: float):
        """Record a command execution."""
        if success:
            self.commands_processed += 1
        else:
            self.commands_failed += 1
        
        self.response_times.append(response_time)
        if len(self.response_times) > 1000:  # Keep last 1000 response times
            self.response_times.pop(0)
    
    def set_bot_status(self, status: str):
        """Set bot status."""
        self.bot_status = status
    
    def get_metrics(self) -> AppMetrics:
        """Get current application metrics."""
        avg_response_time = 0.0
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
        
        metrics = AppMetrics(
            timestamp=time.time(),
            commands_processed=self.commands_processed,
            commands_failed=self.commands_failed,
            avg_response_time=avg_response_time,
            bot_status=self.bot_status,
            uptime=time.time() - self.start_time
        )
        
        # Store in history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
        
        return metrics
    
    def get_success_rate(self) -> float:
        """Get command success rate."""
        total = self.commands_processed + self.commands_failed
        if total == 0:
            return 0.0
        return self.commands_processed / total
    
    def get_metrics_history(self, hours: int = 24) -> List[AppMetrics]:
        """Get metrics history for the last N hours."""
        cutoff_time = time.time() - (hours * 3600)
        return [m for m in self.metrics_history if m.timestamp > cutoff_time]

class AIQualityMonitor:
    """AI response quality monitoring."""
    
    def __init__(self):
        self.responses: List[AIResponseQuality] = []
        self.max_responses = 1000
    
    def evaluate_response(self, user_input: str, ai_response: str, 
                         response_time: float, context: Dict) -> float:
        """Evaluate AI response quality and return a score (0-10)."""
        quality_score = self._calculate_quality_score(user_input, ai_response, context)
        
        response_quality = AIResponseQuality(
            timestamp=time.time(),
            user_input=user_input,
            ai_response=ai_response,
            quality_score=quality_score,
            response_time=response_time,
            context=context
        )
        
        self.responses.append(response_quality)
        if len(self.responses) > self.max_responses:
            self.responses.pop(0)
        
        return quality_score
    
    def _calculate_quality_score(self, user_input: str, ai_response: str, context: Dict) -> float:
        """Calculate quality score based on various factors."""
        score = 5.0  # Base score
        
        # Relevance to user input
        if self._is_relevant(user_input, ai_response):
            score += 2.0
        
        # Completeness
        if len(ai_response.strip()) > 10:
            score += 1.0
        
        # Appropriate tone for context
        if self._has_appropriate_tone(ai_response, context):
            score += 1.0
        
        # Technical accuracy (basic check)
        if self._is_technically_accurate(ai_response):
            score += 1.0
        
        return min(score, 10.0)  # Cap at 10
    
    def _is_relevant(self, user_input: str, ai_response: str) -> bool:
        """Check if response is relevant to user input."""
        # Simple keyword matching for now
        # In production, this could use more sophisticated NLP
        user_words = set(user_input.lower().split())
        response_words = set(ai_response.lower().split())
        
        if not user_words:
            return True
        
        overlap = len(user_words.intersection(response_words))
        return overlap > 0
    
    def _has_appropriate_tone(self, response: str, context: Dict) -> bool:
        """Check if response has appropriate tone for context."""
        # Check for professional tone in leadership context
        if context.get('is_leadership_chat', False):
            professional_words = ['admin', 'management', 'team', 'fixture', 'squad']
            return any(word in response.lower() for word in professional_words)
        
        return True
    
    def _is_technically_accurate(self, response: str) -> bool:
        """Basic technical accuracy check."""
        # Check for common technical errors
        error_indicators = ['error', 'failed', 'not found', 'invalid']
        return not any(indicator in response.lower() for indicator in error_indicators)
    
    def get_average_quality(self, hours: int = 24) -> float:
        """Get average quality score for the last N hours."""
        cutoff_time = time.time() - (hours * 3600)
        recent_responses = [r for r in self.responses if r.timestamp > cutoff_time]
        
        if not recent_responses:
            return 0.0
        
        return sum(r.quality_score for r in recent_responses) / len(recent_responses)
    
    def get_quality_distribution(self) -> Dict:
        """Get distribution of quality scores."""
        if not self.responses:
            return {}
        
        scores = [r.quality_score for r in self.responses]
        return {
            'excellent': len([s for s in scores if s >= 9]),
            'good': len([s for s in scores if 7 <= s < 9]),
            'average': len([s for s in scores if 5 <= s < 7]),
            'poor': len([s for s in scores if s < 5])
        }

class MonitoringManager:
    """Main monitoring manager that coordinates all monitoring systems."""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.app_monitor = AppMonitor()
        self.ai_monitor = AIQualityMonitor()
        self.alerts: List[Dict] = []
    
    def collect_all_metrics(self) -> Dict:
        """Collect all metrics."""
        return {
            'system': asdict(self.system_monitor.collect_metrics()),
            'application': asdict(self.app_monitor.get_metrics()),
            'ai_quality': {
                'average_quality': self.ai_monitor.get_average_quality(),
                'quality_distribution': self.ai_monitor.get_quality_distribution()
            },
            'timestamp': time.time()
        }
    
    def check_alerts(self) -> List[Dict]:
        """Check for alert conditions."""
        alerts = []
        
        # System alerts
        system_metrics = self.system_monitor.collect_metrics()
        if system_metrics.cpu_percent > 80:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'message': f'High CPU usage: {system_metrics.cpu_percent}%',
                'timestamp': time.time()
            })
        
        if system_metrics.memory_percent > 80:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'message': f'High memory usage: {system_metrics.memory_percent}%',
                'timestamp': time.time()
            })
        
        # Application alerts
        app_metrics = self.app_monitor.get_metrics()
        success_rate = self.app_monitor.get_success_rate()
        if success_rate < 0.95:  # Less than 95% success rate
            alerts.append({
                'type': 'application',
                'severity': 'warning',
                'message': f'Low success rate: {success_rate:.2%}',
                'timestamp': time.time()
            })
        
        if app_metrics.avg_response_time > 5.0:  # More than 5 seconds
            alerts.append({
                'type': 'application',
                'severity': 'warning',
                'message': f'High response time: {app_metrics.avg_response_time:.2f}s',
                'timestamp': time.time()
            })
        
        # AI quality alerts
        avg_quality = self.ai_monitor.get_average_quality()
        if avg_quality < 6.0:  # Less than 6/10 average quality
            alerts.append({
                'type': 'ai_quality',
                'severity': 'warning',
                'message': f'Low AI response quality: {avg_quality:.2f}/10',
                'timestamp': time.time()
            })
        
        # Store alerts
        self.alerts.extend(alerts)
        if len(self.alerts) > 100:  # Keep last 100 alerts
            self.alerts = self.alerts[-100:]
        
        return alerts
    
    def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data."""
        return {
            'current_metrics': self.collect_all_metrics(),
            'alerts': self.check_alerts(),
            'system_history': [asdict(m) for m in self.system_monitor.get_metrics_history(1)],
            'app_history': [asdict(m) for m in self.app_monitor.get_metrics_history(1)],
            'ai_responses': len(self.ai_monitor.responses)
        }

# Global monitoring manager instance
monitoring_manager = MonitoringManager()

def main():
    """Main monitoring process."""
    logger.info("Starting KICKAI monitoring system...")
    
    while True:
        try:
            # Collect metrics
            metrics = monitoring_manager.collect_all_metrics()
            
            # Check for alerts
            alerts = monitoring_manager.check_alerts()
            
            # Log metrics and alerts
            if alerts:
                logger.warning(f"Alerts detected: {alerts}")
            
            logger.debug(f"Metrics collected: {metrics}")
            
            # Sleep for monitoring interval
            time.sleep(60)  # Monitor every minute
            
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main() 