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
