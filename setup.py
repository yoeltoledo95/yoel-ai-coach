#!/usr/bin/env python3
"""
Setup script for AI Coach application
"""
import os
import shutil
from pathlib import Path

def setup_environment():
    """Setup environment configuration"""
    print("🔧 Setting up AI Coach environment...")
    
    # Check if .env exists
    env_file = Path(".env")
    template_file = Path("env.template")
    
    if not env_file.exists():
        if template_file.exists():
            print("📋 Creating .env file from template...")
            shutil.copy(template_file, env_file)
            print("✅ Created .env file")
            print("⚠️  Please edit .env file with your actual API keys:")
            print("   - OPENAI_API_KEY")
            print("   - WHATSAPP_API_TOKEN (if using WhatsApp)")
            print("   - WHATSAPP_PHONE_NUMBER_ID (if using WhatsApp)")
            print("   - WHATSAPP_VERIFY_TOKEN (if using WhatsApp)")
        else:
            print("❌ env.template not found")
            return False
    else:
        print("✅ .env file already exists")
    
    # Create necessary directories
    directories = [
        "data/users",
        "data/exercises", 
        "data/mentors",
        "data/knowledge_base",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    print("\n🎉 Setup complete!")
    print("📝 Next steps:")
    print("   1. Edit .env file with your API keys")
    print("   2. Run: python src/main.py")
    
    return True

if __name__ == "__main__":
    setup_environment() 