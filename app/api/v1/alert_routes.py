from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.repositories.alert_repo import AlertRepository
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.post("/")
def create_alert(alert_data: dict, db: Session = Depends(get_db)):
    alert_repo = AlertRepository(db)
    alert_service = AlertService(alert_repo)
    return alert_service.create_alert(alert_data)

@router.get("/{alert_id}")
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert_repo = AlertRepository(db)
    alert_service = AlertService(alert_repo)
    alert = alert_service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.get("/active")
def list_active_alerts(db: Session = Depends(get_db)):
    alert_repo = AlertRepository(db)
    alert_service = AlertService(alert_repo)
    return alert_service.list_active_alerts(datetime.utcnow())
