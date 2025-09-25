from abc import ABC, abstractmethod
from app.models.alert import Alert
from app.models.user import User


class NotificationChannel(ABC):
    """Abstract base class for all notification channels."""

    @abstractmethod
    def send(self, alert: Alert, user: User) -> None:
        """Send a notification to a user via this channel."""
        pass
