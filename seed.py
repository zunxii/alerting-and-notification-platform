"""
Seed script to create sample data for testing the Alerting & Notification Platform.
Creates users, teams, and sample alerts with all required attributes.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.repositories.team_repo import TeamRepository
from app.repositories.alert_repo import AlertRepository
from app.services.user_service import UserService
from app.services.alert_service import AlertService

def create_seed_data(db: Session):
    """Create seed data for testing."""
    
    # Initialize repositories and services
    user_repo = UserRepository(db)
    team_repo = TeamRepository(db)
    alert_repo = AlertRepository(db)
    
    user_service = UserService(user_repo, team_repo)
    alert_service = AlertService(alert_repo)
    
    print("Creating seed data...")
    
    # 1. Create Teams
    teams_data = [
        {"name": "Engineering"},
        {"name": "Marketing"},
        {"name": "Operations"},
        {"name": "Sales"},
        {"name": "HR"}
    ]
    
    teams = {}
    for team_data in teams_data:
        team = team_repo.create_team(team_data["name"])
        teams[team_data["name"]] = team
        print(f" Created team: {team.name} (ID: {team.id})")
    
    # 2. Create Users
    users_data = [
        {"name": "John Doe", "team": "Engineering"},
        {"name": "Jane Smith", "team": "Engineering"},
        {"name": "Mike Johnson", "team": "Marketing"},
        {"name": "Sarah Wilson", "team": "Marketing"},
        {"name": "David Brown", "team": "Operations"},
        {"name": "Lisa Davis", "team": "Operations"},
        {"name": "Tom Miller", "team": "Sales"},
        {"name": "Amy Taylor", "team": "HR"},
        {"name": "Admin User", "team": None},
        {"name": "Guest User", "team": None}
    ]
    
    users = {}
    for user_data in users_data:
        team_id = teams[user_data["team"]].id if user_data["team"] else None
        user = user_service.create_user(user_data["name"], team_id)
        users[user_data["name"]] = user
        team_name = user_data["team"] or "No Team"
        print(f" Created user: {user.name} (ID: {user.id}, Team: {team_name})")
    
    # 3. Create Sample Alerts with full attributes
    alerts_data = [
        {
            "title": "System Maintenance Scheduled",
            "body": "Scheduled maintenance will occur tonight from 11 PM to 2 AM. Please save your work.",
            "severity": "WARNING",
            "delivery_types": ["in_app"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 120,
            "visibility": {"org": True},
            "start_time": datetime.utcnow(),
            "expiry_time": datetime.utcnow() + timedelta(days=1),
            "is_archived": False,
            "created_at": datetime.utcnow()
        },
        {
            "title": "CRITICAL Security Update",
            "body": "A CRITICAL security patch has been released. Please update your systems immediately.",
            "severity": "CRITICAL",
            "delivery_types": ["in_app", "email"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 60,
            "visibility": {"org": True},
            "start_time": datetime.utcnow(),
            "expiry_time": datetime.utcnow() + timedelta(hours=12),
            "is_archived": False,
            "created_at": datetime.utcnow()
        },
        {
            "title": "New Marketing Campaign Launch",
            "body": "The Q4 marketing campaign goes live tomorrow. Please review the final materials.",
            "severity": "INFO",
            "delivery_types": ["in_app", "email"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 120,
            "visibility": {"teams": [str(teams["Marketing"].id)]},
            "start_time": datetime.utcnow(),
            "expiry_time": datetime.utcnow() + timedelta(days=2),
            "is_archived": False,
            "created_at": datetime.utcnow()
        },
        {
            "title": "Engineering Code Review Required",
            "body": "New pull requests are waiting for code review. Please prioritize CRITICAL fixes.",
            "severity": "WARNING",
            "delivery_types": ["in_app"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 90,
            "visibility": {"teams": [str(teams["Engineering"].id)]},
            "start_time": datetime.utcnow(),
            "expiry_time": datetime.utcnow() + timedelta(days=3),
            "is_archived": False,
            "created_at": datetime.utcnow()
        },
        {
            "title": "Sales Target Reminder",
            "body": "Monthly sales targets are due for review. Please update your forecasts.",
            "severity": "INFO",
            "delivery_types": ["in_app", "email"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 120,
            "visibility": {"teams": [str(teams["Sales"].id)]},
            "start_time": datetime.utcnow(),
            "expiry_time": datetime.utcnow() + timedelta(days=5),
            "is_archived": False,
            "created_at": datetime.utcnow()
        },
        {
            "title": "Personal Task Reminder",
            "body": "Don't forget to submit your quarterly report by end of week.",
            "severity": "INFO",
            "delivery_types": ["in_app", "email", "sms"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 180,
            "visibility": {"users": [str(users["John Doe"].id)]},
            "start_time": datetime.utcnow(),
            "expiry_time": datetime.utcnow() + timedelta(days=7),
            "is_archived": False,
            "created_at": datetime.utcnow()
        },
        {
            "title": "HR Policy Update",
            "body": "New remote work policies have been updated. Please review the changes in the employee handbook.",
            "severity": "WARNING",
            "delivery_types": ["in_app", "email"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 120,
            "visibility": {"teams": [str(teams["HR"].id)]},
            "start_time": datetime.utcnow(),
            "expiry_time": datetime.utcnow() + timedelta(days=10),
            "is_archived": False,
            "created_at": datetime.utcnow()
        },
        {
            "title": "Server Monitoring Alert",
            "body": "High CPU usage detected on production servers. Operations team please investigate.",
            "severity": "CRITICAL",
            "delivery_types": ["in_app", "email", "sms"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 60,
            "visibility": {"teams": [str(teams["Engineering"].id), str(teams["Operations"].id)]},
            "start_time": datetime.utcnow(),
            "expiry_time": datetime.utcnow() + timedelta(hours=6),
            "is_archived": False,
            "created_at": datetime.utcnow()
        },
        {
            "title": "Company All-Hands Meeting",
            "body": "Quarterly all-hands meeting scheduled for next Friday at 2 PM in the main conference room.",
            "severity": "INFO",
            "delivery_types": ["in_app"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 120,
            "visibility": {"org": True},
            "start_time": datetime.utcnow(),
            "expiry_time": datetime.utcnow() + timedelta(days=14),
            "is_archived": False,
            "created_at": datetime.utcnow()
        },
        {
            "title": "Development Environment Maintenance",
            "body": "Development servers will be down for maintenance this weekend. Plan accordingly.",
            "severity": "WARNING",
            "delivery_types": ["in_app", "email"],
            "reminder_enabled": True,
            "reminder_freq_minutes": 120,
            "visibility": {"teams": [str(teams["Engineering"].id)]},
            "start_time": datetime.utcnow(),
            "expiry_time": datetime.utcnow() + timedelta(days=4),
            "is_archived": False,
            "created_at": datetime.utcnow()
        }
    ]

    alerts = {}
    for i, alert_data in enumerate(alerts_data):
        alert = alert_service.create_alert(alert_data)
        alerts[f"alert_{i+1}"] = alert
        
        visibility_desc = ""
        if alert_data["visibility"].get("org"):
            visibility_desc = "Organization-wide"
        elif alert_data["visibility"].get("teams"):
            team_names = [team.name for team in teams.values() if team.id in alert_data["visibility"]["teams"]]
            visibility_desc = f"Teams: {', '.join(team_names)}"
        elif alert_data["visibility"].get("users"):
            user_names = [user.name for user in users.values() if user.id in alert_data["visibility"]["users"]]
            visibility_desc = f"Users: {', '.join(user_names)}"
        
        print(f" Created alert: {alert.title} (ID: {alert.id}, Severity: {alert.severity}, Visibility: {visibility_desc})")
    
    print(f"\nSeed data created successfully!")
    print(f"Summary:")
    print(f"  - Teams: {len(teams)}")
    print(f"   - Users: {len(users)}")
    print(f"   - Alerts: {len(alerts)}")
    print(f"\ You can now test the APIs with this data!")
    print(f"   - Use any user ID to test user endpoints")
    print(f"   - Alerts have different visibility settings to test targeting")
    print(f"   - Some alerts will expire soon to test expiry logic")

def main():
    """Main function to run seed data creation."""
    db = next(get_db())
    try:
        create_seed_data(db)
        db.commit()
    except Exception as e:
        print(f" Error creating seed data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()