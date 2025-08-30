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
from application.interfaces.web_chat_interface import WebChatInterface
from shared.exceptions import ConfigurationError

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        
        # Validate configuration (skip validation for legacy config)
        if hasattr(config, 'validate'):
            config.validate()
        
        # Initialize application container
        container.initialize()
        
        # Get Web chat interface from container
        web_interface = container.get_service('web_chat_interface')
        
        # Run the application (web chat)
        import socket
        port = 8001
        # Find available port if 8001 is in use
        for test_port in range(8001, 8010):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', test_port))
            sock.close()
            if result != 0:  # Port is available
                port = test_port
                break
        
        print(f"🚀 Starting AI Coach on http://localhost:{port}")
        debug_mode = getattr(config, 'debug', False)
        web_interface.run(host='0.0.0.0', port=port, debug=debug_mode)
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 