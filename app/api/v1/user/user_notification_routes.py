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

router = APIRouter(prefix="/notifications")

def get_notification_service(db: Session = Depends(get_db)):
    """Dependency to create NotificationService with repositories and default channels."""
    delivery_repo = DeliveryRepository(db)
    pref_repo = UserPreferenceRepository(db)
    alert_repo = AlertRepository(db)
    user_repo = UserRepository(db)
    
    # For MVP: only In-App channel
    channels = [InAppChannel()]
    
    return NotificationService(delivery_repo, pref_repo, alert_repo, user_repo, channels)

@router.get("/deliveries/{user_id}")
def get_user_deliveries(user_id: str, db: Session = Depends(get_db)):
    """Get all notification deliveries for a user (End User)"""
    user_repo = UserRepository(db)
    delivery_repo = DeliveryRepository(db)
    
    # Verify user exists
    user = user_repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    deliveries = delivery_repo.get_user_deliveries(user_id)
    unread_deliveries = delivery_repo.get_unread_deliveries(user_id)
    
    return {
        "user_id": user_id,
        "total_deliveries": len(deliveries),
        "unread_count": len(unread_deliveries),
        "deliveries": deliveries
    }

@router.get("/deliveries/{user_id}/unread")
def get_unread_deliveries(user_id: str, db: Session = Depends(get_db)):
    """Get unread notification deliveries for a user (End User)"""
    user_repo = UserRepository(db)
    delivery_repo = DeliveryRepository(db)
    
    # Verify user exists
    user = user_repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    unread_deliveries = delivery_repo.get_unread_deliveries(user_id)
    
    return {
        "user_id": user_id,
        "unread_count": len(unread_deliveries),
        "unread_deliveries": unread_deliveries
    }

@router.post("/deliveries/{delivery_id}/read")
def mark_delivery_as_read(delivery_id: str, db: Session = Depends(get_db)):
    """Mark a specific notification delivery as read (End User)"""
    delivery_repo = DeliveryRepository(db)
    delivery = delivery_repo.mark_read(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return {
        "message": f"Delivery {delivery_id} marked as read",
        "delivery": delivery
    }

# Legacy endpoints for backward compatibility 
@router.post("/reminders")
def trigger_reminders(service: NotificationService = Depends(get_notification_service)):
    """Trigger reminders manually (for testing/admin use)"""
    return service.trigger_reminders()

@router.post("/alerts/{alert_id}/deliver/{user_id}")
def deliver_alert_to_user(
    alert_id: str, 
    user_id: str, 
    service: NotificationService = Depends(get_notification_service)
):
    """Deliver specific alert to specific user manually (for testing/admin use)"""
    alert = service.alert_repo.get_alert_by_id(alert_id)
    user = service.user_repo.get_user(user_id)

    if not alert or not user:
        raise HTTPException(status_code=404, detail="Alert or User not found")

    return service.deliver(alert, user)

@router.post("/alerts/{alert_id}/deliver/{user_id}/channels")
def deliver_alert_with_specific_channels(
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