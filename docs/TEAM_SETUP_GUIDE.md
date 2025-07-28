# KICKAI Team Setup Guide

This guide provides step-by-step instructions for setting up a new team in the KICKAI system, from initial bot creation to final verification.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1: Bot Creation](#step-1-bot-creation)
3. [Step 2: Chat Creation](#step-2-chat-creation)
4. [Step 3: Backend Database Setup](#step-3-backend-database-setup)
5. [Step 4: Admin Setup in Telegram](#step-4-admin-setup-in-telegram)
6. [Step 5: Bot Startup and Admin Registration](#step-5-bot-startup-and-admin-registration)
7. [Step 6: Verification](#step-6-verification)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting the team setup process, ensure you have:

- **System Admin Access**: Access to the KICKAI backend server
- **Telegram Account**: Admin privileges in Telegram
- **Team Information**: Complete team details including league information
- **Environment Access**: Access to the target environment (testing/production)

### Required Team Information

Gather the following information before starting:

- **Team Name**: Official team name (e.g., "KickAI Testing")
- **League Name**: Full league name (e.g., "Leighton District & Luton Sunday Football League")
- **Division**: Team's division (e.g., "Division 1")
- **Home Pitch**: Home ground name and address
- **FA Website URL**: Team's page on the FA website
- **Admin Contact**: Primary admin's name, phone, and email
- **Team Contact Details**: Additional team contacts (optional)

## Step 1: Bot Creation

### 1.1 Create Bot via BotFather

1. Open Telegram and search for `@BotFather`
2. Start a conversation with BotFather
3. Send `/newbot` command
4. Provide bot name (e.g., "KickAI Testing Bot")
5. Provide bot username (e.g., "KickAITesting_bot")
6. Save the bot token provided by BotFather

### 1.2 Configure Bot Settings

1. Send `/setcommands` to BotFather
2. Select your bot
3. Set up basic commands (optional - KICKAI will handle commands)

### 1.3 Update Environment Variables

Add the bot token to your environment configuration:

```bash
# Add to .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

## Step 2: Chat Creation

### 2.1 Create Main Team Chat

1. In Telegram, create a new group
2. Name it: `[Team Name]` (e.g., "KickAI Testing")
3. Add the bot to the group
4. Note the chat ID (you'll need this later)

### 2.2 Create Leadership Chat

1. Create another new group
2. Name it: `[Team Name] - Leadership` (e.g., "KickAI Testing - Leadership")
3. Add the bot to this group
4. Note the chat ID (you'll need this later)

### 2.3 Get Chat IDs

To get the chat IDs:

1. Add the bot to both chats
2. Send a message in each chat
3. Access the bot's webhook or logs to see the chat IDs
4. Alternatively, use the chat ID finder script:

```bash
PYTHONPATH=src python scripts/find_chat_ids.py --bot-token YOUR_BOT_TOKEN
```

## Step 3: Backend Database Setup

### 3.1 Navigate to Project Directory

```bash
cd /path/to/KICKAI
source venv311/bin/activate
```

### 3.2 Run Team Bootstrap Script

```bash
PYTHONPATH=src python scripts/bootstrap_team.py \
  --team-name "KickAI Testing" \
  --main-chat-id -4889304885 \
  --leadership-chat-id -4814449926 \
  --bot-username "KickAITesting_bot" \
  --admin-phone "+447123456789" \
  --admin-name "John Admin" \
  --admin-email "admin@kickai.com" \
  --league-name "Leighton District & Luton Sunday Football League" \
  --division "Division 1" \
  --home-pitch "Leighton Buzzard Recreation Ground" \
  --fa-website-url "https://fulltime-league.thefa.com/ListPublicFixture.do?league=123456"
```

### 3.3 Verify Database Setup

```bash
# Check team configuration
PYTHONPATH=src python scripts/verify_team_setup.py --team-name "KickAI Testing"

# Check bot mapping
PYTHONPATH=src python scripts/check_bot_status.py
```

## Step 4: Admin Setup in Telegram

### 4.1 Add Admin to Chats

1. **In Main Chat**:
   - Add the admin's Telegram account to the main team chat
   - Right-click on admin's name
   - Select "Promote to Admin"
   - Grant necessary permissions

2. **In Leadership Chat**:
   - Add the admin's Telegram account to the leadership chat
   - Right-click on admin's name
   - Select "Promote to Admin"
   - Grant necessary permissions

### 4.2 Required Admin Permissions

Ensure the admin has the following permissions in both chats:
- ✅ Post messages
- ✅ Delete messages
- ✅ Ban users
- ✅ Add users
- ✅ Pin messages
- ✅ Edit group info

### 4.3 Verify Admin Status

The admin should see an admin badge (👑) next to their name in both chats.

### 4.4 Promoting Members to Admin

To promote a member to admin, use `/promote <member_id>` in the leadership chat (admin only).

## Step 5: Bot Startup and Admin Registration

### 5.1 Start the Bot

```bash
# Start the Telegram bot
PYTHONPATH=src python run_bot_local.py
```

### 5.2 Admin Registration

1. **In Leadership Chat**:
   - Admin types: `/start`
   - Bot should respond with welcome message
   - Admin receives confirmation of successful registration

2. **Verify Registration**:
   - Admin types: `/myinfo`
   - Bot should display admin's information
   - Admin types: `/help`
   - Bot should show available commands

### 5.3 Test Basic Functionality

1. **Test Admin Commands**:
   ```
   /add [Name] [Phone] [Position]  # Add a player
   /list                           # List all players
   /status [phone]                 # Check player status
   ```

2. **Test Player Registration**:
   - Add a test player using `/add`
   - Verify player appears in `/list`
   - Check player status with `/status`

## Step 6: Verification

### 6.1 Run Verification Scripts

```bash
# Comprehensive verification
PYTHONPATH=src python scripts/verify_team_setup.py --team-name "KickAI Testing"

# Check bot connectivity
PYTHONPATH=src python scripts/check_bot_status.py

# Verify admin permissions
PYTHONPATH=src python scripts/verify_admin_permissions.py --admin-phone "+447123456789"

# Test database connectivity
PYTHONPATH=src python scripts/test_database_connection.py
```

### 6.2 Manual Verification Checklist

- [ ] Bot responds to commands in both chats
- [ ] Admin can use leadership commands
- [ ] Team information is correctly stored
- [ ] League and division information is accurate
- [ ] FA website URL is accessible
- [ ] Admin has proper permissions in both chats
- [ ] Bot can send messages to both chats
- [ ] Database contains all team data

### 6.3 Health Check

```bash
# Run health check
PYTHONPATH=src python scripts/run_health_checks.py --team-name "KickAI Testing"
```

## Troubleshooting

### Common Issues

#### Bot Not Responding
- **Check**: Bot token is correct
- **Check**: Bot is added to both chats
- **Check**: Bot has permission to send messages
- **Solution**: Restart bot and verify token

#### Admin Commands Not Working
- **Check**: Admin has admin privileges in both chats
- **Check**: Admin is registered in the system
- **Check**: Bot recognizes admin's Telegram ID
- **Solution**: Re-run admin registration with `/start`

#### Database Errors
- **Check**: Database connection is working
- **Check**: Team data was created correctly
- **Check**: Bot mapping exists
- **Solution**: Re-run bootstrap script

#### Chat ID Issues
- **Check**: Chat IDs are correct
- **Check**: Bot is in both chats
- **Check**: Chat names match expected format
- **Solution**: Use chat ID finder script to verify

### Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Bot not found" | Invalid bot token | Verify token with BotFather |
| "Chat not found" | Invalid chat ID | Use chat ID finder script |
| "Admin not registered" | Admin not in database | Re-run bootstrap script |
| "Permission denied" | Admin lacks permissions | Promote to admin in chats |
| "Database connection failed" | Database not accessible | Check database configuration |

### Recovery Procedures

#### If Bootstrap Fails
```bash
# Clean up failed setup
PYTHONPATH=src python scripts/cleanup_team_setup.py --team-name "KickAI Testing"

# Re-run bootstrap
PYTHONPATH=src python scripts/bootstrap_team.py [parameters]
```

#### If Admin Loses Permissions
1. Re-promote admin in both chats
2. Re-run admin registration: `/start`
3. Verify with: `/myinfo`

#### If Bot Stops Working
1. Check bot logs for errors
2. Restart bot: `python run_bot_local.py`
3. Verify bot token is still valid
4. Check database connectivity

## Next Steps

After successful team setup:

1. **Add Players**: Use `/add` command to add team members
2. **Configure Match Settings**: Set up match scheduling preferences
3. **Set Up Payment Integration**: Configure payment methods (if applicable)
4. **Train Team Members**: Educate team on bot usage
5. **Monitor Usage**: Track bot usage and team engagement

## Support

For additional support:
- Check the [KICKAI Documentation](../README.md)
- Review [Troubleshooting Guide](TROUBLESHOOTING.md)
- Contact system administrator for technical issues

---

**Note**: This guide assumes you have the necessary scripts (`bootstrap_team.py`, `verify_team_setup.py`, etc.) available. If these scripts don't exist, they need to be created first. 