from typing import List
from datetime import datetime, timedelta, date
from app.models.alert import Alert
from app.models.user import User
from app.models.user_alert_pref import UserAlertPreference
from app.channels.base import NotificationChannel

class NotificationService:
    """Service that fetches alerts, checks user prefs, and dispatches via channels."""

    REMINDER_INTERVAL_HOURS = 2  # default reminder frequency

    def __init__(self, delivery_repo, pref_repo, alert_repo, user_repo, channels: List[NotificationChannel] = None):
        self.delivery_repo = delivery_repo
        self.pref_repo = pref_repo
        self.alert_repo = alert_repo
        self.user_repo = user_repo
        self.channels = channels or self._get_default_channels()

    def trigger_reminders(self) -> dict:
        alerts = self.alert_repo.get_active_alerts()
        users = self.user_repo.get_all_users()
        
        for alert in alerts:
            for user in self.get_users_for_alert(alert, users):
                if self.should_deliver(alert, user):
                    self.deliver(alert, user)
        
        return {"message": "Reminders triggered successfully"}

    def should_deliver(self, alert: Alert, user: User) -> bool:
        """Check if alert should be delivered based on snooze, read/unread, and reminder frequency."""
        pref: UserAlertPreference = self.pref_repo.get_user_alert_preference(user.id, alert.id)

        # 1. Check if user has snoozed today
        if pref and pref.snoozed_date == date.today():
            return False

        # 2. Check reminder interval
        last_delivered = pref.last_delivered_at if pref else None
        if last_delivered:
            elapsed = datetime.utcnow() - last_delivered
            if elapsed < timedelta(hours=alert.reminder_freq_minutes / 60):
                return False  # Not enough time passed

        return True

    def deliver(self, alert: Alert, user: User) -> dict:
        """Send the alert via all enabled channels and update delivery log & preferences."""
        for channel in self.channels:
            channel.send(alert, user)

        # Log delivery
        self.delivery_repo.create_delivery(alert.id, user.id)

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
        
        return {"message": f"Alert {alert.id} delivered to user {user.id}"}

    def get_users_for_alert(self, alert: Alert, users: List[User]) -> List[User]:
        """Determine which users should receive the alert based on visibility."""
        if not alert.visibility:
            return users  # fallback: all users

        org_visible = alert.visibility.get("org", True)
        team_ids = alert.visibility.get("teams", [])
        user_ids = alert.visibility.get("users", [])

        filtered = []
        for user in users:
            if org_visible:
                filtered.append(user)
            elif user.team_id and user.team_id in team_ids:
                filtered.append(user)
            elif user.id in user_ids:
                filtered.append(user)
        return filtered

    def _get_default_channels(self):
        """Default channel (MVP: in-app)."""
        from app.channels.in_app import InAppChannel
        return [InAppChannel()]
