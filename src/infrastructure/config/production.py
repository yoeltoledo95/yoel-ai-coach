"""
Production-specific configuration.
"""
from .base import BaseConfig, Environment, LogLevel


class ProductionConfig(BaseConfig):
    """Configuration for production environment"""
    
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO
    
    # Production rate limits
    rate_limit_per_minute: int = 30
    rate_limit_per_hour: int = 500
    
    # Production timeouts
    request_timeout: int = 30
    openai_timeout: int = 30
    
    # Production paths
    database_path: str = "/app/data/coach_data.db"
    chroma_path: str = "/app/data/vector_store"
    
    # Production monitoring
    metrics_enabled: bool = True
    health_check_enabled: bool = True
    
    # Stricter CORS in production
    cors_origins: list = ["https://aicoach.app", "https://www.aicoach.app"]
    
    model_config = {
        "env_prefix": "PROD_",
        "extra": "ignore"
    }
