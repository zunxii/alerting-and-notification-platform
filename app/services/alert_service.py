from datetime import datetime
from app.repositories.alert_repo import AlertRepository

class AlertService:
    def __init__(self, alert_repo: AlertRepository):
        self.repo = alert_repo

    def create_alert(self, alert_data: dict):
        return self.repo.create_alert(alert_data)

    def list_active_alerts(self):
        return self.repo.get_active_alerts(datetime.utcnow())

    def archive_alert(self, alert_id):
        return self.repo.archive_alert(alert_id)
