from sqlalchemy import Column, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class UserAlertPreference(Base):
    __tablename__ = "user_alert_preferences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False)
    snoozed_date = Column(Date, nullable=True)  # If snoozed, store date
    last_delivered_at = Column(DateTime, nullable=True)

    def is_snoozed_today(self, user_id: str, alert_id: str):
        from datetime import date
        return self.snoozed_date == date.today() if self.snoozed_date else False