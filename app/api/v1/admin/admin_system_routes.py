from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.session import get_db
from app.services.scheduler_service import scheduler_service
from app.channels.factory import ChannelFactory, ChannelType

router = APIRouter(prefix="/system")

@router.get("/scheduler/status")
def get_scheduler_status():
    """Get scheduler status and job information (Admin only)"""
    return scheduler_service.get_job_status()

@router.post("/scheduler/start")
def start_scheduler():
    """Start the scheduler (Admin only)"""
    try:
        if scheduler_service.is_running():
            return {"message": "Scheduler is already running"}
        
        scheduler_service.start()
        return {"message": "Scheduler started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")

@router.post("/scheduler/stop")
def stop_scheduler():
    """Stop the scheduler (Admin only)"""
    try:
        if not scheduler_service.is_running():
            return {"message": "Scheduler is not running"}
        
        scheduler_service.stop()
        return {"message": "Scheduler stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")

@router.post("/scheduler/jobs/{job_id}/trigger")
def trigger_job_manually(job_id: str):
    """Manually trigger a specific job (Admin only)"""
    result = scheduler_service.trigger_job_manually(job_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@router.post("/scheduler/reminders/trigger")
def trigger_reminders_now():
    """Manually trigger reminders immediately (Admin only)"""
    result = scheduler_service.trigger_job_manually("reminder_trigger")
    return {"message": "Reminder job triggered", "result": result}

@router.post("/scheduler/snooze/reset")
def reset_snoozes_now():
    """Manually reset daily snoozes (Admin only)"""
    result = scheduler_service.trigger_job_manually("daily_snooze_reset")
    return {"message": "Snooze reset job triggered", "result": result}

@router.get("/channels/types")
def get_available_channel_types():
    """Get available notification channel types (Admin only)"""
    return {
        "available_types": ChannelFactory.get_available_channel_types(),
        "default_type": "in_app",
        "description": {
            "in_app": "In-application notifications (MVP)",
            "email": "Email notifications (Future scope)",
            "sms": "SMS notifications (Future scope)"
        }
    }

@router.post("/channels/test")
def test_channel_configuration(channel_config: Dict[str, Any]):
    """Test a channel configuration (Admin only)"""
    try:
        channel_type_str = channel_config.get("type", "in_app")
        channel_type = ChannelType(channel_type_str)
        config = channel_config.get("config", {})
        
        # Create channel instance
        channel = ChannelFactory.create_channel(channel_type, config)
        
        # Validate configuration
        is_valid = channel.validate_config()
        
        return {
            "channel_type": channel_type_str,
            "configuration_valid": is_valid,
            "status": "ready" if is_valid else "configuration_required"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid channel type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Channel test failed: {str(e)}")

@router.get("/health")
def get_system_health():
    """Get overall system health status (Admin only)"""
    scheduler_running = scheduler_service.is_running()
    scheduler_jobs = scheduler_service.get_job_status()
    
    # Basic health checks
    health_status = "healthy"
    issues = []
    
    if not scheduler_running:
        health_status = "warning"
        issues.append("Scheduler is not running")
    
    if scheduler_jobs["total_jobs"] == 0:
        health_status = "warning" 
        issues.append("No scheduled jobs found")
    
    return {
        "status": health_status,
        "scheduler": {
            "running": scheduler_running,
            "jobs_count": scheduler_jobs["total_jobs"]
        },
        "channels": {
            "available_types": len(ChannelFactory.get_available_channel_types()),
            "default_configured": True  # In-app is always available
        },
        "issues": issues,
        "checked_at": scheduler_jobs.get("checked_at")
    }

@router.post("/maintenance/cleanup")
def run_maintenance_cleanup():
    """Run maintenance cleanup tasks (Admin only)"""
    result = scheduler_service.trigger_job_manually("cleanup_expired")
    return {"message": "Maintenance cleanup triggered", "result": result}

@router.get("/configuration")
def get_system_configuration():
    """Get current system configuration (Admin only)"""
    return {
        "reminder_frequency": {
            "default_hours": 2,
            "description": "Default reminder frequency as per PRD"
        },
        "snooze_policy": {
            "duration": "until_next_day",
            "reset_time": "midnight",
            "description": "Snooze resets daily as per PRD"
        },
        "channels": {
            "enabled": ChannelFactory.get_available_channel_types(),
            "default": "in_app",
            "mvp_scope": ["in_app"]
        },
        "scheduler": {
            "auto_start": True,
            "jobs": [
                {"name": "2-hour reminders", "frequency": "every 2 hours"},
                {"name": "daily snooze reset", "frequency": "daily at midnight"},
                {"name": "cleanup expired", "frequency": "daily at 2 AM"}
            ]
        }
    }