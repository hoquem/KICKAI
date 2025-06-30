#!/usr/bin/env python3
"""
Configuration Management for KICKAI
Supports both local development and Railway production environments
Includes feature flags for Phase 1 improvements.
"""

import os
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Phase 1 Feature Flags
ENABLE_INTELLIGENT_ROUTING = os.getenv('ENABLE_INTELLIGENT_ROUTING', 'false').lower() == 'true'
ENABLE_DYNAMIC_TASK_DECOMPOSITION = os.getenv('ENABLE_DYNAMIC_TASK_DECOMPOSITION', 'false').lower() == 'true'
ENABLE_ADVANCED_MEMORY = os.getenv('ENABLE_ADVANCED_MEMORY', 'false').lower() == 'true'

# Phase 1 Configuration
AGENTIC_MEMORY_ENABLED = os.getenv('AGENTIC_MEMORY_ENABLED', 'true').lower() == 'true'
AGENTIC_PERFORMANCE_MONITORING = os.getenv('AGENTIC_PERFORMANCE_MONITORING', 'true').lower() == 'true'
AGENTIC_ANALYTICS_ENABLED = os.getenv('AGENTIC_ANALYTICS_ENABLED', 'false').lower() == 'true'

# Memory System Configuration
MEMORY_RETENTION_DAYS = int(os.getenv('MEMORY_RETENTION_DAYS', '30'))
MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '50'))
MAX_EPISODIC_MEMORY = int(os.getenv('MAX_EPISODIC_MEMORY', '1000'))

# Performance Monitoring Configuration
PERFORMANCE_MONITORING_INTERVAL = int(os.getenv('PERFORMANCE_MONITORING_INTERVAL', '300'))
AGENT_OPTIMIZATION_ENABLED = os.getenv('AGENT_OPTIMIZATION_ENABLED', 'true').lower() == 'true'

# Routing Configuration
COMPLEXITY_THRESHOLD_FOR_COLLABORATION = float(os.getenv('COMPLEXITY_THRESHOLD_FOR_COLLABORATION', '7.0'))
MAX_NEGOTIATION_ROUNDS = int(os.getenv('MAX_NEGOTIATION_ROUNDS', '3'))

# Debug Configuration
DEBUG_AGENTIC_SYSTEM = os.getenv('DEBUG_AGENTIC_SYSTEM', 'false').lower() == 'true'

# Database configuration
database_config = {
    'type': 'firebase',
    'firebase': {
        'project_id': os.getenv('FIREBASE_PROJECT_ID'),
        'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
        'private_key': os.getenv('FIREBASE_PRIVATE_KEY'),
        'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
        'client_id': os.getenv('FIREBASE_CLIENT_ID'),
        'auth_uri': os.getenv('FIREBASE_AUTH_URI'),
        'token_uri': os.getenv('FIREBASE_TOKEN_URI'),
        'auth_provider_x509_cert_url': os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
        'client_x509_cert_url': os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
    }
}

class KICKAIConfig:
    """Configuration manager for KICKAI system."""
    
    def __init__(self):
        self.environment = os.getenv('RAILWAY_ENVIRONMENT', 'development')
        self.is_production = self.environment == 'production'
        
    @property
    def ai_provider(self) -> str:
        """Get AI provider based on environment."""
        if self.is_production:
            return 'google'  # Use Google AI in production
        else:
            return 'ollama'  # Use Ollama for local development
    
    @property
    def database_config(self) -> Dict[str, str]:
        """Get database configuration."""
        if self.is_production:
            # Production: Use Railway environment variables
            return {
                'type': 'firebase',
                'firebase': {
                    'project_id': os.getenv('FIREBASE_PROJECT_ID'),
                    'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    'private_key': os.getenv('FIREBASE_PRIVATE_KEY'),
                    'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
                    'client_id': os.getenv('FIREBASE_CLIENT_ID'),
                    'auth_uri': os.getenv('FIREBASE_AUTH_URI'),
                    'token_uri': os.getenv('FIREBASE_TOKEN_URI'),
                    'auth_provider_x509_cert_url': os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
                    'client_x509_cert_url': os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
                }
            }
        else:
            # Development: Use local .env file
            return {
                'type': 'local'
            }
    
    @property
    def ai_config(self) -> Dict[str, Any]:
        """Get AI configuration based on environment."""
        if self.is_production:
            # Production: Google AI
            return {
                'provider': 'google',
                'api_key': os.getenv('GOOGLE_API_KEY'),
                'model': 'gemini-1.5-flash',
                'base_url': None
            }
        else:
            # Development: Ollama
            return {
                'provider': 'ollama',
                'api_key': None,
                'model': 'llama3.1:8b-instruct-q4_0',
                'base_url': 'http://localhost:11434'
            }
    
    @property
    def telegram_config(self) -> Dict[str, Any]:
        """Get Telegram configuration."""
        return {
            'polling_timeout': 15 if self.is_production else 30,
            'max_retries': 3 if self.is_production else 5,
            'webhook_cleanup': True
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for CrewAI."""
        config = self.ai_config
        
        if config['provider'] == 'google':
            return {
                'model': config['model'],
                'api_key': config['api_key'],
                'temperature': 0.7,
                'max_tokens': 1000
            }
        else:  # ollama
            return {
                'model': config['model'],
                'base_url': config['base_url'],
                'temperature': 0.7,
                'timeout': 60
            }
    
    def validate_config(self) -> bool:
        """Validate configuration for current environment."""
        errors = []
        
        # Check AI configuration
        ai_config = self.ai_config
        if self.is_production and not ai_config['api_key']:
            errors.append("Missing Google AI API key for production")
        
        # Check Firebase configuration
        firebase_config = self.database_config.get('firebase', {})
        required_firebase_vars = [
            'project_id', 'private_key_id', 'private_key', 'client_email',
            'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url',
            'client_x509_cert_url'
        ]
        
        for var in required_firebase_vars:
            if not firebase_config.get(var):
                errors.append(f"Missing Firebase configuration: {var}")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        logger.info(f"✅ Configuration valid for {self.environment} environment")
        logger.info(f"   AI Provider: {self.ai_provider}")
        logger.info(f"   Database: {self.database_config['type']}")
        return True

def get_feature_flags():
    """Get all feature flags for easy access."""
    return {
        'intelligent_routing': ENABLE_INTELLIGENT_ROUTING,
        'dynamic_task_decomposition': ENABLE_DYNAMIC_TASK_DECOMPOSITION,
        'advanced_memory': ENABLE_ADVANCED_MEMORY,
        'performance_monitoring': AGENTIC_PERFORMANCE_MONITORING,
        'analytics': AGENTIC_ANALYTICS_ENABLED,
        'debug': DEBUG_AGENTIC_SYSTEM
    }

def is_phase1_enabled():
    """Check if any Phase 1 features are enabled."""
    return any([
        ENABLE_INTELLIGENT_ROUTING,
        ENABLE_DYNAMIC_TASK_DECOMPOSITION,
        ENABLE_ADVANCED_MEMORY
    ])

def get_phase1_config():
    """Get Phase 1 configuration for easy access."""
    return {
        'feature_flags': get_feature_flags(),
        'memory': {
            'retention_days': MEMORY_RETENTION_DAYS,
            'max_conversation_history': MAX_CONVERSATION_HISTORY,
            'max_episodic_memory': MAX_EPISODIC_MEMORY
        },
        'performance': {
            'monitoring_interval': PERFORMANCE_MONITORING_INTERVAL,
            'optimization_enabled': AGENT_OPTIMIZATION_ENABLED
        },
        'routing': {
            'complexity_threshold': COMPLEXITY_THRESHOLD_FOR_COLLABORATION,
            'max_negotiation_rounds': MAX_NEGOTIATION_ROUNDS
        }
    }

if __name__ == "__main__":
    # Print current configuration
    print("🔧 KICKAI Phase 1 Configuration")
    print("=" * 40)
    
    print("\n📋 Feature Flags:")
    flags = get_feature_flags()
    for flag, enabled in flags.items():
        status = "✅ Enabled" if enabled else "❌ Disabled"
        print(f"  {flag}: {status}")
    
    print(f"\n🚀 Phase 1 Status: {'✅ Active' if is_phase1_enabled() else '❌ Inactive'}")
    
    print("\n⚙️ Configuration:")
    config = get_phase1_config()
    for section, settings in config.items():
        if section != 'feature_flags':
            print(f"  {section}:")
            for key, value in settings.items():
                print(f"    {key}: {value}")
    
    print("\n📝 Environment Variables to Set:")
    print("  ENABLE_INTELLIGENT_ROUTING=true")
    print("  ENABLE_DYNAMIC_TASK_DECOMPOSITION=true")
    print("  ENABLE_ADVANCED_MEMORY=true")
    print("  DEBUG_AGENTIC_SYSTEM=true")

# Global configuration instance
config = KICKAIConfig() 