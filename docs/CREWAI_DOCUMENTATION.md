# CrewAI Documentation - Comprehensive Guide

*Last Updated: January 2025*  
*CrewAI Version: 0.98+ (Latest)*

## Table of Contents

1. [Introduction & Overview](#introduction--overview)
2. [Installation & Setup](#installation--setup)
3. [Core Concepts](#core-concepts)
4. [Agents](#agents)
5. [Tasks](#tasks)
6. [Crews](#crews)
7. [Tools](#tools)
8. [Memory Systems](#memory-systems)
9. [CrewAI Flows (2025)](#crewai-flows-2025)
10. [LLM Integration](#llm-integration)
11. [Best Practices](#best-practices)
12. [API Reference](#api-reference)
13. [Examples & Use Cases](#examples--use-cases)
14. [Troubleshooting](#troubleshooting)

---

## Introduction & Overview

### What is CrewAI?

CrewAI is a cutting-edge, open-source Python framework for orchestrating role-playing, autonomous AI agents. By fostering collaborative intelligence, CrewAI empowers agents to work together seamlessly, tackling complex tasks that require multiple specialized skills.

**Key Features:**
- **Standalone Framework**: Built from scratch, independent of LangChain or other frameworks
- **Autonomous Collaboration**: Agents work together with true agency and decision-making
- **Role-Based Architecture**: Each agent has distinct expertise, tools, and responsibilities  
- **Event-Driven Workflows**: New Flows feature for precise control over complex automations
- **Enterprise-Ready**: Scalable with tracing, observability, and unified control plane

### 2025 Updates

CrewAI has reached significant milestones:
- **30.5K GitHub stars** and **1M monthly downloads**
- **100,000+ certified developers** through community courses
- Major new features: **CrewAI Flows**, **Enterprise Suite**, **Enhanced Memory**
- Optimized for production-ready AI automation

---

## Installation & Setup

### Requirements
- Python >=3.10 <3.14
- UV package manager (recommended) or pip

### Installation

```bash
# Basic installation
pip install crewai

# With additional tools
pip install 'crewai[tools]'

# Development installation
git clone https://github.com/crewAIInc/crewAI.git
cd crewAI
pip install -e .
```

### Environment Setup

```bash
# Create virtual environment
python -m venv crewai-env
source crewai-env/bin/activate  # Linux/Mac
# or
crewai-env\Scripts\activate  # Windows

# Install dependencies
pip install crewai python-dotenv
```

---

## Core Concepts

### 1. Agents
Individual AI entities with defined roles, goals, and capabilities. Each agent has:
- **Role**: Specific function or expertise area
- **Goal**: Primary objective to achieve
- **Backstory**: Context that shapes behavior
- **Tools**: Available functions and integrations

### 2. Tasks
Specific assignments completed by agents, including:
- **Description**: What needs to be done
- **Expected Output**: Desired result format
- **Agent**: Responsible agent (optional)
- **Tools**: Required tools for execution

### 3. Crews
Collections of agents working together toward a common goal:
- **Process**: Workflow definition (sequential, hierarchical)
- **Memory**: Shared context and learning
- **Verbose**: Logging and monitoring settings

### 4. Flows (New in 2025)
Event-driven workflows providing precise control over complex automations:
- **Event-Based**: Triggered by specific conditions
- **Fine-Grained Control**: Detailed execution paths
- **Production-Ready**: Enterprise-grade reliability

---

## Agents

### Agent Creation

```python
from crewai import Agent

# Basic agent
agent = Agent(
    role="Senior Data Researcher",
    goal="Research and analyze data trends",
    backstory="You are an expert data researcher with 10+ years of experience...",
    verbose=True,
    allow_delegation=False
)

# Advanced agent with tools and memory
from crewai_tools import SerperDevTool

agent = Agent(
    role="Research Specialist",
    goal="Conduct thorough research on given topics",
    backstory="""You are a meticulous researcher with expertise in 
                 gathering and analyzing information from multiple sources.""",
    tools=[SerperDevTool()],
    verbose=True,
    memory=True,
    max_iter=5,
    max_rpm=10
)
```

### Agent Configuration

```python
# Using configuration dictionary
agent_config = {
    "role": "Content Writer",
    "goal": "Create engaging content",
    "backstory": "Expert writer...",
    "tools": [writing_tool],
    "llm": custom_llm,
    "system_template": "Custom system template...",
    "prompt_template": "Custom prompt template...",
    "response_template": "Custom response template..."
}

agent = Agent(**agent_config)
```

### Agent Properties

| Property | Type | Description |
|----------|------|-------------|
| `role` | str | Agent's role/title |
| `goal` | str | Primary objective |
| `backstory` | str | Context and personality |
| `tools` | List | Available tools |
| `llm` | LLM | Language model |
| `verbose` | bool | Enable detailed logging |
| `allow_delegation` | bool | Can delegate to other agents |
| `max_iter` | int | Maximum iterations |
| `max_rpm` | int | Rate limiting |
| `memory` | bool | Enable memory |

---

## Tasks

### Task Creation

```python
from crewai import Task

# Basic task
task = Task(
    description="Research the latest AI trends for 2025",
    expected_output="A comprehensive report with top 10 AI trends",
    agent=research_agent
)

# Advanced task with tools and context
task = Task(
    description="Analyze market data and create investment recommendations",
    expected_output="Investment report with 3-5 recommendations",
    agent=analyst_agent,
    tools=[market_data_tool, analysis_tool],
    async_execution=False,
    context=[previous_task],
    output_file="investment_report.md"
)
```

### Task Configuration

```python
# Structured output with Pydantic
from pydantic import BaseModel

class ReportOutput(BaseModel):
    title: str
    summary: str
    recommendations: List[str]
    confidence_score: float

task = Task(
    description="Generate investment report",
    expected_output="Structured investment analysis",
    agent=analyst_agent,
    output_pydantic=ReportOutput
)
```

### Task Properties

| Property | Type | Description |
|----------|------|-------------|
| `description` | str | Task details |
| `expected_output` | str | Desired output format |
| `agent` | Agent | Assigned agent |
| `tools` | List | Required tools |
| `context` | List | Dependent tasks |
| `async_execution` | bool | Asynchronous execution |
| `output_file` | str | Output file path |
| `output_pydantic` | BaseModel | Structured output |
| `callback` | function | Post-execution callback |

---

## Crews

### Crew Creation

```python
from crewai import Crew, Process

# Basic crew
crew = Crew(
    agents=[research_agent, writer_agent],
    tasks=[research_task, writing_task],
    verbose=2
)

# Advanced crew configuration
crew = Crew(
    agents=[research_agent, analyst_agent, writer_agent],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=100,
    share_crew=False,
    manager_llm=manager_llm,
    function_calling_llm=function_llm,
    verbose=2,
    output_log_file="crew_log.txt"
)
```

### Process Types

```python
from crewai import Process

# Sequential execution (default)
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    process=Process.sequential
)

# Hierarchical execution with manager
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    process=Process.hierarchical,
    manager_llm=manager_llm
)
```

### Crew Execution

```python
# Execute crew
result = crew.kickoff()

# Execute with inputs
result = crew.kickoff(inputs={
    "topic": "AI trends 2025",
    "format": "markdown"
})

# Asynchronous execution
import asyncio

async def run_crew():
    result = await crew.kickoff_async()
    return result

result = asyncio.run(run_crew())
```

---

## Tools

### Creating Custom Tools

#### Using @tool Decorator

```python
from crewai.tools import BaseTool, tool
import requests

@tool("Weather Information")
def get_weather(location: str) -> str:
    """Get current weather for a location."""
    # API call implementation
    response = requests.get(f"https://api.weather.com/{location}")
    return f"Weather in {location}: {response.json()['weather']}"

# Use with agent
agent = Agent(
    role="Weather Assistant",
    tools=[get_weather]
)
```

#### Using BaseTool Class

```python
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    location: str = Field(description="Location for weather lookup")

class WeatherTool(BaseTool):
    name: str = "Weather Lookup"
    description: str = "Get current weather information"
    args_schema: Type[BaseModel] = WeatherInput
    
    def _run(self, location: str) -> str:
        # Implementation
        return f"Weather data for {location}"
```

### Built-in Tools

```python
from crewai_tools import (
    SerperDevTool,    # Web search
    WebsiteSearchTool, # Website scraping
    FileReadTool,     # File operations
    DirectoryReadTool, # Directory operations
    CodeDocsSearchTool, # Code documentation
    YoutubeVideoSearchTool # YouTube search
)

# Configure tools
search_tool = SerperDevTool(api_key="your_serper_key")
web_tool = WebsiteSearchTool()

agent = Agent(
    role="Research Assistant",
    tools=[search_tool, web_tool]
)
```

---

## Memory Systems

### Memory Types

#### Short-term Memory
```python
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    memory=True  # Enables short-term memory
)
```

#### Long-term Memory
```python
from crewai.memory import LongTermMemory

crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    memory=True,
    long_term_memory=LongTermMemory(
        storage_type="qdrant",  # or "chroma"
        storage_config={
            "host": "localhost",
            "port": 6333
        }
    )
)
```

#### Entity Memory
```python
from crewai.memory import EntityMemory

crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    memory=True,
    entity_memory=EntityMemory()
)
```

### Memory Configuration

```python
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    memory=True,
    memory_config={
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "crew_memory"
        }
    }
)
```

---

## CrewAI Flows (2025)

### Introduction to Flows

Flows are production-ready, event-driven workflows that provide precise control over complex automations. They complement Crews by offering fine-grained control over execution paths.

### Basic Flow Example

```python
from crewai.flow import Flow, listen, start

class ResearchFlow(Flow):
    
    @start()
    def start_research(self):
        return "Starting research process"
    
    @listen(start_research)
    def gather_data(self, context):
        # Trigger crew for data gathering
        crew = self.create_research_crew()
        result = crew.kickoff()
        return result
    
    @listen(gather_data)
    def analyze_data(self, context):
        # Trigger analysis crew
        crew = self.create_analysis_crew()
        result = crew.kickoff(inputs=context)
        return result
    
    @listen(analyze_data)
    def generate_report(self, context):
        # Final report generation
        return f"Research completed: {context}"

# Execute flow
flow = ResearchFlow()
result = flow.kickoff()
```

### Flow with Conditions

```python
from crewai.flow import Flow, listen, start, router

class ConditionalFlow(Flow):
    
    @start()
    def begin(self):
        return {"data_quality": "high"}
    
    @router(begin)
    def route_based_on_quality(self, context):
        if context["data_quality"] == "high":
            return "process_immediately"
        else:
            return "needs_cleaning"
    
    @listen("process_immediately")
    def fast_process(self, context):
        return "Fast processing completed"
    
    @listen("needs_cleaning")
    def clean_and_process(self, context):
        return "Data cleaned and processed"
```

### Flow Benefits

- **Event-Driven**: Responds to specific triggers and conditions
- **Precise Control**: Fine-grained workflow management
- **Production-Ready**: Enterprise-grade reliability and monitoring
- **Combines with Crews**: Use crews within flow steps for complex processing

---

## LLM Integration

### Supported LLM Providers

CrewAI supports multiple LLM providers:

```python
from crewai import LLM

# OpenAI
llm = LLM(
    model="gpt-4",
    api_key="your_openai_key"
)

# Groq
llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key="your_groq_key"
)

# Google Gemini
llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key="your_google_key"
)

# Ollama (local)
llm = LLM(
    model="ollama/llama3.1:8b",
    base_url="http://localhost:11434"
)

# Azure OpenAI
llm = LLM(
    model="azure/gpt-4",
    api_key="your_azure_key",
    api_version="2024-02-15-preview",
    azure_endpoint="your_endpoint"
)
```

### Agent-Specific LLMs

```python
# Different LLMs for different agents
researcher = Agent(
    role="Researcher",
    llm=LLM(model="gpt-4")  # More capable for research
)

writer = Agent(
    role="Writer", 
    llm=LLM(model="gpt-3.5-turbo")  # Cost-effective for writing
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task]
)
```

---

## Best Practices

### 1. Agent Design

```python
# ✅ Good: Specific role and clear goal
agent = Agent(
    role="Senior Financial Analyst",
    goal="Analyze market data and provide investment recommendations",
    backstory="""You are a seasoned financial analyst with 15 years of experience 
                 in equity research and portfolio management. You specialize in 
                 technology sector analysis and have a track record of identifying 
                 high-growth opportunities.""",
    tools=[market_data_tool, financial_analysis_tool],
    verbose=True
)

# ❌ Bad: Vague role and unclear goal
agent = Agent(
    role="Analyst",
    goal="Do analysis",
    backstory="You analyze things."
)
```

### 2. Task Definition

```python
# ✅ Good: Clear description and expected output
task = Task(
    description="""Analyze the quarterly earnings reports of FAANG companies 
                   (Facebook, Amazon, Apple, Netflix, Google) for Q4 2024. 
                   Focus on revenue growth, profit margins, and future guidance.""",
    expected_output="""A structured report containing:
                       1. Executive summary
                       2. Individual company analysis
                       3. Comparative analysis
                       4. Investment recommendations
                       5. Risk assessment""",
    agent=financial_agent,
    tools=[earnings_tool, market_data_tool]
)
```

### 3. Memory Management

```python
# Enable memory for learning and context retention
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    memory=True,
    memory_config={
        "provider": "qdrant",
        "config": {
            "collection_name": "project_memory",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
        }
    }
)
```

### 4. Error Handling

```python
import logging
from crewai.exceptions import CrewException

logging.basicConfig(level=logging.INFO)

try:
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()
except CrewException as e:
    logging.error(f"Crew execution failed: {e}")
    # Handle gracefully
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    # Fallback mechanism
```

### 5. Performance Optimization

```python
# Use caching for repeated operations
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    cache=True,
    max_rpm=50,  # Rate limiting
    verbose=1    # Reduce logging overhead
)

# Async execution for I/O bound tasks
async def run_multiple_crews():
    tasks = [crew1.kickoff_async(), crew2.kickoff_async()]
    results = await asyncio.gather(*tasks)
    return results
```

---

## API Reference

### Agent Class

```python
class Agent:
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: List[BaseTool] = None,
        llm: LLM = None,
        function_calling_llm: LLM = None,
        max_iter: int = 25,
        max_rpm: int = None,
        verbose: bool = False,
        allow_delegation: bool = False,
        step_callback: Callable = None,
        cache: bool = True,
        system_template: str = None,
        prompt_template: str = None,
        response_template: str = None,
        memory: bool = False,
        max_execution_time: int = None,
        use_system_prompt: bool = True,
        respect_context_window: bool = True
    )
```

### Task Class

```python
class Task:
    def __init__(
        self,
        description: str,
        expected_output: str,
        agent: Agent = None,
        tools: List[BaseTool] = None,
        async_execution: bool = False,
        context: List["Task"] = None,
        config: Dict = None,
        output_file: str = None,
        output_json: Type[BaseModel] = None,
        output_pydantic: Type[BaseModel] = None,
        callback: Callable = None,
        human_input: bool = False
    )
```

### Crew Class

```python
class Crew:
    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        process: Process = Process.sequential,
        verbose: bool = False,
        manager_llm: LLM = None,
        function_calling_llm: LLM = None,
        config: Dict = None,
        max_rpm: int = None,
        language: str = "en",
        memory: bool = False,
        cache: bool = True,
        embedder: Embedder = None,
        full_output: bool = False,
        step_callback: Callable = None,
        task_callback: Callable = None,
        share_crew: bool = False,
        output_log_file: bool = False,
        planning: bool = False,
        planning_llm: LLM = None
    )
    
    def kickoff(self, inputs: Dict = None) -> CrewOutput:
        """Execute the crew synchronously."""
        
    async def kickoff_async(self, inputs: Dict = None) -> CrewOutput:
        """Execute the crew asynchronously."""
```

---

## Examples & Use Cases

### 1. Content Creation Pipeline

```python
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, FileWriterTool

# Agents
researcher = Agent(
    role="Content Researcher",
    goal="Research comprehensive information on given topics",
    backstory="Expert researcher with deep knowledge of web research techniques",
    tools=[SerperDevTool()],
    verbose=True
)

writer = Agent(
    role="Content Writer", 
    goal="Create engaging, well-structured content",
    backstory="Professional writer specializing in technical content",
    tools=[FileWriterTool()],
    verbose=True
)

editor = Agent(
    role="Content Editor",
    goal="Review and improve content quality",
    backstory="Experienced editor with keen eye for detail and flow",
    verbose=True
)

# Tasks
research_task = Task(
    description="Research the latest trends in {topic} for 2025",
    expected_output="Comprehensive research summary with key points and sources",
    agent=researcher
)

writing_task = Task(
    description="Write a 1500-word article about {topic} based on research",
    expected_output="Well-structured article with introduction, main sections, and conclusion",
    agent=writer,
    context=[research_task]
)

editing_task = Task(
    description="Edit and improve the article for clarity and engagement",
    expected_output="Polished, publication-ready article",
    agent=editor,
    context=[writing_task],
    output_file="final_article.md"
)

# Crew
content_crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    verbose=2
)

# Execute
result = content_crew.kickoff(inputs={"topic": "Artificial Intelligence"})
```

### 2. Financial Analysis System

```python
# Financial analysis crew
analyst = Agent(
    role="Financial Analyst",
    goal="Analyze financial data and market trends",
    backstory="CFA with 10 years experience in equity research",
    tools=[market_data_tool, financial_calculator_tool]
)

researcher = Agent(
    role="Market Researcher", 
    goal="Gather comprehensive market intelligence",
    backstory="Expert in market research and competitive analysis",
    tools=[news_tool, company_data_tool]
)

# Tasks with structured output
class FinancialReport(BaseModel):
    symbol: str
    recommendation: str
    target_price: float
    risk_level: str
    key_metrics: Dict[str, float]
    analysis_summary: str

analysis_task = Task(
    description="Analyze {company} stock performance and financials",
    expected_output="Complete financial analysis with metrics and recommendation",
    agent=analyst,
    output_pydantic=FinancialReport
)

crew = Crew(agents=[analyst], tasks=[analysis_task])
result = crew.kickoff(inputs={"company": "AAPL"})
```

### 3. KICKAI Integration Example

```python
# KICKAI-specific CrewAI integration
from kickai.config.llm_config import get_llm_config
from kickai.core.enums import AgentRole

class KICKAICrewFactory:
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.llm_config = get_llm_config()
    
    def create_player_management_crew(self):
        # Use KICKAI's LLM configuration
        main_llm = self.llm_config.main_llm
        tool_llm = self.llm_config.tool_llm
        
        # Player coordinator agent
        player_agent = Agent(
            role="Player Coordinator",
            goal="Manage player registrations and status updates",
            backstory="Expert in football team player management",
            llm=main_llm,
            tools=[get_player_status_tool, register_player_tool],
            verbose=True
        )
        
        # Player analysis task
        analysis_task = Task(
            description="Analyze player {player_name} performance and status",
            expected_output="Player analysis report with recommendations", 
            agent=player_agent
        )
        
        return Crew(
            agents=[player_agent],
            tasks=[analysis_task],
            verbose=True
        )
```

---

## Troubleshooting

### Common Issues & Solutions

#### 1. LLM Connection Issues
```python
# Problem: LLM not connecting
# Solution: Verify API keys and model names
try:
    llm = LLM(model="groq/llama-3.1-8b-instant", api_key=api_key)
    test_response = llm.invoke("Hello")
    print("✅ LLM connection successful")
except Exception as e:
    print(f"❌ LLM connection failed: {e}")
```

#### 2. Tool Import Errors
```python
# Problem: Tool not found
# Solution: Check tool registration
from crewai.tools import tool

@tool("Custom Tool")
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Result: {param}"

# Verify tool is properly decorated and exported
```

#### 3. Memory Configuration Issues
```python
# Problem: Memory not persisting
# Solution: Proper memory configuration
crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True,
    memory_config={
        "provider": "qdrant",  # Ensure provider is installed
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": f"crew_memory_{team_id}"
        }
    }
)
```

#### 4. Task Execution Failures
```python
# Problem: Task fails with unclear error
# Solution: Add verbose logging and error handling
task = Task(
    description="Clear, specific task description",
    expected_output="Detailed expected output format",
    agent=agent,
    tools=[verified_tool],  # Ensure tools are working
)

crew = Crew(agents=[agent], tasks=[task], verbose=2)  # Maximum verbosity
```

### Debugging Tips

1. **Enable Verbose Logging**: Set `verbose=2` for detailed execution logs
2. **Test Tools Individually**: Verify each tool works before adding to agents
3. **Validate LLM Configuration**: Test LLM connections before creating crews
4. **Check Dependencies**: Ensure all required packages are installed
5. **Use Structured Outputs**: Define clear output formats with Pydantic models
6. **Monitor Rate Limits**: Set appropriate `max_rpm` values for your API limits

### Performance Optimization

1. **Use Caching**: Enable `cache=True` for repeated operations
2. **Optimize Prompts**: Keep descriptions clear and concise
3. **Batch Operations**: Use async execution for multiple crews
4. **Memory Management**: Configure appropriate memory settings
5. **Tool Efficiency**: Use efficient, well-tested tools

---

## Conclusion

CrewAI represents a significant advancement in multi-agent AI systems, combining the power of autonomous agent collaboration with precise workflow control. With the addition of Flows in 2025, developers can build sophisticated, production-ready AI automations that handle complex, real-world scenarios.

Key takeaways:
- **Start Simple**: Begin with basic agent-task-crew patterns
- **Scale Gradually**: Add complexity with memory, tools, and flows
- **Follow Best Practices**: Use clear descriptions, structured outputs, and proper error handling
- **Leverage Community**: Join the 100,000+ developer community for support and learning

For more information:
- **Official Documentation**: https://docs.crewai.com
- **GitHub Repository**: https://github.com/crewAIInc/crewAI
- **Community Learning**: https://learn.crewai.com
- **Enterprise Solutions**: https://crewai.com/enterprise

---

*This documentation covers CrewAI version 0.98+ with the latest 2025 features. For the most up-to-date information, always refer to the official CrewAI documentation.*