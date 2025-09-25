from app.channels.base import NotificationChannel
from app.models.alert import Alert
from app.models.user import User


class EmailChannel(NotificationChannel):
    """Email notification delivery."""

    def send(self, alert: Alert, user: User) -> None:
        print(f"[Email] Alert '{alert.title}' would be emailed to {user.name}")
