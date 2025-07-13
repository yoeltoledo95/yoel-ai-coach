import unittest
import tempfile
import os
import json
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import uuid
import importlib

# Import the modules to test
import sys
sys.path.append('..')
import coach_core.data
import coach_core.database

from coach_core.database import CoachDatabase

class TestDataModule(unittest.TestCase):
    def setUp(self):
        """Set up isolated test environment."""
        # Create temporary directory and test database
        self.temp_dir = tempfile.mkdtemp()
        unique_db = f"test_coach_{uuid.uuid4().hex}.db"
        self.test_db_path = os.path.join(self.temp_dir, unique_db)
        
        # Create test database instance
        self.test_db = CoachDatabase(self.test_db_path)
        
        # Create empty test JSON files
        self.test_profile_path = os.path.join(self.temp_dir, "test_profile.json")
        self.test_logs_path = os.path.join(self.temp_dir, "test_logs.json")
        
        # Create empty JSON files
        with open(self.test_profile_path, 'w') as f:
            json.dump({}, f)
        with open(self.test_logs_path, 'w') as f:
            json.dump([], f)
        
        # Import functions from coach_core.data
        from coach_core.data import (
            load_profile, save_profile, load_logs, save_logs, 
            add_log, get_log_by_date, get_recent_logs, get_stats
        )
        
        # Store functions for use in tests
        self.load_profile = load_profile
        self.save_profile = save_profile
        self.load_logs = load_logs
        self.save_logs = save_logs
        self.add_log = add_log
        self.get_log_by_date = get_log_by_date
        self.get_recent_logs = get_recent_logs
        self.get_stats = get_stats
    
    def clear_test_db(self):
        """Clear all data from test database."""
        print(f"🔍 Clearing test database: {self.test_db_path}")
        self.test_db.save_profile({})
        with sqlite3.connect(self.test_db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM daily_logs')
            conn.commit()
        
        # Clear JSON files too
        with open(self.test_profile_path, 'w') as f:
            json.dump({}, f)
        with open(self.test_logs_path, 'w') as f:
            json.dump([], f)
        
        # Debug: check what's left in the database
        with sqlite3.connect(self.test_db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM daily_logs')
            log_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM profile')
            profile_count = cursor.fetchone()[0]
            print(f"🔍 After clearing - Logs: {log_count}, Profile entries: {profile_count}")
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up test files
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists(self.test_profile_path):
            os.remove(self.test_profile_path)
        if os.path.exists(self.test_logs_path):
            os.remove(self.test_logs_path)
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass
    
    def test_load_profile_empty(self):
        """Test loading empty profile."""
        self.clear_test_db()
        profile = self.load_profile(path=self.test_profile_path, db=self.test_db)
        self.assertEqual(profile, {})
    
    def test_load_logs_empty(self):
        """Test loading empty logs."""
        self.clear_test_db()
        print(f"🔍 Test database path: {self.test_db.db_path}")
        logs = self.load_logs(path=self.test_logs_path, db=self.test_db)
        print(f"🔍 Loaded {len(logs)} logs from test database")
        print(f"🔍 First log if any: {logs[0] if logs else 'None'}")
        self.assertEqual(logs, [])
    
    def test_save_and_load_logs(self):
        """Test saving and loading logs."""
        self.clear_test_db()
        
        test_logs = [
            {
                "date": "2025-01-13",
                "timestamp": "2025-01-13T10:00:00",
                "mood": "7",
                "energy": "8",
                "sleep_hours": "7.5",
                "sleep_quality": "8",
                "stress_level": "3",
                "soreness": "none",
                "training_done": "Push Day - Moderate",
                "training_quality": "8",
                "nutrition": "Test meal",
                "hydration": "7",
                "notes": "Test log",
                "recovery_score": "8",
                "training_volume": "moderate",
                "split": "Push"
            },
            {
                "date": "2025-01-14",
                "timestamp": "2025-01-14T10:00:00",
                "mood": "8",
                "energy": "9",
                "sleep_hours": "8.0",
                "sleep_quality": "9",
                "stress_level": "2",
                "soreness": "chest, shoulders",
                "training_done": "Pull Day - Heavy",
                "training_quality": "9",
                "nutrition": "Another test meal",
                "hydration": "8",
                "notes": "Second test log",
                "recovery_score": "9",
                "training_volume": "heavy",
                "split": "Pull"
            }
        ]
        
        self.save_logs(test_logs, path=self.test_logs_path, db=self.test_db)
        loaded_logs = self.load_logs(path=self.test_logs_path, db=self.test_db)
        
        self.assertEqual(len(loaded_logs), 2)
        self.assertEqual(loaded_logs[0]["date"], "2025-01-14")
        self.assertEqual(loaded_logs[1]["date"], "2025-01-13")
        self.assertEqual(loaded_logs[0]["mood"], "8")
        self.assertEqual(loaded_logs[1]["training_done"], "Push Day - Moderate")
    
    def test_get_stats(self):
        """Test getting statistics."""
        self.clear_test_db()
        
        # Use current dates for realistic testing
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        test_logs = [
            {"date": today, "timestamp": f"{today}T10:00:00", "mood": "7"},
            {"date": yesterday, "timestamp": f"{yesterday}T10:00:00", "mood": "8"},
        ]
        
        for log in test_logs:
            self.add_log(log, db=self.test_db)
        
        stats = self.get_stats(db=self.test_db)
        
        self.assertIn('total_logs', stats)
        self.assertIn('date_range', stats)
        self.assertIn('recent_logs_7_days', stats)
        self.assertIn('min', stats['date_range'])
        self.assertIn('max', stats['date_range'])
        self.assertEqual(stats['total_logs'], 2)
        self.assertEqual(stats['recent_logs_7_days'], 2)

if __name__ == '__main__':
    unittest.main() 