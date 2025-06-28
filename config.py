#!/usr/bin/env python3
"""
Configuration Management for KICKAI
Supports both local development and Railway production environments
"""

import os
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

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
                'url': os.getenv('SUPABASE_URL'),
                'key': os.getenv('SUPABASE_KEY'),
                'type': 'cloud'
            }
        else:
            # Development: Use local .env file
            return {
                'url': os.getenv('SUPABASE_URL'),
                'key': os.getenv('SUPABASE_KEY'),
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
        
        # Check database config
        db_config = self.database_config
        if not db_config['url'] or not db_config['key']:
            errors.append("Missing Supabase configuration")
        
        # Check AI config
        ai_config = self.ai_config
        if self.is_production and not ai_config['api_key']:
            errors.append("Missing Google AI API key for production")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        logger.info(f"✅ Configuration valid for {self.environment} environment")
        logger.info(f"   AI Provider: {self.ai_provider}")
        logger.info(f"   Database: {db_config['type']}")
        return True

# Global configuration instance
config = KICKAIConfig() 