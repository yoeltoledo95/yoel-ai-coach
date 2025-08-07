"""
User Memory Store - Centralized storage for evolving user context
"""
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from shared.logging import get_logger

logger = get_logger(__name__)


class UserMemoryStore:
    """Centralized user memory store for evolving context"""
    
    def __init__(self, db_path: str = "data/users/user_memory.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Conversation history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        message TEXT NOT NULL,
                        response TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        context TEXT,
                        intent TEXT
                    )
                """)
                
                # User feedback table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        feedback_type TEXT NOT NULL,
                        feedback_text TEXT,
                        rating INTEGER,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        context TEXT
                    )
                """)
                
                # Progress milestones table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS progress_milestones (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        milestone_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        achieved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        context TEXT
                    )
                """)
                
                # User preferences evolution table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences_evolution (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        preference_type TEXT NOT NULL,
                        old_value TEXT,
                        new_value TEXT,
                        changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        reason TEXT
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation_user_id ON conversation_history(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON conversation_history(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON user_feedback(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_milestones_user_id ON progress_milestones(user_id)")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error initializing user memory store: {e}")
    
    def store_conversation(self, user_id: str, message: str, response: str, context: Dict[str, Any] = None, intent: str = None):
        """Store a conversation exchange"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversation_history (user_id, message, response, context, intent)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, message, response, json.dumps(context) if context else None, intent))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
    
    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT message, response, timestamp, context, intent
                    FROM conversation_history
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (user_id, limit))
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        "message": row[0],
                        "response": row[1],
                        "timestamp": row[2],
                        "context": json.loads(row[3]) if row[3] else {},
                        "intent": row[4]
                    })
                
                return conversations
                
        except Exception as e:
            logger.error(f"Error getting recent conversations: {e}")
            return []
    
    def store_user_feedback(self, user_id: str, feedback_type: str, feedback_text: str = None, rating: int = None, context: Dict[str, Any] = None):
        """Store user feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_feedback (user_id, feedback_type, feedback_text, rating, context)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, feedback_type, feedback_text, rating, json.dumps(context) if context else None))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing user feedback: {e}")
    
    def get_user_feedback(self, user_id: str, limit: int = 20) -> Dict[str, Any]:
        """Get user feedback and preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT feedback_type, feedback_text, rating, timestamp, context
                    FROM user_feedback
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (user_id, limit))
                
                feedback = {
                    "recent_feedback": [],
                    "feedback_summary": {},
                    "preferences_evolution": []
                }
                
                for row in cursor.fetchall():
                    feedback["recent_feedback"].append({
                        "type": row[0],
                        "text": row[1],
                        "rating": row[2],
                        "timestamp": row[3],
                        "context": json.loads(row[4]) if row[4] else {}
                    })
                
                # Get preferences evolution
                cursor.execute("""
                    SELECT preference_type, old_value, new_value, changed_at, reason
                    FROM user_preferences_evolution
                    WHERE user_id = ?
                    ORDER BY changed_at DESC
                    LIMIT 10
                """, (user_id,))
                
                for row in cursor.fetchall():
                    feedback["preferences_evolution"].append({
                        "type": row[0],
                        "old_value": row[1],
                        "new_value": row[2],
                        "changed_at": row[3],
                        "reason": row[4]
                    })
                
                return feedback
                
        except Exception as e:
            logger.error(f"Error getting user feedback: {e}")
            return {}
    
    def store_progress_milestone(self, user_id: str, milestone_type: str, description: str, context: Dict[str, Any] = None):
        """Store a progress milestone"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO progress_milestones (user_id, milestone_type, description, context)
                    VALUES (?, ?, ?, ?)
                """, (user_id, milestone_type, description, json.dumps(context) if context else None))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing progress milestone: {e}")
    
    def get_progress_milestones(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user progress milestones"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT milestone_type, description, achieved_at, context
                    FROM progress_milestones
                    WHERE user_id = ?
                    ORDER BY achieved_at DESC
                    LIMIT ?
                """, (user_id, limit))
                
                milestones = []
                for row in cursor.fetchall():
                    milestones.append({
                        "type": row[0],
                        "description": row[1],
                        "achieved_at": row[2],
                        "context": json.loads(row[3]) if row[3] else {}
                    })
                
                return milestones
                
        except Exception as e:
            logger.error(f"Error getting progress milestones: {e}")
            return []
    
    def store_preference_change(self, user_id: str, preference_type: str, old_value: str, new_value: str, reason: str = None):
        """Store a change in user preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_preferences_evolution (user_id, preference_type, old_value, new_value, reason)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, preference_type, old_value, new_value, reason))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing preference change: {e}")
    
    def get_user_memory_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a comprehensive summary of user memory"""
        try:
            recent_conversations = self.get_recent_conversations(user_id, 5)
            user_feedback = self.get_user_feedback(user_id, 10)
            progress_milestones = self.get_progress_milestones(user_id, 10)
            
            # Analyze conversation patterns
            conversation_patterns = self._analyze_conversation_patterns(recent_conversations)
            
            # Analyze feedback patterns
            feedback_patterns = self._analyze_feedback_patterns(user_feedback)
            
            return {
                "recent_conversations": recent_conversations,
                "user_feedback": user_feedback,
                "progress_milestones": progress_milestones,
                "conversation_patterns": conversation_patterns,
                "feedback_patterns": feedback_patterns,
                "last_interaction": recent_conversations[0]["timestamp"] if recent_conversations else None
            }
            
        except Exception as e:
            logger.error(f"Error getting user memory summary: {e}")
            return {}
    
    def _analyze_conversation_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in conversation history"""
        if not conversations:
            return {}
        
        intents = [conv.get("intent") for conv in conversations if conv.get("intent")]
        common_intents = {}
        for intent in intents:
            common_intents[intent] = common_intents.get(intent, 0) + 1
        
        return {
            "common_intents": common_intents,
            "total_conversations": len(conversations),
            "recent_activity": len([c for c in conversations if c.get("timestamp")])
        }
    
    def _analyze_feedback_patterns(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in user feedback"""
        recent_feedback = feedback.get("recent_feedback", [])
        if not recent_feedback:
            return {}
        
        feedback_types = [f.get("type") for f in recent_feedback]
        common_types = {}
        for f_type in feedback_types:
            common_types[f_type] = common_types.get(f_type, 0) + 1
        
        avg_rating = sum(f.get("rating", 0) for f in recent_feedback if f.get("rating")) / len(recent_feedback) if recent_feedback else 0
        
        return {
            "common_feedback_types": common_types,
            "average_rating": avg_rating,
            "total_feedback": len(recent_feedback)
        } 