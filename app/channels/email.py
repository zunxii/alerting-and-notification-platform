import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from app.channels.base import NotificationChannel
from app.models.alert import Alert
from app.models.user import User

class EmailChannel(NotificationChannel):
    """Email notification channel implementation (future scope)."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.smtp_server = self.config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = self.config.get("smtp_port", 587)
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.from_address = self.config.get("from_address", "alerts@company.com")
        super().__init__()
    
    def send(self, alert: Alert, user: User) -> Dict[str, Any]:
        """Send email notification."""
        # For MVP, simulate email sending
        if not self.validate_config():
            return {"status": "skipped", "reason": "Email not configured"}
        
        # Create email content
        subject = f"[{alert.severity.upper()}] {alert.title}"
        
        html_body = f"""
        <html>
            <body>
                <h2>{alert.title}</h2>
                <p><strong>Severity:</strong> {alert.severity}</p>
                <p><strong>Message:</strong></p>
                <p>{alert.message}</p>
                <p><em>Sent at: {alert.created_at}</em></p>
            </body>
        </html>
        """
        
        # In production, would actually send email
        # For now, just simulate
        print(f"[EMAIL] Would send '{subject}' to {user.name} ({getattr(user, 'email', 'no-email@example.com')})")
        
        return {
            "channel": "email",
            "alert_id": alert.id,
            "user_id": user.id,
            "recipient": getattr(user, 'email', 'no-email@example.com'),
            "subject": subject,
            "status": "simulated"
        }
    
    def validate_config(self) -> bool:
        """Validate email configuration."""
        required_fields = ["username", "password"]
        return all(self.config.get(field) for field in required_fields)
    
    def _send_actual_email(self, to_address: str, subject: str, body: str):
        """Helper method to send actual email (for production)."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_address
            msg['To'] = to_address
            
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False