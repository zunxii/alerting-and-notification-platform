from sqlalchemy.orm import Session
from datetime import datetime
from app.models.notification_delivery import NotificationDelivery

class DeliveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_delivery(self, alert_id: str, user_id: str, channel: str = "in_app") -> NotificationDelivery:
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

    def mark_read(self, delivery_id: str):
        delivery = self.db.query(NotificationDelivery).filter(NotificationDelivery.id == delivery_id).first()
        if delivery:
            delivery.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(delivery)
        return delivery

    def get_delivery_by_id(self, delivery_id: str):
        return self.db.query(NotificationDelivery).filter(NotificationDelivery.id == delivery_id).first()

    def get_user_deliveries(self, user_id: str):
        return self.db.query(NotificationDelivery).filter(NotificationDelivery.user_id == user_id).all()

    def get_alert_deliveries(self, alert_id: str):
        return self.db.query(NotificationDelivery).filter(NotificationDelivery.alert_id == alert_id).all()

    def get_unread_deliveries(self, user_id: str):
        return self.db.query(NotificationDelivery).filter(
            NotificationDelivery.user_id == user_id,
            NotificationDelivery.read_at == None
        ).all()
