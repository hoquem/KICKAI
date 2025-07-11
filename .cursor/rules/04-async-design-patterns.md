# Async Design Patterns for KICKAI

## Principle: Async All the Way Down
- All service, tool, and handler methods that perform IO (database, network, LLM, etc.) **must be async**.
- Never call `asyncio.run()` or `asyncio.run_coroutine_threadsafe` inside the bot, agent, or handler code. Only use these at the very top-level (CLI entry points, test scripts).
- If you must call sync code from async, use `await loop.run_in_executor(...)`.
- All Telegram handlers, agents, and tools should be async and use `await` for all IO.

## Pattern: CQRS + Async Service Layer
- Define clear async interfaces for all operations that may touch the network, database, or external APIs.
- Use dependency injection to provide these services to your agents/tools/handlers.
- All command/query operations should be async and use `await`.

## Pattern: Adapter for Legacy Sync Code
- If you have legacy sync code, wrap it in an async adapter using `run_in_executor`.
- This keeps the async/sync boundary explicit and safe.

## Summary Table
| Pattern/Principle         | What to do                                      | Why?                        |
|---------------------------|-------------------------------------------------|-----------------------------|
| Async All the Way Down    | Make all IO methods async, use `await`          | Prevents event loop issues  |
| CQRS + Async Service Layer| Separate command/query, async interfaces        | Clear contracts, testable   |
| Adapter Pattern           | Wrap sync code in async adapters                | Safe async/sync boundary    |
| No asyncio.run() in Handlers| Only use at top-level scripts                 | Prevents event loop breakage|

## Migration Checklist
- [ ] Refactor all service/tool methods to be async if they perform IO
- [ ] Update all callers to use `await`
- [ ] Remove all `asyncio.run()` and `run_coroutine_threadsafe` from the codebase (except CLI/test entry points)
- [ ] Use `run_in_executor` for any sync code that must be called from async
- [ ] Add type hints and docstrings to clarify which methods are async 