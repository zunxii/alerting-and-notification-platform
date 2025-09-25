from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.base import Base

class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    channel = Column(String, nullable=False)  # e.g. in_app/email/sms
    delivered_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
