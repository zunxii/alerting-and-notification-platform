from sqlalchemy.orm import Session
from datetime import datetime
from app.models.notification_delivery import NotificationDelivery

class DeliveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_delivery(self, alert_id, user_id, channel: str) -> NotificationDelivery:
        delivery = NotificationDelivery(
            alert_id=alert_id,
            user_id=user_id,
            channel=channel,
            delivered_at=datetime.utcnow()
        )
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def mark_read(self, delivery_id):
        delivery = self.db.query(NotificationDelivery).filter(NotificationDelivery.id == delivery_id).first()
        if delivery:
            delivery.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(delivery)
        return delivery
