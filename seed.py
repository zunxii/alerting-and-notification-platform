from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.repositories.team_repo import TeamRepository
from app.repositories.user_repo import UserRepository
from app.repositories.alert_repo import AlertRepository

def seed_data():
    db = SessionLocal()

    try:
        # ===== Teams =====
        team_repo = TeamRepository(db)
        engineering = team_repo.create_team("Engineering")
        marketing = team_repo.create_team("Marketing")
        hr = team_repo.create_team("HR")

        print(f"Teams created: {[engineering.name, marketing.name, hr.name]}")

        # ===== Users =====
        user_repo = UserRepository(db)
        alice = user_repo.create_user("Alice", engineering.id)
        bob = user_repo.create_user("Bob", marketing.id)
        charlie = user_repo.create_user("Charlie", hr.id)

        print(f"Users created: {[alice.name, bob.name, charlie.name]}")

        # ===== Alerts =====
        alert_repo = AlertRepository(db)
        now = datetime.utcnow()
        alert1 = alert_repo.create_alert({
            "title": "Server Maintenance",
            "body": "Scheduled maintenance at midnight.",
            "severity": "WARNING",
            "delivery_types": ["in_app"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 120,
            "start_time": now,
            "expiry_time": now + timedelta(days=1),
            # convert UUIDs to strings
            "visibility": {"org": False, "teams": [str(engineering.id)], "users": []}
        })

        alert2 = alert_repo.create_alert({
            "title": "New Policy Update",
            "body": "Please review the updated leave policy.",
            "severity": "INFO",
            "delivery_types": ["in_app"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 120,
            "start_time": now,
            "expiry_time": now + timedelta(days=3),
            "visibility": {"org": True, "teams": [], "users": []}
        })


        print(f"Alerts created: {[alert1.title, alert2.title]}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
