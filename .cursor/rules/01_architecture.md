# KICKAI Architecture

## Overview

KICKAI follows a **Clean Architecture** pattern with **Domain-Driven Design** principles, implemented as a **feature-based modular system** with **13-agent CrewAI orchestration**. The system is designed for scalability, maintainability, and extensibility with a comprehensive **service discovery system** for dynamic service management.

## 🏗️ **Current Architecture Status**

### ✅ **Fully Implemented Components**
- **Core System**: Complete with dependency injection, command registry, and agent orchestration
- **Service Discovery System**: **NEW** - Dynamic service registration, health monitoring, and circuit breaker
- **Player Management**: Full player registration, approval, and management system
- **Match Management**: Complete match creation, scheduling, and attendance tracking
- **Attendance Management**: Full attendance tracking and reporting system
- **Payment Management**: Complete payment creation and tracking system
- **Communication**: Full team messaging and announcement system
- **Agent System**: 13-agent CrewAI orchestration working correctly
- **Comprehensive Test Suite**: **NEW** - Unit, integration, and E2E tests with service discovery testing

### 🚧 **Partially Implemented Components**
- **Training Management**: Domain entities and tools implemented, commands defined but not integrated
- **Advanced Analytics**: Basic implementation, needs enhancement

## System Architecture Layers

### 1. **Presentation Layer** (Telegram Integration)
```
kickai/telegram/
├── modular_message_handler.py    # Unified message handling
├── handlers/                     # Message type handlers
└── integration/                  # Telegram API integration
```

**Responsibilities**:
- Handle Telegram message reception
- Route messages to appropriate agents
- Format and send responses
- Manage chat-specific behavior

### 2. **Application Layer** (Feature Commands)
```
kickai/features/{feature_name}/application/
├── commands/                     # Command definitions with @command decorator
└── handlers/                     # Command handlers (delegate to agents)
```

**Responsibilities**:
- Define command interfaces
- Handle command registration
- Delegate execution to domain layer
- Manage command metadata and help

### 3. **Domain Layer** (Business Logic)
```
kickai/features/{feature_name}/domain/
├── entities/                     # Business entities (Player, Match, etc.)
├── services/                     # Business logic services
├── tools/                       # CrewAI tools for agent integration
└── interfaces/                  # Repository interfaces
```

**Responsibilities**:
- Define business entities and rules
- Implement business logic
- Provide CrewAI tools for agents
- Define repository contracts

### 2.5. **Service Discovery Layer** (NEW)
```
kickai/core/service_discovery/
├── interfaces.py                 # Service definitions and protocols
├── registry.py                   # Central service registry with circuit breaker
├── discovery.py                  # Auto-discovery mechanisms
├── health_checkers.py           # Specialized health checkers by service type
└── config.py                    # Configuration loading and defaults
```

**Responsibilities**:
- Dynamic service registration and discovery
- Health monitoring with specialized checkers
- Circuit breaker pattern for failure isolation
- Configuration-driven service definitions

### 4. **Infrastructure Layer** (External Dependencies)
```
kickai/features/{feature_name}/infrastructure/
├── firestore_*_repository.py    # Firebase implementations
└── external_integrations/       # Third-party service integrations
```

**Responsibilities**:
- Implement data persistence
- Handle external API integrations
- Manage configuration and secrets
- Provide logging and monitoring

## Feature-Based Modular Design

### Current Feature Modules

#### ✅ **Fully Implemented Features**

**Player Registration** (`kickai/features/player_registration/`)
```
├── application/commands/
│   ├── player_commands.py       # /addplayer, /approve, /reject
│   └── info_commands.py         # /myinfo, /status
├── domain/
│   ├── entities/                # Player, TeamMember entities
│   ├── services/                # Player management services
│   └── tools/                   # CrewAI tools for player operations
└── infrastructure/
    └── firestore_player_repository.py
```

**Match Management** (`kickai/features/match_management/`)
```
├── application/commands/
│   └── match_commands.py        # /creatematch, /listmatches, etc.
├── domain/
│   ├── entities/                # Match entity
│   ├── services/                # Match management services
│   └── tools/                   # CrewAI tools for match operations
└── infrastructure/
    └── firestore_match_repository.py
```

**Attendance Management** (`kickai/features/attendance_management/`)
```
├── application/commands/
│   └── attendance_commands.py   # /markattendance, /attendance, etc.
├── domain/
│   ├── entities/                # Attendance entity
│   ├── services/                # Attendance services
│   └── tools/                   # CrewAI tools for attendance
└── infrastructure/
    └── firestore_attendance_repository.py
```

**Payment Management** (`kickai/features/payment_management/`)
```
├── application/commands/
│   └── payment_commands.py      # /createpayment, /payments, etc.
├── domain/
│   ├── entities/                # Payment entity
│   ├── services/                # Payment services
│   └── tools/                   # CrewAI tools for payments
└── infrastructure/
    └── firestore_payment_repository.py
```

**Communication** (`kickai/features/communication/`)
```
├── application/commands/
│   └── communication_commands.py # /announce, /remind, /broadcast
├── domain/
│   ├── entities/                # Message entity
│   ├── services/                # Communication services
│   └── tools/                   # CrewAI tools for messaging
└── infrastructure/
    └── firebase_message_repository.py
```

#### 🚧 **Partially Implemented Features**

**Training Management** (`kickai/features/training_management/`)
```
├── application/commands/
│   └── training_commands.py     # Commands defined but not integrated
├── domain/
│   ├── entities/                # ✅ TrainingSession, TrainingAttendance
│   ├── services/                # 🚧 Basic services implemented
│   └── tools/                   # ✅ Training tools implemented
└── infrastructure/
    └── firestore_training_repository.py  # ✅ Implemented
```

**Missing Integration**:
- Training commands not added to `constants.py`
- Training commands not registered in command registry
- Training tools not integrated with agent system

## Agent Architecture

### 13-Agent CrewAI System

The system uses 13 specialized agents organized in logical layers for intelligent task processing:

#### Primary Interface Layer

**1. MESSAGE_PROCESSOR**
- **Primary Role**: Primary interface for user interactions and routing
- **Commands**: `/version`, general natural language processing
- **Tools**: Intent analysis, context extraction, message parsing

**2. TEAM_MANAGER**
- **Primary Role**: Team administration and member management
- **Commands**: `/list`, `/approve`, `/reject`, `/team`, `/invite`
- **Tools**: Team management, player administration, team coordination

#### Operational Layer

**3. PLAYER_COORDINATOR**
- **Primary Role**: Player registration, status, and management
- **Commands**: `/addplayer`, `/addmember`, `/update`, `/myinfo`, `/status`
- **Tools**: Player management, registration, status tracking

**4. TRAINING_COORDINATOR**
- **Primary Role**: Training session management and coordination
- **Commands**: `/scheduletraining`, `/listtrainings`, `/marktraining`, `/canceltraining`
- **Tools**: Training management, session coordination, attendance tracking

**5. SQUAD_SELECTOR**
- **Primary Role**: Match squad selection and availability
- **Commands**: `/selectsquad`, `/availableplayers`, match-related operations
- **Tools**: Squad selection, availability tracking, match coordination

**6. AVAILABILITY_MANAGER**
- **Primary Role**: Player availability tracking
- **Commands**: `/markattendance`, `/attendance`, attendance operations
- **Tools**: Attendance tracking, availability management, reporting

#### Specialized Layer

**7. HELP_ASSISTANT**
- **Primary Role**: Help system and command guidance
- **Commands**: `/help`, command assistance
- **Tools**: Help generation, command documentation, user guidance

**8. ONBOARDING_AGENT**
- **Primary Role**: New user registration and onboarding
- **Commands**: `/start`, onboarding flows
- **Tools**: User onboarding, registration assistance, guidance

**9. COMMUNICATION_MANAGER**
- **Primary Role**: Team communications and announcements
- **Commands**: `/announce`, `/remind`, `/broadcast`
- **Tools**: Team messaging, announcements, communication coordination

**10. PERFORMANCE_ANALYST**
- **Primary Role**: Performance analysis and insights
- **Commands**: `/stats`, `/analytics`, performance reports
- **Tools**: Data analysis, performance metrics, reporting

#### Infrastructure Layer

**11. FINANCE_MANAGER**
- **Primary Role**: Financial tracking and payment management
- **Commands**: `/createpayment`, `/payments`, `/budget`, `/markpaid`
- **Tools**: Payment management, financial tracking, budget analysis

**12. LEARNING_AGENT**
- **Primary Role**: Continuous learning and system improvement
- **Commands**: System learning and adaptation
- **Tools**: Learning algorithms, pattern recognition, system optimization

**13. COMMAND_FALLBACK_AGENT**
- **Primary Role**: Fallback for unhandled requests
- **Commands**: Fallback for unknown commands and error scenarios
- **Tools**: Error handling, user guidance, fallback processing

## Core System Components

### Command Registry System
```
kickai/core/
├── command_registry.py          # Central command registry
├── command_registry_initializer.py  # Command discovery and initialization
├── constants.py                 # Command definitions and constants
└── enums.py                     # System enums (PermissionLevel, ChatType)
```

**Features**:
- Automatic command discovery from feature modules
- Permission-based command filtering
- Chat-specific command handling
- Command metadata and help system

### Dependency Injection Container
```
kickai/core/di/
└── modern_container.py          # Dependency injection container
```

**Features**:
- Service registration and resolution
- Singleton and transient service management
- Interface-based dependency injection
- Clean architecture enforcement

### Agent System
```
kickai/agents/
├── agent_types.py               # Agent type definitions
├── agentic_message_router.py    # Agent routing and orchestration
└── handlers/                    # Agent-specific handlers
```

**Features**:
- Intelligent message routing
- Agent capability matching
- Task decomposition and orchestration
- Context-aware processing

## Data Architecture

### Firestore Collections
```
kickai_{team_id}_players         # Player records
kickai_{team_id}_team_members    # Team member records
kickai_{team_id}_matches         # Match records
kickai_{team_id}_attendance      # Attendance records
kickai_{team_id}_payments        # Payment records
kickai_{team_id}_training_sessions  # Training session records
kickai_{team_id}_training_attendance  # Training attendance records
```

### Entity Relationships
```
Team
├── Players (1:N)
├── Team Members (1:N)
├── Matches (1:N)
├── Training Sessions (1:N)
└── Payments (1:N)

Match
├── Attendance Records (1:N)
└── Squad Selection (1:N)

Training Session
└── Training Attendance Records (1:N)
```

## Security and Access Control

### Permission Levels
- **PUBLIC**: Available to everyone
- **PLAYER**: Available to team members
- **LEADERSHIP**: Available in leadership chat
- **ADMIN**: Available to admins only

### Chat-Based Access Control
- **Main Chat**: Read-only commands for players
- **Leadership Chat**: Full administrative access
- **Private Messages**: Limited command set

## Integration Points

### External Services
- **Telegram Bot API**: Message handling and responses
- **Firebase Firestore**: Data persistence
- **CrewAI**: Agent orchestration and LLM integration

### Internal Integrations
- **Command Registry**: Centralized command management
- **Agent System**: Intelligent task processing
- **Dependency Injection**: Service management
- **Event Bus**: Inter-feature communication

## Scalability Considerations

### Horizontal Scaling
- Stateless agent design
- Database connection pooling
- Caching strategies
- Load balancing ready

### Vertical Scaling
- Modular feature architecture
- Lazy loading of components
- Efficient resource management
- Performance monitoring

## Monitoring and Observability

### Logging
- Structured logging with loguru
- Feature-specific loggers
- Performance metrics
- Error tracking

### Health Checks
- System health monitoring
- Agent status tracking
- Database connectivity
- External service status

## Future Architecture Enhancements

### Planned Improvements
1. **Training Management Integration**: Complete training feature integration
2. **Advanced Analytics**: Enhanced reporting and analytics
3. **Real-time Notifications**: WebSocket-based real-time updates
4. **API Gateway**: REST API for external integrations
5. **Microservices**: Service decomposition for large-scale deployment

### Architecture Principles
- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Open for extension, closed for modification
- **Dependency Inversion**: Depend on abstractions, not concretions
- **Interface Segregation**: Small, focused interfaces
- **Liskov Substitution**: Subtypes are substitutable for base types