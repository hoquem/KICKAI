#!/usr/bin/env python3
"""
Minimal CrewAI + Ollama test with debug output
"""

import sys
import os
from dotenv import load_dotenv
sys.path.append('src')
load_dotenv()

from crewai import Crew, Agent, Task
from langchain_ollama import OllamaLLM

try:
    print("[DEBUG] Initializing Ollama LLM...")
    llm = OllamaLLM(model="llama3.1:8b", temperature=0.5, verbose=True)
    print("[DEBUG] LLM initialized.")

    agent = Agent(
        role="Test Agent",
        goal="Say hello",
        backstory="You are a helpful assistant.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[]
    )
    print("[DEBUG] Agent created.")

    task = Task(
        description="Say 'Hello from CrewAI and Ollama!' and add a football emoji.",
        agent=agent,
        expected_output="A friendly greeting with a football emoji."
    )
    print("[DEBUG] Task created.")

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    print("[DEBUG] Crew created.")

    print("\n🚀 Running minimal CrewAI + Ollama test...")
    result = crew.kickoff()
    print("\nResult:")
    print(result)

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc() 