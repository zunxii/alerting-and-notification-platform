from app.channels.base import NotificationChannel
from app.models.alert import Alert
from app.models.user import User


class SMSChannel(NotificationChannel):
    """SMS notification delivery."""

    def send(self, alert: Alert, user: User) -> None:
        print(f"[SMS] Alert '{alert.title}' would be SMSed to {user.name}")
