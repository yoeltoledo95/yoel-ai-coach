"""
Application configuration management
"""
import os
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration"""
    sqlite_path: str = "data/users/user_memory.db"
    chroma_path: str = "data/vector_store"
    backup_enabled: bool = True


@dataclass
class OpenAIConfig:
    """OpenAI configuration"""
    api_key: Optional[str] = None
    model: str = "gpt-4o"
    max_tokens: int = 1200
    temperature: float = 0.8
    timeout: int = 30


@dataclass
class WhatsAppConfig:
    """WhatsApp configuration"""
    api_token: Optional[str] = None
    phone_number_id: Optional[str] = None
    api_url: Optional[str] = None
    webhook_secret: Optional[str] = None


@dataclass
class AppConfig:
    """Main application configuration"""
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Paths
    base_path: Path = Path(__file__).parent.parent.parent.parent
    data_path: Path = base_path / "data"
    logs_path: Path = base_path / "logs"
    
    # Database
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # External APIs
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    whatsapp: WhatsAppConfig = field(default_factory=WhatsAppConfig)
    
    # Features
    enable_rag: bool = True
    enable_image_processing: bool = True
    enable_weekly_planning: bool = True
    
    def __post_init__(self):
        """Initialize configuration from environment variables"""
        # OpenAI
        self.openai.api_key = os.getenv("OPENAI_API_KEY")
        self.openai.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
        # WhatsApp
        self.whatsapp.api_token = os.getenv("WHATSAPP_API_TOKEN")
        self.whatsapp.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.whatsapp.webhook_secret = os.getenv("WHATSAPP_VERIFY_TOKEN")
        
        # Environment
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        
        # Create directories
        self.data_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)
        (self.data_path / "users").mkdir(exist_ok=True)
        (self.data_path / "exercises").mkdir(exist_ok=True)
        (self.data_path / "mentors").mkdir(exist_ok=True)
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        if not self.openai.api_key:
            errors.append("OPENAI_API_KEY is required")
        
        if self.environment == "production":
            if not self.whatsapp.api_token:
                errors.append("WHATSAPP_API_TOKEN is required in production")
            if not self.whatsapp.phone_number_id:
                errors.append("WHATSAPP_PHONE_NUMBER_ID is required in production")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    def get_database_url(self) -> str:
        """Get database URL"""
        return f"sqlite:///{self.database.sqlite_path}"
    
    def get_chroma_path(self) -> str:
        """Get ChromaDB path"""
        return str(self.database.chroma_path)


# Global configuration instance
config = AppConfig() 