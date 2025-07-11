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

- **Intent Recognition Agent**: A dedicated CrewAI agent, the "Intent Recognizer," will be the primary interface for natural language. Its sole job is to receive raw text from the user and translate it into a structured command and its associated parameters (e.g., `{"command": "add_player", "params": {"name": "John Smith", "position": "Striker"}}`), which the application layer can then process deterministically.

### Agentic & AI Architecture Principles

This section defines the core design patterns for the CrewAI-based agentic system.

- **Hierarchical Multi-Agent System**: The system must be structured as a crew of 9 specialized agents organized into logical layers:
    - **Primary Interface Layer** (`Message Processor`): Handles initial user interaction and routing.
    - **Strategic Layer** (`Team Manager`, `Learning Agent`): Oversees high-level planning, coordination, and system improvement.
    - **Operational Layer** (`Player Coordinator`, `Communication Specialist`, `Finance Manager`): Manages day-to-day team operations.
    - **Specialized Layer** (`Match Analyst`, `Squad Selection Specialist`, `Analytics Specialist`): Provides deep, domain-specific analysis.

- **Intelligent Routing & Task Decomposition**:
    - An LLM-powered **Intelligent Router** must serve as the entry point for natural language requests. Its responsibility is to analyze the request's complexity and intent.
    - Based on the analysis, the router must select the appropriate agent, pair of agents, or a multi-agent crew to handle the task.
    - For complex requests, a **Dynamic Task Decomposer** must be used to break the request into a sequence of smaller, manageable sub-tasks assigned to the appropriate agents.

- **Defined Communication Patterns**: Agent interactions must follow established patterns:
    - **Delegation**: A higher-level agent passes a specific task to a specialist agent.
    - **Collaboration**: Multiple agents work together, sharing information to complete a complex task that spans their domains.
    - **Consensus**: Multiple agents provide input or suggestions on a topic, with a manager agent responsible for reaching a final decision.

- **Dedicated Learning & Adaptation**: A dedicated **Learning Agent** is a core component. Its purpose is to analyze interaction data, learn user preferences and successful response patterns, and provide feedback to optimize other agents' prompts and routing logic. The Learning Agent provides:
    - **Pattern Learning**: Analyzes message-response pairs for patterns and success rates
    - **User Preference Analysis**: Learns communication style, response length, and topic preferences
    - **Response Optimization**: Dynamically adapts responses based on learned preferences
    - **System Improvement**: Monitors performance and suggests system enhancements

- **Abstracted Tool-Based Execution**: Agents **must not** interact directly with external systems (e.g., Firebase, Telegram API). All external actions must be performed through a **Tool Layer**. These tools (e.g., `PlayerTools`, `TelegramTools`) abstract the implementation details and are the only components that interact directly with infrastructure services.