"""
Testing-specific configuration.
"""
from .base import BaseConfig, Environment, LogLevel


class TestingConfig(BaseConfig):
    """Configuration for testing environment"""
    
    environment: Environment = Environment.TESTING
    debug: bool = True
    log_level: LogLevel = LogLevel.WARNING
    
    # High rate limits for testing
    rate_limit_per_minute: int = 1000
    rate_limit_per_hour: int = 10000
    
    # Fast timeouts for testing
    request_timeout: int = 5
    openai_timeout: int = 10
    
    # In-memory/temporary paths for testing
    database_path: str = ":memory:"
    user_memory_db_path: str = ":memory:"
    chroma_path: str = "/tmp/test_chroma"
    
    # Disable external services in testing
    rate_limit_enabled: bool = False
    metrics_enabled: bool = False
    
    # Test-specific settings
    openai_api_key: str = "sk-test-key-for-testing"
    secret_key: str = "test-secret-key-that-is-long-enough-for-validation"
    
    model_config = {
        "env_prefix": "TEST_",
        "extra": "ignore"
    }
