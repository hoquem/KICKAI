# Database - Firebase Patterns & Access

## Firebase Architecture
**Database:** Firebase Firestore with async operations
**Pattern:** Repository pattern with Clean Architecture

## Repository Pattern
```python
# Domain interface
class PlayerRepositoryInterface(ABC):
    @abstractmethod
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str) -> Optional[Player]:
        pass

# Infrastructure implementation  
class FirebasePlayerRepository(PlayerRepositoryInterface):
    def __init__(self, database: DataStoreInterface):
        self.database = database
        
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str):
        collection = self.database.collection('kickai_players')
        query = collection.where('telegram_id', '==', telegram_id).where('team_id', '==', team_id)
        docs = await query.get()
        return Player.from_dict(docs[0].to_dict()) if docs else None
```

## Collection Structure
- `kickai_teams` - Team configurations
- `kickai_players` - Player registrations  
- `kickai_team_members` - Team staff/members
- `kickai_matches` - Match information
- `kickai_availability` - Player availability

## Data Access Rules
- **Domain Services:** Use repository interfaces only
- **Infrastructure:** Implement Firebase-specific logic
- **Testing:** Mock repositories for unit tests, real Firebase for integration tests

## Common Patterns
```python
# Async operations (always)
player = await player_repository.get_player_by_telegram_id(telegram_id, team_id)

# Error handling
try:
    result = await repository.create_player(player)
except DatabaseError as e:
    return create_json_response(ResponseStatus.ERROR, message=str(e))

# Batch operations
players = await repository.get_players_by_team(team_id)
```

## Testing Database
- **Unit Tests:** Mock repositories with test data
- **Integration Tests:** Use Firebase test environment
- **E2E Tests:** Clean test data after each run

**Database Manager:** `kickai/core/database/database_manager.py`