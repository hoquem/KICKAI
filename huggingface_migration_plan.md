# KICKAI Hugging Face Migration Plan

## Overview
Migrate KICKAI from Google Gemini to Hugging Face free tier models while maintaining system reliability and performance. This plan implements a phased approach with comprehensive fallback mechanisms.

## Current Architecture Analysis

### LLM Integration Points
1. **LLMFactory** (`kickai/utils/llm_factory.py`) - Main model creation
2. **Agent Creation** (`kickai/agents/entity_specific_agents.py`) - Agent-specific temperature settings
3. **Configuration** (`kickai/config/llm_config.py`) - LLM configuration management
4. **Settings** (`kickai/core/settings.py`) - Environment variable handling

### Current Temperature Settings by Agent
- **Data-Critical Agents** (Temp 0.1): PLAYER_COORDINATOR, HELP_ASSISTANT, MESSAGE_PROCESSOR, FINANCE_MANAGER
- **Onboarding Agent** (Temp 0.2): ONBOARDING_AGENT  
- **Administrative Agents** (Temp 0.3): TEAM_MANAGER, AVAILABILITY_MANAGER
- **Creative Agents** (Temp 0.7): PERFORMANCE_ANALYST, LEARNING_AGENT, SQUAD_SELECTOR

## Phase 1: Infrastructure Setup (Week 1-2)

### 1.1 Add Hugging Face Provider Support

**File**: `kickai/utils/llm_factory.py`

Add new HuggingFaceProvider class:

```python
class HuggingFaceProvider(LLMProvider):
    """Hugging Face Inference API provider for free tier models."""
    
    def validate_config(self, config: LLMConfig) -> bool:
        """Validate Hugging Face configuration."""
        if not config.api_key:
            raise LLMProviderError("Hugging Face requires HF_API_TOKEN")
        if not config.model_name:
            raise LLMProviderError("Hugging Face requires model_name")
        return True
    
    def create_llm(self, config: LLMConfig):
        """Create Hugging Face LLM instance."""
        self.validate_config(config)
        
        try:
            from huggingface_hub import InferenceClient
            
            class HuggingFaceLLM:
                def __init__(self, model_name: str, api_key: str, temperature: float = 0.7):
                    self.model_name = model_name
                    self.api_key = api_key
                    self.temperature = temperature
                    self.client = InferenceClient(model=model_name, token=api_key)
                    
                    # CrewAI compatibility attributes
                    self.supports_functions = False
                    self.supports_tools = False
                    self.stop = None
                
                def supports_stop_words(self) -> bool:
                    return False
                
                def invoke(self, messages, **kwargs):
                    """Synchronous invocation."""
                    try:
                        # Convert messages to text prompt
                        prompt = self._format_messages(messages)
                        
                        response = self.client.text_generation(
                            prompt=prompt,
                            temperature=self.temperature,
                            max_new_tokens=kwargs.get('max_tokens', 1000),
                            do_sample=True if self.temperature > 0 else False
                        )
                        
                        return response
                    except Exception as e:
                        logger.error(f"HuggingFace API Error: {e}")
                        raise
                
                async def ainvoke(self, messages, **kwargs):
                    """Async invocation (runs sync for now)."""
                    return self.invoke(messages, **kwargs)
                
                def __call__(self, messages, **kwargs):
                    return self.invoke(messages, **kwargs)
                
                def _format_messages(self, messages):
                    """Format messages for Hugging Face models."""
                    if isinstance(messages, list):
                        # Extract content from message objects
                        text_parts = []
                        for msg in messages:
                            if hasattr(msg, 'content'):
                                text_parts.append(msg.content)
                            elif isinstance(msg, dict) and 'content' in msg:
                                text_parts.append(msg['content'])
                            else:
                                text_parts.append(str(msg))
                        return "\n".join(text_parts)
                    return str(messages)
            
            return HuggingFaceLLM(
                model_name=config.model_name,
                api_key=config.api_key,
                temperature=config.temperature
            )
            
        except ImportError:
            raise LLMProviderError("huggingface_hub package not installed. Run: pip install huggingface_hub")
        except Exception as e:
            raise LLMProviderError(f"Failed to create Hugging Face LLM: {e}")
```

Register the provider:
```python
# Add to LLMFactory._providers
AIProvider.HUGGINGFACE: HuggingFaceProvider,
```

### 1.2 Update Settings Configuration

**File**: `kickai/core/settings.py`

Add Hugging Face configuration:

```python
# Add to Settings class
huggingface_api_token: Optional[str] = Field(
    default=None, 
    description="Hugging Face API token for inference"
)

def get_ai_api_key(self) -> str:
    """Get the appropriate API key for the AI provider."""
    if self.ai_provider == AIProvider.GEMINI:
        return self.google_api_key
    elif self.ai_provider == AIProvider.HUGGINGFACE:
        return self.huggingface_api_token or ""
    elif self.ai_provider == AIProvider.OLLAMA:
        return ""
    return ""
```

### 1.3 Update Environment Configuration

**File**: `env.example`

```bash
# Hugging Face Configuration
HUGGINGFACE_API_TOKEN=your_hugging_face_token_here

# AI Provider can now be: gemini, huggingface, ollama, mock
AI_PROVIDER=huggingface
```

### 1.4 Add Hugging Face to AIProvider Enum

**File**: `kickai/core/enums.py`

```python
class AIProvider(str, Enum):
    """AI provider options."""
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    MOCK = "mock"
```

## Phase 2: Agent-Specific Model Mapping (Week 2-3)

### 2.1 Create Agent Model Configuration

**New File**: `kickai/config/agent_models.py`

```python
"""Agent-specific model configurations for different providers."""

from typing import Dict, Optional
from kickai.core.enums import AgentRole, AIProvider

# Agent-specific model mappings
AGENT_MODEL_CONFIG = {
    # Data-Critical Agents (Anti-hallucination priority)
    AgentRole.PLAYER_COORDINATOR: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",
            "temperature": 0.1,
            "max_tokens": 500
        },
        AIProvider.GEMINI: {
            "model": "gemini-1.5-flash",
            "temperature": 0.1,
            "max_tokens": 500
        }
    },
    
    AgentRole.MESSAGE_PROCESSOR: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",
            "temperature": 0.1,
            "max_tokens": 300
        },
        AIProvider.GEMINI: {
            "model": "gemini-1.5-flash",
            "temperature": 0.1,
            "max_tokens": 300
        }
    },
    
    AgentRole.HELP_ASSISTANT: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",
            "temperature": 0.1,
            "max_tokens": 800
        },
        AIProvider.GEMINI: {
            "model": "gemini-1.5-flash",
            "temperature": 0.1,
            "max_tokens": 800
        }
    },
    
    AgentRole.FINANCE_MANAGER: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",
            "temperature": 0.1,
            "max_tokens": 400
        },
        AIProvider.GEMINI: {
            "model": "gemini-1.5-flash",
            "temperature": 0.1,
            "max_tokens": 400
        }
    },
    
    # Administrative Agents
    AgentRole.TEAM_MANAGER: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-3B-Instruct",
            "temperature": 0.3,
            "max_tokens": 600
        },
        AIProvider.GEMINI: {
            "model": "gemini-1.5-flash",
            "temperature": 0.3,
            "max_tokens": 600
        }
    },
    
    AgentRole.AVAILABILITY_MANAGER: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-3B-Instruct",
            "temperature": 0.3,
            "max_tokens": 500
        },
        AIProvider.GEMINI: {
            "model": "gemini-1.5-flash",
            "temperature": 0.3,
            "max_tokens": 500
        }
    },
    
    # Onboarding Agent
    AgentRole.ONBOARDING_AGENT: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-3B-Instruct",
            "temperature": 0.2,
            "max_tokens": 700
        },
        AIProvider.GEMINI: {
            "model": "gemini-1.5-flash",
            "temperature": 0.2,
            "max_tokens": 700
        }
    },
    
    # Creative/Analytical Agents
    AgentRole.PERFORMANCE_ANALYST: {
        AIProvider.HUGGINGFACE: {
            "model": "google/gemma-2-2b-it",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        AIProvider.GEMINI: {
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    },
    
    AgentRole.LEARNING_AGENT: {
        AIProvider.HUGGINGFACE: {
            "model": "google/gemma-2-2b-it",
            "temperature": 0.7,
            "max_tokens": 800
        },
        AIProvider.GEMINI: {
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 800
        }
    },
    
    AgentRole.SQUAD_SELECTOR: {
        AIProvider.HUGGINGFACE: {
            "model": "google/gemma-2-2b-it",
            "temperature": 0.7,
            "max_tokens": 600
        },
        AIProvider.GEMINI: {
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 600
        }
    }
}

def get_agent_model_config(agent_role: AgentRole, provider: AIProvider) -> Optional[Dict]:
    """Get model configuration for specific agent and provider."""
    return AGENT_MODEL_CONFIG.get(agent_role, {}).get(provider)

def get_fallback_config(agent_role: AgentRole) -> Dict:
    """Get fallback configuration (Gemini) for any agent."""
    gemini_config = AGENT_MODEL_CONFIG.get(agent_role, {}).get(AIProvider.GEMINI)
    if gemini_config:
        return gemini_config
    
    # Default fallback
    return {
        "model": "gemini-1.5-flash",
        "temperature": 0.3,
        "max_tokens": 500
    }
```

### 2.2 Update Agent Creation with Model Selection

**File**: `kickai/agents/entity_specific_agents.py`

```python
def _get_agent_specific_llm_with_temperature(base_llm: Any, role: AgentRole) -> Any:
    """Apply agent-specific model and temperature settings."""
    try:
        from kickai.config.agent_models import get_agent_model_config, get_fallback_config
        from kickai.core.settings import get_settings
        
        settings = get_settings()
        
        # Get agent-specific model config
        model_config = get_agent_model_config(role, settings.ai_provider)
        
        if not model_config:
            logger.warning(f"No model config for {role.value} with {settings.ai_provider.value}, using fallback")
            model_config = get_fallback_config(role)
        
        # Create agent-specific LLM with proper model and temperature
        from kickai.utils.llm_factory import LLMFactory, LLMConfig
        
        agent_config = LLMConfig(
            provider=settings.ai_provider,
            model_name=model_config["model"],
            api_key=settings.get_ai_api_key(),
            temperature=model_config["temperature"],
            timeout_seconds=settings.ai_timeout,
            max_retries=settings.ai_max_retries
        )
        
        agent_llm = LLMFactory.create_llm(agent_config)
        
        logger.info(f"🤖 Created {role.value} agent with {settings.ai_provider.value}:{model_config['model']} (temp={model_config['temperature']})")
        
        return agent_llm
        
    except Exception as e:
        logger.error(f"Failed to create agent-specific LLM for {role.value}: {e}")
        logger.info(f"Falling back to base LLM for {role.value}")
        return base_llm
```

## Phase 3: Hybrid Deployment with Fallback (Week 3-4)

### 3.1 Implement Smart Provider Selection

**New File**: `kickai/utils/smart_provider.py`

```python
"""Smart provider selection with automatic fallback."""

import asyncio
from typing import Optional, Dict, Any
from kickai.core.enums import AIProvider, AgentRole
from kickai.utils.llm_factory import LLMFactory, LLMConfig
from kickai.config.agent_models import get_agent_model_config, get_fallback_config
from loguru import logger

class SmartProviderManager:
    """Manages intelligent provider selection with fallback mechanisms."""
    
    def __init__(self):
        self._provider_health = {
            AIProvider.HUGGINGFACE: True,
            AIProvider.GEMINI: True
        }
        self._error_counts = {
            AIProvider.HUGGINGFACE: 0,
            AIProvider.GEMINI: 0
        }
        self._max_errors = 3
    
    def get_optimal_provider(self, agent_role: AgentRole, primary_provider: AIProvider) -> AIProvider:
        """Get the optimal provider for an agent with fallback logic."""
        
        # Check if primary provider is healthy
        if self._provider_health[primary_provider]:
            return primary_provider
        
        # Fallback to Gemini if primary fails
        if primary_provider != AIProvider.GEMINI and self._provider_health[AIProvider.GEMINI]:
            logger.warning(f"⚠️ Falling back to Gemini for {agent_role.value} due to {primary_provider.value} issues")
            return AIProvider.GEMINI
        
        # Last resort - use primary even if unhealthy
        logger.error(f"🚨 Using unhealthy provider {primary_provider.value} for {agent_role.value} - no alternatives")
        return primary_provider
    
    def report_error(self, provider: AIProvider, error: Exception):
        """Report an error for a provider."""
        self._error_counts[provider] += 1
        
        if self._error_counts[provider] >= self._max_errors:
            self._provider_health[provider] = False
            logger.error(f"🚨 Marking {provider.value} as unhealthy after {self._error_counts[provider]} errors")
    
    def report_success(self, provider: AIProvider):
        """Report a successful request for a provider."""
        if self._error_counts[provider] > 0:
            self._error_counts[provider] = max(0, self._error_counts[provider] - 1)
            
        if not self._provider_health[provider] and self._error_counts[provider] == 0:
            self._provider_health[provider] = True
            logger.info(f"✅ Restored {provider.value} to healthy status")

# Global instance
_smart_provider = SmartProviderManager()

def get_smart_provider() -> SmartProviderManager:
    """Get the global smart provider instance."""
    return _smart_provider
```

### 3.2 Create Resilient LLM Wrapper

**New File**: `kickai/utils/resilient_llm.py`

```python
"""Resilient LLM wrapper with automatic fallback."""

from typing import Any, Dict, Optional
from kickai.core.enums import AgentRole, AIProvider
from kickai.utils.smart_provider import get_smart_provider
from kickai.utils.llm_factory import LLMFactory, LLMConfig
from kickai.config.agent_models import get_agent_model_config, get_fallback_config
from kickai.core.settings import get_settings
from loguru import logger

class ResilientLLM:
    """LLM wrapper that automatically handles provider fallback."""
    
    def __init__(self, agent_role: AgentRole):
        self.agent_role = agent_role
        self.settings = get_settings()
        self.smart_provider = get_smart_provider()
        self.primary_llm = None
        self.fallback_llm = None
        self._initialize_llms()
    
    def _initialize_llms(self):
        """Initialize primary and fallback LLMs."""
        # Primary LLM (Hugging Face)
        primary_config = get_agent_model_config(self.agent_role, AIProvider.HUGGINGFACE)
        if primary_config:
            try:
                config = LLMConfig(
                    provider=AIProvider.HUGGINGFACE,
                    model_name=primary_config["model"],
                    api_key=self.settings.huggingface_api_token or "",
                    temperature=primary_config["temperature"],
                    timeout_seconds=30,
                    max_retries=2
                )
                self.primary_llm = LLMFactory.create_llm(config)
                logger.info(f"✅ Initialized primary HF LLM for {self.agent_role.value}")
            except Exception as e:
                logger.error(f"Failed to initialize primary HF LLM: {e}")
        
        # Fallback LLM (Gemini)
        fallback_config = get_fallback_config(self.agent_role)
        try:
            config = LLMConfig(
                provider=AIProvider.GEMINI,
                model_name=fallback_config["model"],
                api_key=self.settings.google_api_key,
                temperature=fallback_config["temperature"],
                timeout_seconds=30,
                max_retries=2
            )
            self.fallback_llm = LLMFactory.create_llm(config)
            logger.info(f"✅ Initialized fallback Gemini LLM for {self.agent_role.value}")
        except Exception as e:
            logger.error(f"Failed to initialize fallback Gemini LLM: {e}")
    
    def invoke(self, messages, **kwargs):
        """Invoke with automatic fallback."""
        # Try primary provider first
        if self.primary_llm and self.smart_provider._provider_health[AIProvider.HUGGINGFACE]:
            try:
                result = self.primary_llm.invoke(messages, **kwargs)
                self.smart_provider.report_success(AIProvider.HUGGINGFACE)
                return result
            except Exception as e:
                logger.warning(f"Primary HF LLM failed for {self.agent_role.value}: {e}")
                self.smart_provider.report_error(AIProvider.HUGGINGFACE, e)
        
        # Fallback to Gemini
        if self.fallback_llm:
            try:
                logger.info(f"🔄 Using Gemini fallback for {self.agent_role.value}")
                result = self.fallback_llm.invoke(messages, **kwargs)
                self.smart_provider.report_success(AIProvider.GEMINI)
                return result
            except Exception as e:
                logger.error(f"Fallback Gemini LLM failed for {self.agent_role.value}: {e}")
                self.smart_provider.report_error(AIProvider.GEMINI, e)
                raise
        
        raise Exception(f"All LLM providers failed for {self.agent_role.value}")
    
    async def ainvoke(self, messages, **kwargs):
        """Async invoke with automatic fallback."""
        return self.invoke(messages, **kwargs)
    
    def __call__(self, messages, **kwargs):
        return self.invoke(messages, **kwargs)
    
    # CrewAI compatibility
    @property
    def supports_functions(self):
        return False
    
    @property
    def supports_tools(self):
        return False
    
    @property
    def stop(self):
        return None
    
    def supports_stop_words(self):
        return False
```

## Phase 4: Testing & Validation (Week 4-5)

### 4.1 Create Migration Test Suite

**New File**: `tests/migration/test_huggingface_migration.py`

```python
"""Test suite for Hugging Face migration."""

import pytest
from unittest.mock import Mock, patch
from kickai.core.enums import AgentRole, AIProvider
from kickai.utils.resilient_llm import ResilientLLM
from kickai.config.agent_models import get_agent_model_config

class TestHuggingFaceMigration:
    """Test suite for HF migration."""
    
    def test_agent_model_config_exists(self):
        """Test that all agents have model configurations."""
        critical_agents = [
            AgentRole.PLAYER_COORDINATOR,
            AgentRole.MESSAGE_PROCESSOR,
            AgentRole.HELP_ASSISTANT,
            AgentRole.TEAM_MANAGER
        ]
        
        for agent in critical_agents:
            hf_config = get_agent_model_config(agent, AIProvider.HUGGINGFACE)
            gemini_config = get_agent_model_config(agent, AIProvider.GEMINI)
            
            assert hf_config is not None, f"Missing HF config for {agent.value}"
            assert gemini_config is not None, f"Missing Gemini config for {agent.value}"
            
            # Verify required fields
            assert "model" in hf_config
            assert "temperature" in hf_config
            assert "max_tokens" in hf_config
    
    @patch('kickai.utils.llm_factory.LLMFactory.create_llm')
    def test_resilient_llm_fallback(self, mock_create_llm):
        """Test that ResilientLLM properly falls back to Gemini."""
        # Mock primary LLM failure
        mock_primary = Mock()
        mock_primary.invoke.side_effect = Exception("HF API Error")
        
        # Mock successful fallback
        mock_fallback = Mock()
        mock_fallback.invoke.return_value = "Fallback response"
        
        mock_create_llm.side_effect = [mock_primary, mock_fallback]
        
        resilient_llm = ResilientLLM(AgentRole.PLAYER_COORDINATOR)
        
        # Should fallback and return response
        result = resilient_llm.invoke([{"role": "user", "content": "test"}])
        assert result == "Fallback response"
    
    def test_temperature_settings_preserved(self):
        """Test that agent-specific temperatures are preserved."""
        critical_agent_config = get_agent_model_config(
            AgentRole.PLAYER_COORDINATOR, 
            AIProvider.HUGGINGFACE
        )
        creative_agent_config = get_agent_model_config(
            AgentRole.PERFORMANCE_ANALYST, 
            AIProvider.HUGGINGFACE
        )
        
        assert critical_agent_config["temperature"] == 0.1
        assert creative_agent_config["temperature"] == 0.7
```

## Phase 5: Deployment & Monitoring (Week 5-6)

### 5.1 Environment Setup Instructions

**File**: `HUGGINGFACE_SETUP.md`

```markdown
# Hugging Face Migration Setup

## 1. Get Hugging Face API Token
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with "Read" permissions
3. Copy the token

## 2. Update Environment Variables
```bash
# Add to your .env file
HUGGINGFACE_API_TOKEN=hf_your_token_here
AI_PROVIDER=huggingface

# Keep Gemini as fallback
GOOGLE_API_KEY=your_google_api_key
```

## 3. Install Dependencies
```bash
pip install huggingface_hub
```

## 4. Test Configuration
```bash
python test_llm_config.py
```
```

### 5.2 Monitoring & Alerting

**New File**: `kickai/utils/migration_monitor.py`

```python
"""Migration monitoring and alerting."""

from typing import Dict, Any
from datetime import datetime, timedelta
from kickai.core.enums import AIProvider
from loguru import logger

class MigrationMonitor:
    """Monitor migration success and issues."""
    
    def __init__(self):
        self.stats = {
            AIProvider.HUGGINGFACE: {"requests": 0, "errors": 0, "avg_latency": 0},
            AIProvider.GEMINI: {"requests": 0, "errors": 0, "avg_latency": 0}
        }
        self.start_time = datetime.now()
    
    def log_request(self, provider: AIProvider, latency_ms: float, success: bool):
        """Log a request for monitoring."""
        stats = self.stats[provider]
        stats["requests"] += 1
        
        if not success:
            stats["errors"] += 1
        
        # Update average latency
        current_avg = stats["avg_latency"]
        total_requests = stats["requests"]
        stats["avg_latency"] = ((current_avg * (total_requests - 1)) + latency_ms) / total_requests
    
    def get_migration_report(self) -> Dict[str, Any]:
        """Get migration status report."""
        runtime = datetime.now() - self.start_time
        
        return {
            "runtime_hours": runtime.total_seconds() / 3600,
            "providers": self.stats,
            "huggingface_success_rate": self._calculate_success_rate(AIProvider.HUGGINGFACE),
            "gemini_success_rate": self._calculate_success_rate(AIProvider.GEMINI),
            "cost_savings_estimate": self._estimate_cost_savings()
        }
    
    def _calculate_success_rate(self, provider: AIProvider) -> float:
        """Calculate success rate for a provider."""
        stats = self.stats[provider]
        if stats["requests"] == 0:
            return 0.0
        return (stats["requests"] - stats["errors"]) / stats["requests"]
    
    def _estimate_cost_savings(self) -> Dict[str, float]:
        """Estimate cost savings from migration."""
        hf_requests = self.stats[AIProvider.HUGGINGFACE]["requests"]
        
        # Rough cost estimates (per 1000 requests)
        gemini_cost_per_1k = 0.05  # Conservative estimate
        hf_cost_per_1k = 0.0  # Free tier
        
        potential_savings = (hf_requests / 1000) * gemini_cost_per_1k
        
        return {
            "huggingface_requests": hf_requests,
            "estimated_savings_usd": potential_savings,
            "projected_monthly_savings": potential_savings * 30
        }

# Global monitor instance
_migration_monitor = MigrationMonitor()

def get_migration_monitor() -> MigrationMonitor:
    return _migration_monitor
```

## Implementation Timeline

### Week 1: Infrastructure
- [ ] Add HuggingFaceProvider to LLMFactory
- [ ] Update settings and environment configuration  
- [ ] Add HUGGINGFACE to AIProvider enum
- [ ] Test basic HF API connectivity

### Week 2: Agent Configuration
- [ ] Create agent_models.py with model mappings
- [ ] Update agent creation logic
- [ ] Test agent-specific model selection
- [ ] Verify temperature settings are preserved

### Week 3: Resilient Architecture  
- [ ] Implement SmartProviderManager
- [ ] Create ResilientLLM wrapper
- [ ] Add automatic fallback logic
- [ ] Test failure scenarios

### Week 4: Testing & Validation
- [ ] Create comprehensive test suite
- [ ] Test all agent types with HF models
- [ ] Validate fallback mechanisms
- [ ] Performance benchmarking

### Week 5: Deployment
- [ ] Deploy to testing environment
- [ ] Monitor performance and errors
- [ ] Fine-tune configurations
- [ ] Document issues and solutions

### Week 6: Production Migration
- [ ] Gradual rollout to production
- [ ] Monitor migration metrics
- [ ] Generate cost savings report
- [ ] Complete documentation

## Rollback Plan

If issues arise during migration:

1. **Immediate Rollback**: Set `AI_PROVIDER=gemini` in environment
2. **Partial Rollback**: Use ResilientLLM to automatically fallback problematic agents
3. **Agent-Specific Rollback**: Modify agent_models.py to force specific agents to use Gemini

## Success Metrics

- **Cost Reduction**: Target 80%+ requests through free HF tier
- **Performance**: Maintain <2s average response time
- **Reliability**: >95% success rate across all agents
- **Error Rate**: <5% fallback to Gemini due to HF failures

## Risk Mitigation

1. **API Rate Limits**: Monitor HF usage, implement request queuing if needed
2. **Model Availability**: Have backup models for each agent type
3. **Performance Degradation**: Automatic fallback to Gemini for complex queries
4. **Service Outages**: Dual-provider architecture ensures continuity

This migration plan provides a comprehensive, phased approach to moving KICKAI to Hugging Face free tier while maintaining system reliability and performance.