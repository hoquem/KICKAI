# CrewAI Context Passing Strategic Solution

## Problem Analysis

The current system is showing `"TO_BE_EXTRACTED_FROM_CONTEXT"` instead of actual team_id because:

1. **CrewAI's Native Limitation**: CrewAI tools don't automatically receive execution context
2. **Broken Wrapper System**: The `ContextAwareToolWrapper` is trying to extract context from task descriptions using regex, which is unreliable
3. **Architectural Mismatch**: The system assumes context flows automatically, but CrewAI requires explicit context passing
4. **Brittle Fallbacks**: Multiple layers of fallback mechanisms create confusion and inconsistency

## Root Cause

**CrewAI tools are stateless functions that don't have access to execution context by default.** The current approach of trying to extract context from task descriptions is fundamentally flawed because:

- Task descriptions are meant for the LLM, not for tool parameter extraction
- Regex-based extraction is brittle and unreliable
- The wrapper system adds unnecessary complexity
- Context extraction happens too late in the execution flow

## Strategic Solution: CrewAI-Native Context Passing

### 1. **Context Injection at Task Level** ✅

Instead of trying to pass context to individual tools, inject context into the task description that the LLM uses to call tools with the correct parameters.

```python
def _enhance_task_with_context(self, task: str, context: dict[str, Any]) -> str:
    """Inject context into task description for LLM consumption."""
    return f"""
EXECUTION CONTEXT:
- User ID: {context.get('user_id', 'unknown')}
- Team ID: {context.get('team_id', 'unknown')}
- Chat Type: {context.get('chat_type', 'unknown')}
- Username: {context.get('username', '')}

TASK: {task}

IMPORTANT: When calling tools, use the exact values from the execution context above.
For example:
- Use team_id="{context.get('team_id', 'unknown')}" in tool calls
- Use user_id="{context.get('user_id', 'unknown')}" in tool calls
"""
```

### 2. **Tool Parameter Standardization** ✅

Standardize all tools to accept explicit parameters instead of relying on context extraction:

```python
@tool("get_team_overview")
def get_team_overview(team_id: str, user_id: str = None) -> str:
    """Get team overview for a specific team."""
    # Tool now receives explicit team_id parameter
    return f"Team Overview for {team_id}: ..."
```

### 3. **LLM Prompt Engineering** ✅

Train the LLM to always pass explicit parameters to tools:

```python
def _create_agent_with_context_awareness(self, config: AgentConfig) -> Agent:
    """Create agent with enhanced context awareness."""
    
    # Add context awareness to agent's backstory
    enhanced_backstory = f"""
{config.backstory}

CONTEXT AWARENESS RULES:
1. Always extract team_id, user_id, and other context from the task description
2. Pass these as explicit parameters to tools, never use placeholders
3. Use the exact values provided in the execution context
4. If context is missing, ask for clarification rather than guessing
"""
    
    return Agent(
        role=config.role.value,
        goal=config.goal,
        backstory=enhanced_backstory,
        tools=tools,
        llm=self.llm
    )
```

### 4. **Remove ContextAwareToolWrapper** ✅

Eliminate the problematic wrapper system entirely:

```python
def _get_tools_for_role(self, tool_names: list[str]) -> list[Any]:
    """Get tools for a specific role without wrappers."""
    tools = []
    
    for tool_name in tool_names:
        tool_metadata = self.tool_registry.get_tool(tool_name)
        if tool_metadata and tool_metadata.tool_function:
            # Use tools directly - no wrapping needed
            tools.append(tool_metadata.tool_function)
            logger.info(f"✅ Found tool '{tool_name}' for role")
    
    return tools
```

### 5. **Context Validation at Task Level** ✅

Validate context completeness before task execution:

```python
def _validate_execution_context(self, context: dict[str, Any]) -> bool:
    """Validate that execution context has required fields."""
    required_fields = ['user_id', 'team_id', 'chat_type']
    missing_fields = [field for field in required_fields if not context.get(field)]
    
    if missing_fields:
        logger.error(f"❌ Missing required context fields: {missing_fields}")
        return False
    
    return True
```

## Implementation Plan

### Phase 1: Remove Wrapper System (Immediate)
1. Remove `ContextAwareToolWrapper` from tool registry
2. Update all tools to accept explicit parameters
3. Remove `requires_context` flag from tool metadata

### Phase 2: Enhance Task Context Injection (Immediate)
1. Improve `_enhance_task_with_context` method
2. Add context validation
3. Update agent creation to include context awareness

### Phase 3: Tool Standardization (Short-term)
1. Update all existing tools to use explicit parameters
2. Remove hardcoded team_id fallbacks
3. Add parameter validation to tools

### Phase 4: LLM Training (Short-term)
1. Enhance agent backstories with context awareness
2. Add context extraction examples to prompts
3. Test with various context scenarios

## Benefits of This Approach

1. **CrewAI-Native**: Works with CrewAI's design philosophy, not against it
2. **Reliable**: No more regex extraction or complex wrappers
3. **Maintainable**: Clear separation of concerns
4. **Debuggable**: Easy to trace context flow
5. **Scalable**: Works with any number of tools and agents
6. **Robust**: No brittle fallback mechanisms

## Migration Strategy

1. **Backward Compatibility**: Keep existing tool signatures during transition
2. **Gradual Rollout**: Update tools one feature at a time
3. **Testing**: Comprehensive testing with various context scenarios
4. **Monitoring**: Add logging to track context flow

## Success Metrics

1. **Context Accuracy**: 100% of tools receive correct team_id
2. **System Stability**: No more "TO_BE_EXTRACTED_FROM_CONTEXT" errors
3. **Performance**: Reduced complexity and faster execution
4. **Maintainability**: Easier to add new tools and agents

This solution addresses the root cause by working with CrewAI's architecture rather than trying to work around it, resulting in a more robust and maintainable system. 