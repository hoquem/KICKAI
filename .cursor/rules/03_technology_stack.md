# Technology Stack

- **Python**: Version 3.10+ with strict, mandatory type hinting everywhere.
- **Telegram Bot**: `python-telegram-bot` (version 20+), using its `asyncio` features.
- **Agents**: `CrewAI` for the agentic workforce.
- **Data Models**: `Pydantic` V2 for all data models in the `domain` layer (`Player`, `Match`, etc.) to enforce strict data validation.
- **DI Container**: `dependency-injector` for wiring the application together.

---
### AI Model Strategy (New Section)

- **Starting Point**: We will begin with a powerful, general-purpose model. All initial development will use the **Google Gemini** family of models via their API.

- **Design for Extensibility**: The connection to the LLM **must be abstracted**. We will define an `ILLMService` interface in the `application` layer. All agents and services will use this interface, not a concrete LLM client. This is crucial for swapping models without refactoring the core logic.

- **Incorporate Specialized Models**: The architecture must support integrating smaller, specialized open-source models from hubs like **Hugging Face**. The `ILLMService` abstraction will allow us to route specific tasks (e.g., high-accuracy NLP, intent recognition) to a dedicated, fine-tuned model while using Gemini for general reasoning.