#!/usr/bin/env python3
"""
Simple Web Interface for Testing AI Coach
Run this to test the AI coach through a web browser
"""

import sys
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify

# Add src to path
sys.path.append('src')

# HTML template for the test interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Coach Testing Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .test-scenario { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
        .scenario-title { font-weight: bold; color: #007bff; }
        .scenario-message { color: #666; font-style: italic; }
        .response { background: #e8f5e8; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #28a745; }
        .response-title { font-weight: bold; color: #28a745; }
        .response-text { white-space: pre-wrap; }
        .input-group { margin: 20px 0; }
        input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .loading { color: #666; font-style: italic; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 5px; }
        .success { color: #155724; background: #d4edda; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Coach Testing Interface</h1>
        
        <div class="input-group">
            <label for="user-message">Test Message:</label>
            <input type="text" id="user-message" placeholder="Type your test message here..." value="Hi! I'm new to fitness and want to get stronger. Can you help me create a workout plan?">
            <button onclick="sendMessage()">Send Message</button>
        </div>
        
        <div id="response-area"></div>
        
        <h2>🧪 Quick Test Scenarios</h2>
        <div class="test-scenario">
            <div class="scenario-title">New User - General Fitness</div>
            <div class="scenario-message">"Hi! I'm new to fitness and want to get stronger. Can you help me create a workout plan?"</div>
            <button onclick="testScenario(this)">Test This</button>
        </div>
        
        <div class="test-scenario">
            <div class="scenario-title">Weight Loss Goal</div>
            <div class="scenario-message">"I want to lose weight and tone up. I have 30 minutes a day to work out."</div>
            <button onclick="testScenario(this)">Test This</button>
        </div>
        
        <div class="test-scenario">
            <div class="scenario-title">Injury Recovery</div>
            <div class="scenario-message">"I have a knee injury from running. What exercises should I avoid and what can I do instead?"</div>
            <button onclick="testScenario(this)">Test This</button>
        </div>
        
        <div class="test-scenario">
            <div class="scenario-title">Advanced Exercise</div>
            <div class="scenario-message">"I want to learn how to do a handstand. What's the best progression?"</div>
            <button onclick="testScenario(this)">Test This</button>
        </div>
        
        <div class="test-scenario">
            <div class="scenario-title">Mobility Focus</div>
            <div class="scenario-message">"My hips are really tight and I can't squat properly. Help me improve my mobility."</div>
            <button onclick="testScenario(this)">Test This</button>
        </div>
        
        <div class="test-scenario">
            <div class="scenario-title">Mentor-Specific (Ido Portal)</div>
            <div class="scenario-message">"I want to train like Ido Portal. What exercises should I focus on?"</div>
            <button onclick="testScenario(this)">Test This</button>
        </div>
        
        <div class="test-scenario">
            <div class="scenario-title">Equipment Question</div>
            <div class="scenario-message">"I only have dumbbells at home. What workouts can I do?"</div>
            <button onclick="testScenario(this)">Test This</button>
        </div>
        
        <div class="test-scenario">
            <div class="scenario-title">Motivation Request</div>
            <div class="scenario-message">"I'm feeling unmotivated to work out today. Can you help me get motivated?"</div>
            <button onclick="testScenario(this)">Test This</button>
        </div>
    </div>

    <script>
        function sendMessage() {
            const message = document.getElementById('user-message').value;
            if (!message.trim()) {
                alert('Please enter a message');
                return;
            }
            
            document.getElementById('response-area').innerHTML = '<div class="loading">🤖 AI Coach is thinking...</div>';
            
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: 'test_user_' + Date.now()
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('response-area').innerHTML = '<div class="error">❌ Error: ' + data.error + '</div>';
                } else {
                    document.getElementById('response-area').innerHTML = `
                        <div class="response">
                            <div class="response-title">🤖 AI Coach Response:</div>
                            <div class="response-text">${data.response}</div>
                        </div>
                    `;
                }
            })
            .catch(error => {
                document.getElementById('response-area').innerHTML = '<div class="error">❌ Network error: ' + error.message + '</div>';
            });
        }
        
        function testScenario(button) {
            const scenarioDiv = button.parentElement;
            const messageElement = scenarioDiv.querySelector('.scenario-message');
            const message = messageElement.textContent.replace(/"/g, '').trim();
            
            document.getElementById('user-message').value = message;
            sendMessage();
        }
        
        // Allow Enter key to send message
        document.getElementById('user-message').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'test_user')
        
        if not message:
            return jsonify({'error': 'No message provided'})
        
        # Import and use the AI coach
        from application.container import container
        coaching_use_case = container.get_coaching_response_use_case()
        
        if not coaching_use_case:
            return jsonify({'error': 'AI Coach not available'})
        
        # Get AI response
        response = coaching_use_case.execute(
            user_id=user_id,
            message=message
        )
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'AI Coach Test Interface'})

if __name__ == '__main__':
    print("🌐 Starting AI Coach Test Interface...")
    print("📱 Open your browser to: http://localhost:5001")
    print("🔄 Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5001, debug=True) 