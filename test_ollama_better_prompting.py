#!/usr/bin/env python3
"""
Test Ollama with better prompting for agent compatibility
"""

from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage, SystemMessage

def test_better_prompting():
    """Test Ollama with system prompts to guide output format."""
    print("🤖 Testing Ollama with Better Prompting")
    print("=" * 50)
    
    # Create LLM with system prompt
    llm = OllamaLLM(
        model="llama3.1:8b-instruct-q4_0",
        temperature=0.5
    )
    
    # Test 1: Direct call with system prompt
    print("\n🧪 Test 1: Direct call with system prompt")
    messages = [
        SystemMessage(content="You are a helpful assistant. Always respond in a clear, concise manner. When asked to say hello, respond with just the greeting and any requested emoji."),
        HumanMessage(content="Say 'Hello from KICKAI!' and add a football emoji.")
    ]
    
    try:
        response = llm.invoke(messages)
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Agent-style prompt
    print("\n🧪 Test 2: Agent-style prompt")
    agent_prompt = """You are an AI agent. You have access to tools and must respond in a specific format.

When you need to use a tool, respond with:
Thought: [your reasoning]
Action: [tool_name]
Action Input: [input for the tool]

When you have the final answer, respond with:
Final Answer: [your answer]

Current task: Say hello to KICKAI and add a football emoji. You don't need to use any tools for this simple task."""

    try:
        response = llm.invoke(agent_prompt)
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: ReAct format prompt
    print("\n🧪 Test 3: ReAct format prompt")
    react_prompt = """Answer the following question using the ReAct format:

Question: Say hello to KICKAI and add a football emoji.

Available tools:
- hello_tool: Returns a hello message

Format your response as:
Thought: [your reasoning]
Action: [tool_name or "Final Answer"]
Action Input: [input or final answer]

Begin:"""

    try:
        response = llm.invoke(react_prompt)
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_better_prompting() 