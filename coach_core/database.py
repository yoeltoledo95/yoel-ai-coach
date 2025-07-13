import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

DATABASE_PATH = "coach_data.db"

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
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_date ON daily_logs(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_timestamp ON daily_logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_date_timestamp ON daily_logs(date, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_energy ON daily_logs(energy)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_training_done ON daily_logs(training_done)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_recovery_score ON daily_logs(recovery_score)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_logs_split ON daily_logs(split)')
            
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
        """Get basic statistics about the data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total logs
            cursor.execute('SELECT COUNT(*) FROM daily_logs')
            total_logs = cursor.fetchone()[0]
            
            # Date range
            cursor.execute('SELECT MIN(date), MAX(date) FROM daily_logs')
            min_date, max_date = cursor.fetchone()
            
            # Recent activity
            cursor.execute('''
                SELECT COUNT(*) FROM daily_logs 
                WHERE date >= date('now', '-7 days')
            ''')
            recent_logs = cursor.fetchone()[0]
            
            return {
                'total_logs': total_logs,
                'date_range': {'min': min_date, 'max': max_date},
                'recent_logs_7_days': recent_logs
            }
    
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