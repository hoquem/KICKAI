# Clean Architecture Compliance Refactoring Plan

**Project:** KICKAI AI Football Team Management System  
**Goal:** 100% compliance with Clean Architecture dependency rules  
**Estimated Timeline:** 3-4 weeks  
**Risk Level:** Medium (extensive changes but well-structured)

## Executive Summary

The KICKAI project has good architectural foundations but violates Clean Architecture in three key areas:
1. Framework dependencies in domain layer (`@tool` decorators)
2. Direct database access bypassing repository interfaces
3. Domain services knowing about dependency injection container

This plan provides a systematic approach to achieve 100% Clean Architecture compliance while maintaining all existing functionality.

## Current Architecture Assessment

### ✅ **Strengths (Keep)**
- Repository pattern with interfaces
- Feature-first organization
- Dependency injection container
- Clear separation of entities and services

### ❌ **Violations (Fix)**
- 26 domain tool files with `@tool` decorators
- 43 domain service files potentially accessing container directly
- Repository interfaces missing some operations
- Tools in domain layer instead of application layer

## Refactoring Strategy

### Phase 1: Create Application Layer (Week 1)
**Goal:** Move all framework dependencies to application layer

#### 1.1 Tool Migration Pattern
```
BEFORE (Violation):
kickai/features/player_registration/domain/tools/player_tools.py
├── @tool decorator (CrewAI framework)
├── get_container() calls
└── Business logic mixed with framework concerns

AFTER (Compliant):
kickai/features/player_registration/application/tools/player_tools.py
├── @tool decorators (framework boundary)
├── get_container() calls (DI resolution)
└── Delegates to pure domain services

kickai/features/player_registration/domain/services/player_service.py
├── Pure business logic
├── Only repository interfaces
└── No framework knowledge
```

#### 1.2 Files to Create/Move
**New Application Tool Files (26 files):**
```
kickai/features/communication/application/tools/
├── communication_tools.py
└── telegram_tools.py

kickai/features/match_management/application/tools/
├── attendance_tools.py
├── availability_tools.py
├── match_tools.py
└── squad_tools.py

kickai/features/player_registration/application/tools/
├── player_tools.py
└── player_update_tools.py

kickai/features/shared/application/tools/
├── help_tools.py
├── nlp_tools.py
├── onboarding_tools.py
├── permission_tools.py
├── system_tools.py
└── user_tools.py

kickai/features/system_infrastructure/application/tools/
└── help_tools.py

kickai/features/team_administration/application/tools/
├── player_management_tools.py
├── simplified_team_member_tools.py
├── team_management_tools.py
├── team_member_tools.py
├── team_member_update_tools.py
└── update_team_member_tools.py
```

#### 1.3 Tool Refactoring Template
```python
# APPLICATION LAYER: kickai/features/*/application/tools/*.py
from crewai.tools import tool
from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.utils.tool_helpers import create_json_response

@tool("tool_name", result_as_answer=True)
async def tool_name(telegram_id: int, team_id: str, username: str, chat_type: str, **kwargs) -> str:
    """Application boundary - handles framework concerns"""
    try:
        # DI resolution at application boundary
        container = get_container()
        service = container.get_service(DomainServiceInterface)
        
        # Pure domain operation
        result = await service.domain_operation(telegram_id, team_id, **kwargs)
        
        # Application layer formats response
        return create_json_response(ResponseStatus.SUCCESS, data=result)
    except Exception as e:
        return create_json_response(ResponseStatus.ERROR, message=str(e))

# DOMAIN LAYER: kickai/features/*/domain/services/*.py
class DomainService:
    def __init__(self, repository: RepositoryInterface):
        """Pure dependency injection - no container knowledge"""
        self.repository = repository
    
    async def domain_operation(self, telegram_id: int, team_id: str, **kwargs) -> DomainModel:
        """Pure business logic - no framework knowledge"""
        return await self.repository.some_operation(telegram_id, team_id)
```

### Phase 2: Repository Interface Expansion (Week 2)
**Goal:** Eliminate direct database access from domain services

#### 2.1 Repository Interface Audit
**Current Missing Methods:**
```python
# Need to add to PlayerRepositoryInterface
async def get_player_by_telegram_id(self, telegram_id: int, team_id: str) -> Optional[Player]
async def get_players_by_status_and_team(self, status: str, team_id: str) -> List[Player]

# Need to add to TeamMemberRepositoryInterface  
async def get_member_by_telegram_id(self, telegram_id: int, team_id: str) -> Optional[TeamMember]
async def activate_member(self, member_id: str, team_id: str) -> TeamMember

# Need to add to TeamRepositoryInterface
async def get_team_config(self, team_id: str) -> Optional[TeamConfig]
async def get_leadership_chat_id(self, team_id: str) -> Optional[str]
```

#### 2.2 Service Refactoring Pattern
```python
# BEFORE (Violation): Direct database access
class PlayerService:
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str):
        container = get_container()
        database = container.get_database()  # VIOLATION
        return await database.get_player_by_telegram_id(telegram_id, team_id)

# AFTER (Compliant): Repository interface
class PlayerService:
    def __init__(self, player_repository: PlayerRepositoryInterface):
        self.player_repository = player_repository
    
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str):
        return await self.player_repository.get_player_by_telegram_id(telegram_id, team_id)
```

### Phase 3: Dependency Injection Purification (Week 3)
**Goal:** Remove all container knowledge from domain layer

#### 3.1 Service Registration Updates
**Update dependency container to register all services with proper interfaces:**
```python
# kickai/core/dependency_container.py
def _register_services(self):
    # Register with interface contracts
    self.register_service(IPlayerService, PlayerService(
        player_repository=self.get_service(PlayerRepositoryInterface)
    ))
    self.register_service(ITeamMemberService, TeamMemberService(
        team_member_repository=self.get_service(TeamMemberRepositoryInterface)
    ))
```

#### 3.2 Agent Configuration Updates
**Update agent tool assignments to point to new application layer tools:**
```yaml
# kickai/config/agents.yaml
PLAYER_COORDINATOR:
  tools:
    - "kickai.features.player_registration.application.tools.player_tools:get_my_status"
    - "kickai.features.player_registration.application.tools.player_tools:get_player_status"
```

### Phase 4: Testing & Validation (Week 4)
**Goal:** Ensure no functionality regression and full compliance

#### 4.1 Compliance Validation Script
```python
#!/usr/bin/env python3
"""Clean Architecture Compliance Validator"""

def validate_domain_layer_purity():
    """Ensure domain layer has no framework dependencies"""
    violations = []
    
    # Check for framework imports in domain
    for file in glob("kickai/features/*/domain/**/*.py"):
        content = read_file(file)
        if "from crewai" in content:
            violations.append(f"{file}: CrewAI import in domain layer")
        if "get_container" in content:
            violations.append(f"{file}: Container access in domain layer")
    
    return violations

def validate_dependency_direction():
    """Ensure all dependencies flow inward"""
    # Implementation to check import directions
    pass

def validate_interface_compliance():
    """Ensure all repositories implement interfaces"""
    # Implementation to verify interface compliance
    pass
```

#### 4.2 Test Migration
- Update all existing tests to use new application layer entry points
- Ensure domain service tests use pure dependency injection
- Verify integration tests still pass with new architecture

## Implementation Timeline

### Week 1: Foundation (Phase 1)
- **Day 1-2:** Create application/tools directory structure
- **Day 3-4:** Migrate shared and system infrastructure tools
- **Day 5:** Migrate player registration tools
- **Day 6-7:** Migrate team administration and communication tools

### Week 2: Repository Enhancement (Phase 2)  
- **Day 1-2:** Expand repository interfaces
- **Day 3-4:** Update infrastructure implementations
- **Day 5:** Refactor domain services to use expanded interfaces
- **Day 6-7:** Remove direct database access from domain services

### Week 3: Purification (Phase 3)
- **Day 1-2:** Update dependency container configuration
- **Day 3-4:** Update agent tool assignments
- **Day 5:** Remove container dependencies from domain
- **Day 6-7:** Update all service registrations

### Week 4: Validation (Phase 4)
- **Day 1-2:** Create and run compliance validation scripts  
- **Day 3-4:** Fix any remaining violations
- **Day 5:** Update all tests and documentation
- **Day 6-7:** Final system testing and validation

## Risk Mitigation

### High Risk Areas
1. **Agent Tool Discovery**: Tools moved to application layer may break agent loading
2. **Service Initialization**: Dependency injection changes may cause startup failures
3. **Test Compatibility**: Extensive testing updates required

### Mitigation Strategies
1. **Gradual Migration**: Move one feature at a time
2. **Backward Compatibility**: Keep old tools temporarily with deprecation warnings
3. **Comprehensive Testing**: Test each phase before proceeding
4. **Rollback Plan**: Maintain git branches for each phase

## Success Criteria

### Compliance Metrics
- [ ] Zero framework imports in domain layer
- [ ] Zero container access in domain services
- [ ] All database access through repository interfaces
- [ ] All tools in application layer
- [ ] 100% test coverage maintained

### Functional Requirements
- [ ] All existing commands work unchanged
- [ ] No performance degradation
- [ ] All tests pass
- [ ] Agent routing unchanged from user perspective
- [ ] Mock testing framework still works

## File Change Summary

### Files to Create (26 new application tool files)
```
kickai/features/*/application/tools/*.py (26 files)
```

### Files to Modify (43 domain service files)
```
kickai/features/*/domain/services/*.py (43 files)
kickai/features/*/domain/repositories/*_interface.py (15 files)
kickai/features/*/infrastructure/*_repository.py (15 files)
kickai/core/dependency_container.py (1 file)
kickai/config/agents.yaml (1 file)
```

### Files to Remove/Deprecate (26 domain tool files)
```
kickai/features/*/domain/tools/*.py (26 files) - Move to application layer
```

**Total Impact:** ~81 files created/modified, ~26 files moved

## Conclusion

This refactoring plan achieves 100% Clean Architecture compliance while maintaining all existing functionality. The systematic approach minimizes risk through gradual migration and comprehensive testing. The result will be a more maintainable, testable, and architecturally sound system that properly separates business logic from framework concerns.

**Next Steps:**
1. Review and approve this plan
2. Create feature branch: `feat/clean-architecture-compliance`  
3. Begin Phase 1 implementation
4. Regular progress reviews at end of each phase