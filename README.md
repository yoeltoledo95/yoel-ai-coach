# Yoel's AI Coach - V2: WhatsApp Bot

## 🎯 V2: WhatsApp AI Coach

This is the **WhatsApp version** of Yoel's AI Coach - a movement-focused AI fitness coach that works directly through WhatsApp.

### What's Different in V2:
- **WhatsApp Bot** instead of web interface
- **Movement-only focus** (no nutrition)
- **Weekly coaching loop** (Monday plan → daily feedback → Sunday reflection)
- **Clean, minimal architecture**

### Core Features:
- **AI Coaching Brain** - Mentor-powered responses using world-class fitness knowledge
- **Weekly Training Plans** - Personalized movement programs
- **Daily Feedback System** - Simple logging through WhatsApp
- **Sunday Reflection** - Weekly progress review and plan evolution

### Architecture:
```
coach_core/          # AI coaching brain (same as V1)
├── ai.py           # OpenAI integration
├── data.py         # Data management
├── mentor_brain.py # 15 world-class fitness mentors
└── utils.py        # Helper functions

whatsapp_bot.py     # WhatsApp integration (NEW)
requirements.txt     # Dependencies
```

### V1 vs V2:
- **V1**: Streamlit web app with full UI
- **V2**: WhatsApp bot with same AI brain, different interface

---

## 🚀 Quick Start

1. **Set up Meta Developer Account** (you're doing this now)
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure WhatsApp API**
4. **Run the bot**: `python whatsapp_bot.py`

---

## 📁 Project Structure

```
yoel_ai_coach/
├── coach_core/          # AI coaching brain (from V1)
│   ├── ai.py           # OpenAI integration
│   ├── data.py         # Data management
│   ├── mentor_brain.py # Fitness mentor knowledge
│   └── utils.py        # Helper functions
├── whatsapp_bot.py     # WhatsApp integration (NEW)
├── requirements.txt     # Dependencies
├── yoel_profile.json   # Your profile data
└── daily_logs.json     # Your logs
```

---

## 🔄 Weekly Coaching Loop

**Monday**: AI generates personalized movement plan
**Daily**: Simple feedback via WhatsApp ("felt great", "shoulder tight")
**Sunday**: Reflection and plan evolution for next week

---

## 🧠 AI Coaching Brain

The same mentor-powered AI system from V1:
- 15 world-class fitness mentors
- Personalized responses based on your profile
- Movement-focused coaching (no nutrition)
- Weekly training plan generation

---

## 📱 WhatsApp Integration

Coming soon - will integrate with Meta's Cloud API for WhatsApp Business.

---

## 🏷️ Version History

- **V1.0**: Complete Streamlit AI Coach (tagged and saved)
- **V2.0**: WhatsApp AI Coach (current development)

---

*Ready to build the WhatsApp bot while you set up your Meta developer account!* 