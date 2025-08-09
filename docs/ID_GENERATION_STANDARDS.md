# KICKAI ID Generation Standards

## Overview

This document defines the standardized approach for generating unique identifiers (IDs) across the KICKAI system. The system uses three distinct ID generation utilities, each serving specific purposes with clear, human-readable formats.

## ID Generation Utilities

### 1. Football ID Generator (`football_id_generator.py`)
**Purpose**: Generate football-contextual IDs that make sense to football people  
**Use Cases**: When football context is important (positions, jersey numbers, competitions)

### 2. Simple ID Generator (`simple_id_generator.py`)
**Purpose**: Generate simple, human-readable IDs with initials and numbers  
**Use Cases**: Standard player and team member registration

### 3. User ID Generator (`user_id_generator.py`)
**Purpose**: Generate consistent user IDs from Telegram IDs  
**Use Cases**: Linking users across different roles (player/team member)

## ID Format Standards

### Player ID

#### Standard Format (Simple ID Generator)
```
Format: {Number}{Initials}
Examples:
- 01MH (First Mahmudul Hoque)
- 02MH (Second Mahmudul Hoque)
- 01JS (John Smith)
```

**Generation Rules:**
- Extract initials from full name (first letter of each word)
- Use 2-digit sequential number starting from 01
- Increment number for same initials to avoid collisions
- Maximum 99 players with same initials (fallback to hash suffix)

#### Football Context Format (Football ID Generator)
```
Format: {JerseyNumber}{PositionCode}{Initials}
Examples:
- 01GKJS (Jersey #1, Goalkeeper, John Smith)
- 10MFMH (Jersey #10, Midfielder, Mahmudul Hoque)
- 09FWAB (Jersey #9, Forward, Alex Brown)
```

**Position Codes:**
- GK: Goalkeeper
- DF: Defender
- MF: Midfielder
- FW: Forward
- WG: Winger
- ST: Striker

**Jersey Number Assignment:**
- Position-appropriate numbers (1 for GK, 9 for FW, etc.)
- Avoids duplicates within team
- Falls back to next available number

### Team Member ID

#### Standard Format
```
Format: user_{Number}{Initials}
Examples:
- user_01MH (Mahmudul Hoque)
- user_02JS (John Smith)
```

**Generation Rules:**
- Prefix "user_" to distinguish from player IDs
- Same initials and numbering logic as player IDs

### Team ID

#### Simple Format (Default)
```
Format: {TeamCode}
Examples:
- KTI (Kicks Team International)
- AFC (Arsenal Football Club)
- MCI (Manchester City)
```

**Generation Rules:**
- 3-4 character abbreviation
- First letter of each word for multi-word names
- First 3-4 letters for single-word names
- All uppercase

#### League Context Format (Football ID Generator)
```
Format: {LeaguePrefix}{TeamCode}
Examples:
- PLMCI (Premier League Manchester City)
- SUNKAI (Sunday League Kicks AI)
- NONTFC (Non-League Town FC)
```

**League Prefixes:**
- PL: Premier League
- EFL: EFL Championship
- EFL1: EFL League One
- EFL2: EFL League Two
- FA: FA Cup
- EFLC: EFL Cup
- SUN: Sunday League
- FRI: Friendly
- NON: Non-League

### Match ID

#### Standard Format
```
Format: M{DD}{MM}{HomeTeam}{AwayTeam}
Examples:
- M1501KTIAFC (15th January, KTI vs AFC)
- M2503MCILIV (25th March, MCI vs LIV)
```

**Generation Rules:**
- Prefix "M" for match
- 2-digit day (DD)
- 2-digit month (MM)
- Home team code
- Away team code
- Collision resolution with numeric suffix if needed

#### Alternative Format (Simple ID Generator)
```
Format: MATCH_{YYYY-MM-DD}_{TeamID}_{OpponentClean}
Example: MATCH_2024-01-15_KTI_ARSENAL
```

### User ID (Cross-Role Linking)

```
Format: user_{telegram_id}
Examples:
- user_8148917292
- user_123456789
```

**Purpose:**
- Links Team Members and Players for the same person
- Consistent identification across different roles
- Direct mapping to Telegram user ID

### Availability ID

```
Format: AVAIL_{MatchID}_{PlayerID}
Example: AVAIL_M1501KTIAFC_01MH
```

### Attendance ID

```
Format: ATTEND_{MatchID}_{PlayerID}
Example: ATTEND_M1501KTIAFC_01MH
```

### Training Session ID

```
Format: TRAIN{DD}{MM}{TeamID}-{TypeCode}-{Time}
Examples:
- TRAIN1501KTI-TECH-1800 (15th Jan, KTI, Technical Skills, 6:00 PM)
- TRAIN2003AFC-FIT-0900 (20th March, AFC, Fitness, 9:00 AM)
```

**Training Type Codes:**
- TECH: Technical Skills
- TACT: Tactical Awareness
- FIT: Fitness Conditioning
- MATCH: Match Practice
- REC: Recovery Session

## Implementation Guidelines

### 1. Choosing the Right Generator

**Use Simple ID Generator when:**
- Registering new players or team members
- Simple, clean IDs are sufficient
- No football context needed

**Use Football ID Generator when:**
- Football context is important
- Jersey numbers and positions matter
- League/competition context needed

**Use User ID Generator when:**
- Linking entities across roles
- Working with Telegram user IDs
- Need consistent cross-role identification

### 2. Collision Handling

All generators implement collision detection:
1. Check if generated ID exists
2. If collision, increment counter or add suffix
3. Maximum 99 attempts with counter
4. Fallback to hash suffix for extreme cases

### 3. ID Persistence

- IDs are immutable once created
- Store ID mappings for consistency
- Same input always generates same ID (idempotent)

### 4. Migration Considerations

When migrating existing data:
1. Preserve existing IDs where possible
2. Generate new IDs only for entities without IDs
3. Maintain mapping tables for legacy ID references
4. Use batch generation to ensure uniqueness

## Code Examples

### Player Registration
```python
from kickai.utils.simple_id_generator import generate_simple_player_id

# Standard registration
player_id = generate_simple_player_id(
    name="Mahmudul Hoque",
    team_id="KTI",
    existing_ids=existing_player_ids
)
# Result: "01MH"
```

### Football Context Registration
```python
from kickai.utils.football_id_generator import generate_football_player_id

# With football context
player_id = generate_football_player_id(
    name="John Smith",
    position="Goalkeeper",
    team_id="KTI",
    existing_ids=existing_player_ids
)
# Result: "01GKJS"
```

### Cross-Role User Linking
```python
from kickai.utils.user_id_generator import generate_user_id

# Link user across roles
user_id = generate_user_id(telegram_id=8148917292)
# Result: "user_8148917292"
```

### Match Creation
```python
from kickai.utils.football_id_generator import generate_football_match_id

# Create match ID
match_id = generate_football_match_id(
    home_team="Kicks Team International",
    away_team="Arsenal FC",
    match_date="2024-01-15",
    competition="FRIENDLY"
)
# Result: "M1501KTIAFC"
```

## Validation

### ID Format Validation
```python
import re

# Player ID: {Number}{Initials}
player_pattern = r'^[0-9]{2}[A-Z]{2}[0-9]?$'

# Team Member ID: user_{Number}{Initials}
member_pattern = r'^user_[0-9]{2}[A-Z]{2}[0-9]?$'

# Match ID: M{DD}{MM}{Teams}
match_pattern = r'^M[0-9]{4}[A-Z]{3,8}[0-9]?$'

# User ID: user_{telegram_id}
user_pattern = r'^user_[0-9]+$'
```

## Best Practices

1. **Always provide existing_ids** parameter to prevent collisions
2. **Use appropriate generator** based on context
3. **Store ID mappings** for consistency
4. **Validate IDs** before database operations
5. **Log ID generation** for audit trail
6. **Handle edge cases** (empty names, special characters)
7. **Maintain backward compatibility** when updating formats

## Migration Strategy

### From Legacy to New IDs
1. Identify entities without standardized IDs
2. Generate new IDs using appropriate generator
3. Create mapping table: `legacy_id -> new_id`
4. Update references gradually
5. Maintain dual support during transition
6. Deprecate legacy IDs after full migration

## Error Handling

### Common Scenarios
- **Empty name**: Use "XX" for initials
- **Single name**: Duplicate initial (John -> JJ)
- **Special characters**: Remove before processing
- **Collision limit**: Fallback to hash suffix
- **Invalid format**: Raise ValueError with clear message

## Testing Requirements

### Unit Tests
- ID generation for various name formats
- Collision handling
- Edge cases (empty, special characters)
- Format validation

### Integration Tests
- Database persistence
- Cross-service ID usage
- Migration scenarios
- Performance with large datasets

## Performance Considerations

- ID generation is O(1) for non-collision cases
- Collision resolution is O(n) worst case
- Cache generated IDs in memory
- Batch generation for bulk operations
- Index ID fields in database

## Future Enhancements

1. **UUID Support**: Optional UUID fallback for extreme scale
2. **Custom Prefixes**: Configurable prefixes per deployment
3. **ID Analytics**: Track ID usage patterns
4. **Auto-Migration**: Automated legacy ID migration tools
5. **ID Recycling**: Safe reuse of deleted entity IDs

## Conclusion

This standardized ID generation approach ensures:
- **Human-readable** IDs for easy communication
- **Consistent** formats across the system
- **Collision-free** generation with proper handling
- **Football-contextual** options when needed
- **Cross-role** linking capabilities

Follow these standards to maintain data integrity and system consistency across all KICKAI components.