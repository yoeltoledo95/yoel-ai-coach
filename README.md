# 🏗️ AI Coach - Clean Architecture

A sophisticated AI-powered fitness coaching system built with **Clean Architecture** principles, featuring WhatsApp integration and comprehensive exercise knowledge management.

## 🎯 **Architecture Overview**

This application follows **Clean Architecture** with **Domain-Driven Design** principles:

```
src/
├── domain/           # Business logic & entities
│   ├── entities/     # Core business objects
│   ├── repositories/ # Data access interfaces
│   └── services/     # Business logic services
├── infrastructure/   # External concerns
│   ├── database/     # Data persistence
│   ├── external/     # External APIs
│   └── config/       # Configuration
├── application/      # Use cases & orchestration
│   ├── use_cases/    # Application use cases
│   └── interfaces/   # Interface adapters
└── shared/          # Shared utilities
```

## 🚀 **Key Features**

### **Core Capabilities**
- ✅ **75+ Exercises** from multiple sources (StrengthLog, DIE RINGE, White Coat Trainer)
- ✅ **15 World-Class Mentors** with specialized knowledge
- ✅ **RAG System** for intelligent knowledge retrieval
- ✅ **WhatsApp Integration** for mobile coaching
- ✅ **Personalized Coaching** based on user patterns
- ✅ **Weekly Planning** with AI-generated programs

### **Technical Excellence**
- 🏗️ **Clean Architecture** with clear separation of concerns
- 🔄 **Dependency Injection** for loose coupling
- 🛡️ **Comprehensive Error Handling** with custom exceptions
- 📊 **Centralized Logging** and monitoring
- ⚙️ **Configuration Management** with environment variables
- 🧪 **Testable Design** with repository pattern

## 📁 **Project Structure**

```
yoel_ai_coach/
├── src/                          # Application source code
│   ├── domain/                   # Business logic & entities
│   │   ├── entities/            # Core business objects
│   │   │   ├── user.py
│   │   │   ├── exercise.py
│   │   │   └── mentor.py
│   │   ├── repositories/        # Data access interfaces
│   │   │   ├── user_repository.py
│   │   │   ├── exercise_repository.py
│   │   │   └── mentor_repository.py
│   │   └── services/           # Business logic services
│   │       └── coaching_service.py
│   ├── infrastructure/          # External concerns
│   │   ├── database/           # Data persistence
│   │   ├── external/           # External APIs
│   │   │   ├── openai_client.py
│   │   │   └── whatsapp_client.py
│   │   └── config/             # Configuration
│   │       └── settings.py
│   ├── application/            # Use cases & orchestration
│   │   ├── use_cases/         # Application use cases
│   │   │   ├── get_coaching_response.py
│   │   │   ├── create_weekly_plan.py
│   │   │   └── analyze_user_patterns.py
│   │   ├── interfaces/        # Interface adapters
│   │   │   └── whatsapp_interface.py
│   │   └── container.py       # Dependency injection
│   └── shared/                # Shared utilities
│       ├── exceptions.py
│       └── logging.py
├── data/                       # Data files
│   ├── exercises/
│   ├── mentors/
│   └── users/
├── tests/                      # Test suite
├── scripts/                    # Utility scripts
├── docs/                       # Documentation
├── config/                     # Configuration files
└── deployment/                 # Deployment configs
```

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.8+
- OpenAI API key
- WhatsApp Business API credentials

### **Environment Variables**
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# WhatsApp (for production)
WHATSAPP_API_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_WEBHOOK_SECRET=your_webhook_secret

# Optional
ENVIRONMENT=development
DEBUG=true
OPENAI_MODEL=gpt-4o
```

### **Installation**
```bash
# Clone repository
git clone https://github.com/yoeltoledo95/yoel-ai-coach.git
cd yoel_ai_coach

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

## 🏃‍♂️ **Usage**

### **WhatsApp Integration**
The system automatically handles WhatsApp messages through webhooks:

1. **Setup Webhook** in Meta Developer Console
2. **Configure URL** to point to your server
3. **Send Messages** to your WhatsApp number

### **Message Types**
- **General Coaching**: "I'm feeling tired today"
- **Weekly Plans**: "Create my weekly plan"
- **Progress Analysis**: "Show my progress"

## 🧪 **Testing**

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/
```

## 📊 **Architecture Benefits**

### **✅ Maintainability**
- Clear separation of concerns
- Single responsibility principle
- Easy to understand and modify

### **✅ Testability**
- Dependency injection
- Repository pattern
- Mockable interfaces

### **✅ Scalability**
- Modular design
- Loose coupling
- Easy to extend

### **✅ Reliability**
- Comprehensive error handling
- Retry logic for external APIs
- Centralized logging

## 🔄 **Development Workflow**

### **Adding New Features**
1. **Domain Layer**: Define entities and business rules
2. **Repository Layer**: Define data access interfaces
3. **Infrastructure Layer**: Implement data access
4. **Application Layer**: Create use cases
5. **Interface Layer**: Add user interfaces

### **Example: Adding Exercise Categories**
```python
# 1. Domain Entity
@dataclass
class ExerciseCategory:
    name: str
    description: str
    exercises: List[Exercise]

# 2. Repository Interface
class ExerciseCategoryRepository(ABC):
    @abstractmethod
    def get_categories(self) -> List[ExerciseCategory]:
        pass

# 3. Use Case
class GetExerciseCategoriesUseCase:
    def execute(self) -> List[ExerciseCategory]:
        return self.repository.get_categories()
```

## 🚀 **Deployment**

### **Local Development**
```bash
python src/main.py
```

### **Production**
```bash
# Using Docker
docker build -t ai-coach .
docker run -p 5000:5000 ai-coach

# Using Python directly
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## 📈 **Performance & Monitoring**

- **Logging**: Centralized logging with different levels
- **Error Tracking**: Custom exceptions with detailed messages
- **Health Checks**: `/health` endpoint for monitoring
- **Metrics**: Training session analytics and user patterns

## 🤝 **Contributing**

1. **Fork** the repository
2. **Create** a feature branch
3. **Follow** the clean architecture principles
4. **Add** comprehensive tests
5. **Submit** a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using Clean Architecture principles** 