#!/usr/bin/env python3
"""
CrewAI test with correct Ollama model format.
"""

import os
import logging
import traceback
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama

# Load environment variables
load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crewai_ollama_correct.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_crewai_with_correct_ollama():
    """Test CrewAI with correct Ollama model format."""
    logger.info("=== Testing CrewAI with Correct Ollama Format ===")
    try:
        # Create LLM with correct format for CrewAI
        llm = Ollama(model="llama3.1:8b-instruct-q4_0")
        logger.info("LLM created with Ollama")
        
        # Create a simple agent
        agent = Agent(
            role='Test Agent',
            goal='Test if CrewAI works with Ollama using correct format',
            backstory='A simple test agent for Ollama integration',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        logger.info("Agent created successfully")
        
        # Create a simple task
        task = Task(
            description='Say "Hello from CrewAI with Ollama"',
            agent=agent,
            expected_output="A greeting message from CrewAI with Ollama"
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
        logger.error(f"CrewAI test failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_crewai_with_ollama_prefix():
    """Test CrewAI with ollama/ prefix in model name."""
    logger.info("=== Testing CrewAI with Ollama Prefix ===")
    try:
        # Create LLM with ollama/ prefix
        llm = Ollama(model="ollama/llama3.1:8b-instruct-q4_0")
        logger.info("LLM created with ollama/ prefix")
        
        # Create a simple agent
        agent = Agent(
            role='Test Agent',
            goal='Test if CrewAI works with Ollama using ollama/ prefix',
            backstory='A simple test agent for Ollama integration with prefix',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        logger.info("Agent created successfully")
        
        # Create a simple task
        task = Task(
            description='Say "Hello from CrewAI with Ollama prefix"',
            agent=agent,
            expected_output="A greeting message from CrewAI with Ollama prefix"
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
        logger.error(f"CrewAI test with prefix failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_crewai_with_litellm_direct():
    """Test CrewAI with direct LiteLLM configuration."""
    logger.info("=== Testing CrewAI with Direct LiteLLM ===")
    try:
        import litellm
        
        # Test LiteLLM directly
        logger.info("Testing LiteLLM with Ollama directly...")
        response = litellm.completion(
            model="ollama/llama3.1:8b-instruct-q4_0",
            messages=[{"role": "user", "content": "Say hello"}],
            api_base="http://localhost:11434"
        )
        logger.info(f"LiteLLM direct response: {response}")
        
        # Create LLM with direct configuration
        llm = Ollama(model="llama3.1:8b-instruct-q4_0")
        logger.info("LLM created for CrewAI")
        
        # Create a simple agent
        agent = Agent(
            role='Test Agent',
            goal='Test if CrewAI works with direct LiteLLM',
            backstory='A simple test agent for direct LiteLLM integration',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        logger.info("Agent created successfully")
        
        # Create a simple task
        task = Task(
            description='Say "Hello from CrewAI with direct LiteLLM"',
            agent=agent,
            expected_output="A greeting message from CrewAI with direct LiteLLM"
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
        logger.error(f"CrewAI test with direct LiteLLM failed: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all tests."""
    logger.info("=== Starting CrewAI Ollama Correct Format Tests ===")
    
    # Test 1: Standard Ollama format
    test_crewai_with_correct_ollama()
    
    # Test 2: Ollama with prefix
    test_crewai_with_ollama_prefix()
    
    # Test 3: Direct LiteLLM
    test_crewai_with_litellm_direct()
    
    logger.info("=== All tests completed ===")

if __name__ == "__main__":
    main() 