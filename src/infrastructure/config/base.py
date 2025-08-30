"""
Base configuration for AI Coach application.
Provides structured configuration management with validation.
"""
import os
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from enum import Enum


class Environment(str, Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BaseConfig(BaseSettings):
    """Base configuration with common settings"""
    
    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        env="ENVIRONMENT",
        description="Application environment"
    )
    
    debug: bool = Field(
        default=True,
        env="DEBUG",
        description="Enable debug mode"
    )
    
    # Logging
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        env="LOG_LEVEL",
        description="Logging level"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
        description="Log message format"
    )
    
    # Server
    host: str = Field(
        default="0.0.0.0",
        env="HOST",
        description="Server host"
    )
    
    port: int = Field(
        default=8001,
        env="PORT",
        ge=1024,
        le=65535,
        description="Server port"
    )
    
    # Database
    database_path: str = Field(
        default="data/users/coach_data.db",
        env="DATABASE_PATH",
        description="SQLite database path"
    )
    
    user_memory_db_path: str = Field(
        default="data/users/user_memory.db",
        env="USER_MEMORY_DB_PATH",
        description="User memory database path"
    )
    
    # Vector Store
    chroma_path: str = Field(
        default="data/vector_store",
        env="CHROMA_PATH",
        description="ChromaDB storage path"
    )
    
    # OpenAI
    openai_api_key: Optional[str] = Field(
        default=None,
        env="OPENAI_API_KEY",
        description="OpenAI API key"
    )
    
    openai_model: str = Field(
        default="gpt-4",
        env="OPENAI_MODEL",
        description="OpenAI model to use"
    )
    
    openai_max_tokens: int = Field(
        default=1500,
        env="OPENAI_MAX_TOKENS",
        ge=100,
        le=4000,
        description="Maximum tokens for OpenAI responses"
    )
    
    openai_timeout: int = Field(
        default=30,
        env="OPENAI_TIMEOUT",
        ge=5,
        le=120,
        description="OpenAI API timeout in seconds"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        env="RATE_LIMIT_ENABLED",
        description="Enable rate limiting"
    )
    
    rate_limit_per_minute: int = Field(
        default=60,
        env="RATE_LIMIT_PER_MINUTE",
        ge=1,
        le=1000,
        description="Requests per minute per user"
    )
    
    rate_limit_per_hour: int = Field(
        default=1000,
        env="RATE_LIMIT_PER_HOUR",
        ge=10,
        le=10000,
        description="Requests per hour per user"
    )
    
    # Security
    secret_key: Optional[str] = Field(
        default=None,
        env="SECRET_KEY",
        description="Flask secret key"
    )
    
    jwt_secret: Optional[str] = Field(
        default=None,
        env="JWT_SECRET",
        description="JWT signing secret"
    )
    
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS",
        description="Allowed CORS origins"
    )
    
    # Performance
    max_concurrent_requests: int = Field(
        default=100,
        env="MAX_CONCURRENT_REQUESTS",
        ge=1,
        le=1000,
        description="Maximum concurrent requests"
    )
    
    request_timeout: int = Field(
        default=30,
        env="REQUEST_TIMEOUT",
        ge=5,
        le=300,
        description="Request timeout in seconds"
    )
    
    # Monitoring
    metrics_enabled: bool = Field(
        default=True,
        env="METRICS_ENABLED",
        description="Enable metrics collection"
    )
    
    health_check_enabled: bool = Field(
        default=True,
        env="HEALTH_CHECK_ENABLED",
        description="Enable health check endpoints"
    )
    
    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_key(cls, v):
        """Validate OpenAI API key format"""
        if v and not v.startswith('sk-'):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v
    
    @field_validator('secret_key')
    @classmethod  
    def validate_secret_key(cls, v):
        """Validate secret key strength"""
        if v and len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @field_validator('cors_origins')
    @classmethod
    def validate_cors_origins(cls, v):
        """Validate CORS origins format"""
        if isinstance(v, str):
            # Handle comma-separated string from environment
            v = [origin.strip() for origin in v.split(',')]
        
        for origin in v:
            if not origin.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid CORS origin format: {origin}")
        
        return v
    
    def get_database_url(self) -> str:
        """Get database URL"""
        return f"sqlite:///{self.database_path}"
    
    def get_chroma_path(self) -> str:
        """Get ChromaDB path"""
        return self.chroma_path
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.environment == Environment.TESTING
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8", 
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra environment variables
    }
