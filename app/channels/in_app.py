from app.channels.base import NotificationChannel
from app.models.alert import Alert
from app.models.user import User


class InAppChannel(NotificationChannel):
    """In-App notification delivery."""

    def send(self, alert: Alert, user: User) -> None:
        print(f"[In-App] Alert '{alert.title}' sent to user {user.name}")
