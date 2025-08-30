"""
Centralized logging configuration
"""
import logging
import sys
from pathlib import Path
from infrastructure.config.settings import config


def setup_logging() -> None:
    """Setup application logging"""
    # Create logs directory
    logs_path = getattr(config, 'logs_path', Path('logs'))
    logs_path.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Get debug mode safely
    debug_mode = getattr(config, 'debug', False)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG if debug_mode else logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(logs_path / "app.log")
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Log application startup
    logger = logging.getLogger(__name__)
    logger.info("Application logging configured")
    logger.info(f"Environment: {getattr(config, 'environment', 'development')}")
    logger.info(f"Debug mode: {getattr(config, 'debug', False)}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name) 