from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid
from app.db.base import Base

class Severity(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class DeliveryType(enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    severity = Column(Enum(Severity), default=Severity.INFO)
    delivery_types = Column(JSON, default=["in_app"])  
    reminder_enabled = Column(Boolean, default=True)
    reminder_freq_minutes = Column(Integer, default=120)
    start_time = Column(DateTime)
    expiry_time = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, default=False)
    visibility = Column(JSON, default={"org": True, "teams": [], "users": []})