from sqlalchemy.orm import Session
from datetime import datetime, date
from app.models.user_alert_pref import UserAlertPreference

class UserPreferenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_pref(self, user_id: str, alert_id: str):
        return self.db.query(UserAlertPreference).filter_by(user_id=user_id, alert_id=alert_id).first()

    def get_user_alert_preference(self, user_id: str, alert_id: str):
        return self.get_user_pref(user_id, alert_id)

    def create_preference(self, user_id: str, alert_id: str, state: str = "Unread", last_delivered_at: datetime = None):
        pref = UserAlertPreference(
            user_id=user_id,
            alert_id=alert_id,
            last_delivered_at=last_delivered_at or datetime.utcnow()
        )
        self.db.add(pref)
        self.db.commit()
        self.db.refresh(pref)
        return pref

    def update_preference(self, pref: UserAlertPreference):
        self.db.commit()
        self.db.refresh(pref)
        return pref

    def update_last_delivered(self, user_id: str, alert_id: str):
        pref = self.get_user_pref(user_id, alert_id)
        if not pref:
            pref = UserAlertPreference(user_id=user_id, alert_id=alert_id)
            self.db.add(pref)
        pref.last_delivered_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pref)
        return pref

    def snooze_alert_today(self, user_id: str, alert_id: str):
        today = date.today()
        pref = self.get_user_pref(user_id, alert_id)
        if not pref:
            pref = UserAlertPreference(user_id=user_id, alert_id=alert_id)
            self.db.add(pref)
        pref.snoozed_date = today
        self.db.commit()
        self.db.refresh(pref)
        return pref

    def mark_as_read(self, user_id: str, alert_id: str):
        pref = self.get_user_pref(user_id, alert_id)
        if not pref:
            pref = UserAlertPreference(user_id=user_id, alert_id=alert_id)
            self.db.add(pref)
        pref.snoozed_date = None  # clear snooze
        self.db.commit()
        self.db.refresh(pref)
        return pref

    def mark_as_unread(self, user_id: str, alert_id: str):
        pref = self.get_user_pref(user_id, alert_id)
        if not pref:
            pref = UserAlertPreference(user_id=user_id, alert_id=alert_id)
            self.db.add(pref)
        self.db.commit()
        self.db.refresh(pref)
        return pref

    def get_user_preferences(self, user_id: str):
        return self.db.query(UserAlertPreference).filter(UserAlertPreference.user_id == user_id).all()

    def is_snoozed_today(self, user_id: str, alert_id: str):
        pref = self.get_user_pref(user_id, alert_id)
        if not pref or not pref.snoozed_date:
            return False
        return pref.snoozed_date == date.today()
