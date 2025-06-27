#!/usr/bin/env python3
"""
Comprehensive CrewAI test with detailed logging to debug issues.
"""

import os
import logging
import traceback
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
from langchain_community.tools import DuckDuckGoSearchRun

# Load environment variables
load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crewai_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_ollama_connection():
    """Test basic Ollama connection."""
    logger.info("=== Testing Ollama Connection ===")
    try:
        llm = Ollama(model="llama3.1:8b-instruct-q4_0")
        logger.info("Ollama LLM created successfully")
        
        # Test a simple call
        response = llm.invoke("Say hello in one word")
        logger.info(f"Ollama response: {response}")
        return True
    except Exception as e:
        logger.error(f"Ollama connection failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_crewai_minimal():
    """Test minimal CrewAI setup."""
    logger.info("=== Testing Minimal CrewAI Setup ===")
    try:
        # Create LLM
        llm = Ollama(model="llama3.1:8b-instruct-q4_0")
        logger.info("LLM created for CrewAI")
        
        # Create a simple agent
        agent = Agent(
            role='Test Agent',
            goal='Test if CrewAI works with Ollama',
            backstory='A simple test agent',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        logger.info("Agent created successfully")
        
        # Create a simple task
        task = Task(
            description='Say "Hello from CrewAI"',
            agent=agent,
            expected_output="A greeting message from CrewAI"
        )
        logger.info("Task created successfully")
        
        # Create crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True,
            memory=False
        )
        logger.info("Crew created successfully")
        
        # Execute
        logger.info("Starting crew execution...")
        result = crew.kickoff()
        logger.info(f"Crew execution completed: {result}")
        return True
        
    except Exception as e:
        logger.error(f"CrewAI minimal test failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_crewai_with_tools():
    """Test CrewAI with tools."""
    logger.info("=== Testing CrewAI with Tools ===")
    try:
        # Create LLM
        llm = Ollama(model="llama3.1:8b-instruct-q4_0")
        logger.info("LLM created for CrewAI with tools")
        
        # Create search tool
        search_tool = DuckDuckGoSearchRun()
        logger.info("Search tool created")
        
        # Create agent with tool
        agent = Agent(
            role='Researcher',
            goal='Research and provide information',
            backstory='A research agent that uses search tools',
            verbose=True,
            allow_delegation=False,
            tools=[search_tool],
            llm=llm
        )
        logger.info("Agent with tools created successfully")
        
        # Create task
        task = Task(
            description='Search for information about Python programming',
            agent=agent,
            expected_output="Information about Python programming from search results"
        )
        logger.info("Task created successfully")
        
        # Create crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True,
            memory=False
        )
        logger.info("Crew with tools created successfully")
        
        # Execute
        logger.info("Starting crew execution with tools...")
        result = crew.kickoff()
        logger.info(f"Crew execution with tools completed: {result}")
        return True
        
    except Exception as e:
        logger.error(f"CrewAI with tools test failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_crewai_llm_direct():
    """Test LLM directly with CrewAI format."""
    logger.info("=== Testing LLM Direct with CrewAI Format ===")
    try:
        llm = Ollama(model="llama3.1:8b-instruct-q4_0")
        
        # Test with a prompt that might be similar to what CrewAI sends
        test_prompt = """You are a helpful AI assistant. Please respond to the following request:

Request: Say hello and introduce yourself briefly.

Please provide a clear, concise response."""
        
        logger.info("Testing LLM with CrewAI-style prompt...")
        response = llm.invoke(test_prompt)
        logger.info(f"LLM response: {response}")
        
        # Test with JSON format request
        json_prompt = """You are a helpful AI assistant. Please respond in JSON format.

Request: Provide your name and role in JSON format.

Response format:
{
    "name": "your name",
    "role": "your role"
}"""
        
        logger.info("Testing LLM with JSON format request...")
        json_response = llm.invoke(json_prompt)
        logger.info(f"LLM JSON response: {json_response}")
        
        return True
        
    except Exception as e:
        logger.error(f"LLM direct test failed: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all tests."""
    logger.info("=== Starting Comprehensive CrewAI Debug Tests ===")
    
    # Test 1: Basic Ollama connection
    if not test_ollama_connection():
        logger.error("Basic Ollama connection failed. Stopping tests.")
        return
    
    # Test 2: LLM direct testing
    test_crewai_llm_direct()
    
    # Test 3: Minimal CrewAI
    test_crewai_minimal()
    
    # Test 4: CrewAI with tools
    test_crewai_with_tools()
    
    logger.info("=== All tests completed ===")

if __name__ == "__main__":
    main() 