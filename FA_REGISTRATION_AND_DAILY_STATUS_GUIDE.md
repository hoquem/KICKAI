# FA Registration Checker & Daily Status Service Guide

## Overview

This guide covers the two new features implemented for the KICKAI Team Management System:

1. **FA Registration Checker** - Automatically monitors FA website for player registrations
2. **Daily Status Service** - Generates and sends daily team status reports to leadership chat

## 🏆 FA Registration Checker

### Purpose
The FA Registration Checker periodically scrapes the Football Association website to check if players have been registered with the FA. This ensures that the team management system stays synchronized with official FA registrations.

### Configuration
- **FA Team URL**: `https://fulltime.thefa.com/displayTeam.html?id=925698828#tab-4`
- **FA Fixtures URL**: `https://fulltime.thefa.com/displayTeam.html?id=925698828#tab-1`
- **Check Frequency**: Every 24 hours automatically
- **Manual Check**: Available via `/checkfa` command

### How It Works

1. **Player Filtering**: Only checks players who:
   - Are not yet FA registered (`fa_registered = False`)
   - Have completed onboarding (`onboarding_status = COMPLETED`)

2. **Website Scraping**: 
   - Scrapes the BP Hatters FC team page on the FA website
   - Extracts player names from the registered players list
   - Compares against local player database

3. **Automatic Updates**:
   - When a player is found on the FA website, their `fa_registered` status is updated to `True`
   - `fa_registration_date` is set to the current timestamp
   - Logs the update for tracking

### Manual Commands

#### `/checkfa`
Triggers an immediate FA registration check.

**Usage**: `/checkfa`

**Response Examples**:
```
✅ FA Registration Check Complete

Found 2 new FA registrations:
• Player JS1 is now FA registered!
• Player AB1 is now FA registered!
```

```
ℹ️ FA Registration Check Complete

No new FA registrations found.
```

### Technical Implementation

**File**: `src/services/fa_registration_checker.py`

**Key Components**:
- `FARegistrationChecker` class with async context manager
- `scrape_team_page()` method for website scraping
- `check_player_registration()` method for database updates
- `run_fa_registration_check()` function for manual execution

**Dependencies**:
- `aiohttp` for async HTTP requests
- `beautifulsoup4` for HTML parsing
- `requests` for synchronous HTTP requests

## 📊 Daily Status Service

### Purpose
The Daily Status Service generates comprehensive team status reports and sends them to the leadership chat. This provides daily insights into team composition, player statistics, and system status.

### Configuration
- **Report Time**: 9:00 AM daily
- **Target Chat**: Leadership chat (configured in bot settings)
- **Manual Trigger**: Available via `/dailystatus` command
- **Format**: HTML-formatted Telegram message

### Report Contents

1. **Basic Information**:
   - Date and team name
   - System status indicators

2. **Player Statistics**:
   - Total players
   - Active players (completed onboarding)
   - Pending approvals
   - FA registered count
   - FA eligible count

3. **Position Breakdown**:
   - Count of players by position (goalkeeper, defender, etc.)

4. **Recent Activity**:
   - Players added in the last 7 days
   - New FA registrations found
   - Recent fixtures/results from FA website

5. **System Status**:
   - Database connection status
   - FA website monitoring status
   - Bot online status

6. **Next Actions**:
   - Reminders for pending approvals
   - FA registration monitoring
   - Fixture checking

### Manual Commands

#### `/dailystatus`
Generates and displays a daily status report immediately.

**Usage**: `/dailystatus`

**Response Example**:
```
📊 Daily Team Status Report
📅 Date: Thursday, July 03, 2025
🏆 Team: BP Hatters FC

👥 Player Statistics:
• Total Players: 4
• Active Players: 0
• Pending Approval: 0
• FA Registered: 0
• FA Eligible: 4

⚽ Position Breakdown:
• Midfielder: 2
• Striker: 1
• Utility: 1

🆕 Recent Additions (Last 7 Days):
• PLAYER TEST (PT1)
• ALIMA BEGUM (AB1)
• MAHMUDUL HOQUE (MH1)

📅 Recent Fixtures/Results:
• Cup Match: BP Hatters FC vs Opponent

🔧 System Status:
• Database: ✅ Connected
• FA Website: ✅ Monitored
• Bot: ✅ Online

💡 Next Actions:
• Review pending approvals: 0 players
• Monitor FA registration progress
• Check upcoming fixtures
```

### Technical Implementation

**File**: `src/services/daily_status_service.py`

**Key Components**:
- `DailyStatusService` class
- `TeamStats` dataclass for structured data
- `generate_team_stats()` method for data collection
- `format_daily_status_message()` method for message formatting
- `schedule_daily_status_task()` method for automated scheduling

**Integration**:
- Uses `FARegistrationChecker` for FA data
- Integrates with `PlayerService`, `TeamService`, and `TeamMemberService`
- Sends messages via Telegram Bot API

## 🔧 Background Task Management

### Purpose
The Background Task Manager coordinates all periodic tasks and ensures they run reliably.

### Implementation

**File**: `src/services/background_tasks.py`

**Key Features**:
- `BackgroundTaskManager` class for task coordination
- Automatic task scheduling and execution
- Error handling and retry logic
- Graceful shutdown capabilities

### Task Scheduling

1. **FA Registration Checker**:
   - Runs every 24 hours
   - Retries on failure (1-hour intervals)
   - Logs all activities

2. **Daily Status Service**:
   - Runs daily at 9:00 AM
   - Sends reports to leadership chat
   - Includes FA registration updates

### Starting Background Tasks

```python
from src.services.background_tasks import start_background_tasks_for_team

# Start background tasks for a team
await start_background_tasks_for_team("team_id")
```

## 🚀 Integration with Main Bot

### New Commands Added

The following commands have been added to the player registration handler:

1. **`/checkfa`** - Manual FA registration check
2. **`/dailystatus`** - Manual daily status report

### Access Control

- Both commands are **admin-only** and require leadership chat access
- Commands are routed through the existing access control system
- Proper error handling and logging implemented

### Help Message Updates

The help message (`/help`) has been updated to include the new commands:

```
👨‍💼 Admin Commands:
• /approve <player_id> - Approve a player
• /reject <player_id> [reason] - Reject a player
• /pending - List players pending approval
• /checkfa - Check FA registration status
• /dailystatus - Generate daily team status report
```

## 📋 Testing

### Test Script
A comprehensive test script is available: `test_fa_and_daily_status.py`

**Test Coverage**:
- FA registration checker functionality
- Daily status service functionality
- Manual command handling
- Integration with existing services

**Running Tests**:
```bash
python test_fa_and_daily_status.py
```

### Test Results
All tests should pass with the following output:
```
📋 Test Summary:
  • FA Registration Checker: ✅ PASS
  • Daily Status Service: ✅ PASS
  • Manual Commands: ✅ PASS
```

## 🔍 Monitoring and Logging

### Logging
All operations are logged with appropriate levels:

- **INFO**: Normal operations, successful checks
- **WARNING**: Non-critical issues (e.g., no players to check)
- **ERROR**: Failed operations, retry attempts

### Performance Monitoring
All operations include performance timing:

- `fa_check_player_registration`
- `fa_scrape_team_page`
- `fa_scrape_fixtures`
- `daily_status_generate_stats`
- `daily_status_format_message`
- `daily_status_send_report`

### Error Handling
- Network timeouts and connection errors
- FA website structure changes
- Database connection issues
- Telegram API errors

## 🛠️ Configuration

### Environment Variables
No additional environment variables are required. The system uses existing configuration:

- `TEAM_ID` - Team identifier
- Bot configuration from `bot_config_manager`
- Firebase credentials

### FA Website URLs
The FA website URLs are hardcoded for BP Hatters FC:

```python
self.fa_team_url = "https://fulltime.thefa.com/displayTeam.html?id=925698828#tab-4"
self.fa_fixtures_url = "https://fulltime.thefa.com/displayTeam.html?id=925698828#tab-1"
```

**Note**: For other teams, these URLs would need to be updated or made configurable.

## 🔄 Dependencies

### New Dependencies Added
- `aiohttp>=3.8.0` - Async HTTP client
- `beautifulsoup4>=4.11.0` - HTML parsing

### Installation
```bash
pip install aiohttp beautifulsoup4
```

## 📈 Future Enhancements

### Potential Improvements
1. **Configurable FA URLs**: Make FA website URLs configurable per team
2. **Enhanced Scraping**: More sophisticated HTML parsing for different FA site layouts
3. **Notification System**: Send notifications when FA registrations are found
4. **Historical Tracking**: Track FA registration history and trends
5. **Multiple Team Support**: Extend to support multiple teams with different FA configurations
6. **Webhook Integration**: Integrate with FA webhooks if available
7. **Advanced Analytics**: More detailed team analytics and reporting

### Scalability Considerations
- Current implementation is designed for single-team use
- Background tasks can be extended to support multiple teams
- Database queries are optimized for current team size
- FA website scraping includes rate limiting considerations

## 🚨 Troubleshooting

### Common Issues

1. **FA Website Not Accessible**:
   - Check network connectivity
   - Verify FA website is online
   - Check for IP blocking or rate limiting

2. **No Players Found for FA Check**:
   - Verify players have completed onboarding
   - Check that players are not already FA registered
   - Review player data in database

3. **Daily Status Not Sending**:
   - Verify leadership chat ID is configured
   - Check bot token is valid
   - Review Telegram API rate limits

4. **Background Tasks Not Starting**:
   - Check bot configuration is loaded correctly
   - Verify Firebase connection
   - Review service initialization logs

### Debug Commands
- Use `/checkfa` to manually test FA registration checking
- Use `/dailystatus` to manually test status report generation
- Check logs for detailed error information

## 📞 Support

For issues or questions regarding these features:

1. Check the logs for detailed error messages
2. Run the test script to verify functionality
3. Review this documentation for configuration details
4. Contact the development team for technical support

---

**Version**: 1.0  
**Last Updated**: July 3, 2025  
**Compatibility**: KICKAI v1.5.0+ 