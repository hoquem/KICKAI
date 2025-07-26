# CrewAI Best Practices Guide

## 🎯 **Overview**

This document provides comprehensive best practices for using CrewAI in the KickAI system. **All implementations MUST follow these guidelines and use CrewAI's native features exclusively.**

## 🚨 **Core Principle: CrewAI Native First**

> **ALWAYS use CrewAI's built-in capabilities before inventing custom solutions.**
> 
> - Use CrewAI's native classes and methods
> - Follow CrewAI's intended design patterns
> - Leverage CrewAI's built-in features
> - Avoid custom workarounds and invented solutions

## 🏗️ **Agent Implementation**

### **✅ CORRECT: CrewAI Native Agent Creation**

```python
from crewai import Agent

# ✅ Use CrewAI's native Agent class
agent = Agent(
    role="Player Coordinator",
    goal="Manage player registration and status",
    backstory="Expert in player management and team coordination",
    tools=[get_my_status, add_player, get_all_players],
    verbose=True
)
```

### **❌ WRONG: Custom Agent Wrappers**

```python
# ❌ Don't create custom agent wrappers
class CustomAgent:
    def __init__(self, role, tools):
        self.role = role
        self.tools = tools
    
    def execute(self, task):
        # Custom execution logic
        pass
```

## 🛠️ **Tool Implementation**

### **✅ CORRECT: CrewAI Native Tool Creation**

```python
from crewai.tools import tool

@tool("get_my_status")
async def get_my_status(team_id: str, user_id: str) -> str:
    """
    Get the current status of the requesting user.
    
    Args:
        team_id: Team ID from context
        user_id: User ID from context
        
    Returns:
        User's current status or error message
    """
    # Implementation here
    return f"Status for user {user_id} in team {team_id}"
```

### **❌ WRONG: Custom Tool Wrappers**

```python
# ❌ Don't create custom tool wrappers
class CustomTool:
    def __init__(self, func, name):
        self.func = func
        self.name = name
    
    def run(self, *args, **kwargs):
        # Custom execution logic
        return self.func(*args, **kwargs)
```

## 📋 **Task Implementation**

### **✅ CORRECT: CrewAI Native Task Creation**

```python
from crewai import Task

# ✅ Use CrewAI's native Task class
task = Task(
    description="Get the status of the current user",
    agent=agent,
    expected_output="User's current status information",
    config={'team_id': 'TEST', 'user_id': '12345'}  # ✅ Use config for context
)
```

### **❌ WRONG: Custom Task Wrappers**

```python
# ❌ Don't create custom task wrappers
class CustomTask:
    def __init__(self, description, agent):
        self.description = description
        self.agent = agent
    
    def execute(self):
        # Custom execution logic
        pass
```

## 🚀 **Crew Orchestration**

### **✅ CORRECT: CrewAI Native Crew Usage**

```python
from crewai import Crew

# ✅ Use CrewAI's native Crew class
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    verbose=True
)

# ✅ Use CrewAI's native kickoff method
result = crew.kickoff()
```

### **❌ WRONG: Custom Orchestration**

```python
# ❌ Don't create custom orchestration
def custom_orchestrate(agents, tasks):
    for task in tasks:
        for agent in agents:
            if agent.can_handle(task):
                result = agent.execute(task)
                break
    return result
```

## 🔄 **Context Passing**

### **✅ CORRECT: CrewAI Native Context Passing**

```python
# ✅ Use Task.config for context data
task = Task(
    description="Process user request",
    agent=agent,
    config={
        'team_id': 'TEST',
        'user_id': '12345',
        'additional_context': 'some_data'
    }
)

# ✅ Include context in task description for LLM
enhanced_description = f"""
{original_description}

Available context parameters:
- team_id: {context['team_id']}
- user_id: {context['user_id']}

Please use these parameters when calling tools that require them.
"""
```

### **❌ WRONG: Custom Context Passing**

```python
# ❌ Don't invent custom context passing
def inject_context_manually(task_description, context):
    # Custom context injection logic
    return f"{task_description}\n\nContext: {context}"

# ❌ Don't use custom context wrappers
class ContextWrapper:
    def __init__(self, context):
        self.context = context
    
    def get_parameter(self, key):
        return self.context.get(key)
```

## 🎯 **Parameter Extraction**

### **✅ CORRECT: Let LLM Handle Parameter Extraction**

```python
@tool("my_tool")
def my_tool(param1: str, param2: str) -> str:
    """
    My tool that requires param1 and param2.
    
    Args:
        param1: First parameter from context
        param2: Second parameter from context
    """
    # LLM will automatically extract param1 and param2 from context
    return process_data(param1, param2)
```

### **❌ WRONG: Manual Parameter Extraction**

```python
# ❌ Don't manually extract parameters in tools
@tool("my_tool")
def my_tool(context: dict) -> str:
    # Manual parameter extraction
    param1 = context.get('param1')
    param2 = context.get('param2')
    return process_data(param1, param2)
```

## 🔧 **Error Handling**

### **✅ CORRECT: CrewAI Native Error Handling**

```python
@tool("my_tool")
def my_tool(param1: str, param2: str) -> str:
    try:
        # Validate parameters
        if not param1 or not param2:
            return "Error: Missing required parameters"
        
        # Process request
        result = process_data(param1, param2)
        return result
        
    except Exception as e:
        return f"Error: {str(e)}"
```

### **❌ WRONG: Complex Error Handling**

```python
# ❌ Don't create complex error handling systems
class ErrorHandler:
    def __init__(self):
        self.error_types = {}
    
    def handle_error(self, error, context):
        # Complex error handling logic
        pass
```

## 🧪 **Testing**

### **✅ CORRECT: Test CrewAI Native Features**

```python
def test_crewai_native_implementation():
    # Test CrewAI native agent creation
    agent = Agent(
        role="Test Agent",
        goal="Test goal",
        backstory="Test backstory",
        tools=[test_tool]
    )
    
    # Test CrewAI native task creation
    task = Task(
        description="Test task",
        agent=agent,
        config={'test_param': 'test_value'}
    )
    
    # Test CrewAI native crew creation
    crew = Crew(agents=[agent], tasks=[task])
    
    # Test execution
    result = crew.kickoff()
    assert result is not None
```

### **❌ WRONG: Test Custom Implementations**

```python
# ❌ Don't test custom implementations
def test_custom_implementation():
    custom_agent = CustomAgent("Test", [])
    custom_task = CustomTask("Test", custom_agent)
    result = custom_task.execute()
    assert result is not None
```

## 📚 **Best Practices Summary**

### **1. Always Use CrewAI Native Classes**
- ✅ `Agent` from `crewai`
- ✅ `Task` from `crewai`
- ✅ `Crew` from `crewai`
- ✅ `@tool` decorator from `crewai.tools`

### **2. Use CrewAI's Built-in Features**
- ✅ `Task.config` for context passing
- ✅ `crew.kickoff()` for execution
- ✅ LLM-driven parameter extraction
- ✅ Native error handling

### **3. Follow CrewAI's Design Patterns**
- ✅ Simple tool signatures
- ✅ Clear task descriptions
- ✅ Proper agent configuration
- ✅ Standard orchestration

### **4. Avoid Custom Workarounds**
- ❌ Custom agent wrappers
- ❌ Custom tool wrappers
- ❌ Custom task wrappers
- ❌ Custom orchestration logic
- ❌ Custom context passing
- ❌ Custom parameter extraction

## 🎯 **Implementation Checklist**

### **✅ Required for All New Code**
- [ ] Use `crewai.Agent` for agent creation
- [ ] Use `crewai.Task` for task creation
- [ ] Use `crewai.Crew` for orchestration
- [ ] Use `@tool` decorator for tool creation
- [ ] Use `Task.config` for context passing
- [ ] Let LLM handle parameter extraction
- [ ] Follow CrewAI's error handling patterns

### **❌ Never Implement**
- [ ] Custom agent classes
- [ ] Custom tool wrappers
- [ ] Custom task wrappers
- [ ] Custom orchestration logic
- [ ] Custom context passing mechanisms
- [ ] Custom parameter extraction logic

## 📖 **CrewAI Documentation References**

- [CrewAI Official Documentation](https://docs.crewai.com/)
- [CrewAI Agents Guide](https://docs.crewai.com/how-to/use-agents/)
- [CrewAI Tasks Guide](https://docs.crewai.com/how-to/use-tasks/)
- [CrewAI Tools Guide](https://docs.crewai.com/how-to/use-tools/)
- [CrewAI Crews Guide](https://docs.crewai.com/how-to/use-crews/)

## 🚨 **Remember**

**ALWAYS use CrewAI's native features. Never invent custom solutions when CrewAI provides built-in capabilities. This ensures maintainability, reliability, and proper integration with the CrewAI ecosystem.** 