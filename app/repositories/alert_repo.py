from sqlalchemy.orm import Session
from datetime import datetime
from app.models.alert import Alert

class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(self, alert_data: dict) -> Alert:
        alert = Alert(**alert_data)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_alert_by_id(self, alert_id: str):
        return self.db.query(Alert).filter(Alert.id == alert_id).first()

    def get_active_alerts(self, now: datetime = None):
        """Fetch alerts that are active (not archived, within start/expiry)."""
        now = now or datetime.utcnow()
        return self.db.query(Alert).filter(
            Alert.is_archived == False,
            Alert.start_time <= now,
            (Alert.expiry_time == None) | (Alert.expiry_time > now)
        ).all()

    def archive_alert(self, alert_id: str):
        alert = self.get_alert_by_id(alert_id)
        if alert:
            alert.is_archived = True
            self.db.commit()
            self.db.refresh(alert)
        return alert

    def update_alert(self, alert_id: str, update_data: dict):
        alert = self.get_alert_by_id(alert_id)
        if alert:
            for key, value in update_data.items():
                if hasattr(alert, key):
                    setattr(alert, key, value)
            self.db.commit()
            self.db.refresh(alert)
        return alert

    def get_all_alerts(self):
        return self.db.query(Alert).all()
