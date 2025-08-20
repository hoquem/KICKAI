# Agentic Design Philosophy

We will leverage agents for what they do best and fall back on deterministic code for efficiency and reliability.

- **Agentic Tasks**: Use `CrewAI` agents for tasks requiring reasoning, context, or creativity.
  - Natural Language Understanding (NLU).
  - Generating match summaries or tactical suggestions.

- **Primary Agent Pattern**: The MESSAGE_PROCESSOR serves as the primary interface for all user interactions, collaborating with NLP_PROCESSOR for intelligent routing decisions based on context and intent analysis.

### Agentic & AI Architecture Principles

This section defines the core design patterns for the CrewAI-based agentic system.

- **6-Agent CrewAI Native Collaboration System**: The system uses CrewAI native agent collaboration patterns with intelligent routing:
    - **Primary Interface Layer** (`MESSAGE_PROCESSOR`): Primary interface with intelligent coordination capabilities.
    - **Operational Layer** (`PLAYER_COORDINATOR`, `TEAM_ADMINISTRATOR`, `SQUAD_SELECTOR`): Specialist agents for domain-specific operations.
    - **Support Layer** (`HELP_ASSISTANT`): Specialized help system and user guidance.
    - **Intelligent Routing Layer** (`NLP_PROCESSOR`): Context-aware analysis and agent selection.

- **CrewAI Native Collaboration**: All implementations must use CrewAI's native agent collaboration features:
  - **Primary Agent Pattern**: MESSAGE_PROCESSOR coordinates with specialist agents
  - **Tool-Based Collaboration**: Agents collaborate through specialized tools, not direct communication
  - **Intelligent Routing**: NLP_PROCESSOR provides context-aware agent selection
  - **Multi-Agent Patterns**: Sequential, parallel, and hierarchical collaboration workflows

- **Context-Aware Routing & Agent Selection**:
    - The **AgenticMessageRouter** serves as the entry point for all user requests.
    - Agent selection is based on chat type (main chat vs leadership chat) and command intent.
    - Commands behave differently based on context (e.g., `/list` shows active players in main chat, all players and members in leadership chat).

- **Defined Communication Patterns**: Agent interactions follow established patterns:
    - **Direct Routing**: Messages are routed directly to the appropriate agent based on context.
    - **Tool-Based Execution**: Agents use specialized tools for their domain.
    - **Context Preservation**: Chat type and user context are preserved throughout processing.
    - **Inter-Agent Delegation**: Agents can delegate tasks to each other using CrewAI's delegation tools.
    - **Memory-Aware Interactions**: Agents maintain context through entity-specific memory systems.

- **Tool-Based Architecture**: Agents **must not** interact directly with external systems. All external actions must be performed through a **Tool Layer**. These tools abstract the implementation details and are the only components that interact directly with infrastructure services.

### Agent Responsibilities

#### **MESSAGE_PROCESSOR** (Primary Interface)
- **Goal**: Process and route incoming messages to appropriate agents
- **Tools**: `send_message`, `send_announcement`, `get_available_commands`, `list_team_members_and_players`
- **Responsibilities**:
  - Intent analysis and routing
  - Help system management
  - Team member and player listing (leadership chat)
  - Message broadcasting and announcements

#### **PLAYER_COORDINATOR** (Player Management)
- **Goal**: Manage player registration, status, and information
- **Tools**: `get_my_status`, `get_player_status`, `get_active_players`, `approve_player`, `register_player`, `add_player`
- **Responsibilities**:
  - Player registration and onboarding
  - Player status management
  - Active player listing (main chat)
  - Player approval workflow

#### **TEAM_ADMINISTRATOR** (Team Administration)
- **Goal**: Manage team administration and member operations
- **Tools**: `get_my_team_member_status`, `get_team_members`, `add_team_member_role`, `promote_team_member_to_admin`, `remove_team_member_role`
- **Responsibilities**:
  - Team member management
  - Role assignment and permissions
  - Team administration tasks
  - Leadership operations

#### **SQUAD_SELECTOR** (Match Operations)
- **Goal**: Manage squad selection and match operations
- **Tools**: `get_match`, `get_all_players`, `get_player_status`
- **Responsibilities**:
  - Squad selection for matches
  - Match operations management
  - Player availability for matches

#### **HELP_ASSISTANT** (Help System)
- **Goal**: Provide comprehensive help and guidance
- **Tools**: `get_available_commands`, `get_command_help`, `get_welcome_message`, `FINAL_HELP_RESPONSE`
- **Responsibilities**:
  - Command help and guidance
  - System usage assistance
  - User onboarding support
  - Welcome message generation

#### **NLP_PROCESSOR** (Natural Language Processing)
- **Goal**: Provide advanced natural language understanding and processing
- **Tools**: `advanced_intent_recognition`, `entity_extraction_tool`, `conversation_context_tool`, `semantic_similarity_tool`, `routing_recommendation_tool`
- **Responsibilities**:
  - Advanced intent recognition with conversation awareness
  - Entity extraction for football-specific terms and concepts
  - Conversation context management for multi-turn interactions
  - Semantic similarity matching for command suggestions
  - Intelligent routing recommendations based on intent analysis

### Memory Mapping by Agent Role

Each agent has access to specific memory systems optimized for their role:

- **PLAYER_COORDINATOR**: Player-specific memory for player preferences and history
- **TEAM_ADMINISTRATOR**: Team member memory for team management context
- **SQUAD_SELECTOR**: Player memory for squad selection decisions
- **MESSAGE_PROCESSOR**: Short-term session memory for conversation context
- **HELP_ASSISTANT**: Short-term session memory for help interactions
- **NLP_PROCESSOR**: Conversation memory for multi-turn context and intent tracking

### Delegation Capabilities

Agents can delegate tasks to each other using CrewAI's built-in delegation tools:

- **MESSAGE_PROCESSOR** → **PLAYER_COORDINATOR**: Complex player queries
- **MESSAGE_PROCESSOR** → **TEAM_ADMINISTRATOR**: Team management requests
- **SQUAD_SELECTOR** → **TEAM_ADMINISTRATOR**: Team member availability queries
- **Any Agent** → **HELP_ASSISTANT**: Help and guidance requests
- **Any Agent** → **NLP_PROCESSOR**: Natural language understanding and intent analysis

### Context-Aware Routing

The system implements intelligent routing based on chat context and permission levels. For complete command routing information, see [11_unified_command_system.md](11_unified_command_system.md).

**Key Routing Principles:**
- **Main Chat**: Player commands routed to `PLAYER_COORDINATOR`
- **Leadership Chat**: Leadership commands routed to `TEAM_ADMINISTRATOR` or `SQUAD_SELECTOR`
- **Permission-Based**: Commands routed based on permission level and agent capabilities

### Tool Independence

**CRITICAL**: Tools must be completely independent functions following CrewAI best practices:

- **❌ NEVER**: Tools calling other tools or services directly (delegate via CrewAI tasks instead).
- **✅ ALWAYS**: Tools are simple, independent async functions.
- **✅ ALWAYS**: Use direct parameter passing with type hints.
- **✅ ALWAYS**: Tools return simple string responses.
- **✅ ALWAYS**: Use `@tool` decorator from `crewai.tools`.

**📋 For complete tool implementation standards, see [04_development_standards.md](04_development_standards.md)**

### Service Layer Standards

**CRITICAL**: Services must use domain models and repository interfaces, never direct database calls:

- **❌ NEVER**: Services calling database directly (Firebase, Firestore, etc.)
- **❌ NEVER**: Services using raw database clients or SDKs
- **✅ ALWAYS**: Services use domain models (Player, Team, Match, etc.)
- **✅ ALWAYS**: Services use repository interfaces (PlayerRepositoryInterface, etc.)
- **✅ ALWAYS**: Services work with domain entities, not raw data
- **✅ ALWAYS**: Database operations handled by repository implementations

**📋 For complete service layer standards, see [04_development_standards.md](04_development_standards.md)**

### Domain Model Usage

**MANDATORY**: All business logic must work with domain models:

**📋 For complete domain model usage standards, see [04_development_standards.md](04_development_standards.md)**
