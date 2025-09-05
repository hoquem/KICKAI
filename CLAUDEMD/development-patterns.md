# Development Patterns - Clean Architecture Guide

## Layer Structure (Clean Architecture ✅)
```
kickai/features/[feature]/
├── application/tools/     # @tool decorators (CrewAI interface)
├── domain/
│   ├── entities/         # Business objects
│   ├── services/         # Pure business logic
│   └── repositories/     # Abstract interfaces
└── infrastructure/       # Firebase, external APIs
```

**Rules:** Domain → no external deps | Application → uses domain | Infrastructure → implements domain interfaces

## Development Patterns

### Context-Aware Tool Pattern (NEW - 2025-09-02)
**Problem:** Tools lacked context awareness, causing routing confusion (e.g., `/myinfo` using member tools in player context)

**Solution:** Context-specific tool naming and implementation
```python
# PLAYER context tools (main/private chat) - use "_player_" in name
@tool("get_player_status_current") 
def get_player_status_current(telegram_id: str, team_id: str) -> str:
    """Get current user's player status - for game participants."""
    return await get_player_status_current_domain(telegram_id, team_id)

# MEMBER context tools (leadership chat) - use "_member_" in name
@tool("get_member_status_current")
def get_member_status_current(telegram_id: str, team_id: str) -> str:
    """Get current user's member status - for admins/leadership."""  
    return await get_member_status_current_domain(telegram_id, team_id)

# Context-aware naming prevents routing confusion
# Agent backstories specify which tools to use in which context
```

**Context-Aware Agent Integration:**
```yaml
# agents.yaml - Agent backstories include context understanding
PLAYER_COORDINATOR:
  backstory: |
    🎯 CONTEXT UNDERSTANDING:
    You handle PLAYERS - people who participate in matches and games.
    Users in MAIN CHAT and PRIVATE CHAT are treated as PLAYERS.
    
    TOOL SELECTION BY CONTEXT:
    • /myinfo → get_player_status_current (current user as player)
    • /info [name] → get_player_status (lookup any player)

TEAM_ADMINISTRATOR:
  backstory: |
    🎯 CONTEXT UNDERSTANDING: 
    You handle TEAM MEMBERS - administrative users and leadership roles.
    Users in LEADERSHIP CHAT are treated as TEAM MEMBERS.
    
    TOOL SELECTION BY CONTEXT:
    • /myinfo → get_member_status_current (current user as member/admin)
    • /info [name] → get_member_status (lookup any member)
```

### Tool Implementation (Standard Pattern)
```python
# Application: features/*/application/tools/
@tool("name")
async def name(
    telegram_id: str,  # Only include if tool needs user identity
    team_id: str,      # Only include if tool needs team context
    specific_param: str # Tool-specific parameters as needed
) -> str:
    return await name_domain(telegram_id, team_id, specific_param)

# Domain: features/*/domain/tools/ (no @tool decorator)
async def name_domain(telegram_id: str, team_id: str, specific_param: str) -> str:
    # Convert telegram_id to int internally when needed for database
    telegram_id_int = int(telegram_id) if telegram_id else 0
    
    service = get_container().get_service(ServiceClass)
    result = await service.method(telegram_id_int, team_id, specific_param)
    
    # Return plain text response for CrewAI
    return f"✅ Operation completed successfully: {result}"
```

### Service Implementation Pattern
```python
# Domain service with dependency injection
class PlayerService:
    def __init__(self, repository: PlayerRepositoryInterface):
        self.repository = repository
    
    async def get_by_telegram_id(self, telegram_id: int, team_id: str):
        return await self.repository.get_player_by_telegram_id(telegram_id, team_id)

# Repository interface (domain)
class PlayerRepositoryInterface(ABC):
    @abstractmethod
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str) -> Optional[Player]:
        pass

# Repository implementation (infrastructure)
class FirebasePlayerRepository(PlayerRepositoryInterface):
    def __init__(self, database: DataStoreInterface):
        self.database = database
        
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str):
        # Firebase implementation
        pass
```

### Entity Pattern
```python
@dataclass
class Player:
    id: str
    team_id: str
    telegram_id: str  # String type for LLM compatibility
    name: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Tool not found | Export from feature `__init__.py` |
| Import errors | Always use `PYTHONPATH=.` |
| Service unavailable | Check container initialization |
| Async errors | Use `async def` for all tools |
| Type errors | `telegram_id` is `str` in tools (convert to `int` in services), `team_id` is `str` |
| Wrong agent routing | Check chat_type context - main/private=PLAYER, leadership=MEMBER |
| Tool context confusion | Use context-aware naming: `get_player_*` vs `get_member_*` |
| /myinfo wrong data | Ensure correct context: main chat → player tools, leadership → member tools |

## Testing Patterns
```python
# Unit test (domain)
@pytest.mark.asyncio
async def test_service_logic():
    mock_repo = Mock()
    service = PlayerService(mock_repo)
    result = await service.get_by_telegram_id(123, "TEST")
    mock_repo.get_player_by_telegram_id.assert_called_once()

# Integration test (tool)  
@pytest.mark.asyncio
async def test_tool_integration():
    result = await tool_name(
        telegram_id="123456789",  # String type for tools
        team_id="TEST"
        # Only include parameters this specific tool needs
    )
    assert "✅" in result  # Plain text success indicator
```

### Context-Aware Testing Patterns
```python
# Test context-aware routing behavior
@pytest.mark.asyncio
async def test_context_aware_routing():
    from kickai.agents.crew_agents import TeamManagementSystem
    
    team_system = TeamManagementSystem('TEST')
    
    # Test different chat contexts
    main_context = {'chat_type': 'main', 'telegram_id': '123', 'team_id': 'TEST'}
    leadership_context = {'chat_type': 'leadership', 'telegram_id': '123', 'team_id': 'TEST'}
    
    # Main chat should route to player tools
    main_response = await team_system.execute_task('/myinfo', main_context)
    assert 'player' in main_response.lower()  # Should use player tools
    
    # Leadership chat should route to member tools  
    leadership_response = await team_system.execute_task('/myinfo', leadership_context)
    assert 'member' in leadership_response.lower()  # Should use member tools

# Test context-specific tool behavior
@pytest.mark.asyncio
async def test_player_vs_member_tools():
    # Player context tool
    player_result = await get_player_status_current('123', 'TEST')
    assert 'player' in player_result.lower()
    
    # Member context tool
    member_result = await get_member_status_current('123', 'TEST') 
    assert 'member' in member_result.lower()
```

**Migration Status:** ✅ 62 @tool decorators moved to application layer, clean architecture complete | ✅ Context-aware routing implemented