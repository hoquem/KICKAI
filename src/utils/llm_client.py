"""
LLM Client Abstraction Layer

This module provides a pluggable LLM client system that supports multiple backends:
- Ollama (local)
- Google Gemini (cloud)
- OpenAI (cloud)
- Fallback to regex-based extraction

Design Patterns Used:
- Strategy Pattern: Different LLM backends
- Factory Pattern: Client creation
- Adapter Pattern: Unified interface for different APIs
- Dependency Injection: Easy testing and configuration
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    GEMINI = "gemini"
    OPENAI = "openai"
    FALLBACK = "fallback"


@dataclass
class LLMConfig:
    """Configuration for LLM clients."""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 256
    temperature: float = 0.2
    timeout: int = 30


@dataclass
class IntentResult:
    """Result of intent extraction."""
    intent: str
    entities: Dict[str, Any]
    confidence: float = 1.0
    provider: str = "unknown"
    error: Optional[str] = None


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate the configuration for this client."""
        pass
    
    @abstractmethod
    async def extract_intent(self, message: str, context: str = "") -> IntentResult:
        """Extract intent and entities from a message."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the LLM service is available."""
        pass


class OllamaClient(LLMClient):
    """Ollama LLM client for local inference."""
    
    def _validate_config(self) -> None:
        """Validate Ollama configuration."""
        if not self.config.model:
            raise ValueError("Ollama model name is required")
    
    async def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            import ollama
            # Try to list models to check if Ollama is running
            models = ollama.list()
            return any(model['name'] == self.config.model for model in models['models'])
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    async def extract_intent(self, message: str, context: str = "") -> IntentResult:
        """Extract intent using Ollama."""
        try:
            import ollama
            
            prompt = self._build_prompt(message, context)
            
            response = ollama.chat(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful football team onboarding assistant."},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "num_predict": self.config.max_tokens,
                    "temperature": self.config.temperature
                }
            )
            
            content = response['message']['content']
            if content:
                result = json.loads(content)
                return IntentResult(
                    intent=result.get('intent', 'unknown'),
                    entities=result.get('entities', {}),
                    confidence=result.get('confidence', 1.0),
                    provider="ollama"
                )
            else:
                return IntentResult(
                    intent="unknown",
                    entities={},
                    confidence=0.0,
                    provider="ollama",
                    error="Empty response from Ollama"
                )
                
        except Exception as e:
            logger.error(f"Ollama intent extraction failed: {e}")
            return IntentResult(
                intent="unknown",
                entities={},
                confidence=0.0,
                provider="ollama",
                error=str(e)
            )
    
    def _build_prompt(self, message: str, context: str = "") -> str:
        """Build the prompt for intent extraction."""
        return f"""
You are a helpful football team onboarding assistant. Extract the intent and any relevant entities from the following player message. Respond in JSON with 'intent', 'entities', and 'confidence' (0.0-1.0).

Context: {context}

Message: {message}

Respond only with valid JSON.
"""


class GeminiClient(LLMClient):
    """Google Gemini LLM client."""
    
    def _validate_config(self) -> None:
        """Validate Gemini configuration."""
        if not self.config.api_key:
            raise ValueError("Gemini API key is required")
        if not self.config.model:
            self.config.model = "gemini-pro"
    
    async def is_available(self) -> bool:
        """Check if Gemini is available."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config.api_key)
            # Try to list models
            models = genai.list_models()
            return any(model.name == f"models/{self.config.model}" for model in models)
        except Exception as e:
            logger.warning(f"Gemini not available: {e}")
            return False
    
    async def extract_intent(self, message: str, context: str = "") -> IntentResult:
        """Extract intent using Gemini."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.config.api_key)
            model = genai.GenerativeModel(self.config.model)
            
            prompt = self._build_prompt(message, context)
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )
            
            content = response.text
            if content:
                result = json.loads(content)
                return IntentResult(
                    intent=result.get('intent', 'unknown'),
                    entities=result.get('entities', {}),
                    confidence=result.get('confidence', 1.0),
                    provider="gemini"
                )
            else:
                return IntentResult(
                    intent="unknown",
                    entities={},
                    confidence=0.0,
                    provider="gemini",
                    error="Empty response from Gemini"
                )
                
        except Exception as e:
            logger.error(f"Gemini intent extraction failed: {e}")
            return IntentResult(
                intent="unknown",
                entities={},
                confidence=0.0,
                provider="gemini",
                error=str(e)
            )
    
    def _build_prompt(self, message: str, context: str = "") -> str:
        """Build the prompt for intent extraction."""
        return f"""
You are a helpful football team onboarding assistant. Extract the intent and any relevant entities from the following player message. Respond in JSON with 'intent', 'entities', and 'confidence' (0.0-1.0).

Context: {context}

Message: {message}

Respond only with valid JSON.
"""


class OpenAIClient(LLMClient):
    """OpenAI LLM client."""
    
    def _validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.config.api_key:
            raise ValueError("OpenAI API key is required")
        if not self.config.model:
            self.config.model = "gpt-3.5-turbo"
    
    async def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config.api_key)
            # Try to list models
            models = client.models.list()
            return any(model.id == self.config.model for model in models.data)
        except Exception as e:
            logger.warning(f"OpenAI not available: {e}")
            return False
    
    async def extract_intent(self, message: str, context: str = "") -> IntentResult:
        """Extract intent using OpenAI."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.config.api_key)
            
            prompt = self._build_prompt(message, context)
            
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return IntentResult(
                    intent=result.get('intent', 'unknown'),
                    entities=result.get('entities', {}),
                    confidence=result.get('confidence', 1.0),
                    provider="openai"
                )
            else:
                return IntentResult(
                    intent="unknown",
                    entities={},
                    confidence=0.0,
                    provider="openai",
                    error="Empty response from OpenAI"
                )
                
        except Exception as e:
            logger.error(f"OpenAI intent extraction failed: {e}")
            return IntentResult(
                intent="unknown",
                entities={},
                confidence=0.0,
                provider="openai",
                error=str(e)
            )
    
    def _build_prompt(self, message: str, context: str = "") -> str:
        """Build the prompt for intent extraction."""
        return f"""
You are a helpful football team onboarding assistant. Extract the intent and any relevant entities from the following player message. Respond in JSON with 'intent', 'entities', and 'confidence' (0.0-1.0).

Context: {context}

Message: {message}

Respond only with valid JSON.
"""


class FallbackClient(LLMClient):
    """Fallback client using regex-based intent extraction."""
    
    def _validate_config(self) -> None:
        """No validation needed for fallback client."""
        pass
    
    async def is_available(self) -> bool:
        """Fallback client is always available."""
        return True
    
    async def extract_intent(self, message: str, context: str = "") -> IntentResult:
        """Extract intent using pattern matching."""
        message_lower = message.lower().strip()
        
        # Team info and player listing patterns
        if any(word in message_lower for word in ['list', 'show', 'see', 'view', 'all', 'players', 'team', 'roster', 'squad']):
            if any(word in message_lower for word in ['players', 'team', 'roster', 'squad']):
                return IntentResult(
                    intent="get_team_info",
                    entities={"request_type": "list_players"},
                    confidence=0.9,
                    provider="fallback"
                )
        
        # Player info patterns
        if any(word in message_lower for word in ['my', 'info', 'information', 'details', 'status', 'phone', 'position', 'id']):
            return IntentResult(
                intent="get_player_info",
                entities={"info_type": "personal"},
                confidence=0.8,
                provider="fallback"
            )
        
        # Help patterns
        if any(word in message_lower for word in ['help', 'what', 'how', 'commands', 'available']):
            return IntentResult(
                intent="get_help",
                entities={},
                confidence=0.9,
                provider="fallback"
            )
        
        # Emergency contact patterns
        if any(word in message_lower for word in ['emergency', 'contact', 'phone', 'number']):
            return IntentResult(
                intent="update_emergency_contact",
                entities={"emergency_contact": message.strip()},
                confidence=0.8,
                provider="fallback"
            )
        
        # Date of birth patterns
        if any(word in message_lower for word in ['dob', 'birth', 'date', 'born']):
            return IntentResult(
                intent="update_date_of_birth",
                entities={"date_of_birth": message.strip()},
                confidence=0.8,
                provider="fallback"
            )
        
        # FA registration patterns
        if any(word in message_lower for word in ['fa', 'registered', 'registration', 'eligible']):
            # Check for positive confirmation first
            if any(word in message_lower for word in ['yes', 'y', 'eligible']):
                return IntentResult(
                    intent="update_fa_eligibility",
                    entities={"fa_eligible": True},
                    confidence=0.8,
                    provider="fallback"
                )
            # Check for negative confirmation
            elif any(word in message_lower for word in ['no', 'n', 'not eligible', 'ineligible']):
                return IntentResult(
                    intent="update_fa_eligibility",
                    entities={"fa_eligible": False},
                    confidence=0.8,
                    provider="fallback"
                )
            # Default to registration intent
            else:
                return IntentResult(
                    intent="update_fa_registration",
                    entities={"fa_registered": "yes" if "yes" in message_lower else "no"},
                    confidence=0.8,
                    provider="fallback"
                )
        
        # Profile update patterns
        if any(word in message_lower for word in ['name', 'phone', 'position', 'update']):
            return IntentResult(
                intent="update_profile",
                entities={"profile_update": message.strip()},
                confidence=0.7,
                provider="fallback"
            )
        
        # Confirmation patterns
        if any(word in message_lower for word in ['yes', 'confirm', 'correct', 'ok']):
            return IntentResult(
                intent="confirm",
                entities={},
                confidence=0.9,
                provider="fallback"
            )
        
        # Skip patterns
        if any(word in message_lower for word in ['skip', 'next', 'continue']):
            return IntentResult(
                intent="skip",
                entities={},
                confidence=0.9,
                provider="fallback"
            )
        
        # Default
        return IntentResult(
            intent="unknown",
            entities={},
            confidence=0.5,
            provider="fallback"
        )


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create_client(config: LLMConfig) -> LLMClient:
        """Create an LLM client based on configuration."""
        if config.provider == LLMProvider.OLLAMA:
            return OllamaClient(config)
        elif config.provider == LLMProvider.GEMINI:
            return GeminiClient(config)
        elif config.provider == LLMProvider.OPENAI:
            return OpenAIClient(config)
        elif config.provider == LLMProvider.FALLBACK:
            return FallbackClient(config)
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")


class LLMManager:
    """Manager for LLM clients with fallback and caching."""
    
    def __init__(self, configs: Dict[str, LLMConfig]):
        self.configs = configs
        self.clients: Dict[str, LLMClient] = {}
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize all configured clients."""
        for name, config in self.configs.items():
            try:
                self.clients[name] = LLMClientFactory.create_client(config)
                logger.info(f"Initialized LLM client: {name} ({config.provider.value})")
            except Exception as e:
                logger.error(f"Failed to initialize LLM client {name}: {e}")
    
    async def extract_intent(self, message: str, context: str = "", preferred_client: str = None) -> IntentResult:
        """Extract intent using the best available client."""
        # Try preferred client first
        if preferred_client and preferred_client in self.clients:
            client = self.clients[preferred_client]
            if await client.is_available():
                result = await client.extract_intent(message, context)
                if result.error is None:
                    return result
                logger.warning(f"Preferred client {preferred_client} failed: {result.error}")
        
        # Try all clients in order of preference
        client_order = ['ollama', 'gemini', 'openai', 'fallback']
        
        for client_name in client_order:
            if client_name in self.clients:
                client = self.clients[client_name]
                if await client.is_available():
                    result = await client.extract_intent(message, context)
                    if result.error is None:
                        logger.info(f"Used LLM client: {client_name}")
                        return result
                    logger.warning(f"Client {client_name} failed: {result.error}")
        
        # If all else fails, use fallback
        if 'fallback' in self.clients:
            result = await self.clients['fallback'].extract_intent(message, context)
            logger.info("Used fallback LLM client")
            return result
        
        # Last resort
        return IntentResult(
            intent="unknown",
            entities={},
            confidence=0.0,
            provider="none",
            error="No LLM clients available"
        )


def get_llm_config() -> Dict[str, LLMConfig]:
    """Get LLM configuration from environment variables."""
    configs = {}
    
    # Ollama config
    if os.getenv('OLLAMA_MODEL'):
        configs['ollama'] = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model=os.getenv('OLLAMA_MODEL', 'llama2'),
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        )
    
    # Gemini config
    if os.getenv('GEMINI_API_KEY'):
        configs['gemini'] = LLMConfig(
            provider=LLMProvider.GEMINI,
            model=os.getenv('GEMINI_MODEL', 'gemini-pro'),
            api_key=os.getenv('GEMINI_API_KEY')
        )
    
    # OpenAI config
    if os.getenv('OPENAI_API_KEY'):
        configs['openai'] = LLMConfig(
            provider=LLMProvider.OPENAI,
            model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            api_key=os.getenv('OPENAI_API_KEY')
        )
    
    # Always include fallback
    configs['fallback'] = LLMConfig(
        provider=LLMProvider.FALLBACK,
        model='regex'
    )
    
    return configs


# Global LLM manager instance
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get the global LLM manager instance."""
    global _llm_manager
    if _llm_manager is None:
        configs = get_llm_config()
        _llm_manager = LLMManager(configs)
    return _llm_manager


async def extract_intent(message: str, context: str = "", preferred_client: str = None) -> IntentResult:
    """Extract intent using the LLM manager."""
    manager = get_llm_manager()
    return await manager.extract_intent(message, context, preferred_client)


# For backward compatibility
def extract_intent_sync(message: str, context: str = "") -> Dict[str, Any]:
    """Synchronous version for backward compatibility."""
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, use fallback
            manager = get_llm_manager()
            if 'fallback' in manager.clients:
                result = asyncio.create_task(
                    manager.clients['fallback'].extract_intent(message, context)
                )
                # This is not ideal, but maintains backward compatibility
                return {
                    "intent": "unknown",
                    "entities": {},
                    "error": "Async context detected, using fallback"
                }
            else:
                return {"intent": "unknown", "entities": {}}
        else:
            result = loop.run_until_complete(extract_intent(message, context))
            return {
                "intent": result.intent,
                "entities": result.entities,
                "error": result.error
            }
    except Exception as e:
        logger.error(f"Intent extraction failed: {e}")
        return {"intent": "unknown", "entities": {}, "error": str(e)} 