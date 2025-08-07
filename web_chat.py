#!/usr/bin/env python3
"""
Web Chat Launcher for AI Fitness Coach
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, 'src')

def main():
    """Launch the web chat interface"""
    try:
        print("🚀 Starting AI Fitness Coach Web Chat...")
        
        # Import container and web chat interface
        from application.container import container
        from application.interfaces.web_chat_interface import WebChatInterface
        
        print("✅ Container loaded successfully")
        
        # Create web chat interface
        web_chat = WebChatInterface(container)
        
        print("✅ Web chat interface created")
        print("🌐 Opening web chat at: http://localhost:8001")
        print("📱 You can now test the AI coaching system!")
        print("⏹️  Press Ctrl+C to stop")
        
        # Run the web chat
        web_chat.run(host='0.0.0.0', port=8001, debug=False)
        
    except Exception as e:
        print(f"❌ Error starting web chat: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
