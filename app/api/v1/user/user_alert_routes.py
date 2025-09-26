from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.repositories.alert_repo import AlertRepository
from app.repositories.user_repo import UserRepository
from app.repositories.preference_repo import UserPreferenceRepository
from app.repositories.delivery_repo import DeliveryRepository
from app.services.notification_service import NotificationService
from app.channels.in_app import InAppChannel

router = APIRouter(prefix="/alerts")

def get_notification_service(db: Session = Depends(get_db)):
    """Dependency to create NotificationService."""
    delivery_repo = DeliveryRepository(db)
    pref_repo = UserPreferenceRepository(db)
    alert_repo = AlertRepository(db)
    user_repo = UserRepository(db)
    channels = [InAppChannel()]
    return NotificationService(delivery_repo, pref_repo, alert_repo, user_repo, channels)

@router.get("/feed/{user_id}")
def get_user_alert_feed(user_id: str, db: Session = Depends(get_db)):
    """Get active alerts for a specific user (End User)"""
    user_repo = UserRepository(db)
    alert_repo = AlertRepository(db)
    pref_repo = UserPreferenceRepository(db)
    delivery_repo = DeliveryRepository(db)
    
    # Verify user exists
    user = user_repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get active alerts
    active_alerts = alert_repo.get_active_alerts()
    
    # Filter alerts based on visibility
    service = get_notification_service(db)
    relevant_alerts = []
    
    for alert in active_alerts:
        users_for_alert = service.get_users_for_alert(alert, [user])
        if users_for_alert:  # User should receive this alert
            # Get user preference for this alert
            pref = pref_repo.get_user_alert_preference(user_id, alert.id)
            
            # Get latest delivery for this alert-user combination
            deliveries = delivery_repo.get_alert_deliveries(alert.id)
            user_deliveries = [d for d in deliveries if d.user_id == user_id]
            latest_delivery = max(user_deliveries, key=lambda x: x.delivered_at) if user_deliveries else None
            
            relevant_alerts.append({
                "alert": alert,
                "is_read": latest_delivery.read_at is not None if latest_delivery else False,
                "is_snoozed": pref.is_snoozed_today(user_id, alert.id) if pref else False,
                "last_delivered": latest_delivery.delivered_at if latest_delivery else None,
                "delivery_count": len(user_deliveries)
            })
    
    return {
        "user_id": user_id,
        "alerts": relevant_alerts,
        "total_count": len(relevant_alerts),
        "unread_count": len([a for a in relevant_alerts if not a["is_read"]]),
        "snoozed_count": len([a for a in relevant_alerts if a["is_snoozed"]])
    }

@router.get("/snoozed/{user_id}")
def get_snoozed_alerts(user_id: str, db: Session = Depends(get_db)):
    """Get snoozed alerts history for a user (End User)"""
    user_repo = UserRepository(db)
    pref_repo = UserPreferenceRepository(db)
    alert_repo = AlertRepository(db)
    
    # Verify user exists
    user = user_repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user preferences with snooze data
    user_prefs = pref_repo.get_user_preferences(user_id)
    snoozed_alerts = []
    
    for pref in user_prefs:
        if pref.snoozed_date:
            alert = alert_repo.get_alert_by_id(pref.alert_id)
            if alert:
                snoozed_alerts.append({
                    "alert": alert,
                    "snoozed_date": pref.snoozed_date,
                    "is_today": pref.snoozed_date == datetime.now().date()
                })
    
    return {
        "user_id": user_id,
        "snoozed_alerts": snoozed_alerts,
        "total_count": len(snoozed_alerts)
    }

@router.post("/{alert_id}/read/{user_id}")
def mark_alert_as_read(alert_id: str, user_id: str, db: Session = Depends(get_db)):
    """Mark an alert as read for a user (End User)"""
    pref_repo = UserPreferenceRepository(db)
    user_repo = UserRepository(db)
    alert_repo = AlertRepository(db)
    delivery_repo = DeliveryRepository(db)
    
    # Verify user and alert exist
    user = user_repo.get_user(user_id)
    alert = alert_repo.get_alert_by_id(alert_id)
    if not user or not alert:
        raise HTTPException(status_code=404, detail="User or Alert not found")
    
    # Mark preference as read
    pref_repo.mark_as_read(user_id, alert_id)
    
    # Also mark the latest delivery as read if exists
    deliveries = delivery_repo.get_alert_deliveries(alert_id)
    user_deliveries = [d for d in deliveries if d.user_id == user_id]
    if user_deliveries:
        latest_delivery = max(user_deliveries, key=lambda x: x.delivered_at)
        if not latest_delivery.read_at:
            delivery_repo.mark_read(latest_delivery.id)
    
    return {"message": f"Alert {alert_id} marked as read for user {user_id}"}

@router.post("/{alert_id}/unread/{user_id}")
def mark_alert_as_unread(alert_id: str, user_id: str, db: Session = Depends(get_db)):
    """Mark an alert as unread for a user (End User)"""
    pref_repo = UserPreferenceRepository(db)
    user_repo = UserRepository(db)
    alert_repo = AlertRepository(db)
    
    # Verify user and alert exist
    user = user_repo.get_user(user_id)
    alert = alert_repo.get_alert_by_id(alert_id)
    if not user or not alert:
        raise HTTPException(status_code=404, detail="User or Alert not found")
    
    pref_repo.mark_as_unread(user_id, alert_id)
    return {"message": f"Alert {alert_id} marked as unread for user {user_id}"}

@router.post("/{alert_id}/snooze/{user_id}")
def snooze_alert(alert_id: str, user_id: str, db: Session = Depends(get_db)):
    """Snooze an alert for today for a user (End User)"""
    pref_repo = UserPreferenceRepository(db)
    user_repo = UserRepository(db)
    alert_repo = AlertRepository(db)
    
    # Verify user and alert exist
    user = user_repo.get_user(user_id)
    alert = alert_repo.get_alert_by_id(alert_id)
    if not user or not alert:
        raise HTTPException(status_code=404, detail="User or Alert not found")
    
    pref = pref_repo.snooze_alert_today(user_id, alert_id)
    return {
        "message": f"Alert {alert_id} snoozed for user {user_id} until tomorrow",
        "snoozed_date": pref.snoozed_date
    }