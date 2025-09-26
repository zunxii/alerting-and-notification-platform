from typing import Dict, Any
from app.channels.base import NotificationChannel
from app.models.alert import Alert
from app.models.user import User

class InAppChannel(NotificationChannel):
    """In-App notification channel implementation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        super().__init__()
    
    def send(self, alert: Alert, user: User) -> Dict[str, Any]:
        """Send in-app notification."""
        # In MVP, this is just logging/simulation
        # In production, this would push to real-time notification system
        
        notification_data = {
            "channel": "in_app",
            "alert_id": alert.id,
            "user_id": user.id,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity,
            "timestamp": alert.created_at.isoformat(),
            "status": "delivered"
        }
        
        # Simulate delivery
        print(f"[IN-APP] Alert '{alert.title}' sent to user {user.name}")
        
        return notification_data

    def validate_config(self) -> bool:
        """Validate channel configuration."""
        # In-App channel doesn't need special config for MVP
        return True