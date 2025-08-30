"""
Configuration settings for the AI coach application.
Enhanced with environment-specific configurations and validation.
"""
import os
from typing import Union
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import environment-specific configurations
from .base import BaseConfig
from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig


def get_config() -> BaseConfig:
    """
    Get configuration based on environment.
    
    Returns:
        Configuration instance for current environment
    """
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    config_mapping = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'staging': ProductionConfig,  # Use production config for staging
    }
    
    config_class = config_mapping.get(env, DevelopmentConfig)
    
    try:
        return config_class()
    except Exception as e:
        # Fallback to base config if environment-specific config fails
        print(f"Warning: Failed to load {env} config: {e}")
        print("Falling back to base configuration")
        return BaseConfig()


# Global config instance
config = get_config()

# Legacy compatibility attributes for existing code
class LegacyConfigAdapter:
    """Adapter to maintain backward compatibility with existing code"""
    
    def __init__(self, modern_config: BaseConfig):
        self._config = modern_config
    
    @property
    def debug(self) -> bool:
        return self._config.debug
    
    @property
    def host(self) -> str:
        return self._config.host
    
    @property
    def port(self) -> int:
        return self._config.port
    
    @property
    def database_path(self) -> str:
        return self._config.database_path
    
    @property
    def user_memory_db_path(self) -> str:
        return self._config.user_memory_db_path
    
    @property
    def chroma_path(self) -> str:
        return self._config.chroma_path
    
    @property
    def openai_api_key(self) -> str:
        return self._config.openai_api_key or ""
    
    @property
    def openai_model(self) -> str:
        return self._config.openai_model
    
    @property
    def openai_max_tokens(self) -> int:
        return self._config.openai_max_tokens
    
    def get_chroma_path(self) -> str:
        return self._config.get_chroma_path()
    
    def validate(self) -> bool:
        """Legacy validation method"""
        return True  # New config has built-in validation


# For direct access to modern config
modern_config = config

# For legacy code compatibility - expose the adapter
config = LegacyConfigAdapter(modern_config)

# Export both for flexibility
__all__ = ['config', 'modern_config', 'get_config']