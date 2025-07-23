# KICKAI Enums Architecture

## Overview

KICKAI uses a **single source of truth** approach for all enums across the system. All shared enums are defined in one high-level file to prevent circular imports and maintain clean architecture principles.

## Single Source of Truth

### Location
- **File**: `src/core/enums.py`
- **Purpose**: Central repository for all shared enums
- **Import Pattern**: `from core.enums import EnumName`

### Why This Approach?

1. **Prevents Circular Imports**: All modules import from the same source
2. **Clean Architecture**: Follows dependency inversion principle
3. **Maintainability**: Single place to update enum definitions
4. **Consistency**: Ensures all modules use the same enum values

## Enum Categories

### Core System Enums
- `ChatType` - Chat types (MAIN, LEADERSHIP, PRIVATE)
- `PermissionLevel` - Permission levels (PUBLIC, PLAYER, LEADERSHIP, ADMIN, SYSTEM)
- `CommandType` - Command categories
- `AgentRole` - CrewAI agent roles

### Business Domain Enums
- `TeamStatus` - Team status values
- `PaymentType` - Payment types
- `PaymentStatus` - Payment status values
- `ExpenseCategory` - Expense categories

### Technical Enums
- `AIProvider` - AI service providers
- `HealthStatus` - System health status
- `ComponentType` - System component types
- `AlertLevel` - Alert levels
- `TaskStatus` - Task execution status
- `ErrorSeverity` - Error severity levels
- `Environment` - Environment types

### Memory and Cache Enums
- `MemoryType` - Memory storage types
- `MemoryPriority` - Memory priority levels
- `CacheNamespace` - Cache namespace types

### ID and State Enums
- `IDType` - ID generation types
- `ApplicationState` - Application state values

## Usage Guidelines

### Import Pattern
```python
# ✅ Correct - Import from high-level enums
from core.enums import ChatType, PermissionLevel

# ❌ Incorrect - Don't import from feature-specific locations
from features.shared.domain.enums import ChatType  # OLD - REMOVED
```

### Adding New Enums
1. Add the enum to `src/core/enums.py`
2. Update this documentation
3. Update any affected modules to use the new enum

### Migration from Old Structure
The old `src/features/shared/domain/enums.py` has been removed. All imports should now use:
```python
from core.enums import EnumName
```

## Benefits

### 1. Circular Import Prevention
- All modules import from the same source
- No dependency cycles between features
- Clean dependency hierarchy

### 2. Maintainability
- Single file to update enum definitions
- Consistent enum values across the system
- Easy to track enum usage

### 3. Clean Architecture
- Follows dependency inversion principle
- High-level modules don't depend on low-level modules
- Enums are at the highest level of abstraction

### 4. Type Safety
- All enums are properly typed
- IDE support for enum values
- Compile-time checking for enum usage

## Migration Checklist

- [x] Created `src/core/enums.py` with all shared enums
- [x] Updated `PermissionService` to import from `enums`
- [x] Updated `ChatRoleAssignmentService` to import from `enums`
- [x] Updated `PermissionChecker` to import from `enums`
- [x] Updated `ChatMemberHandler` to import from `enums`
- [x] Updated `BehavioralMixins` to import from `enums`
- [x] Removed old `src/features/shared/domain/enums.py`
- [x] Verified no circular imports
- [x] Tested all imports work correctly

## Future Considerations

1. **Enum Validation**: Consider adding validation for enum values
2. **Enum Serialization**: Ensure enums serialize correctly for database storage
3. **Enum Documentation**: Keep enum descriptions up to date
4. **Enum Testing**: Add tests for enum behavior and values

## Related Files

- `src/core/enums.py` - Single source of truth for all enums
- `src/features/system_infrastructure/domain/services/permission_service.py` - Uses ChatType and PermissionLevel
- `src/features/team_administration/domain/services/chat_role_assignment_service.py` - Uses ChatType
- `src/bot_telegram/message_handling/validation/permission_checker.py` - Uses ChatType and PermissionLevel
- `src/bot_telegram/chat_member_handler.py` - Uses ChatType
- `src/agents/behavioral_mixins.py` - Uses ChatType 