import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from ...config.settings import config
DATABASE_PATH = config.database.sqlite_path if hasattr(config, 'database') else "coach_data.db"

class CoachDatabase:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create profile table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profile (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create daily_logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    mood TEXT,
                    energy TEXT,
                    sleep_hours TEXT,
                    sleep_quality TEXT,
                    stress_level TEXT,
                    soreness TEXT,
                    training_done TEXT,
                    training_quality TEXT,
                    nutrition TEXT,
                    hydration TEXT,
                    notes TEXT,
                    recovery_score TEXT,
                    training_volume TEXT,
                    split TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create feedback table for tracking user feedback on AI workouts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workout_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    workout_date TEXT NOT NULL,
                    feedback_type TEXT NOT NULL, -- 'liked', 'disliked', 'completed', 'partial', 'skipped'
                    feedback_text TEXT,
                    workout_summary TEXT,
                    exercises_completed TEXT, -- JSON array of completed exercises
                    exercises_skipped TEXT, -- JSON array of skipped exercises
                    difficulty_rating INTEGER, -- 1-10 scale
                    enjoyment_rating INTEGER, -- 1-10 scale
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create exercise progression tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exercise_progressions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    exercise_name TEXT NOT NULL,
                    current_variation TEXT NOT NULL,
                    progression_level INTEGER DEFAULT 0, -- 0 = regression, 1 = base, 2+ = progressions
                    total_sessions INTEGER DEFAULT 0,
                    last_session_date TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, exercise_name)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_date ON daily_logs(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_timestamp ON daily_logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_date_timestamp ON daily_logs(date, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_energy ON daily_logs(energy)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_training_done ON daily_logs(training_done)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_recovery_score ON daily_logs(recovery_score)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_split ON daily_logs(split)')
            
            # Create indexes for feedback and progression tables
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_workout_feedback_user_date ON workout_feedback(user_id, workout_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_exercise_progressions_user_exercise ON exercise_progressions(user_id, exercise_name)')
            
            conn.commit()
    
    def load_profile(self) -> Dict[str, Any]:
        """Load user profile from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT key, value FROM profile')
            rows = cursor.fetchall()
            
            profile = {}
            for key, value in rows:
                try:
                    # Try to parse JSON values
                    profile[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Fall back to string values
                    profile[key] = value
            
            return profile
    
    def save_profile(self, profile: Dict[str, Any]) -> None:
        """Save user profile to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clear existing profile
            cursor.execute('DELETE FROM profile')
            
            # Insert new profile data
            for key, value in profile.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                cursor.execute(
                    'INSERT OR REPLACE INTO profile (key, value, updated_at) VALUES (?, ?, ?)',
                    (key, str(value), datetime.now().isoformat())
                )
            
            conn.commit()
    
    def load_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load daily logs from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            query = 'SELECT * FROM daily_logs ORDER BY date DESC'
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                log = dict(row)
                # Convert string values back to appropriate types
                if log.get('sleep_hours'):
                    try:
                        log['sleep_hours'] = float(log['sleep_hours'])
                    except (ValueError, TypeError):
                        pass
                logs.append(log)
            
            return logs
    
    def save_logs(self, logs: List[Dict[str, Any]]) -> None:
        """Save daily logs to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for log in logs:
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_logs 
                    (date, timestamp, mood, energy, sleep_hours, sleep_quality, 
                     stress_level, soreness, training_done, training_quality, 
                     nutrition, hydration, notes, recovery_score, training_volume, 
                     split, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    log.get('date'),
                    log.get('timestamp'),
                    log.get('mood'),
                    log.get('energy'),
                    log.get('sleep_hours'),
                    log.get('sleep_quality'),
                    log.get('stress_level'),
                    log.get('soreness'),
                    log.get('training_done'),
                    log.get('training_quality'),
                    log.get('nutrition'),
                    log.get('hydration'),
                    log.get('notes'),
                    log.get('recovery_score'),
                    log.get('training_volume'),
                    log.get('split'),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
    
    def add_log(self, log: Dict[str, Any]) -> None:
        """Add a single log entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO daily_logs 
                (date, timestamp, mood, energy, sleep_hours, sleep_quality, 
                 stress_level, soreness, training_done, training_quality, 
                 nutrition, hydration, notes, recovery_score, training_volume, 
                 split, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log.get('date'),
                log.get('timestamp'),
                log.get('mood'),
                log.get('energy'),
                log.get('sleep_hours'),
                log.get('sleep_quality'),
                log.get('stress_level'),
                log.get('soreness'),
                log.get('training_done'),
                log.get('training_quality'),
                log.get('nutrition'),
                log.get('hydration'),
                log.get('notes'),
                log.get('recovery_score'),
                log.get('training_volume'),
                log.get('split'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def get_log_by_date(self, date: str) -> Optional[Dict[str, Any]]:
        """Get log entry for specific date."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM daily_logs WHERE date = ?', (date,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def delete_log(self, date: str) -> bool:
        """Delete log entry for specific date."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM daily_logs WHERE date = ?', (date,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_recent_logs(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get logs from the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM daily_logs 
                WHERE date >= date('now', '-{} days')
                ORDER BY date DESC
            '''.format(days))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get total logs
            cursor.execute('SELECT COUNT(*) FROM daily_logs')
            total_logs = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute('SELECT MIN(date), MAX(date) FROM daily_logs')
            min_date, max_date = cursor.fetchone()
            
            # Get recent activity
            cursor.execute('''
                SELECT COUNT(*) FROM daily_logs 
                WHERE date >= date('now', '-7 days')
            ''')
            recent_logs = cursor.fetchone()[0]
            
            return {
                "total_logs": total_logs,
                "date_range": {"min": min_date, "max": max_date},
                "recent_activity": recent_logs
            }
    
    def save_workout_feedback(
        self, 
        user_id: str, 
        workout_date: str, 
        feedback_type: str, 
        feedback_text: str = None,
        workout_summary: str = None,
        exercises_completed: List[str] = None,
        exercises_skipped: List[str] = None,
        difficulty_rating: int = None,
        enjoyment_rating: int = None
    ) -> bool:
        """Save workout feedback from user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO workout_feedback 
                    (user_id, workout_date, feedback_type, feedback_text, workout_summary, 
                     exercises_completed, exercises_skipped, difficulty_rating, enjoyment_rating)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, workout_date, feedback_type, feedback_text, workout_summary,
                    json.dumps(exercises_completed) if exercises_completed else None,
                    json.dumps(exercises_skipped) if exercises_skipped else None,
                    difficulty_rating, enjoyment_rating
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving workout feedback: {e}")
            return False
    
    def get_workout_feedback(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workout feedback for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM workout_feedback 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, limit))
                
                rows = cursor.fetchall()
                feedback_list = []
                
                for row in rows:
                    feedback = dict(row)
                    # Parse JSON fields
                    if feedback['exercises_completed']:
                        feedback['exercises_completed'] = json.loads(feedback['exercises_completed'])
                    if feedback['exercises_skipped']:
                        feedback['exercises_skipped'] = json.loads(feedback['exercises_skipped'])
                    feedback_list.append(feedback)
                
                return feedback_list
                
        except Exception as e:
            print(f"Error getting workout feedback: {e}")
            return []
    
    def update_exercise_progression(
        self, 
        user_id: str, 
        exercise_name: str, 
        current_variation: str, 
        progression_level: int = 1,
        notes: str = None
    ) -> bool:
        """Update exercise progression for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO exercise_progressions 
                    (user_id, exercise_name, current_variation, progression_level, notes, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, exercise_name, current_variation, progression_level, notes, datetime.now().isoformat()))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error updating exercise progression: {e}")
            return False
    
    def get_exercise_progression(self, user_id: str, exercise_name: str) -> Optional[Dict[str, Any]]:
        """Get current exercise progression for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM exercise_progressions 
                    WHERE user_id = ? AND exercise_name = ?
                ''', (user_id, exercise_name))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            print(f"Error getting exercise progression: {e}")
            return None
    
    def get_all_exercise_progressions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all exercise progressions for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM exercise_progressions 
                    WHERE user_id = ? 
                    ORDER BY updated_at DESC
                ''', (user_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"Error getting exercise progressions: {e}")
            return []
    
    def increment_exercise_sessions(self, user_id: str, exercise_name: str) -> bool:
        """Increment session count for exercise"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE exercise_progressions 
                    SET total_sessions = total_sessions + 1, 
                        last_session_date = ?, 
                        updated_at = ?
                    WHERE user_id = ? AND exercise_name = ?
                ''', (datetime.now().strftime('%Y-%m-%d'), datetime.now().isoformat(), user_id, exercise_name))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error incrementing exercise sessions: {e}")
            return False
    
    def migrate_from_json(self, profile_path: str = "yoel_profile.json", logs_path: str = "daily_logs.json"):
        """Migrate existing JSON data to SQLite database."""
        # Migrate profile
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    profile = json.load(f)
                self.save_profile(profile)
                print(f"✅ Migrated profile from {profile_path}")
            except Exception as e:
                print(f"⚠️ Failed to migrate profile: {e}")
        
        # Migrate logs
        if os.path.exists(logs_path):
            try:
                with open(logs_path, 'r') as f:
                    logs = json.load(f)
                self.save_logs(logs)
                print(f"✅ Migrated {len(logs)} logs from {logs_path}")
            except Exception as e:
                print(f"⚠️ Failed to migrate logs: {e}") 