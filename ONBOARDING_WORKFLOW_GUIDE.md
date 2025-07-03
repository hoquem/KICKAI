# KICKAI Onboarding Workflow Guide

## 🎯 Overview

The KICKAI onboarding workflow is a comprehensive system that automatically detects new users joining the team via invite links and guides them through a complete registration process. This includes admin approval, profile completion, emergency contact collection, and FA registration guidance.

## 🔄 Workflow Steps

### 1. **New User Detection** 🆕
- **Trigger**: User joins main team chat via invite link
- **Action**: Bot automatically detects new member
- **Result**: Creates pending approval entry or starts onboarding

### 2. **Admin Approval** 👑
- **Trigger**: New user requires approval
- **Action**: Admin reviews and approves/rejects in leadership chat
- **Commands**: 
  - `/approve <player_id>` - Approve user
  - `/reject <player_id> [reason]` - Reject user
  - `/pending` - View all pending approvals

### 3. **Profile Completion** 📝
- **Trigger**: User confirms or updates their details
- **Fields**: Name, phone number, position
- **Validation**: Phone number format, position validation

### 4. **Emergency Contact** 📞
- **Trigger**: Profile completion step
- **Format**: "Name, Phone" (e.g., "Jane Smith, 07987654321")
- **Validation**: UK phone number format

### 5. **Date of Birth** 📅
- **Trigger**: Emergency contact completion
- **Format**: DD/MM/YYYY (e.g., 15/05/1995)
- **Purpose**: FA registration requirement

### 6. **FA Eligibility Check** 🏆
- **Trigger**: Date of birth completion
- **Options**: Yes/No for FA registration eligibility
- **Requirements**: Age 16+, not registered with another club

### 7. **FA Registration Process** 📋
- **Trigger**: FA eligibility confirmed
- **Steps**:
  1. Contact team admin
  2. Prepare required documents
  3. Pay registration fee (£15)
  4. Complete registration forms

### 8. **Team Access Setup** ✅
- **Trigger**: FA registration process initiated
- **Result**: Player gets full team access

## 🛠️ Technical Implementation

### Files and Components

#### Core Onboarding Handler
- **File**: `src/telegram/onboarding_handler.py`
- **Class**: `OnboardingWorkflow`
- **Purpose**: Main onboarding logic and workflow management

#### Integration Points
- **File**: `src/telegram/telegram_command_handler.py`
- **Function**: `langchain_agentic_message_handler`
- **Purpose**: Detects new chat members and triggers onboarding

#### Player Management
- **File**: `src/telegram/player_registration_handler.py`
- **Methods**: `approve_player`, `reject_player`, `get_pending_approvals`
- **Purpose**: Admin approval and player management

### Database Models

#### Player Model Updates
```python
@dataclass
class Player:
    # ... existing fields ...
    onboarding_status: OnboardingStatus = OnboardingStatus.PENDING
    onboarding_step: Optional[str] = None
    emergency_contact: Optional[str] = None
    date_of_birth: Optional[str] = None
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
```

#### Onboarding Status Enum
```python
class OnboardingStatus(Enum):
    PENDING = "pending"
    PENDING_APPROVAL = "pending_approval"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

## 📱 User Experience

### For New Users

1. **Join Team Chat** 🎉
   - User clicks invite link
   - Joins main team chat
   - Bot automatically welcomes them

2. **Admin Approval** ⏳
   - User sees "pending approval" message
   - Admin reviews in leadership chat
   - Admin approves or rejects

3. **Profile Setup** 📝
   - User confirms/updates details
   - Provides emergency contact
   - Enters date of birth

4. **FA Registration** 🏆
   - Confirms FA eligibility
   - Gets guidance on registration process
   - Contacts admin for documents

5. **Team Access** ✅
   - Receives welcome message
   - Gets access to team features
   - Can use team commands

### For Admins

1. **New User Notification** 🔔
   - Automatic notification in leadership chat
   - User details and Telegram info
   - Approval/rejection commands

2. **Approval Process** ✅
   - Review user details
   - Approve or reject with reason
   - Monitor onboarding progress

3. **FA Registration Support** 📋
   - Receive FA registration requests
   - Guide players through process
   - Collect documents and fees

## 🎮 Commands and Usage

### Admin Commands (Leadership Chat Only)

```bash
# View pending approvals
/pending

# Approve a player
/approve JS1

# Reject a player with reason
/reject JS1 "Already registered with another club"

# View player status
/status 07123456789

# List all players
/list
```

### User Commands (Main Chat)

```bash
# View your profile
/myinfo

# Get help
/help

# View team players
/list
```

### Onboarding Responses

Users can respond to onboarding prompts with:

- **Confirmation**: `yes`, `confirm`, `correct`
- **Updates**: `no`, `update`, `change`
- **Skip**: `skip`
- **Help**: `help`
- **FA Ready**: `ready`

## 🔧 Configuration

### Environment Variables

```bash
# Required for onboarding
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_MAIN_CHAT_ID=main_chat_id
TELEGRAM_LEADERSHIP_CHAT_ID=leadership_chat_id
TEAM_ID=your_team_id
```

### Bot Permissions

The bot needs these permissions in the Telegram group:
- ✅ Read messages
- ✅ Send messages
- ✅ Add members (for invite links)
- ✅ Manage chat (for invite links)

## 🧪 Testing

### Test Script

Run the onboarding workflow test:

```bash
python test_onboarding_workflow.py
```

This will test:
1. New member detection
2. Admin approval process
3. Profile completion
4. Emergency contact collection
5. Date of birth validation
6. FA eligibility check
7. FA registration guidance
8. Team access setup

### Manual Testing

1. **New User Joins**:
   - Send invite link to new user
   - User joins main chat
   - Verify onboarding starts

2. **Admin Approval**:
   - Check leadership chat for notification
   - Use `/pending` to see pending users
   - Use `/approve <player_id>` to approve

3. **Onboarding Flow**:
   - User responds to onboarding prompts
   - Verify each step completes correctly
   - Check final welcome message

## 🚨 Troubleshooting

### Common Issues

1. **Onboarding Not Starting**
   - Check bot permissions in group
   - Verify chat IDs are correct
   - Check bot is in main chat

2. **Admin Commands Not Working**
   - Ensure commands run in leadership chat
   - Check user has admin role
   - Verify team member permissions

3. **FA Registration Issues**
   - Confirm player eligibility
   - Check required documents
   - Verify registration fee payment

### Debug Logging

Enable debug logging to troubleshoot:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Error Messages

- **"User is already a team member"**: User already completed onboarding
- **"Not the main team chat"**: Command run in wrong chat
- **"Player not found"**: Player ID doesn't exist
- **"Access denied"**: User lacks permissions

## 🔄 Future Enhancements

### Planned Features

1. **Automated FA Registration**
   - Direct integration with FA systems
   - Automated document processing
   - Online payment integration

2. **Enhanced Validation**
   - Photo ID verification
   - Address verification
   - Age verification

3. **Multi-language Support**
   - Support for different languages
   - Localized messages and guidance

4. **Analytics Dashboard**
   - Onboarding completion rates
   - Time to complete onboarding
   - Drop-off point analysis

### Integration Opportunities

1. **Payment Systems**
   - Stripe integration for FA fees
   - Automated receipt generation

2. **Document Management**
   - Secure document storage
   - Automated document verification

3. **Communication Platforms**
   - Email notifications
   - SMS reminders
   - WhatsApp integration

## 📞 Support

For technical support or questions about the onboarding workflow:

1. Check the logs for error messages
2. Verify configuration settings
3. Test with the provided test script
4. Contact the development team

---

**Version**: 1.0.0  
**Last Updated**: 2024-12-19  
**Maintainer**: KICKAI Development Team 