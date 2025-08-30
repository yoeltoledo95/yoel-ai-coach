#!/usr/bin/env python3
"""
Web-based chat interface for AI fitness coach
"""

import json
import logging
from flask import Flask, render_template, request, jsonify, session, g, make_response
from typing import Dict, Any
import uuid

from shared.security.rate_limiter import rate_limit, rate_limiter
from shared.security.input_validation import InputValidator
from shared.security.security_headers import SecurityHeaders, security_audit_middleware
from shared.exceptions import ValidationError
from infrastructure.config.settings import config

logger = logging.getLogger(__name__)

class WebChatInterface:
    """Web-based chat interface for AI fitness coach"""
    
    def __init__(self, container):
        self.container = container
        self.app = Flask(__name__)
        
        # Setup signal handlers for graceful shutdown
        import signal
        import sys
        
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal, cleaning up...")
            # Clean up any resources here
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Security configuration
        self.app.secret_key = getattr(config, 'secret_key', None) or 'ai_coach_secret_key_yoel_2024'
        self.app.config['SESSION_PERMANENT'] = True
        self.app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
        environment = getattr(config, 'environment', 'development')
        self.app.config['SESSION_COOKIE_SECURE'] = str(environment).lower() == 'production'
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        self.app.config['SESSION_COOKIE_PATH'] = '/'  # Ensure cookie is available for all paths
        self.app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow for localhost
        self.app.config['CORS_ORIGINS'] = getattr(config, 'cors_origins', ['http://localhost:3000', 'http://localhost:8000'])
        
        # Initialize security middleware
        self.security_headers = SecurityHeaders(self.app)
        security_audit_middleware(self.app)
        
        # Initialize input validator
        self.validator = InputValidator()
        
        self.setup_routes()
        self.setup_auth_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def home():
            """Redirect to appropriate page based on authentication status"""
            from flask import redirect, url_for
            
            # Check if user is authenticated
            if 'user_id' in session and session.get('authenticated'):
                logger.info(f"Authenticated user accessing root, redirecting to chat. Session: {dict(session)}")
                return redirect('/chat')
            else:
                logger.info(f"Unauthenticated user accessing root, redirecting to login. Session: {dict(session)}")
                return redirect('/login')
        
        @self.app.route('/chat')
        def chat_interface():
            """Main chat interface - requires authentication"""
            # Debug logging
            logger.info(f"Chat interface accessed. Session: {dict(session)}")
            
            if 'user_id' not in session or not session.get('authenticated'):
                logger.warning(f"Unauthenticated access to chat. Session: {dict(session)}")
                return redirect('/login')
            return render_template('chat.html')
        
        @self.app.route('/api/chat', methods=['POST'])
        @rate_limit(lambda: f"ip:{request.remote_addr}")
        def chat():
            """Handle chat messages with comprehensive security"""
            try:
                # Validate request content type
                if not request.is_json:
                    return jsonify({
                        'status': 'error',
                        'error_code': 'INVALID_CONTENT_TYPE',
                        'message': 'Content-Type must be application/json'
                    }), 400
                
                # Get and validate JSON payload
                try:
                    data = request.get_json()
                    if not data:
                        raise ValidationError("Request body cannot be empty")
                    
                    # Validate payload structure
                    data = self.validator.validate_json_payload(data)
                    
                except Exception as e:
                    return jsonify({
                        'status': 'error',
                        'error_code': 'INVALID_JSON',
                        'message': f'Invalid JSON payload: {str(e)}'
                    }), 400
                
                # Extract and validate inputs
                try:
                    raw_message = data.get('message', '')
                    raw_user_name = data.get('user_name', 'User')
                    
                    # Validate message
                    message = self.validator.validate_message(raw_message)
                    
                    # Validate user name (treat as user input)
                    user_name = self.validator.validate_message(raw_user_name, max_length=50)
                    
                except ValidationError as e:
                    return jsonify({
                        'status': 'error',
                        'error_code': 'VALIDATION_ERROR',
                        'message': str(e)
                    }), 400
                
                # Use authenticated user from session
                if 'user_id' in session and session.get('authenticated'):
                    user_id = session['user_id']
                    user_name = session.get('user_name', user_name)
                else:
                    # Fallback for unauthenticated requests
                    if any(name in user_name.lower() for name in ['yoel', 'coach', 'ai']):
                        user_id = 'yoel_user'
                    elif user_name.lower() in ['user']:
                        user_id = 'yoel_user'
                    else:
                        user_id = f"web_user_{user_name.lower().replace(' ', '_')}"
                
                # Get or create user session
                if 'user_id' not in session:
                    session['user_id'] = user_id
                    session['user_name'] = user_name
                    session['conversation_history'] = []
                
                # Keep only last 3 messages to prevent session bloat
                if 'conversation_history' not in session:
                    session['conversation_history'] = []
                
                session['conversation_history'].append({
                    'role': 'user',
                    'message': message[:200]  # Truncate long messages
                })
                
                # Keep only last 6 messages (3 pairs)
                if len(session['conversation_history']) > 6:
                    session['conversation_history'] = session['conversation_history'][-6:]
                
                # Check for session reset commands
                if message.lower() in ['reset', 'clear', 'start over', 'new conversation']:
                    session.clear()
                    return jsonify({
                        'response': "Session reset! Hi! I'm your AI fitness coach. How can I help you today?",
                        'user_id': user_id,
                        'timestamp': str(uuid.uuid4())
                    })
                
                # Use main coaching response system
                coaching_use_case = self.container.get_service('get_coaching_response_use_case')
                fallback = coaching_use_case.execute(session['user_id'], message, {}, user_name)
                
                # Add bot response to history
                session['conversation_history'].append({
                    'role': 'bot',
                    'message': fallback,
                    'timestamp': str(uuid.uuid4())
                })
                
                return jsonify({
                    'response': fallback,
                    'user_id': session.get('user_id', user_id),
                    'timestamp': str(uuid.uuid4())
                })
                
            except Exception as e:
                logger.error(f"Error processing chat message: {e}", exc_info=True)
                
                # Add error to conversation history
                error_message = "I'm sorry, I encountered an error processing your request. Please try again."
                if 'conversation_history' in session:
                    session['conversation_history'].append({
                        'role': 'bot',
                        'message': error_message,
                        'timestamp': str(uuid.uuid4()),
                        'error': True
                    })
                
                return jsonify({
                    'response': error_message,
                    'user_id': session.get('user_id', 'unknown'),
                    'timestamp': str(uuid.uuid4()),
                    'error': True
                }), 500
        
        @self.app.route('/api/health')
        def health():
            """Health check endpoint"""
            return jsonify({
                'service': 'AI Coach Web Chat',
                'status': 'healthy'
            })
        
        @self.app.route('/api/clear-session', methods=['POST'])
        def clear_session():
            """Clear user session"""
            session.clear()
            return jsonify({
                'message': 'Session cleared successfully',
                'status': 'success'
            })
        
        @self.app.route('/api/debug-session')
        def debug_session():
            """Debug session information"""
            return jsonify({
                'session_data': dict(session),
                'user_id': session.get('user_id'),
                'authenticated': session.get('authenticated'),
                'user_name': session.get('user_name')
            })
        
        @self.app.route('/api/auth/status')
        def auth_status():
            """Check authentication status"""
            return jsonify({
                'authenticated': session.get('authenticated', False),
                'user_id': session.get('user_id'),
                'user_name': session.get('user_name')
            })
    
    def setup_auth_routes(self):
        """Setup authentication routes"""
        
        @self.app.route('/login')
        def login_page():
            """Login page"""
            response = make_response(render_template('login.html'))
            # Add cache-busting headers
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        
        @self.app.route('/onboarding')
        def onboarding_page():
            """Onboarding page"""
            # Debug logging
            logger.info(f"Onboarding page accessed. Session: {dict(session)}")
            response = make_response(render_template('onboarding.html'))
            # Add cache-busting headers
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        
        @self.app.route('/api/auth/login', methods=['POST'])
        @rate_limit(lambda: f"auth:{request.remote_addr}")
        def login():
            """Handle user login"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'status': 'error', 'message': 'No data provided'}), 400
                
                # Validate input
                validated_data = self.validator.validate_auth(data)
                
                email = validated_data['email']
                password = validated_data['password']
                
                # Simple authentication - in production, use proper password hashing
                user_repository = self.container.get_service('user_repository')
                
                # For demo: create user if doesn't exist
                user_id = f"user_{email.replace('@', '_').replace('.', '_')}"
                user = user_repository.get_user(user_id)
                
                if not user:
                    # Create new user for demo
                    coaching_service = self.container.get_service('coaching_service')
                    user = coaching_service._create_new_user_profile(user_id, email.split('@')[0])
                
                # Check if user has completed profile
                needs_onboarding = not user.profile or not hasattr(user.profile, 'level') or user.profile.level is None
                
                # Set session
                session['user_id'] = user_id
                session['user_name'] = user.profile.name if user.profile else email.split('@')[0]
                session['authenticated'] = True
                
                return jsonify({
                    'status': 'success', 
                    'needs_onboarding': needs_onboarding,
                    'user_id': user_id,
                    'redirect': '/chat'
                })
                
            except ValidationError as e:
                return jsonify({'status': 'error', 'message': str(e)}), 400
            except Exception as e:
                logger.error(f"Login error: {e}")
                return jsonify({'status': 'error', 'message': 'Login failed'}), 500
        
        @self.app.route('/api/auth/signup', methods=['POST'])
        @rate_limit(lambda: f"signup:{request.remote_addr}")
        def signup():
            """Handle user signup"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'status': 'error', 'message': 'No data provided'}), 400
                
                # Validate input
                validated_data = self.validator.validate_auth(data)
                
                name = validated_data.get('name', validated_data['email'].split('@')[0])
                email = validated_data['email']
                password = validated_data['password']
                
                # Create new user
                user_id = f"user_{email.replace('@', '_').replace('.', '_')}"
                coaching_service = self.container.get_service('coaching_service')
                user = coaching_service._create_new_user_profile(user_id, name)
                
                if user:
                    # Set session
                    session['user_id'] = user_id
                    session['user_name'] = name
                    session['authenticated'] = True
                    
                    # Debug logging
                    logger.info(f"Session set for user {user_id}: {dict(session)}")
                    
                    # Create response with session data
                    response = jsonify({
                        'status': 'success',
                        'user_id': user_id,
                        'needs_onboarding': True,
                        'redirect': '/onboarding'
                    })
                    
                    # Ensure session is saved
                    session.modified = True
                    
                    return response
                else:
                    return jsonify({'status': 'error', 'message': 'Failed to create account'}), 500
                
            except ValidationError as e:
                return jsonify({'status': 'error', 'message': str(e)}), 400
            except Exception as e:
                logger.error(f"Signup error: {e}")
                return jsonify({'status': 'error', 'message': 'Signup failed'}), 500
        
        @self.app.route('/api/auth/complete-profile', methods=['POST'])
        @rate_limit(lambda: f"profile:{request.remote_addr}")
        def complete_profile():
            """Complete user profile after onboarding"""
            try:
                if not session.get('authenticated'):
                    return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
                
                data = request.get_json()
                if not data:
                    return jsonify({'status': 'error', 'message': 'No data provided'}), 400
                
                user_id = session.get('user_id')
                profile_data = data  # The frontend sends the data directly, not wrapped in 'profile'
                
                # Get user and update profile
                user_repository = self.container.get_service('user_repository')
                user = user_repository.get_user(user_id)
                
                if user and user.profile:
                    # Update profile with onboarding data
                    from domain.entities.user import UserLevel, UserGoal
                    
                    # Set level
                    level_mapping = {
                        'beginner': UserLevel.BEGINNER,
                        'intermediate': UserLevel.INTERMEDIATE,
                        'advanced': UserLevel.ADVANCED
                    }
                    user.profile.level = level_mapping.get(profile_data.get('experience'), UserLevel.BEGINNER)
                    
                    # Set goals
                    goal_mapping = {
                        'strength': UserGoal.STRENGTH,
                        'flexibility': UserGoal.FLEXIBILITY,
                        'mobility': UserGoal.MOBILITY,
                        'hypertrophy': UserGoal.STRENGTH,  # Map hypertrophy to strength
                        'endurance': UserGoal.ENDURANCE,
                        'weight_loss': UserGoal.WEIGHT_LOSS,
                        'skill': UserGoal.SKILL  # Add skill mapping
                    }
                    goals = []
                    for goal_str in profile_data.get('goals', []):
                        if goal_str in goal_mapping:
                            goals.append(goal_mapping[goal_str])
                    user.profile.goals = goals
                    
                    # Set other profile data
                    if profile_data.get('age'):
                        user.profile.age = profile_data['age']
                    
                    # Update injury history
                    injury_info = {}
                    if profile_data.get('injuries'):
                        injury_info['general'] = profile_data['injuries']
                    
                    limitations = profile_data.get('limitations', [])
                    if 'knee' in limitations:
                        injury_info['knee'] = 'User reported knee issues'
                    if 'shoulder' in limitations:
                        injury_info['shoulder'] = 'User reported shoulder issues'
                    if 'back' in limitations:
                        injury_info['back'] = 'User reported back issues'
                    if 'wrist' in limitations:
                        injury_info['wrist'] = 'User reported wrist issues'
                    
                    user.profile.injury_history = injury_info
                    
                    # Update training preferences
                    training_prefs = {
                        'time_available': profile_data.get('timeAvailable'),
                        'equipment': profile_data.get('equipment', []),
                        'specific_goals': profile_data.get('specificGoals')
                    }
                    user.profile.training_preferences = training_prefs
                    
                    # Save updated user
                    user_repository.save_user(user, user_id)
                    
                    # Ensure session is maintained
                    session['user_id'] = user_id
                    session['authenticated'] = True
                    
                    # Debug logging
                    logger.info(f"Profile completed for user {user_id}. Session: {dict(session)}")
                    
                    # Create response with session data and redirect
                    response = jsonify({
                        'status': 'success',
                        'redirect_url': '/chat'
                    })
                    
                    # Ensure session is saved
                    session.modified = True
                    
                    return response
                else:
                    return jsonify({'status': 'error', 'message': 'User not found'}), 404
                
            except Exception as e:
                logger.error(f"Profile completion error: {e}")
                return jsonify({'status': 'error', 'message': 'Failed to save profile'}), 500
        
        @self.app.route('/api/auth/logout', methods=['POST'])
        def logout():
            """Handle user logout"""
            session.clear()
            return jsonify({'status': 'success'})
        
        @self.app.route('/api/shutdown', methods=['POST'])
        def shutdown():
            """Graceful shutdown endpoint"""
            import os
            import signal
            os.kill(os.getpid(), signal.SIGTERM)
            return jsonify({'status': 'shutting down'})
    
    def run(self, host='0.0.0.0', port=8001, debug=False):
        """Run the web chat interface"""
        logger.info(f"Starting web chat interface on {host}:{port}")
        
        # Completely disable multiprocessing to prevent semaphore leaks
        import os
        os.environ['FLASK_ENV'] = 'development'
        
        # Disable multiprocessing reloader to prevent semaphore leaks
        if debug:
            # Use simple reloader instead of multiprocessing
            self.app.run(
                host=host, 
                port=port, 
                debug=True,
                threaded=True,
                use_reloader=False  # Disable reloader to prevent semaphore leaks
            )
        else:
            # Production mode
            self.app.run(
                host=host, 
                port=port, 
                debug=False,
                threaded=True
            )
