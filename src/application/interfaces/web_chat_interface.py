#!/usr/bin/env python3
"""
Web-based chat interface for AI fitness coach
"""

import json
import logging
from flask import Flask, render_template, request, jsonify, session
from typing import Dict, Any
import uuid

logger = logging.getLogger(__name__)

class WebChatInterface:
    """Web-based chat interface for AI fitness coach"""
    
    def __init__(self, container):
        self.container = container
        self.app = Flask(__name__)
        self.app.secret_key = 'ai_coach_secret_key'
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def home():
            """Main chat interface"""
            return render_template('chat.html')
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """Handle chat messages"""
            try:
                data = request.get_json()
                message = data.get('message', '').strip()
                user_id = data.get('user_id', 'web_user')
                
                if not message:
                    return jsonify({'error': 'Message is required'}), 400
                
                # Get coaching response
                coaching_use_case = self.container.get_service('get_coaching_response_use_case')
                response = coaching_use_case.execute(user_id, message, {})
                
                return jsonify({
                    'response': response,
                    'user_id': user_id,
                    'timestamp': str(uuid.uuid4())
                })
                
            except Exception as e:
                logger.error(f"Error processing chat message: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/health')
        def health():
            """Health check endpoint"""
            return jsonify({
                'service': 'AI Coach Web Chat',
                'status': 'healthy'
            })
    
    def run(self, host='0.0.0.0', port=8001, debug=False):
        """Run the web chat interface"""
        logger.info(f"Starting web chat interface on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
