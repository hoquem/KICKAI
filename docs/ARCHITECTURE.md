# KICKAI Architecture & Dependency Rules

## Overview

KICKAI follows a **Clean Architecture** approach with **feature-first organization** and **layered dependencies**. This document defines the architectural principles, dependency hierarchy, and import rules to maintain code quality and prevent circular dependencies.

## 🏗️ Architectural Layers

### 1. **Infrastructure Layer** (Bottom)
- **Purpose**: External interfaces, data persistence, third-party integrations
- **Components**: 
  - `src/database/` - Firebase/Firestore client
  - `src/services/interfaces/` - Service interfaces
  - `src/utils/` - Utility functions, LLM clients
  - `src/core/` - Configuration, exceptions, core utilities
- **Dependencies**: None (base layer)

### 2. **Domain Layer** (Core Business Logic)
- **Purpose**: Business entities, repositories, domain services
- **Components**:
  - `src/database/models_improved.py` - Data models
  - `src/services/` - Business logic services
- **Dependencies**: Infrastructure Layer only

### 3. **Application Layer** (Use Cases & State Management)
- **Purpose**: Application services, state management, orchestration
- **Components**:
  - `src/agents/` - AI agents and crew management
  - `src/services/` - Service implementations
  - `src/tasks/` - Background tasks
- **Dependencies**: Domain Layer, Infrastructure Layer

### 4. **Presentation Layer** (Top)
- **Purpose**: User interface, message handling, command processing
- **Components**:
  - `src/telegram/` - Telegram bot handlers and commands
  - `src/tools/` - Tool implementations
- **Dependencies**: Application Layer, Domain Layer

## 📁 Feature-First Organization

```
src/
├── agents/           # AI agents and crew management
├── core/            # Core utilities, config, exceptions
├── database/        # Data models and persistence
├── services/        # Business logic services
│   └── interfaces/  # Service contracts
├── tasks/           # Background tasks
├── telegram/        # Telegram bot presentation layer
├── tools/           # Tool implementations
└── utils/           # Utility functions
```

## 🔄 Dependency Rules

### ✅ Allowed Dependencies

1. **Presentation → Application → Domain → Infrastructure** ✅
2. **Same layer dependencies** ✅ (with caution)
3. **Infrastructure → Infrastructure** ✅
4. **Domain → Domain** ✅

### ❌ Forbidden Dependencies

1. **Infrastructure → Domain** ❌
2. **Infrastructure → Application** ❌
3. **Infrastructure → Presentation** ❌
4. **Domain → Application** ❌
5. **Domain → Presentation** ❌
6. **Application → Presentation** ❌

### 🔧 Import Rules

#### 1. **Top-Level Imports Only**
```python
# ✅ GOOD - Top-level imports
from src.services.player_service import PlayerService
from src.database.models_improved import Player

# ❌ BAD - In-function imports (except for circular dependency resolution)
def some_function():
    from src.services.player_service import PlayerService  # Avoid this pattern
```

#### 2. **Service Layer Dependencies**
```python
# ✅ GOOD - Services depend on interfaces and models
from src.services.interfaces.player_service_interface import PlayerServiceInterface
from src.database.models_improved import Player

# ❌ BAD - Services importing from presentation layer
from src.telegram.unified_command_system import SomeCommand  # Wrong direction
```

#### 3. **Presentation Layer Dependencies**
```python
# ✅ GOOD - Presentation depends on services and models
from src.services.player_service import PlayerService
from src.database.models_improved import Player

# ❌ BAD - Presentation importing from other presentation components
from src.telegram.telegram_command_handler import SomeHandler  # Use interfaces instead
```

## 🚫 Circular Import Prevention

### 1. **Interface-Based Design**
- Define service contracts in `src/services/interfaces/`
- Implement services in `src/services/`
- Import interfaces, not implementations

### 2. **Dependency Injection**
- Pass dependencies as constructor parameters
- Avoid direct imports of concrete implementations

### 3. **Event-Driven Communication**
- Use events for cross-layer communication
- Decouple components through event systems

## 📋 Import Guidelines

### Service Layer
```python
# ✅ Correct service imports
from src.database.models_improved import Player, Team
from src.services.interfaces.player_service_interface import PlayerServiceInterface
from src.core.exceptions import AccessDeniedError
from src.utils.id_generator import generate_id
```

### Presentation Layer
```python
# ✅ Correct presentation imports
from src.services.player_service import PlayerService
from src.services.team_service import TeamService
from src.database.models_improved import Player, Team
from src.core.exceptions import AccessDeniedError
```

### Agent Layer
```python
# ✅ Correct agent imports
from src.services.player_service import PlayerService
from src.services.team_service import TeamService
from src.database.models_improved import Player, Team
from src.utils.llm_client import LLMClient
```

## 🔍 Linting Rules

### Import Order
1. Standard library imports
2. Third-party imports
3. Local application imports (src/)

### Import Organization
```python
# Standard library
import logging
from typing import List, Optional

# Third-party
from telegram import Update
from telegram.ext import ContextTypes

# Local imports (src/)
from src.services.player_service import PlayerService
from src.database.models_improved import Player
from src.core.exceptions import AccessDeniedError
```

## 🛠️ Enforcement

### 1. **Pre-commit Hooks**
- Run import order checks
- Validate dependency direction
- Check for circular imports

### 2. **CI/CD Pipeline**
- Automated dependency analysis
- Import rule validation
- Architecture compliance checks

### 3. **Code Review**
- Review import statements
- Verify dependency direction
- Check for architectural violations

## 📚 Best Practices

### 1. **Single Responsibility**
- Each module has one clear purpose
- Avoid mixing concerns across layers

### 2. **Interface Segregation**
- Define specific interfaces for each use case
- Avoid large, monolithic interfaces

### 3. **Dependency Inversion**
- Depend on abstractions, not concretions
- Use dependency injection for flexibility

### 4. **Clean Imports**
- Import only what you need
- Use explicit imports over wildcard imports
- Group imports logically

## 🔧 Migration Guide

### From Legacy Code
1. **Identify circular dependencies**
2. **Extract interfaces** where needed
3. **Refactor imports** to follow hierarchy
4. **Update service contracts**
5. **Test thoroughly**

### Adding New Features
1. **Determine the layer** for your feature
2. **Follow dependency rules** strictly
3. **Create interfaces** for cross-layer communication
4. **Update this document** if architecture changes

## 📖 Examples

### ✅ Good Architecture
```python
# Presentation Layer (telegram/)
from src.services.player_service import PlayerService
from src.database.models_improved import Player

class PlayerCommand:
    def __init__(self, player_service: PlayerService):
        self.player_service = player_service
    
    def execute(self, player_id: str) -> str:
        player = self.player_service.get_player(player_id)
        return f"Player: {player.name}"
```

### ❌ Bad Architecture
```python
# Infrastructure Layer (database/)
from src.telegram.unified_command_system import PlayerCommand  # Wrong direction!

class DatabaseClient:
    def get_player(self, player_id: str):
        # This creates a circular dependency
        command = PlayerCommand()
        return command.execute(player_id)
```

## 🎯 Summary

- **Follow the dependency hierarchy strictly**
- **Use interfaces for cross-layer communication**
- **Avoid in-function imports unless absolutely necessary**
- **Keep imports clean and organized**
- **Review architecture regularly**
- **Enforce rules through linting and CI/CD**

This architecture ensures maintainable, testable, and scalable code while preventing the common pitfalls of circular dependencies and tight coupling. 