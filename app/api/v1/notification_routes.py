from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.delivery_repo import DeliveryRepository
from app.repositories.preference_repo import UserPreferenceRepository
from app.repositories.alert_repo import AlertRepository
from app.repositories.user_repo import UserRepository
from app.services.notification_service import NotificationService
from app.channels.in_app import InAppChannel
from app.channels.email import EmailChannel
from app.channels.sms import SMSChannel

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_notification_service(db: Session = Depends(get_db)):
    """Dependency to create NotificationService with repositories and default channels."""
    delivery_repo = DeliveryRepository(db)
    pref_repo = UserPreferenceRepository(db)
    alert_repo = AlertRepository(db)
    user_repo = UserRepository(db)
    
    # For MVP: only In-App channel
    # Future: can be configurable based on alert settings or user preferences
    channels = [InAppChannel()]
    
    return NotificationService(delivery_repo, pref_repo, alert_repo, user_repo, channels)


# Trigger reminders manually 
@router.post("/reminders")
def trigger_reminders(service: NotificationService = Depends(get_notification_service)):
    return service.trigger_reminders()


# Deliver one alert manually (Admin use/demo)
@router.post("/alerts/{alert_id}/deliver/{user_id}")
def deliver_alert(alert_id: str, user_id: str, service: NotificationService = Depends(get_notification_service)):
    alert = service.alert_repo.get_alert_by_id(alert_id)
    user = service.user_repo.get_user(user_id)

    if not alert or not user:
        raise HTTPException(status_code=404, detail="Alert or User not found")

    return service.deliver(alert, user)


# Deliver alert with specific channels (for testing/admin)
@router.post("/alerts/{alert_id}/deliver/{user_id}/channels")
def deliver_alert_with_channels(
    alert_id: str, 
    user_id: str, 
    channel_types: list[str],  # ["in_app", "email", "sms"]
    db: Session = Depends(get_db)
):
    """Deliver alert with specific channels - useful for testing or admin overrides."""
    delivery_repo = DeliveryRepository(db)
    pref_repo = UserPreferenceRepository(db)
    alert_repo = AlertRepository(db)
    user_repo = UserRepository(db)
    
    # Build channels based on request
    channels = []
    channel_map = {
        "in_app": InAppChannel(),
        "email": EmailChannel(),
        "sms": SMSChannel()
    }
    
    for channel_type in channel_types:
        if channel_type in channel_map:
            channels.append(channel_map[channel_type])
    
    service = NotificationService(delivery_repo, pref_repo, alert_repo, user_repo, channels)
    
    alert = alert_repo.get_alert_by_id(alert_id)
    user = user_repo.get_user(user_id)

    if not alert or not user:
        raise HTTPException(status_code=404, detail="Alert or User not found")

    return service.deliver(alert, user)


# Snooze an alert for today
@router.post("/alerts/{alert_id}/snooze/{user_id}")
def snooze_alert(alert_id: str, user_id: str, db: Session = Depends(get_db)):
    pref_repo = UserPreferenceRepository(db)
    return pref_repo.snooze_alert_today(user_id, alert_id)


# Mark a notification delivery as read
@router.post("/deliveries/{delivery_id}/read")
def mark_read(delivery_id: str, db: Session = Depends(get_db)):
    delivery_repo = DeliveryRepository(db)
    return delivery_repo.mark_read(delivery_id)