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