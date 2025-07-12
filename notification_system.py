import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from collections import defaultdict
import statistics

class NotificationSystem:
    def __init__(self, logs_file="daily_logs.json", profile_file="yoel_profile.json"):
        self.logs_file = logs_file
        self.profile_file = profile_file
        self.load_data()
    
    def load_data(self):
        """Load logs and profile data"""
        # Load logs
        if os.path.exists(self.logs_file):
            with open(self.logs_file, "r") as f:
                try:
                    self.logs = json.load(f)
                except json.JSONDecodeError:
                    self.logs = []
        else:
            self.logs = []
        
        # Load profile
        if os.path.exists(self.profile_file):
            with open(self.profile_file, "r") as f:
                try:
                    self.profile = json.load(f)
                except json.JSONDecodeError:
                    self.profile = {}
        else:
            self.profile = {}
    
    def check_daily_reminder(self):
        """Check if daily reminder should be sent"""
        today = datetime.now().strftime("%Y-%m-%d")
        logged_today = any(log.get("date") == today for log in self.logs)
        
        if not logged_today:
            return {
                "should_send": True,
                "type": "daily_reminder",
                "message": "💪 Time to log your daily progress! How are you feeling today?",
                "priority": "high"
            }
        return {"should_send": False}
    
    def generate_weekly_summary(self):
        """Generate weekly summary if it's Sunday"""
        today = datetime.now()
        if today.weekday() == 6:  # Sunday
            week_logs = self.logs[-7:] if len(self.logs) >= 7 else self.logs
            
            if not week_logs:
                return {"should_send": False}
            
            # Calculate weekly stats
            energies = [float(log.get("energy", 5)) for log in week_logs if log.get("energy")]
            recovery_scores = [float(log.get("recovery_score", 5)) for log in week_logs if log.get("recovery_score")]
            training_days = sum(1 for log in week_logs if log.get("training_done") and log.get("training_done").lower() != "none")
            
            avg_energy = statistics.mean(energies) if energies else 5
            avg_recovery = statistics.mean(recovery_scores) if recovery_scores else 5
            
            # Generate insights
            insights = []
            if avg_energy < 6:
                insights.append("⚠️ Your energy has been low this week. Consider more rest or lighter training.")
            elif avg_energy > 8:
                insights.append("⚡ Great energy levels! You're in a good rhythm.")
            
            if avg_recovery < 6:
                insights.append("🔄 Recovery scores are low. Focus on sleep and recovery days.")
            elif avg_recovery > 8:
                insights.append("✅ Excellent recovery! You're managing your training load well.")
            
            if training_days >= 5:
                insights.append("🏋️ You trained frequently this week. Great consistency!")
            elif training_days <= 2:
                insights.append("💪 You could increase training frequency if you're feeling good.")
            
            # Training split analysis
            split_counts = {"Push": 0, "Pull": 0, "Legs": 0, "Recovery": 0}
            for log in week_logs:
                split = log.get("split", "")
                if split in split_counts:
                    split_counts[split] += 1
            
            # Check for imbalances
            if split_counts["Push"] > split_counts["Pull"] + 1:
                insights.append("💪 You've been doing more push work. Consider adding more pull exercises for balance.")
            elif split_counts["Pull"] > split_counts["Push"] + 1:
                insights.append("💪 You've been doing more pull work. Time for some push exercises!")
            
            if split_counts["Legs"] < 1:
                insights.append("🦵 You haven't trained legs this week. Consider adding leg work for your goals.")
            
            message = f"""
📊 Weekly Summary - {today.strftime('%B %d, %Y')}

📈 Stats:
• Average Energy: {avg_energy:.1f}/10
• Average Recovery: {avg_recovery:.1f}/10
• Training Days: {training_days}/7

💡 Insights:
{chr(10).join(insights) if insights else "Keep up the great work!"}

🎯 Next Week Goals:
• Focus on your handstand and pancake progressions
• Maintain good sleep and recovery
• Stay consistent with your training split

Keep pushing towards your goals! 💪
            """.strip()
            
            return {
                "should_send": True,
                "type": "weekly_summary",
                "message": message,
                "priority": "medium"
            }
        
        return {"should_send": False}
    
    def check_milestone_reminder(self):
        """Check for training milestones and achievements"""
        if len(self.logs) < 7:
            return {"should_send": False}
        
        recent_logs = self.logs[-7:]
        training_days = sum(1 for log in recent_logs if log.get("training_done") and log.get("training_done").lower() != "none")
        
        if training_days >= 5:
            return {
                "should_send": True,
                "type": "milestone",
                "message": "🎉 Achievement unlocked: 5+ training days this week! You're building great habits!",
                "priority": "medium"
            }
        
        return {"should_send": False}
    
    def check_recovery_alert(self):
        """Check if recovery alert should be sent"""
        if len(self.logs) < 3:
            return {"should_send": False}
        
        recent_logs = self.logs[-3:]
        recovery_scores = [float(log.get("recovery_score", 5)) for log in recent_logs if log.get("recovery_score")]
        
        if recovery_scores and statistics.mean(recovery_scores) < 5:
            return {
                "should_send": True,
                "type": "recovery_alert",
                "message": "⚠️ Your recovery scores have been low. Consider a rest day or light mobility work today.",
                "priority": "high"
            }
        
        return {"should_send": False}
    
    def get_all_notifications(self):
        """Get all pending notifications"""
        notifications = []
        
        # Check different notification types
        daily = self.check_daily_reminder()
        if daily["should_send"]:
            notifications.append(daily)
        
        weekly = self.generate_weekly_summary()
        if weekly["should_send"]:
            notifications.append(weekly)
        
        milestone = self.check_milestone_reminder()
        if milestone["should_send"]:
            notifications.append(milestone)
        
        recovery = self.check_recovery_alert()
        if recovery["should_send"]:
            notifications.append(recovery)
        
        return notifications
    
    def send_email_notification(self, to_email, subject, message):
        """Send email notification (requires email configuration)"""
        # This would require email server configuration
        # For now, just print the notification
        print(f"📧 Email Notification to {to_email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print("---")
    
    def send_push_notification(self, message, priority="medium"):
        """Send push notification (would integrate with mobile push services)"""
        # This would integrate with services like OneSignal, Firebase, etc.
        print(f"📱 Push Notification ({priority})")
        print(f"Message: {message}")
        print("---")
    
    def process_notifications(self):
        """Process and send all pending notifications"""
        notifications = self.get_all_notifications()
        
        for notification in notifications:
            message = notification["message"]
            priority = notification["priority"]
            
            # For now, just print notifications
            # In production, this would send actual notifications
            print(f"🔔 {notification['type'].replace('_', ' ').title()}")
            print(f"Priority: {priority}")
            print(f"Message: {message}")
            print("---")
            
            # Example of how to send actual notifications:
            # self.send_push_notification(message, priority)
            # self.send_email_notification("user@example.com", "AI Coach Update", message)

# Example usage
if __name__ == "__main__":
    notifier = NotificationSystem()
    notifier.process_notifications() 