# One-Off Scripts

This directory contains one-off scripts for specific tasks and maintenance operations.

## Scripts

### `add_leadership_admins.py`

**Purpose**: Adds all administrators from the leadership Telegram chat as team members in Firestore.

**What it does**:
1. Connects to Telegram using the bot token
2. Gets the list of administrators in the leadership chat
3. Checks for existing team members in Firestore
4. Adds new administrators as team members with appropriate roles
5. Provides a summary of the operation

**Usage**:
```bash
# Activate virtual environment
source venv/bin/activate

# Run the script
python scripts-oneoff/add_leadership_admins.py
```

**Environment Variables Required**:
- `TELEGRAM_BOT_TOKEN`: The bot token for Telegram API access
- `TELEGRAM_LEADERSHIP_CHAT_ID`: The chat ID of the leadership chat
- `TEAM_ID`: The team ID (defaults to 'KTI' if not specified)

**Output**:
- Logs the process to console
- Shows summary of added members
- Reports any errors encountered

**Role Assignment**:
- Chat Creator → "Team Owner"
- Chat Administrator → "Team Administrator"
- Other members → "Team Member"

**Safety Features**:
- Checks for existing team members to avoid duplicates
- Handles errors gracefully
- Provides detailed logging
- Only adds new members (doesn't modify existing ones)

**Example Output**:
```
🤖 Leadership Admin Addition Script
==================================================
Team ID: KTI
Initialized LeadershipAdminAdder for team: KTI
Leadership chat ID: -4969733370
🚀 Starting leadership admin addition process...
Fetching chat administrators...
Found admin: John Smith (@johnsmith) - Status: creator
Found admin: Jane Doe (@janedoe) - Status: administrator
Found 2 chat members
Found 0 existing team members
📝 Found 2 new members to add
✅ Added team member: John Smith as Team Owner
✅ Added team member: Jane Doe as Team Administrator
📊 Summary:
   Total chat members: 2
   Existing team members: 0
   New members added: 2
   Errors: 0
✅ Leadership admin addition completed successfully!
```

**When to use**:
- Initial team setup
- After adding new administrators to the leadership chat
- When team members need to be synchronized with chat administrators
- As a maintenance task to ensure consistency

**Notes**:
- This script is safe to run multiple times
- It will only add new members, not modify existing ones
- All added members will have admin privileges in the system
- The script uses the same Firestore collections as the main application

### `manage_team_members.py`

**Purpose**: Comprehensive team member management script for backend support engineers.

**What it does**:
1. Add new team members with validation
2. Check if team members are in leadership chat
3. Get Telegram information for team members
4. Validate existing team member data
5. List all team members with their status
6. Remove team members (with confirmation)

**Usage**:
```bash
# Activate virtual environment
source venv/bin/activate

# Add a new team member
python scripts-oneoff/manage_team_members.py --action add --team-id KTI --name "John Smith" --phone "+1234567890" --role "admin" --telegram-id "123456789" --telegram-username "johnsmith"

# List all team members
python scripts-oneoff/manage_team_members.py --action list --team-id KTI

# Validate team members against leadership chat
python scripts-oneoff/manage_team_members.py --action validate --team-id KTI

# Remove a team member
python scripts-oneoff/manage_team_members.py --action remove --team-id KTI --telegram-id "123456789"
```

**Environment Variables Required**:
- `TELEGRAM_BOT_TOKEN`: The bot token for Telegram API access
- `TELEGRAM_LEADERSHIP_CHAT_ID`: The chat ID of the leadership chat

**Actions**:
- **add**: Add a new team member (requires name, phone, role)
- **list**: List all team members with details
- **validate**: Validate team members against leadership chat membership
- **remove**: Remove a team member (requires telegram-id)

**Features**:
- Validates team members are in leadership chat
- Checks for duplicate phone numbers
- Provides detailed validation reports
- Safe removal with confirmation
- Comprehensive logging and error handling

**Example Output (validate)**:
```
🤖 Team Member Management Script
==================================================
Team ID: KTI
Action: validate
Initialized TeamMemberManager for team: KTI
Collection: kickai_KTI_team_members
Leadership chat ID: -4969733370
🔍 Starting team member validation...
Fetching leadership chat members...
Found member: John Smith (@johnsmith) - Status: administrator
Found member: Jane Doe (@janedoe) - Status: member
Found 2 members in leadership chat
Found 2 team members in Firestore
📊 Validation Results:
   Total members: 2
   In leadership chat: 1
   Not in leadership chat: 1
   Missing Telegram info: 0

📋 Detailed Results:
✅ John Smith (+1234567890)
❌ Jane Doe (+0987654321)
   ⚠️  Not in leadership chat
```

**When to use**:
- Backend support engineer tasks
- Team member onboarding and validation
- Data consistency checks
- Team member management and cleanup
- Troubleshooting team member issues

**Notes**:
- Requires manual verification for phone number matching
- Validates against actual Telegram chat membership
- Provides comprehensive audit trail
- Safe for production use with proper validation 