from sqlalchemy.orm import Session
from datetime import datetime, date
from app.models.user_alert_pref import UserAlertPreference

class UserPreferenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_pref(self, user_id, alert_id):
        return self.db.query(UserAlertPreference).filter_by(user_id=user_id, alert_id=alert_id).first()

    def update_last_delivered(self, user_id, alert_id):
        pref = self.get_user_pref(user_id, alert_id)
        if not pref:
            pref = UserAlertPreference(user_id=user_id, alert_id=alert_id)
            self.db.add(pref)
        pref.last_delivered_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pref)
        return pref

    def snooze_alert_today(self, user_id, alert_id):
        today = date.today()
        pref = self.get_user_pref(user_id, alert_id)
        if not pref:
            pref = UserAlertPreference(user_id=user_id, alert_id=alert_id)
            self.db.add(pref)
        pref.snoozed_date = today
        self.db.commit()
        self.db.refresh(pref)
        return pref
