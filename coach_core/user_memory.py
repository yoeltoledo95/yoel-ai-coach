"""
User Memory Database
Stores and manages all extracted information from user conversations
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class UserMemoryDB:
    """SQLite database for storing user conversation data and extracted information"""
    
    def __init__(self, db_path: str = "user_memory.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path, timeout=20.0) as conn:
            cursor = conn.cursor()
            
            # Main user interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    raw_message TEXT NOT NULL,
                    ai_response TEXT,
                    goals TEXT,
                    achievements TEXT,
                    struggles TEXT,
                    injuries TEXT,
                    weekly_reflection TEXT,
                    preferences TEXT,
                    feedback TEXT,
                    session_log TEXT,
                    questions TEXT,
                    mood TEXT,
                    intentions TEXT,
                    lifestyle TEXT,
                    milestones TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User profiles table for persistent user data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    first_seen TEXT NOT NULL,
                    last_active TEXT NOT NULL,
                    total_interactions INTEGER DEFAULT 0,
                    current_goals TEXT,
                    known_injuries TEXT,
                    preferences TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Weekly summaries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weekly_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    week_start TEXT NOT NULL,
                    week_end TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    training_focus TEXT,
                    mood_trends TEXT,
                    achievements TEXT,
                    challenges TEXT,
                    next_week_plan TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("✅ User memory database initialized")
    
    def store_interaction(self, user_id: str, raw_message: str, ai_response: str, 
                         extracted_info: Dict[str, Any]) -> bool:
        """Store a complete user interaction with extracted information"""
        try:
            with sqlite3.connect(self.db_path, timeout=20.0) as conn:
                cursor = conn.cursor()
                
                # Store the interaction
                cursor.execute("""
                    INSERT INTO user_interactions (
                        user_id, timestamp, raw_message, ai_response,
                        goals, achievements, struggles, injuries, weekly_reflection,
                        preferences, feedback, session_log, questions, mood,
                        intentions, lifestyle, milestones
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    datetime.now().isoformat(),
                    raw_message,
                    ai_response,
                    extracted_info.get('goals'),
                    extracted_info.get('achievements'),
                    extracted_info.get('struggles'),
                    extracted_info.get('injuries'),
                    extracted_info.get('weekly_reflection'),
                    extracted_info.get('preferences'),
                    extracted_info.get('feedback'),
                    extracted_info.get('session_log'),
                    extracted_info.get('questions'),
                    extracted_info.get('mood'),
                    extracted_info.get('intentions'),
                    extracted_info.get('lifestyle'),
                    extracted_info.get('milestones')
                ))
                
                # Update or create user profile in the same transaction
                cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = ?", (user_id,))
                user_exists = cursor.fetchone()
                
                if user_exists:
                    # Update existing user
                    updates = []
                    params = []
                    
                    if extracted_info.get('goals'):
                        updates.append("current_goals = ?")
                        params.append(extracted_info['goals'])
                    
                    if extracted_info.get('injuries'):
                        updates.append("known_injuries = ?")
                        params.append(extracted_info['injuries'])
                    
                    if extracted_info.get('preferences'):
                        updates.append("preferences = ?")
                        params.append(extracted_info['preferences'])
                    
                    if updates:
                        params.extend([datetime.now().isoformat(), user_id])
                        cursor.execute(f"""
                            UPDATE user_profiles 
                            SET {', '.join(updates)}, updated_at = ?
                            WHERE user_id = ?
                        """, params)
                
                else:
                    # Create new user
                    cursor.execute("""
                        INSERT INTO user_profiles (
                            user_id, first_seen, last_active, current_goals, 
                            known_injuries, preferences
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        extracted_info.get('goals'),
                        extracted_info.get('injuries'),
                        extracted_info.get('preferences')
                    ))
                
                conn.commit()
                logger.info(f"✅ Stored interaction for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error storing interaction: {e}")
            return False
    
    def _update_user_profile(self, user_id: str, extracted_info: Dict[str, Any]):
        """Update user profile with latest extracted information - DEPRECATED"""
        # This method is now deprecated as profile updates are handled in store_interaction
        pass
    
    def get_user_recent_interactions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent interactions for a user"""
        try:
            with sqlite3.connect(self.db_path, timeout=20.0) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM user_interactions 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Error getting user interactions: {e}")
            return []
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            with sqlite3.connect(self.db_path, timeout=20.0) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"❌ Error getting user profile: {e}")
            return None
    
    def get_user_goals(self, user_id: str) -> List[str]:
        """Get all goals mentioned by user"""
        try:
            with sqlite3.connect(self.db_path, timeout=20.0) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT goals FROM user_interactions 
                    WHERE user_id = ? AND goals IS NOT NULL
                    ORDER BY timestamp DESC
                """, (user_id,))
                
                return [row[0] for row in cursor.fetchall() if row[0]]
                
        except Exception as e:
            logger.error(f"❌ Error getting user goals: {e}")
            return []
    
    def get_user_injuries(self, user_id: str) -> List[str]:
        """Get all injuries mentioned by user"""
        try:
            with sqlite3.connect(self.db_path, timeout=20.0) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT injuries FROM user_interactions 
                    WHERE user_id = ? AND injuries IS NOT NULL
                    ORDER BY timestamp DESC
                """, (user_id,))
                
                return [row[0] for row in cursor.fetchall() if row[0]]
                
        except Exception as e:
            logger.error(f"❌ Error getting user injuries: {e}")
            return []
    
    def get_weekly_interactions(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get interactions from the last N days"""
        try:
            with sqlite3.connect(self.db_path, timeout=20.0) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM user_interactions 
                    WHERE user_id = ? 
                    AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                """.format(days), (user_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Error getting weekly interactions: {e}")
            return []
    
    def store_weekly_summary(self, user_id: str, week_start: str, week_end: str, 
                           summary: str, training_focus: str = None, mood_trends: str = None,
                           achievements: str = None, challenges: str = None, 
                           next_week_plan: str = None) -> bool:
        """Store a weekly summary generated by AI"""
        try:
            with sqlite3.connect(self.db_path, timeout=20.0) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO weekly_summaries (
                        user_id, week_start, week_end, summary, training_focus,
                        mood_trends, achievements, challenges, next_week_plan
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, week_start, week_end, summary, training_focus,
                    mood_trends, achievements, challenges, next_week_plan
                ))
                
                conn.commit()
                logger.info(f"✅ Stored weekly summary for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error storing weekly summary: {e}")
            return False
    
    def get_latest_weekly_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent weekly summary for a user"""
        try:
            with sqlite3.connect(self.db_path, timeout=20.0) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM weekly_summaries 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (user_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"❌ Error getting weekly summary: {e}")
            return None

# Global instance
user_memory_db = UserMemoryDB() 