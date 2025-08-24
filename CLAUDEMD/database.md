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

## Clean Architecture Database Implementation ✅

### Repository Pattern (Uncle Bob's Clean Architecture)
```python
# Domain Layer - Abstract Interface
class PlayerRepositoryInterface(ABC):
    @abstractmethod
    async def get_player_by_id(self, player_id: str, team_id: str) -> Optional[Player]:
        pass
    
    @abstractmethod
    async def create_player(self, player: Player) -> Player:
        pass

# Infrastructure Layer - Firebase Implementation
class FirebasePlayerRepository(PlayerRepositoryInterface):
    def __init__(self, database: DataStoreInterface):  # Dependency inversion
        self.database = database
    
    async def get_player_by_id(self, player_id: str, team_id: str) -> Optional[Player]:
        doc = await self.database.get_document(f'kickai_teams/{team_id}/players/{player_id}')
        return Player.from_dict(doc) if doc else None
```

### Dependency Injection Pattern
```python
# Application Layer - Tool uses container
@tool("get_player_status", result_as_answer=True)
async def get_player_status(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    container = get_container()  # ✅ OK in application layer
    service = container.get_service(PlayerService)
    result = await service.get_player_status(telegram_id=telegram_id, team_id=team_id)
    return create_json_response(ResponseStatus.SUCCESS, data=result)

# Domain Layer - Service uses constructor injection
class PlayerService:
    def __init__(self, player_repository: PlayerRepositoryInterface):  # ✅ Pure DI
        self.player_repository = player_repository  # No container dependency
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

## Clean Architecture Data Access Rules (Strictly Enforced)
- **Application Layer (Tools)**: Use `get_container()`, access domain services only
- **Domain Layer (Services)**: Use constructor-injected repositories, NO container access  
- **Domain Layer (Repositories)**: Abstract interfaces only, NO implementation details
- **Infrastructure Layer**: Firebase implementations, database connections, external APIs
- **Entities**: Pure business objects with validation, framework-agnostic

### Layer Boundaries
```python
# ✅ CORRECT: Clean architecture pattern
Application → Domain Services → Repository Interface ← Infrastructure Implementation

# ❌ WRONG: Direct database access
Application → Database (violates clean architecture)

# ❌ WRONG: Container in domain
Domain Service → get_container() (violates dependency rule)
```

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