"""
Main application entry point
"""
import os
import sys
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

# Add src to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from shared.logging import setup_logging
from infrastructure.config.settings import config
from application.container import container
from application.interfaces.whatsapp_interface import WhatsAppInterface
from shared.exceptions import ConfigurationError

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        
        # Validate configuration
        config.validate()
        
        # Initialize application container
        container.initialize()
        
        # Get WhatsApp interface from container
        whatsapp_interface = container.get_service('whatsapp_interface')
        
        # Run the application
        whatsapp_interface.run()
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 