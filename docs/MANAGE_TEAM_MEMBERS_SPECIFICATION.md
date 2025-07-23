# Team Member Management Script Specification

## Overview

The `manage_team_members.py` script is a comprehensive team member management tool that synchronizes team members between Telegram leadership chats and Firestore. It ensures data consistency between the Telegram chat membership and the Firestore database.

## Core Functionality

### 1. Team Selection
- **Source**: Reads teams from `kickai_teams` collection in Firestore
- **Configuration**: Uses bot settings from `settings` object within team documents
- **Display**: Shows team name, ID, configuration status, and bot details
- **Selection**: Interactive team selection with validation

### 2. Team Member Synchronization

#### 2.1 Telegram Leadership Chat Analysis
- **Connection**: Uses team's bot token to connect to Telegram API
- **Chat Members**: Fetches all members from the leadership chat
- **Data Extraction**: Extracts member details including:
  - Telegram ID
  - Username
  - Full name
  - Admin status
  - Join date

#### 2.2 Firestore Team Members Analysis
- **Collection**: Reads from `kickai_{team_id}_team_members` collection
- **Data Structure**: TeamMember objects with:
  - `id`: Unique identifier
  - `team_id`: Team identifier
  - `user_id`: User identifier
  - `telegram_id`: Telegram user ID
  - `username`: Telegram username
  - `first_name`, `last_name`, `full_name`: Name components
  - `role`: Member role (e.g., "Club Administrator", "Player")
  - `status`: Member status ("active", "inactive", "pending")
  - `is_admin`: Admin status boolean
  - `created_at`, `updated_at`: Timestamps

#### 2.3 Synchronization Logic

##### Scenario 1: Telegram Members Not in Firestore
- **Detection**: Members in Telegram chat but not in Firestore
- **Action**: Offer to add them to Firestore
- **Process**:
  1. Display list of Telegram-only members
  2. Prompt for role assignment
  3. Add to Firestore with default status "active"
  4. Confirm addition

##### Scenario 2: Firestore Members Not in Telegram
- **Detection**: Members in Firestore but not in Telegram chat
- **Action**: Offer to either:
  - Add them to Telegram leadership chat (if possible)
  - Remove them from Firestore
- **Process**:
  1. Display list of Firestore-only members
  2. For each member, offer options:
     - Add to Telegram chat (requires username/contact)
     - Remove from Firestore
     - Skip (keep as is)

##### Scenario 3: Members in Both (Synchronized)
- **Detection**: Members present in both Telegram and Firestore
- **Action**: Display current status and offer updates
- **Process**:
  1. Show synchronized members
  2. Allow role/status updates
  3. Confirm changes

## Menu Structure

### Main Menu Options
1. **Synchronize Team Members** - Main synchronization workflow
2. **View Current Members** - Display all team members from both sources
3. **Add Team Member** - Manual addition to Firestore
4. **Update Team Member** - Modify existing member details
5. **Remove Team Member** - Remove from Firestore
6. **Exit** - Quit the application

### Synchronization Workflow
1. **Analysis Phase**
   - Fetch Telegram leadership chat members
   - Fetch Firestore team members
   - Compare and categorize members

2. **Display Phase**
   - Show summary of findings
   - Display members by category:
     - 🔵 Telegram Only (need to add to Firestore)
     - 🟡 Firestore Only (need to sync or remove)
     - 🟢 Synchronized (both sources)

3. **Action Phase**
   - Process Telegram-only members
   - Process Firestore-only members
   - Update synchronized members

## Data Models

### Team Model
```python
@dataclass
class Team:
    id: str
    name: str
    bot_token: Optional[str]
    main_chat_id: Optional[str]
    leadership_chat_id: Optional[str]
    settings: Dict[str, Any]
```

### TeamMember Model
```python
@dataclass
class TeamMember:
    id: str
    team_id: str
    user_id: str
    telegram_id: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    role: str
    status: str
    is_admin: bool
    created_at: Optional[str]
    updated_at: Optional[str]
```

### TelegramMember Model
```python
@dataclass
class TelegramMember:
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    is_admin: bool
    join_date: Optional[str]
```

## Error Handling

### Connection Errors
- **Firebase Connection**: Graceful handling of credential issues
- **Telegram Connection**: Validation of bot token and chat access
- **Network Issues**: Retry logic with exponential backoff

### Data Validation
- **Required Fields**: Validation of essential member data
- **Duplicate Detection**: Prevention of duplicate entries
- **Format Validation**: Phone numbers, usernames, etc.

### User Input Validation
- **Menu Selection**: Valid range checking
- **Confirmation Prompts**: Clear yes/no options
- **Data Entry**: Format validation for user inputs

## Security Considerations

### Access Control
- **Bot Permissions**: Verify bot has admin rights in leadership chat
- **Firebase Security**: Use service account with appropriate permissions
- **Data Privacy**: Mask sensitive information in logs

### Data Integrity
- **Backup**: Create backup before bulk operations
- **Transaction Safety**: Use Firestore transactions for critical updates
- **Audit Trail**: Log all member changes

## Configuration

### Environment Variables
- `FIREBASE_CREDENTIALS_FILE`: Path to Firebase service account JSON
- `TELEGRAM_BOT_TOKEN`: Default bot token (if not in Firestore)

### Firestore Collections
- `kickai_teams`: Team configuration data
- `kickai_{team_id}_team_members`: Team member data

### Telegram API
- **Rate Limiting**: Respect Telegram API rate limits
- **Error Handling**: Handle API errors gracefully
- **Retry Logic**: Implement retry for transient failures

## Usage Examples

### Basic Synchronization
```bash
python scripts/manage_team_members_standalone.py
```

### Workflow Example
1. Select team from list
2. Choose "Synchronize Team Members"
3. Review analysis results
4. Process Telegram-only members (add to Firestore)
5. Process Firestore-only members (sync or remove)
6. Update synchronized members as needed
7. Confirm all changes

## Future Enhancements

### Planned Features
- **Bulk Operations**: Process multiple members simultaneously
- **Import/Export**: CSV import/export functionality
- **Role Templates**: Predefined role configurations
- **Audit Reports**: Detailed change history
- **Automated Sync**: Scheduled synchronization

### Integration Points
- **Player Registration System**: Integration with existing registration flow
- **Notification System**: Alert team admins of member changes
- **Analytics**: Member activity and engagement metrics

## Testing Strategy

### Unit Tests
- Data model validation
- Synchronization logic
- Error handling

### Integration Tests
- Firebase connectivity
- Telegram API integration
- End-to-end workflows

### Manual Testing
- Real team synchronization
- Error scenario testing
- User experience validation

## Maintenance

### Logging
- **Structured Logging**: JSON format for easy parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Log Rotation**: Prevent log file bloat

### Monitoring
- **Health Checks**: Verify script functionality
- **Performance Metrics**: Track execution times
- **Error Tracking**: Monitor failure rates

### Documentation
- **Code Comments**: Inline documentation
- **User Guide**: Step-by-step usage instructions
- **Troubleshooting**: Common issues and solutions 