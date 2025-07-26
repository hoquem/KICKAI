# CrewAI Native Implementation Guide

## 🎯 **Overview**

This document serves as the **definitive guide** for implementing CrewAI native features in the KickAI system. **All implementations MUST use CrewAI's native capabilities** - no custom workarounds, no invented solutions, no non-standard patterns.

## 🚨 **CrewAI Native First Principle**

> **ALWAYS use CrewAI's built-in features before inventing custom solutions.**
> 
> - Use `Task.config` for context passing
> - Use `@tool` decorator for tool creation
> - Use `Agent` and `Crew` classes as intended
> - Use CrewAI's parameter passing mechanisms
> - Use CrewAI's orchestration patterns

## ✅ **Implementation Status: COMPLETED**

All phases have been successfully implemented using **100% CrewAI native features**.

## 🏗️ **CrewAI Native Architecture**

### **1. Context Passing Strategy**

**CrewAI Native Approach (REQUIRED):**
- ✅ Use `Task.config` parameter for context data
- ✅ Include context in `Task.description` for LLM access
- ✅ Let LLM extract parameters from context intelligently
- ✅ Tools receive parameters directly from LLM decisions
- ❌ **NEVER** use custom context extraction wrappers
- ❌ **NEVER** invent custom parameter passing mechanisms

### **2. Task Creation (CrewAI Native)**

**File**: `kickai/agents/configurable_agent.py`

```python
# ✅ CORRECT: CrewAI Native Task Creation
async def execute(self, task: str, context: dict[str, Any] = None) -> str:
    """Execute a task using CrewAI's native context passing."""
    try:
        # Include context data in the task description for the LLM to use
        enhanced_task = task
        if context:
            context_info = []
            for key, value in context.items():
                if isinstance(value, str) and value.strip():
                    context_info.append(f"{key}: {value}")
            
            if context_info:
                enhanced_task = f"{task}\n\nAvailable context parameters: {', '.join(context_info)}\n\nPlease use these context parameters when calling tools that require them."
        
        # ✅ Use CrewAI's native Task creation
        crew_task = Task(
            description=enhanced_task,
            agent=self._crew_agent,
            expected_output="A clear and helpful response to the user's request",
            config=context or {}  # ✅ Use Task.config for context data
        )
        
        # ✅ Use CrewAI's native Crew creation
        crew = Crew(
            agents=[self._crew_agent],
            tasks=[crew_task],
            verbose=True
        )
        
        # ✅ Use CrewAI's native kickoff method
        result = crew.kickoff()
        return result
        
    except Exception as e:
        logger.error(f"❌ [CONFIGURABLE AGENT] Task execution failed: {e}")
        raise
```

### **3. Tool Implementation (CrewAI Native)**

**File**: `kickai/features/player_registration/domain/tools/player_tools.py`

```python
# ✅ CORRECT: CrewAI Native Tool Implementation
from crewai.tools import tool

@tool("get_my_status")
async def get_my_status(team_id: str, user_id: str) -> str:
    """
    Get the current status of the requesting user.
    
    This tool requires team_id and user_id parameters which should be provided from the available context.
    
    Args:
        team_id: Team ID from the available context parameters
        user_id: User ID (telegram user ID) from the available context parameters
        
    Returns:
        User's current status or error message
        
    Example:
        If context provides "team_id: TEST, user_id: 12345", 
        call this tool with team_id="TEST" and user_id="12345"
    """
    try:
        # Validate inputs - these should NOT be None, they must come from context
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return format_tool_error("Team ID is required and must be provided from available context")
        
        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return format_tool_error("User ID is required and must be provided from available context")
        
        # Process the request using the provided parameters
        # ... implementation details ...
        
    except Exception as e:
        logger.error(f"Failed to get player status: {e}", exc_info=True)
        return format_tool_error(f"Failed to get player status: {e}")
```

### **4. Context Extraction (CrewAI Native)**

**File**: `kickai/agents/simplified_orchestration.py`

```python
# ✅ CORRECT: Extract context for CrewAI native usage
def _extract_agent_context(self, execution_context: dict) -> dict:
    """Extract relevant context data for CrewAI native context passing."""
    try:
        # Extract team_id and user_id from the execution_context
        team_id = None
        user_id = None
        
        # Handle nested security_context structure
        if 'security_context' in execution_context:
            security_context = execution_context['security_context']
            if isinstance(security_context, dict):
                team_id = security_context.get('team_id')
                user_id = security_context.get('user_id')
        
        # Fallback to direct extraction
        if not team_id:
            team_id = execution_context.get('team_id')
        if not user_id:
            user_id = execution_context.get('user_id')
        
        # Create clean context for CrewAI native usage
        agent_context = {}
        if team_id:
            agent_context['team_id'] = str(team_id)
        if user_id:
            agent_context['user_id'] = str(user_id)
        
        logger.info(f"🔍 [TASK EXECUTION] Extracted context: team_id={team_id}, user_id={user_id}")
        return agent_context
        
    except Exception as e:
        logger.error(f"❌ [TASK EXECUTION] Failed to extract agent context: {e}")
        return {}
```

## 🎯 **CrewAI Native Best Practices**

### **1. Task Creation**
- ✅ Use `Task(description=..., config=...)` for context passing
- ✅ Include context parameters in task description
- ✅ Use clear, structured context information
- ❌ **NEVER** use custom context injection methods

### **2. Tool Design**
- ✅ Use `@tool` decorator from `crewai.tools`
- ✅ Accept only the parameters your tool needs
- ✅ Provide comprehensive docstrings for LLM understanding
- ✅ Use clear parameter names that match context keys
- ❌ **NEVER** create custom tool wrappers
- ❌ **NEVER** use complex parameter extraction logic

### **3. Agent Configuration**
- ✅ Use CrewAI's `Agent` class as intended
- ✅ Pass tools directly to agents
- ✅ Use CrewAI's native tool assignment
- ❌ **NEVER** create custom agent wrappers

### **4. Crew Orchestration**
- ✅ Use `Crew(agents=..., tasks=...)` for orchestration
- ✅ Use `crew.kickoff()` for execution
- ✅ Let CrewAI handle agent coordination
- ❌ **NEVER** implement custom orchestration logic

### **5. Context Management**
- ✅ Extract context at orchestration level
- ✅ Pass clean context dictionaries to tasks
- ✅ Let LLM handle parameter extraction
- ❌ **NEVER** implement complex context parsing in tools

## ❌ **Anti-Patterns to Avoid**

### **1. Custom Context Wrappers**
```python
# ❌ WRONG: Custom context wrapper
class ContextAwareTool(BaseTool):
    def _run(self, *args, **kwargs):
        context = self._extract_context_from_args(args, kwargs)
        return self.original_tool(context, *args, **kwargs)

# ✅ CORRECT: CrewAI native tool
@tool("my_tool")
def my_tool(param1: str, param2: str) -> str:
    return process_data(param1, param2)
```

### **2. Manual Parameter Injection**
```python
# ❌ WRONG: Manual parameter injection
task_description = f"{task}\n\nContext: team_id={team_id}, user_id={user_id}"

# ✅ CORRECT: CrewAI native context passing
crew_task = Task(
    description=task,
    config={'team_id': team_id, 'user_id': user_id}
)
```

### **3. Custom Orchestration**
```python
# ❌ WRONG: Custom orchestration
def custom_execute(agent, task, context):
    # Custom execution logic
    pass

# ✅ CORRECT: CrewAI native orchestration
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

## 🧪 **Testing CrewAI Native Implementation**

### **1. Context Extraction Testing**
```python
def test_context_extraction():
    step = TaskExecutionStep()
    
    # Test nested security_context
    context = {
        'security_context': {
            'team_id': 'TEST',
            'user_id': '12345'
        }
    }
    result = step._extract_agent_context(context)
    assert result == {'team_id': 'TEST', 'user_id': '12345'}
```

### **2. Task Enhancement Testing**
```python
def test_task_enhancement():
    task = "Get my status"
    context = {'team_id': 'TEST', 'user_id': '12345'}
    
    enhanced_task = f"{task}\n\nAvailable context parameters: team_id: TEST, user_id: 12345\n\nPlease use these context parameters when calling tools that require them."
    
    assert "Available context parameters" in enhanced_task
    assert "team_id: TEST" in enhanced_task
```

## 📋 **Implementation Checklist**

### **✅ Completed**
- [x] Use CrewAI's `Task.config` for context passing
- [x] Use CrewAI's `@tool` decorator for tool creation
- [x] Use CrewAI's native parameter passing
- [x] Use CrewAI's `Agent` and `Crew` classes
- [x] Implement proper context extraction
- [x] Remove all custom context wrappers
- [x] Remove all manual parameter injection
- [x] Test CrewAI native implementation

### **🔄 Ongoing**
- [ ] Apply CrewAI native patterns to all tools
- [ ] Ensure all agents use CrewAI native features
- [ ] Validate all orchestration uses CrewAI patterns

## 🎯 **Key Principles**

1. **CrewAI Native First**: Always use CrewAI's built-in features
2. **No Custom Workarounds**: Don't invent solutions when CrewAI provides them
3. **LLM-Driven**: Let the LLM handle parameter extraction intelligently
4. **Simple and Clean**: Keep implementations simple and maintainable
5. **Standard Patterns**: Follow CrewAI's intended design patterns

## 📚 **CrewAI Native Resources**

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI Task API](https://docs.crewai.com/how-to/use-tasks/)
- [CrewAI Tools API](https://docs.crewai.com/how-to/use-tools/)
- [CrewAI Agents API](https://docs.crewai.com/how-to/use-agents/)

---

**Remember**: **ALWAYS use CrewAI native features. Never invent custom solutions when CrewAI provides built-in capabilities.** 