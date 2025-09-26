from datetime import datetime
from typing import Optional
from app.repositories.alert_repo import AlertRepository

class AlertService:
    def __init__(self, alert_repo: AlertRepository):
        self.repo = alert_repo

    def create_alert(self, alert_data: dict):
        """Create a new alert with default reminder frequency if not specified"""
        # Set default reminder frequency to 2 hours (120 minutes) if not provided
        if 'reminder_freq_minutes' not in alert_data:
            alert_data['reminder_freq_minutes'] = 120
            
        if 'start_time' not in alert_data:
            alert_data['start_time'] = datetime.utcnow()
            
        return self.repo.create_alert(alert_data)

    def get_alert_by_id(self, alert_id: str):
        """Get alert by ID"""
        return self.repo.get_alert_by_id(alert_id)

    def list_active_alerts(self):
        """Get all active alerts"""
        return self.repo.get_active_alerts(datetime.utcnow())

    def update_alert(self, alert_id: str, update_data: dict):
        """Update an existing alert"""
        return self.repo.update_alert(alert_id, update_data)

    def archive_alert(self, alert_id: str):
        """Archive an alert"""
        return self.repo.archive_alert(alert_id)

    def list_alerts_with_filters(self, severity: Optional[str] = None, 
                                status: Optional[str] = None, 
                                audience: Optional[str] = None):
        """List alerts with optional filters"""
        alerts = self.repo.get_all_alerts()
        filtered_alerts = []
        
        now = datetime.utcnow()
        
        for alert in alerts:
            # Apply filters
            if severity and alert.severity.lower() != severity.lower():
                continue
                
            # Status filter
            if status:
                is_active = (not alert.is_archived and 
                           alert.start_time <= now and 
                           (not alert.expiry_time or alert.expiry_time > now))
                is_expired = (not alert.is_archived and 
                            alert.expiry_time and alert.expiry_time <= now)
                is_archived = alert.is_archived
                
                if status.lower() == "active" and not is_active:
                    continue
                elif status.lower() == "expired" and not is_expired:
                    continue
                elif status.lower() == "archived" and not is_archived:
                    continue
            
            if audience and alert.visibility:
                audience_match = False
                if audience.lower() == "org" and alert.visibility.get("org"):
                    audience_match = True
                elif audience.lower() == "team" and alert.visibility.get("teams"):
                    audience_match = True
                elif audience.lower() == "user" and alert.visibility.get("users"):
                    audience_match = True
                
                if not audience_match:
                    continue
            
            filtered_alerts.append(alert)
        
        return {
            "alerts": filtered_alerts,
            "total_count": len(filtered_alerts),
            "filters_applied": {
                "severity": severity,
                "status": status,
                "audience": audience
            }
        }