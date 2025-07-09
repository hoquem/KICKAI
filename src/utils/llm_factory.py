#!/usr/bin/env python3
"""
LLM Factory for KICKAI System

This module provides a robust, type-safe factory for creating LLM instances.
Currently supports only Google Gemini as the LLM provider.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable
from src.core.enums import AIProvider

logger = logging.getLogger(__name__)


@runtime_checkable
class LLMInterface(Protocol):
    """Protocol defining the interface that LLM instances must implement."""
    
    def invoke(self, prompt: str) -> str:
        """Invoke the LLM with a prompt and return the response."""
        ...


@dataclass
class LLMConfig:
    """Configuration for LLM instances."""
    provider: AIProvider
    model_name: str
    api_key: str
    temperature: float = 0.7
    timeout_seconds: int = 30
    max_retries: int = 3


class LLMProviderError(Exception):
    """Exception raised when LLM provider operations fail."""
    pass


class LLMFactory:
    """
    Factory for creating LLM instances.
    
    This factory follows the Factory Pattern and ensures type safety.
    Currently supports only Google Gemini as the LLM provider.
    """
    
    @staticmethod
    def create_llm(config: LLMConfig) -> LLMInterface:
        """
        Create an LLM instance based on the provided configuration.
        
        Args:
            config: LLM configuration object
            
        Returns:
            LLM instance implementing the LLMInterface protocol
            
        Raises:
            LLMProviderError: If LLM creation fails
        """
        logger.info(f"Creating LLM with provider: {config.provider.value}, model: {config.model_name}")
        
        if config.provider != AIProvider.GOOGLE_GEMINI:
            raise LLMProviderError(f"Unsupported AI provider: {config.provider}. Only GOOGLE_GEMINI is supported.")
        
        return GeminiLLMFactory.create_gemini_llm(config)


class GeminiLLMFactory:
    """Factory specifically for creating Google Gemini LLM instances."""
    
    @staticmethod
    def create_gemini_llm(config: LLMConfig) -> LLMInterface:
        """
        Create a Google Gemini LLM instance.
        
        Args:
            config: LLM configuration object
            
        Returns:
            Gemini LLM instance implementing LLMInterface
            
        Raises:
            LLMProviderError: If Gemini LLM creation fails
        """
        try:
            import google.generativeai as genai
            
            # Configure Gemini with API key
            genai.configure(api_key=config.api_key)
            
            # Create the model
            model = genai.GenerativeModel(config.model_name)
            
            logger.info("✅ Google Gemini LLM created successfully")
            
            # Return wrapped model that implements LLMInterface
            return GeminiLLMWrapper(model, config)
            
        except ImportError:
            error_msg = "Google Generative AI package not installed. Please install google-generativeai."
            logger.error(error_msg)
            raise LLMProviderError(error_msg)
        except Exception as e:
            error_msg = f"Failed to create Google Gemini LLM: {e}"
            logger.error(error_msg)
            raise LLMProviderError(error_msg)


class GeminiLLMWrapper:
    """
    Wrapper for Google Gemini model to implement LLMInterface.
    
    This wrapper provides a consistent interface for the Gemini model
    and handles response extraction.
    """
    
    def __init__(self, model, config: LLMConfig):
        self.model = model
        self.config = config
    
    def invoke(self, prompt: str) -> str:
        """
        Invoke the Gemini model with a prompt.
        
        Args:
            prompt: The input prompt for the model
            
        Returns:
            The model's response as a string
            
        Raises:
            LLMProviderError: If the model invocation fails
        """
        try:
            response = self.model.generate_content(prompt)
            
            # Extract text from the Gemini response
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].text
            else:
                return str(response)
                
        except Exception as e:
            error_msg = f"Failed to invoke Gemini model: {e}"
            logger.error(error_msg)
            raise LLMProviderError(error_msg) 