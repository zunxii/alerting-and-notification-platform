from typing import List
from datetime import datetime, timedelta, date
from app.models.alert import Alert
from app.models.user import User
from app.models.user_alert_pref import UserAlertPreference
from app.channels.base import NotificationChannel

class NotificationService:
    """Service that fetches alerts, checks user prefs, and dispatches via channels."""

    DEFAULT_REMINDER_INTERVAL_HOURS = 2  # default reminder frequency

    def __init__(self, delivery_repo, pref_repo, alert_repo, user_repo, channels: List[NotificationChannel] = None):
        self.delivery_repo = delivery_repo
        self.pref_repo = pref_repo
        self.alert_repo = alert_repo
        self.user_repo = user_repo
        self.channels = channels or self._get_default_channels()

    def trigger_reminders(self) -> dict:
        """Trigger reminders for all active alerts and eligible users"""
        alerts = self.alert_repo.get_active_alerts()
        users = self.user_repo.get_all_users()
        
        delivered_count = 0
        skipped_count = 0
        
        for alert in alerts:
            eligible_users = self.get_users_for_alert(alert, users)
            for user in eligible_users:
                if self.should_deliver(alert, user):
                    self.deliver(alert, user)
                    delivered_count += 1
                else:
                    skipped_count += 1
        
        return {
            "message": "Reminders triggered successfully",
            "alerts_processed": len(alerts),
            "users_processed": len(users),
            "delivered": delivered_count,
            "skipped": skipped_count
        }

    def should_deliver(self, alert: Alert, user: User) -> bool:
        """Check if alert should be delivered based on snooze, read/unread, and reminder frequency."""
        pref: UserAlertPreference = self.pref_repo.get_user_alert_preference(user.id, alert.id)

        # 1. Check if user has snoozed today
        if pref and pref.snoozed_date == date.today():
            return False

        # 2. Check reminder interval
        last_delivered = pref.last_delivered_at if pref else None
        if last_delivered:
            # Get reminder frequency from alert (default to 2 hours)
            reminder_hours = getattr(alert, 'reminder_freq_minutes', 120) / 60
            elapsed = datetime.utcnow() - last_delivered
            if elapsed < timedelta(hours=reminder_hours):
                return False  # Not enough time passed

        return True

    def deliver(self, alert: Alert, user: User) -> dict:
        """Send the alert via all enabled channels and update delivery log & preferences."""
        delivery_results = []
        
        for channel in self.channels:
            try:
                result = channel.send(alert, user)
                delivery_results.append({
                    "channel": channel.__class__.__name__,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                delivery_results.append({
                    "channel": channel.__class__.__name__,
                    "success": False,
                    "error": str(e)
                })

        # Log delivery
        delivery_log = self.delivery_repo.create_delivery(alert.id, user.id)

        # Update user preference
        pref: UserAlertPreference = self.pref_repo.get_user_alert_preference(user.id, alert.id)
        if pref:
            pref.last_delivered_at = datetime.utcnow()
            self.pref_repo.update_preference(pref)
        else:
            self.pref_repo.create_preference(
                user_id=user.id,
                alert_id=alert.id,
                last_delivered_at=datetime.utcnow()
            )
        
        return {
            "message": f"Alert {alert.id} delivered to user {user.id}",
            "delivery_id": delivery_log.id,
            "channels": delivery_results,
            "delivered_at": datetime.utcnow()
        }

    def get_users_for_alert(self, alert: Alert, users: List[User]) -> List[User]:
        """Determine which users should receive the alert based on visibility."""
        if not alert.visibility:
            return users  # fallback: all users (org-wide)

        # Default to org-wide if no specific visibility is set
        org_visible = alert.visibility.get("org", True)
        team_ids = alert.visibility.get("teams", [])
        user_ids = alert.visibility.get("users", [])

        filtered = []
        for user in users:
            # Check if user should receive this alert
            should_receive = False
            
            # Org-wide visibility
            if org_visible:
                should_receive = True
            
            # Team-specific visibility
            elif user.team_id and str(user.team_id) in [str(tid) for tid in team_ids]:
                should_receive = True
            
            # User-specific visibility
            elif str(user.id) in [str(uid) for uid in user_ids]:
                should_receive = True
            
            if should_receive:
                filtered.append(user)
                
        return filtered

    def reset_daily_snoozes(self) -> dict:
        """Reset snoozes for a new day - should be called daily"""
        # This would typically be called by a scheduler
        # For now, we'll implement this as a manual trigger
        # In production, this should run automatically at midnight
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Get all preferences that were snoozed yesterday
        all_prefs = self.pref_repo.get_all_preferences_by_snooze_date(yesterday)
        
        reset_count = 0
        for pref in all_prefs:
            if pref.snoozed_date == yesterday:
                pref.snoozed_date = None  # Reset snooze
                self.pref_repo.update_preference(pref)
                reset_count += 1
        
        return {
            "message": "Daily snoozes reset",
            "reset_count": reset_count,
            "reset_date": today
        }

    def _get_default_channels(self):
        """Default channel (MVP: in-app)."""
        from app.channels.in_app import InAppChannel
        return [InAppChannel()]