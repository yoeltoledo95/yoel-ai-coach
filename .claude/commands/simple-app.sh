#!/bin/bash
# Build the simple version of the AI coach app

echo "🏗️ Building Simple AI Coach App..."

# Create simple app.py
cat > app.py << 'EOF'
from flask import Flask, request, jsonify, render_template
import openai
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

class FitnessCoach:
    def __init__(self):
        self.user_profile = self._load_user_profile()
        self.exercises = self._load_exercises()
        self.conversation_history = []
    
    def _load_user_profile(self):
        with open('data/users/yoel_profile.json') as f:
            return json.load(f)
    
    def _load_exercises(self):
        with open('data/exercises/exercise_kb.json') as f:
            return json.load(f)
    
    def get_response(self, user_input):
        # Simple context building
        context = f"""
        You are Yoel's personal AI fitness coach. Be conversational and motivating.

        USER PROFILE:
        {json.dumps(self.user_profile, indent=2)}

        RECENT CONVERSATION:
        {json.dumps(self.conversation_history[-3:], indent=2)}

        INSTRUCTIONS:
        - Consider Yoel's injuries (shoulder issues, knee recovered)
        - Focus on his goals (handstand, pancake flexibility, movement quality)
        - Be encouraging and specific
        - Suggest exercises from the database when relevant
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": ai_response
        })
        
        return ai_response

coach = FitnessCoach()

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    response = coach.get_response(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=8001)
EOF

# Create simple HTML template
mkdir -p templates
cat > templates/chat.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Yoel's AI Coach</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #chat { height: 400px; border: 1px solid #ccc; overflow-y: scroll; padding: 10px; }
        #input { width: 80%; padding: 10px; }
        #send { padding: 10px 20px; }
    </style>
</head>
<body>
    <h1>Yoel's AI Fitness Coach</h1>
    <div id="chat"></div>
    <input type="text" id="input" placeholder="Ask me anything about fitness...">
    <button id="send">Send</button>

    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');
        const send = document.getElementById('send');

        function addMessage(text, isUser = false) {
            const div = document.createElement('div');
            div.style.margin = '10px 0';
            div.style.padding = '10px';
            div.style.backgroundColor = isUser ? '#e3f2fd' : '#f5f5f5';
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        async function sendMessage() {
            const message = input.value.trim();
            if (!message) return;

            addMessage(message, true);
            input.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                addMessage(data.response);
            } catch (error) {
                addMessage('Sorry, I encountered an error. Please try again.');
            }
        }

        send.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
EOF

# Create simple requirements.txt
cat > requirements-simple.txt << 'EOF'
flask==2.3.3
openai==1.0.0
python-dotenv==1.0.0
EOF

echo "✅ Simple app created!"
echo "📁 Files created:"
echo "  - app.py (simple Flask app)"
echo "  - templates/chat.html (simple UI)"
echo "  - requirements-simple.txt (minimal dependencies)"
echo ""
echo "🚀 To run: python app.py"
echo "🌐 Open: http://localhost:8001"
