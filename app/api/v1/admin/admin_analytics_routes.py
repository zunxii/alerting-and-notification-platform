from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.services.analytics_service import AnalyticsService
from app.repositories.alert_repo import AlertRepository
from app.repositories.delivery_repo import DeliveryRepository
from app.repositories.preference_repo import UserPreferenceRepository
from app.repositories.user_repo import UserRepository

router = APIRouter(prefix="/analytics")

def get_analytics_service(db: Session = Depends(get_db)):
    """Dependency to create AnalyticsService with all required repositories."""
    alert_repo = AlertRepository(db)
    delivery_repo = DeliveryRepository(db)
    pref_repo = UserPreferenceRepository(db)
    user_repo = UserRepository(db)
    
    return AnalyticsService(alert_repo, delivery_repo, pref_repo, user_repo)

@router.get("/dashboard")
def get_analytics_dashboard(service: AnalyticsService = Depends(get_analytics_service)):
    """Get comprehensive analytics dashboard (Admin only)"""
    return service.get_dashboard_analytics()

@router.get("/alerts/{alert_id}")
def get_alert_analytics(alert_id: str, service: AnalyticsService = Depends(get_analytics_service)):
    """Get detailed analytics for a specific alert (Admin only)"""
    analytics = service.get_alert_analytics(alert_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Alert not found")
    return analytics

@router.get("/alerts/{alert_id}/performance")
def get_alert_performance(alert_id: str, service: AnalyticsService = Depends(get_analytics_service)):
    """Get performance metrics for a specific alert (Admin only)"""
    performance = service.get_alert_performance_metrics(alert_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Alert not found")
    return performance

@router.get("/system/health")
def get_system_health(service: AnalyticsService = Depends(get_analytics_service)):
    """Get system health metrics (Admin only)"""
    return service.get_system_health_metrics()

@router.get("/trends")
def get_trends(
    days: int = 7,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get trending analytics over time (Admin only)"""
    return service.get_trend_analytics(days)

@router.get("/severity/breakdown")
def get_severity_breakdown(service: AnalyticsService = Depends(get_analytics_service)):
    """Get breakdown of alerts by severity (Admin only)"""
    return service.get_severity_breakdown()

@router.get("/engagement/summary")
def get_engagement_summary(service: AnalyticsService = Depends(get_analytics_service)):
    """Get user engagement summary (Admin only)"""
    return service.get_engagement_summary()