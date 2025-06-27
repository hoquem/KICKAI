#!/usr/bin/env python3
"""
Minimal LangChain agent test with OllamaLLM
"""

from langchain_ollama import OllamaLLM
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.tools import tool

# Define a simple tool
@tool
def hello_tool(text: str) -> str:
    """Returns a hello message."""
    return f"Hello, {text}!"

llm = OllamaLLM(model="llama3.1:8b-instruct-q4_0", temperature=0.5)

# Create a simple agent
agent = initialize_agent(
    tools=[Tool.from_function(hello_tool, name="hello_tool", description="Returns a hello message.")],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

if __name__ == "__main__":
    print("\n🚀 Running minimal LangChain agent + Ollama test...")
    result = agent.run("Say hello to KICKAI and add a football emoji.")
    print("\nResult:")
    print(result) 