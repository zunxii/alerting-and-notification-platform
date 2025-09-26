from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.db.session import get_db
from app.repositories.alert_repo import AlertRepository
from app.repositories.delivery_repo import DeliveryRepository
from app.repositories.preference_repo import UserPreferenceRepository
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts")

# ------------------ CREATE & UPDATE ------------------

@router.post("/")
def create_alert(alert_data: dict, db: Session = Depends(get_db)):
    alert_repo = AlertRepository(db)
    alert_service = AlertService(alert_repo)
    return alert_service.create_alert(alert_data)

@router.put("/{alert_id}")
def update_alert(alert_id: UUID, update_data: dict, db: Session = Depends(get_db)):
    alert_repo = AlertRepository(db)
    alert_service = AlertService(alert_repo)
    alert = alert_service.update_alert(alert_id, update_data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

# ------------------ SPECIFIC ROUTES ------------------

@router.get("/active")
def list_active_alerts(db: Session = Depends(get_db)):
    alert_repo = AlertRepository(db)
    alert_service = AlertService(alert_repo)
    return alert_service.list_active_alerts()

@router.get("/{alert_id}/status")
def get_alert_status(alert_id: UUID, db: Session = Depends(get_db)):
    alert_repo = AlertRepository(db)
    delivery_repo = DeliveryRepository(db)
    pref_repo = UserPreferenceRepository(db)
    alert_service = AlertService(alert_repo)
    
    alert = alert_service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    deliveries = delivery_repo.get_alert_deliveries(alert_id)
    total_delivered = len(deliveries)
    total_read = len([d for d in deliveries if d.read_at is not None])
    
    return {
        "alert_id": alert_id,
        "total_delivered": total_delivered,
        "total_read": total_read,
        "read_rate": (total_read / total_delivered * 100) if total_delivered else 0,
        "is_active": not alert.is_archived and (not alert.expiry_time or alert.expiry_time > datetime.utcnow())
    }

@router.post("/{alert_id}/archive")
def archive_alert(alert_id: UUID, db: Session = Depends(get_db)):
    alert_repo = AlertRepository(db)
    alert_service = AlertService(alert_repo)
    alert = alert_service.archive_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": f"Alert {alert_id} archived successfully"}

@router.get("/{alert_id}")
def get_alert(alert_id: UUID, db: Session = Depends(get_db)):
    alert_repo = AlertRepository(db)
    alert_service = AlertService(alert_repo)
    alert = alert_service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.get("/")
def list_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: Info, Warning, Critical"),
    status: Optional[str] = Query(None, description="Filter by status: active, expired, archived"),
    audience: Optional[str] = Query(None, description="Filter by audience: org, team, user"),
    db: Session = Depends(get_db)
):
    alert_repo = AlertRepository(db)
    alert_service = AlertService(alert_repo)
    return alert_service.list_alerts_with_filters(severity, status, audience)
