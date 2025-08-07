"""
SQLite User Repository - Persistent user data storage
"""
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from domain.repositories.user_repository import UserRepository
from domain.entities.user import User, UserProfile, UserSession, UserLevel, UserGoal
from shared.logging import get_logger

logger = get_logger(__name__)


class SQLiteUserRepository(UserRepository):
    """SQLite-based user repository for persistent storage"""
    
    def __init__(self, db_path: str = "data/users/coach_data.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        age INTEGER,
                        goals TEXT,  -- JSON array of goals
                        level TEXT DEFAULT 'beginner',
                        training_preferences TEXT,  -- JSON object
                        injury_history TEXT,  -- JSON object
                        nutrition_preferences TEXT,  -- JSON object
                        recovery_needs TEXT,  -- JSON object
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # User sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        session_date DATE NOT NULL,
                        duration INTEGER,  -- minutes
                        intensity TEXT,
                        exercises TEXT,  -- JSON array
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # User feedback table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        feedback_text TEXT NOT NULL,
                        rating INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # Weekly plans table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weekly_plans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        plan_data TEXT NOT NULL,  -- JSON object
                        week_start DATE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON user_sessions(session_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON user_feedback(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_plans_user_id ON weekly_plans(user_id)")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error initializing user repository database: {e}")
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, name, age, goals, level, training_preferences, 
                           injury_history, nutrition_preferences, recovery_needs
                    FROM users WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    user_id, name, age, goals_json, level, training_prefs_json, \
                    injury_history_json, nutrition_prefs_json, recovery_needs_json = row
                    
                    # Parse JSON fields
                    goals = json.loads(goals_json) if goals_json else []
                    training_preferences = json.loads(training_prefs_json) if training_prefs_json else {}
                    injury_history = json.loads(injury_history_json) if injury_history_json else {}
                    nutrition_preferences = json.loads(nutrition_prefs_json) if nutrition_prefs_json else {}
                    recovery_needs = json.loads(recovery_needs_json) if recovery_needs_json else {}
                    
                    # Convert string goals to UserGoal enums
                    goal_enums = []
                    for goal_str in goals:
                        try:
                            goal_enums.append(UserGoal(goal_str))
                        except ValueError:
                            # If goal doesn't exist in enum, skip it
                            pass
                    
                    # Convert level string to UserLevel enum
                    try:
                        level_enum = UserLevel(level)
                    except ValueError:
                        level_enum = UserLevel.BEGINNER
                    
                    profile = UserProfile(
                        name=name,
                        age=age,
                        goals=goal_enums,
                        level=level_enum,
                        training_preferences=training_preferences,
                        injury_history=injury_history,
                        nutrition_preferences=nutrition_preferences,
                        recovery_needs=recovery_needs
                    )
                    
                    return User(profile)
                    
                return None
                
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def add_user(self, user: User, user_id: str = None) -> bool:
        """Add a new user"""
        return self.save_user(user, user_id)
    
    def save_user(self, user: User, user_id: str = None) -> bool:
        """Save user to storage"""
        try:
            if not user_id:
                logger.error("User ID is required for saving user")
                return False
            
            profile = user.profile
            
            # Convert goals to JSON array of strings
            goals_json = json.dumps([goal.value for goal in profile.goals])
            
            # Convert other fields to JSON
            training_prefs_json = json.dumps(profile.training_preferences)
            injury_history_json = json.dumps(profile.injury_history)
            nutrition_prefs_json = json.dumps(profile.nutrition_preferences)
            recovery_needs_json = json.dumps(profile.recovery_needs)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, name, age, goals, level, training_preferences, 
                     injury_history, nutrition_preferences, recovery_needs, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    user_id, profile.name, profile.age, goals_json, 
                    profile.level.value, training_prefs_json, injury_history_json,
                    nutrition_prefs_json, recovery_needs_json
                ))
                conn.commit()
                
            logger.info(f"Saved user {user_id} to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user {user_id}: {e}")
            return False
    
    def update_user_profile(self, user_id: str, profile: UserProfile) -> bool:
        """Update user profile"""
        user = User(profile)
        return self.save_user(user, user_id)
    
    def add_user_session(self, user_id: str, session: UserSession) -> bool:
        """Add a new session for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_sessions 
                    (user_id, session_date, duration, intensity, exercises, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id, session.date, session.duration, session.intensity,
                    json.dumps(session.exercises), session.notes
                ))
                conn.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error adding session for user {user_id}: {e}")
            return False
    
    def get_user_sessions(self, user_id: str, days: int = 7) -> List[UserSession]:
        """Get user sessions from last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_date, duration, intensity, exercises, notes
                    FROM user_sessions 
                    WHERE user_id = ? AND session_date >= date('now', '-{} days')
                    ORDER BY session_date DESC
                """.format(days), (user_id,))
                
                sessions = []
                for row in cursor.fetchall():
                    session_date, duration, intensity, exercises_json, notes = row
                    exercises = json.loads(exercises_json) if exercises_json else []
                    
                    session = UserSession(
                        date=session_date,
                        duration=duration,
                        intensity=intensity,
                        exercises=exercises,
                        notes=notes
                    )
                    sessions.append(session)
                
                return sessions
                
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            return []
    
    def get_user_feedback(self, user_id: str, limit: int = 10) -> List[str]:
        """Get recent user feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT feedback_text FROM user_feedback 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting feedback for user {user_id}: {e}")
            return []
    
    def add_user_feedback(self, user_id: str, feedback: str) -> bool:
        """Add user feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_feedback (user_id, feedback_text)
                    VALUES (?, ?)
                """, (user_id, feedback))
                conn.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error adding feedback for user {user_id}: {e}")
            return False
    
    def get_weekly_plan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get current weekly plan for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT plan_data FROM weekly_plans 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
                
        except Exception as e:
            logger.error(f"Error getting weekly plan for user {user_id}: {e}")
            return None
    
    def save_weekly_plan(self, user_id: str, plan: Dict[str, Any]) -> bool:
        """Save weekly plan for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO weekly_plans (user_id, plan_data, week_start)
                    VALUES (?, ?, date('now', 'weekday 0'))
                """, (user_id, json.dumps(plan)))
                conn.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving weekly plan for user {user_id}: {e}")
            return False
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user training statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total sessions
                cursor.execute("""
                    SELECT COUNT(*) FROM user_sessions WHERE user_id = ?
                """, (user_id,))
                total_sessions = cursor.fetchone()[0]
                
                # Get average session duration
                cursor.execute("""
                    SELECT AVG(duration) FROM user_sessions WHERE user_id = ?
                """, (user_id,))
                avg_duration = cursor.fetchone()[0] or 0
                
                # Get most common intensity
                cursor.execute("""
                    SELECT intensity, COUNT(*) as count 
                    FROM user_sessions 
                    WHERE user_id = ? 
                    GROUP BY intensity 
                    ORDER BY count DESC 
                    LIMIT 1
                """, (user_id,))
                intensity_row = cursor.fetchone()
                most_common_intensity = intensity_row[0] if intensity_row else "Unknown"
                
                return {
                    "total_sessions": total_sessions,
                    "avg_duration": avg_duration,
                    "most_common_intensity": most_common_intensity
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics for user {user_id}: {e}")
            return {} 