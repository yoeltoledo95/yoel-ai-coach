#!/usr/bin/env python3
"""
Migration script to move existing data to clean architecture
"""
import json
import shutil
import os
from pathlib import Path
from typing import Dict, Any, List

def migrate_exercise_data():
    """Migrate exercise data to new structure"""
    print("🔄 Migrating exercise data...")
    
    # Source files
    exercise_kb_path = Path("coach_core/exercise_kb.json")
    exercise_library_path = Path("coach_core/exercise_library.txt")
    
    # Destination
    data_exercises_path = Path("data/exercises")
    data_exercises_path.mkdir(exist_ok=True)
    
    # Copy exercise KB
    if exercise_kb_path.exists():
        shutil.copy2(exercise_kb_path, data_exercises_path / "exercise_kb.json")
        print(f"✅ Copied {exercise_kb_path} to {data_exercises_path}")
    
    # Copy exercise library
    if exercise_library_path.exists():
        shutil.copy2(exercise_library_path, data_exercises_path / "exercise_library.txt")
        print(f"✅ Copied {exercise_library_path} to {data_exercises_path}")
    
    print("✅ Exercise data migration completed")

def migrate_mentor_data():
    """Migrate mentor data to new structure"""
    print("🔄 Migrating mentor data...")
    
    # Source files
    mentor_brain_path = Path("coach_core/mentor_brain.py")
    knowledge_base_path = Path("knowledge_base/mentors")
    
    # Destination
    data_mentors_path = Path("data/mentors")
    data_mentors_path.mkdir(exist_ok=True)
    
    # Copy mentor brain
    if mentor_brain_path.exists():
        shutil.copy2(mentor_brain_path, data_mentors_path / "mentor_brain.py")
        print(f"✅ Copied {mentor_brain_path} to {data_mentors_path}")
    
    # Copy knowledge base
    if knowledge_base_path.exists():
        shutil.copytree(knowledge_base_path, data_mentors_path / "markdown", dirs_exist_ok=True)
        print(f"✅ Copied {knowledge_base_path} to {data_mentors_path}/markdown")
    
    print("✅ Mentor data migration completed")

def migrate_user_data():
    """Migrate user data to new structure"""
    print("🔄 Migrating user data...")
    
    # Source files
    user_memory_db_path = Path("user_memory.db")
    coach_data_db_path = Path("coach_data.db")
    yoel_profile_path = Path("yoel_profile.json")
    daily_logs_path = Path("daily_logs.json")
    
    # Destination
    data_users_path = Path("data/users")
    data_users_path.mkdir(exist_ok=True)
    
    # Copy database files
    if user_memory_db_path.exists():
        shutil.copy2(user_memory_db_path, data_users_path / "user_memory.db")
        print(f"✅ Copied {user_memory_db_path} to {data_users_path}")
    
    if coach_data_db_path.exists():
        shutil.copy2(coach_data_db_path, data_users_path / "coach_data.db")
        print(f"✅ Copied {coach_data_db_path} to {data_users_path}")
    
    # Copy profile and logs
    if yoel_profile_path.exists():
        shutil.copy2(yoel_profile_path, data_users_path / "yoel_profile.json")
        print(f"✅ Copied {yoel_profile_path} to {data_users_path}")
    
    if daily_logs_path.exists():
        shutil.copy2(daily_logs_path, data_users_path / "daily_logs.json")
        print(f"✅ Copied {daily_logs_path} to {data_users_path}")
    
    print("✅ User data migration completed")

def migrate_scripts():
    """Migrate utility scripts to new structure"""
    print("🔄 Migrating scripts...")
    
    # Source files
    extract_script_path = Path("coach_core/extract_exercises_to_json.py")
    import_script_path = Path("coach_core/import_external_exercises.py")
    
    # Destination
    scripts_path = Path("scripts")
    scripts_path.mkdir(exist_ok=True)
    
    # Copy scripts
    if extract_script_path.exists():
        shutil.copy2(extract_script_path, scripts_path / "extract_exercises.py")
        print(f"✅ Copied {extract_script_path} to {scripts_path}")
    
    if import_script_path.exists():
        shutil.copy2(import_script_path, scripts_path / "import_external_exercises.py")
        print(f"✅ Copied {import_script_path} to {scripts_path}")
    
    print("✅ Scripts migration completed")

def migrate_tests():
    """Migrate tests to new structure"""
    print("🔄 Migrating tests...")
    
    # Source test files
    test_files = [
        "test_ai_coach.py",
        "test_analysis.py",
        "test_enhanced_ai.py",
        "test_image_handling.py",
        "test_rag_system.py",
        "test_user_memory.py",
        "test_whatsapp_bot.py"
    ]
    
    # Destination
    tests_path = Path("tests")
    tests_unit_path = tests_path / "unit"
    tests_integration_path = tests_path / "integration"
    tests_e2e_path = tests_path / "e2e"
    
    tests_unit_path.mkdir(parents=True, exist_ok=True)
    tests_integration_path.mkdir(parents=True, exist_ok=True)
    tests_e2e_path.mkdir(parents=True, exist_ok=True)
    
    # Move test files
    for test_file in test_files:
        source_path = Path(test_file)
        if source_path.exists():
            # Categorize tests (simple heuristic)
            if "whatsapp" in test_file.lower():
                dest_path = tests_e2e_path / test_file
            elif "ai" in test_file.lower() or "coach" in test_file.lower():
                dest_path = tests_integration_path / test_file
            else:
                dest_path = tests_unit_path / test_file
            
            shutil.copy2(source_path, dest_path)
            print(f"✅ Copied {test_file} to {dest_path}")
    
    print("✅ Tests migration completed")

def create_config_files():
    """Create configuration files for new structure"""
    print("🔄 Creating configuration files...")
    
    # Create config directory
    config_path = Path("config")
    config_path.mkdir(exist_ok=True)
    
    # Create .env template
    env_template = """# AI Coach Configuration

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# WhatsApp Configuration (for production)
WHATSAPP_API_TOKEN=your_whatsapp_token_here
WHATSAPP_BUSINESS_ID=your_business_id_here
WHATSAPP_WEBHOOK_SECRET=your_webhook_secret_here

# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=sqlite:///data/users/user_memory.db
CHROMA_PATH=data/vector_store
"""
    
    with open(config_path / ".env.template", "w") as f:
        f.write(env_template)
    
    print("✅ Created .env.template")
    
    # Create deployment config
    deployment_path = Path("deployment")
    deployment_path.mkdir(exist_ok=True)
    
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/
COPY config/ ./config/

EXPOSE 5000

CMD ["python", "src/main.py"]
"""
    
    with open(deployment_path / "Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    print("✅ Created Dockerfile")

def update_requirements():
    """Update requirements.txt for new structure"""
    print("🔄 Updating requirements.txt...")
    
    new_requirements = """flask==2.3.3
requests==2.31.0
python-dotenv==1.0.0
openai>=1.0.0
chromadb==0.4.22
sentence-transformers==2.2.2
numpy==1.24.3
markdown==3.5.1
langchain>=0.1.0
huggingface_hub>=0.20.0
pytest>=7.0.0
pytest-cov>=4.0.0
gunicorn>=20.1.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(new_requirements)
    
    print("✅ Updated requirements.txt")

def main():
    """Main migration function"""
    print("🚀 Starting migration to Clean Architecture...")
    
    try:
        # Create necessary directories
        Path("data").mkdir(exist_ok=True)
        Path("tests").mkdir(exist_ok=True)
        Path("scripts").mkdir(exist_ok=True)
        Path("docs").mkdir(exist_ok=True)
        Path("config").mkdir(exist_ok=True)
        Path("deployment").mkdir(exist_ok=True)
        
        # Run migrations
        migrate_exercise_data()
        migrate_mentor_data()
        migrate_user_data()
        migrate_scripts()
        migrate_tests()
        create_config_files()
        update_requirements()
        
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Set up your environment variables in config/.env")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the application: python src/main.py")
        print("4. Update your deployment configuration")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 