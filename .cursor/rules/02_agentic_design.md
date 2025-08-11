# Agentic Design Philosophy

We will leverage agents for what they do best and fall back on deterministic code for efficiency and reliability.

- **Agentic Tasks**: Use `CrewAI` agents for tasks requiring reasoning, context, or creativity.
  - Natural Language Understanding (NLU).
  - Generating match summaries or tactical suggestions.
  - Scouting players based on descriptive text.

- **Deterministic Tasks**: Use standard Python code for simple, reliable operations.
  - CRUD operations (e.g., adding a player by name).
  - Listing team members or upcoming fixtures.
  - Checking a player's status.

- **Intent Recognition Agent**: A dedicated CrewAI agent, the "Message Processor," will be the primary interface for natural language. Its job is to receive raw text from the user and route it to the appropriate specialized agent based on intent and context.

### Agentic & AI Architecture Principles

This section defines the core design patterns for the CrewAI-based agentic system.

- **5-Agent CrewAI System**: The system is structured as a crew of 5 specialized agents organized into logical layers:
    - **Primary Interface Layer** (`MESSAGE_PROCESSOR`): Handles initial user interaction and routing.
    - **Operational Layer** (`PLAYER_COORDINATOR`, `TEAM_ADMINISTRATOR`, `SQUAD_SELECTOR`): Manages day-to-day team operations.
    - **Support Layer** (`HELP_ASSISTANT`): Provides help and guidance functionality.

- **CrewAI Idiomatic Usage**: All implementations must strictly adhere to CrewAI's native features and design patterns. Avoid custom workarounds for functionalities already supported by the framework (e.g., context passing, memory management, delegation).

- **Enhanced Memory System**: The system uses CrewAI 0.157.0's enhanced memory features:
  - **Entity-Specific Memory**: Each agent has access to entity-specific memory (player, team member, session)
  - **Delegation Tools**: Agents can delegate tasks to each other using CrewAI's built-in delegation tools
  - **Context Retention**: Memory is automatically managed and preserved across agent interactions

- **Context-Aware Routing & Agent Selection**:
    - The **AgenticMessageRouter** serves as the entry point for all user requests.
    - Agent selection is based on chat type (main chat vs leadership chat) and command intent.
    - Commands behave differently based on context (e.g., `/list` shows active players in main chat, all players in leadership chat).

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

### Memory Mapping by Agent Role

Each agent has access to specific memory systems optimized for their role:

- **PLAYER_COORDINATOR**: Player-specific memory for player preferences and history
- **TEAM_ADMINISTRATOR**: Team member memory for team management context
- **SQUAD_SELECTOR**: Player memory for squad selection decisions
- **MESSAGE_PROCESSOR**: Short-term session memory for conversation context
- **HELP_ASSISTANT**: Short-term session memory for help interactions

### Delegation Capabilities

Agents can delegate tasks to each other using CrewAI's built-in delegation tools:

- **MESSAGE_PROCESSOR** → **PLAYER_COORDINATOR**: Complex player queries
- **MESSAGE_PROCESSOR** → **TEAM_ADMINISTRATOR**: Team management requests
- **SQUAD_SELECTOR** → **TEAM_ADMINISTRATOR**: Team member availability queries
- **Any Agent** → **HELP_ASSISTANT**: Help and guidance requests

### Context-Aware Routing

The system implements intelligent routing based on chat context and permission levels. For complete command routing information, see [11_unified_command_system.md](11_unified_command_system.md).

**Key Routing Principles:**
- **Main Chat**: Player commands routed to `PLAYER_COORDINATOR`
- **Leadership Chat**: Leadership commands routed to `TEAM_ADMINISTRATOR` or `SQUAD_SELECTOR`
- **Permission-Based**: Commands routed based on permission level and agent capabilities

### Tool Independence

**CRITICAL**: Tools must be completely independent functions and receive all necessary context via `Task.config`:

- **❌ NEVER**: Tools calling other tools or services directly (delegate via CrewAI tasks instead).
- **✅ ALWAYS**: Tools are simple, independent functions.
- **✅ ALWAYS**: Parameters passed directly via `Task.config`.
- **✅ ALWAYS**: Tools return simple string responses.

### Native CrewAI Features

**MANDATORY**: Use only CrewAI's native features and avoid re-implementing core functionalities:

- **✅ REQUIRED**: `@tool` decorator from `crewai.tools`.
- **✅ REQUIRED**: `Agent` class from `crewai`.
- **✅ REQUIRED**: `Task` class with `config` parameter for context.
- **✅ REQUIRED**: `Crew` orchestration (`process=Process.sequential` or `Process.hierarchical`).
- **✅ REQUIRED**: CrewAI's built-in memory management (EntityMemory, ShortTermMemory, LongTermMemory).
- **✅ REQUIRED**: CrewAI's delegation tools for inter-agent communication.
- **❌ FORBIDDEN**: Custom tool wrappers or parameter passing mechanisms that bypass `Task.config`.
- **❌ FORBIDDEN**: Custom agent orchestration logic outside of CrewAI's `Crew` class.
- **❌ FORBIDDEN**: Re-implementing memory management if CrewAI's native features suffice.