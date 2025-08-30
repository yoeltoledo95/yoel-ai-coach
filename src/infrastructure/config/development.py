"""
Development-specific configuration.
"""
from .base import BaseConfig, Environment, LogLevel


class DevelopmentConfig(BaseConfig):
    """Configuration for development environment"""
    
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    log_level: LogLevel = LogLevel.DEBUG
    
    # More permissive rate limits for development
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 2000
    
    # Shorter timeouts for faster iteration
    request_timeout: int = 15
    openai_timeout: int = 20
    
    # Development-specific paths
    database_path: str = "data/users/coach_data_dev.db"
    chroma_path: str = "data/vector_store_dev"
    
    # Enable all monitoring in development
    metrics_enabled: bool = True
    health_check_enabled: bool = True
    
    model_config = {
        "env_prefix": "DEV_",
        "extra": "ignore"
    }
