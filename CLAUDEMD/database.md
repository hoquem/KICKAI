# Database - Firebase Integration & Data Patterns

## Firebase Integration
- Collections prefixed with `kickai_` (e.g., `kickai_teams`, `kickai_players`)
- All database operations are async
- Use repository pattern - no direct Firestore access from tools/services

## Critical Migrations

### Emergency Contact Field Migration (CRITICAL)
**Current Architecture:** Uses separate fields with NO fallback support
- ✅ `emergency_contact_name` (string)
- ✅ `emergency_contact_phone` (string)  
- ❌ `emergency_contact` (legacy - completely removed, no fallback)

**Migration:** `PYTHONPATH=. python scripts/migrate_emergency_contact_fields.py`

## Database Architecture Patterns

### Repository Pattern
```python
# Interface Definition
class PlayerRepositoryInterface:
    async def get_player_by_id(self, player_id: str, team_id: str) -> Optional[Player]:
        pass
    
    async def create_player(self, player: Player) -> Player:
        pass

# Firebase Implementation
class FirebasePlayerRepository(PlayerRepositoryInterface):
    def __init__(self, db: firestore.Client):
        self.db = db
    
    async def get_player_by_id(self, player_id: str, team_id: str) -> Optional[Player]:
        doc = await self.db.collection(f'kickai_teams/{team_id}/players').document(player_id).get()
        return Player.from_dict(doc.to_dict()) if doc.exists else None
```

### Entity Patterns
```python
@dataclass
class Player:
    player_id: str
    team_id: str
    name: str
    emergency_contact_name: str  # NEW: Separate field
    emergency_contact_phone: str # NEW: Separate field
    status: MemberStatus = MemberStatus.ACTIVE
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Convert database dict to Player entity with proper enum handling."""
        return cls(
            player_id=data['player_id'],
            team_id=data['team_id'],
            name=data['name'],
            emergency_contact_name=data.get('emergency_contact_name', ''),
            emergency_contact_phone=data.get('emergency_contact_phone', ''),
            status=MemberStatus(data.get('status', 'active'))
        )
```

## Database Collections Structure
```
kickai_teams/
├── {team_id}/
│   ├── players/           # Team players
│   ├── team_members/      # Team staff/administration
│   ├── matches/           # Match records
│   ├── availability/      # Player availability
│   └── settings/          # Team configuration

kickai_system/
├── users/                 # Global user registry
├── invites/              # Invitation links
└── audit_logs/           # System audit trail
```

## Data Access Rules
- **Tools**: NEVER access database directly - always use services
- **Services**: Use repository interfaces - never direct Firestore calls
- **Repositories**: Only layer allowed to interact with Firebase
- **Entities**: Immutable data objects with validation

## Firebase Configuration
```bash
# Environment variables
FIREBASE_PROJECT_ID=<your_project>
FIREBASE_CREDENTIALS_FILE=credentials/<file>.json

# Credential files
credentials/
├── firebase_credentials_template.json
├── firebase_credentials_testing.json
└── firebase_credentials_production.json
```