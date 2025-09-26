import asyncio
from datetime import datetime, timedelta, time
from typing import Optional
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.db.session import get_db
from app.repositories.alert_repo import AlertRepository
from app.repositories.delivery_repo import DeliveryRepository
from app.repositories.preference_repo import UserPreferenceRepository
from app.repositories.user_repo import UserRepository
from app.services.notification_service import NotificationService
from app.channels.in_app import InAppChannel

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service to handle automated reminder scheduling as required by PRD."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.notification_service: Optional[NotificationService] = None
        self._is_running = False

    def initialize(self):
        """Initialize the scheduler with default jobs."""
        # Job 1: Trigger reminders every 2 hours (PRD requirement)
        self.scheduler.add_job(
            func=self._trigger_reminders_job,
            trigger=IntervalTrigger(hours=2),
            id="reminder_trigger",
            name="Trigger 2-hour reminders",
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        
        # Job 2: Reset daily snoozes at midnight (PRD requirement)
        self.scheduler.add_job(
            func=self._reset_daily_snoozes_job,
            trigger=CronTrigger(hour=0, minute=0),  # Every day at midnight
            id="daily_snooze_reset",
            name="Reset daily snoozes",
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        
        # Job 3: Cleanup expired alerts (housekeeping)
        self.scheduler.add_job(
            func=self._cleanup_expired_alerts_job,
            trigger=CronTrigger(hour=2, minute=0),  # Every day at 2 AM
            id="cleanup_expired",
            name="Cleanup expired alerts",
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        
        logger.info("Scheduler initialized with default jobs")

    def start(self):
        """Start the scheduler."""
        if not self._is_running:
            self.scheduler.start()
            self._is_running = True
            logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        if self._is_running:
            self.scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("Scheduler stopped")

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._is_running and self.scheduler.running

    async def _trigger_reminders_job(self):
        """Job to trigger reminders every 2 hours as per PRD."""
        try:
            logger.info("Starting 2-hour reminder job")
            
            # Get database session
            db = next(get_db())
            
            # Initialize notification service
            delivery_repo = DeliveryRepository(db)
            pref_repo = UserPreferenceRepository(db)
            alert_repo = AlertRepository(db)
            user_repo = UserRepository(db)
            channels = [InAppChannel()]
            
            notification_service = NotificationService(
                delivery_repo, pref_repo, alert_repo, user_repo, channels
            )
            
            # Trigger reminders
            result = notification_service.trigger_reminders()
            logger.info(f"2-hour reminder job completed: {result}")
            
        except Exception as e:
            logger.error(f"Error in 2-hour reminder job: {str(e)}")
        finally:
            db.close()

    async def _reset_daily_snoozes_job(self):
        """Job to reset daily snoozes at midnight as per PRD."""
        try:
            logger.info("Starting daily snooze reset job")
            
            # Get database session
            db = next(get_db())
            
            # Initialize notification service
            delivery_repo = DeliveryRepository(db)
            pref_repo = UserPreferenceRepository(db)
            alert_repo = AlertRepository(db)
            user_repo = UserRepository(db)
            channels = [InAppChannel()]
            
            notification_service = NotificationService(
                delivery_repo, pref_repo, alert_repo, user_repo, channels
            )
            
            # Reset daily snoozes
            result = notification_service.reset_daily_snoozes()
            logger.info(f"Daily snooze reset job completed: {result}")
            
        except Exception as e:
            logger.error(f"Error in daily snooze reset job: {str(e)}")
        finally:
            db.close()

    async def _cleanup_expired_alerts_job(self):
        """Job to cleanup expired alerts (housekeeping)."""
        try:
            logger.info("Starting expired alerts cleanup job")
            
            # Get database session
            db = next(get_db())
            alert_repo = AlertRepository(db)
            
            # Get expired alerts
            all_alerts = alert_repo.get_all_alerts()
            now = datetime.utcnow()
            expired_count = 0
            
            for alert in all_alerts:
                if (alert.expiry_time and alert.expiry_time < now and 
                    not alert.is_archived):
                    # Auto-archive expired alerts
                    alert_repo.archive_alert(alert.id)
                    expired_count += 1
            
            logger.info(f"Cleanup job completed: {expired_count} expired alerts archived")
            
        except Exception as e:
            logger.error(f"Error in cleanup job: {str(e)}")
        finally:
            db.close()

    def add_custom_reminder_job(self, alert_id: str, frequency_hours: int = 2):
        """Add custom reminder job for specific alert (future extensibility)."""
        job_id = f"custom_reminder_{alert_id}"
        
        self.scheduler.add_job(
            func=self._custom_alert_reminder_job,
            args=[alert_id],
            trigger=IntervalTrigger(hours=frequency_hours),
            id=job_id,
            name=f"Custom reminder for alert {alert_id}",
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        
        logger.info(f"Added custom reminder job for alert {alert_id} every {frequency_hours} hours")

    def remove_custom_reminder_job(self, alert_id: str):
        """Remove custom reminder job for specific alert."""
        job_id = f"custom_reminder_{alert_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed custom reminder job for alert {alert_id}")
        except Exception as e:
            logger.warning(f"Could not remove job {job_id}: {str(e)}")

    async def _custom_alert_reminder_job(self, alert_id: str):
        """Custom reminder job for specific alert."""
        try:
            logger.info(f"Starting custom reminder job for alert {alert_id}")
            
            db = next(get_db())
            
            delivery_repo = DeliveryRepository(db)
            pref_repo = UserPreferenceRepository(db)
            alert_repo = AlertRepository(db)
            user_repo = UserRepository(db)
            channels = [InAppChannel()]
            
            notification_service = NotificationService(
                delivery_repo, pref_repo, alert_repo, user_repo, channels
            )
            
            # Get specific alert
            alert = alert_repo.get_alert_by_id(alert_id)
            if not alert or alert.is_archived:
                # Remove job if alert no longer exists or is archived
                self.remove_custom_reminder_job(alert_id)
                return
            
            # Check if alert is still active
            if alert.expiry_time and alert.expiry_time <= datetime.utcnow():
                # Remove job if alert is expired
                self.remove_custom_reminder_job(alert_id)
                return
            
            # Get users for this alert and trigger reminders
            users = user_repo.get_all_users()
            eligible_users = notification_service.get_users_for_alert(alert, users)
            
            delivered_count = 0
            for user in eligible_users:
                if notification_service.should_deliver(alert, user):
                    notification_service.deliver(alert, user)
                    delivered_count += 1
            
            logger.info(f"Custom reminder job for alert {alert_id} completed: {delivered_count} deliveries")
            
        except Exception as e:
            logger.error(f"Error in custom reminder job for alert {alert_id}: {str(e)}")
        finally:
            db.close()

    def get_job_status(self) -> dict:
        """Get status of all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": self.is_running(),
            "total_jobs": len(jobs),
            "jobs": jobs
        }

    def trigger_job_manually(self, job_id: str):
        """Manually trigger a specific job (for testing/admin purposes)."""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.modify(next_run_time=datetime.now())
                logger.info(f"Manually triggered job: {job_id}")
                return {"success": True, "message": f"Job {job_id} triggered"}
            else:
                return {"success": False, "message": f"Job {job_id} not found"}
        except Exception as e:
            logger.error(f"Error triggering job {job_id}: {str(e)}")
            return {"success": False, "message": str(e)}

# Global scheduler instance
scheduler_service = SchedulerService()