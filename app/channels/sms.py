from typing import Dict, Any
from app.channels.base import NotificationChannel
from app.models.alert import Alert
from app.models.user import User

class SMSChannel(NotificationChannel):
    """SMS notification channel implementation (future scope)."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_key = self.config.get("api_key")
        self.api_secret = self.config.get("api_secret")
        self.from_number = self.config.get("from_number", "+1234567890")
        super().__init__()
    
    def send(self, alert: Alert, user: User) -> Dict[str, Any]:
        """Send SMS notification."""
        # For MVP, simulate SMS sending
        if not self.validate_config():
            return {"status": "skipped", "reason": "SMS not configured"}
        
        # Create SMS content (limited characters)
        message = f"[{alert.severity}] {alert.title}: {alert.message[:100]}..."
        
        # In production, would use service like Twilio
        print(f"[SMS] Would send to {user.name} ({getattr(user, 'phone', 'no-phone')}): {message}")
        
        return {
            "channel": "sms",
            "alert_id": alert.id,
            "user_id": user.id,
            "recipient": getattr(user, 'phone', 'no-phone'),
            "message": message,
            "status": "simulated"
        }
    
    def validate_config(self) -> bool:
        """Validate SMS configuration."""
        required_fields = ["api_key", "api_secret"]
        return all(self.config.get(field) for field in required_fields)
