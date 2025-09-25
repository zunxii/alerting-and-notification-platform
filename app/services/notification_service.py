from app.repositories.delivery_repo import DeliveryRepository
from app.repositories.preference_repo import UserPreferenceRepository

class NotificationService:
    def __init__(self, delivery_repo: DeliveryRepository, pref_repo: UserPreferenceRepository):
        self.delivery_repo = delivery_repo
        self.pref_repo = pref_repo

    def send_notification(self, alert, user, channel="in_app"):
        self.delivery_repo.log_delivery(alert.id, user.id, channel)
        self.pref_repo.update_last_delivered(user.id, alert.id)
        print(f"Sent {channel} notification to {user.name}: {alert.title}")

    def snooze_alert(self, user_id, alert_id):
        return self.pref_repo.snooze_alert_today(user_id, alert_id)

    def mark_as_read(self, delivery_id):
        return self.delivery_repo.mark_read(delivery_id)
