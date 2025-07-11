# Health Check Service Documentation

## Overview

The KICKAI Health Check Service provides comprehensive system monitoring and health assessment capabilities. It monitors all agents, tools, services, and external dependencies to ensure system reliability and provide proactive issue detection.

## Architecture

### Components

1. **HealthCheckService**: Core service that performs health checks on all system components
2. **BackgroundHealthMonitor**: Background service that runs periodic health checks and manages alerts
3. **HealthAlert**: Alert system for notifying about system issues
4. **CLI Interface**: Command-line tools for health monitoring

### Health Check Categories

- **Agents**: All 8 CrewAI agents (MessageProcessor, TeamManager, etc.)
- **Tools**: Communication, logging, player, and team management tools
- **Services**: Player, team, payment, reminder, and other business services
- **External Dependencies**: Database, LLM, payment gateway, Telegram API

## Quick Start

### Running a Health Check

```bash
# Basic health check
python run_health_checks.py check

# Verbose health check with export
python run_health_checks.py check --verbose --export

# Health check for specific team
python run_health_checks.py check --team-id KAI
```

### Starting Background Monitoring

```bash
# Start monitoring with default 5-minute interval
python run_health_checks.py monitor

# Start monitoring with custom interval (2 minutes)
python run_health_checks.py monitor --interval 120

# Monitor specific team
python run_health_checks.py monitor --team-id KAI
```

### Checking Status and Alerts

```bash
# Show monitoring status
python run_health_checks.py status

# Show recent alerts
python run_health_checks.py alerts

# Show alerts from last 6 hours
python run_health_checks.py alerts --hours 6

# Force immediate health check
python run_health_checks.py force
```

## API Usage

### HealthCheckService

```python
from src.services.health_check_service import get_health_check_service

# Get service instance
health_service = get_health_check_service("KAI")

# Perform comprehensive health check
report = await health_service.perform_comprehensive_health_check()

# Check if system is healthy
if report.is_healthy():
    print("System is healthy")
else:
    print(f"System has {len(report.critical_issues)} critical issues")

# Get health history
history = await health_service.get_health_history(hours=24)

# Export health report
export_file = await health_service.export_health_report()
```

### BackgroundHealthMonitor

```python
from src.services.background_health_monitor import get_background_health_monitor

# Get monitor instance
monitor = get_background_health_monitor("KAI")

# Start monitoring
await monitor.start_monitoring()

# Add custom alert handler
async def my_alert_handler(alert):
    print(f"Alert: {alert.level.value} - {alert.message}")

monitor.add_alert_handler(my_alert_handler)

# Get status
status = await monitor.get_status_summary()

# Get active alerts
alerts = await monitor.get_active_alerts()

# Stop monitoring
await monitor.stop_monitoring()
```

## Health Check Details

### Agent Health Checks

The service checks all 8 CrewAI agents:

1. **MessageProcessorAgent**: Primary user interface and command parsing
2. **TeamManagerAgent**: Strategic coordination and planning
3. **PlayerCoordinatorAgent**: Player management and registration
4. **FinanceManagerAgent**: Financial tracking and payments
5. **PerformanceAnalystAgent**: Performance analysis and insights
6. **LearningAgent**: Continuous learning and improvement
7. **OnboardingAgent**: Player onboarding workflows
8. **CommandFallbackAgent**: Unrecognized command handling

Each agent check verifies:
- Agent instantiation and availability
- Configuration integrity
- Tool availability
- LLM connectivity
- Enabled/disabled status

### Tool Health Checks

Checks all domain tools:

- **Communication Tools**: SendMessageTool, SendAnnouncementTool
- **Logging Tools**: LogCommandTool
- **Player Tools**: GetAllPlayersTool, GetPlayerStatusTool
- **Team Management Tools**: GetTeamInfoTool, GetTeamMembersTool

### Service Health Checks

Monitors all business services:

- **PlayerService**: Player management operations
- **TeamService**: Team management operations
- **PaymentService**: Payment processing
- **ReminderService**: Automated reminders
- **DailyStatusService**: Status reporting
- **FARegistrationChecker**: FA registration checking

### External Dependency Checks

- **Database**: Firebase connectivity and operations
- **LLM**: Google Gemini API connectivity
- **Payment Gateway**: Stripe integration
- **Telegram**: Bot API connectivity

## Alert System

### Alert Levels

- **INFO**: Informational messages
- **WARNING**: System degradation or potential issues
- **ERROR**: Component failures that need attention
- **CRITICAL**: System-wide failures requiring immediate action

### Alert Escalation

Alerts automatically escalate based on time:

- **WARNING** → **ERROR**: After 30 minutes
- **ERROR** → **CRITICAL**: After 10 minutes
- **CRITICAL**: No further escalation

### Alert Handlers

You can register custom alert handlers:

```python
async def telegram_alert_handler(alert):
    if alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
        # Send Telegram notification to admin
        await send_telegram_message(admin_chat_id, f"🚨 {alert.message}")

monitor.add_alert_handler(telegram_alert_handler)
```

## Performance Metrics

The service tracks various performance metrics:

- **Check Duration**: Time taken for health checks
- **Response Times**: Component response times
- **Alert Counts**: Number of active alerts over time
- **System Uptime**: Monitoring service uptime
- **Component Health**: Health status distribution

## Configuration

### Check Intervals

Default check intervals can be configured:

```python
# Set health check interval to 10 minutes
health_service.set_check_interval(600)

# Set background monitoring interval to 2 minutes
monitor.set_check_interval(120)
```

### Custom Health Checks

You can add custom health checks:

```python
async def custom_database_check():
    # Custom database health check logic
    return {
        "status": HealthStatus.HEALTHY,
        "message": "Custom database check passed",
        "details": {"custom": True}
    }

health_service.add_custom_check(
    "custom_database", 
    ComponentType.DATABASE, 
    custom_database_check
)
```

## Integration with Existing Systems

### Startup Validation

The health check service integrates with the existing startup validator:

```python
from src.core.startup_validator import StartupValidator

# Run startup validation
validator = StartupValidator()
startup_report = await validator.validate()

# Run comprehensive health check
health_service = get_health_check_service("KAI")
health_report = await health_service.perform_comprehensive_health_check()
```

### Background Tasks

The background monitor can be integrated with the existing background task system:

```python
from src.services.background_tasks import BackgroundTaskManager

# Add health monitoring to background tasks
task_manager = BackgroundTaskManager()
task_manager.add_periodic_task(
    "health_monitoring",
    monitor._monitoring_loop,
    interval_seconds=300
)
```

## Monitoring Best Practices

### 1. Regular Health Checks

- Run health checks at least every 5 minutes in production
- Use background monitoring for continuous oversight
- Set up alert handlers for critical issues

### 2. Alert Management

- Configure appropriate alert levels for different components
- Set up escalation policies for persistent issues
- Monitor alert history for patterns

### 3. Performance Monitoring

- Track health check durations for performance issues
- Monitor component response times
- Set up alerts for performance degradation

### 4. Maintenance

- Regularly review and update custom health checks
- Monitor health check history for trends
- Export health reports for analysis

## Troubleshooting

### Common Issues

1. **Health Check Timeouts**
   - Increase timeout values for slow components
   - Check network connectivity for external dependencies

2. **False Positives**
   - Review component-specific health check logic
   - Adjust alert thresholds as needed

3. **Missing Components**
   - Ensure all required services are initialized
   - Check component registration in health check service

### Debug Mode

Enable verbose logging for debugging:

```python
import logging
logging.getLogger("src.services.health_check_service").setLevel(logging.DEBUG)
```

### Health Report Analysis

Export health reports for detailed analysis:

```python
# Export current health report
export_file = await health_service.export_health_report()

# Analyze health history
history = await health_service.get_health_history(hours=24)
for report in history:
    print(f"Time: {report.timestamp}, Status: {report.overall_status.value}")
```

## Security Considerations

- Health check results may contain sensitive system information
- Ensure health reports are stored securely
- Limit access to health monitoring endpoints
- Use appropriate authentication for health check APIs

## Future Enhancements

1. **Web Dashboard**: Web-based health monitoring interface
2. **Metrics Integration**: Integration with Prometheus/Grafana
3. **Predictive Analytics**: ML-based issue prediction
4. **Automated Remediation**: Automatic issue resolution
5. **Multi-team Monitoring**: Centralized monitoring for multiple teams

## Support

For issues with the health check service:

1. Check the health check logs: `health_check_test.log`
2. Run the test suite: `python test_health_check_service.py`
3. Review the health check documentation
4. Contact the development team with specific error details 