# Alerting & Notification Platform

A lightweight, extensible alerting and notification system built with FastAPI that balances admin configurability with user control. The system ensures clean OOP design, extensibility, and provides recurring reminders every 2 hours until users explicitly snooze alerts.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Setup Guide](#quick-setup-guide)
- [API Documentation](#api-documentation)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Troubleshooting](#troubleshooting)

## Overview

This platform allows administrators to create and manage alerts with configurable visibility (organization-wide, team-specific, or user-specific), while providing end users with the ability to receive, read, and snooze notifications. The system implements automatic 2-hour reminder cycles and daily snooze resets.

### Key Capabilities

- **Admin Features**: Create, update, archive alerts with flexible targeting
- **User Features**: Receive alerts, mark as read/unread, snooze functionality
- **Analytics**: Comprehensive dashboard with engagement metrics
- **Automation**: Scheduled reminders and daily snooze resets
- **Extensibility**: Plugin-based notification channels (In-App, Email, SMS)

## Features

### MVP Features (Implemented)
- ✅ Alert Management with CRUD operations
- ✅ Visibility Control (Organization, Team, User-level)
- ✅ In-App Notifications with real-time delivery
- ✅ Reminder System with 2-hour recurring cycles
- ✅ Snooze Management with daily reset
- ✅ Analytics Dashboard with comprehensive metrics
- ✅ Scheduler Service for automated jobs
- ✅ User & Team Management

### Future Scope (Extensible)
- 🔄 Multi-Channel Delivery (Email, SMS)
- 🔄 Custom Reminder Frequency beyond 2-hour intervals
- 🔄 Role-based Access Control with granular permissions
- 🔄 Push Notifications for mobile integration
- 🔄 Escalation Rules with automatic severity upgrades

## Quick Setup Guide

### 1. Clone and Setup Environment

```bash
git clone https://github.com/yourusername/alerting-platform.git
cd alerting-platform
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:
```env
DATABASE_URL="postgresql://postgres:your_password@db.your_project.supabase.co:5432/postgres"
```

### 3. Initialize Database

```bash
python -m app.db.create_tables
python seed.py
```

### 4. Run Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access Application

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Documentation

### Admin Endpoints

#### Alert Management (`/api/v1/admin/alerts`)

- **POST** `/api/v1/admin/alerts/`  
  _Create new alert_
  ```json
  {
    "title": "System Maintenance Scheduled",
    "body": "Scheduled maintenance will occur tonight from 11 PM to 2 AM. Please save your work.",
    "severity": "WARNING",
    "delivery_types": ["in_app"],
    "reminder_enabled": true,
    "reminder_freq_minutes": 120,
    "visibility": { "org": true },
    "start_time": "2025-09-26T16:36:07.226243",
    "expiry_time": "2025-09-27T16:36:07.226247",
    "is_archived": false,
    "created_at": "2025-09-26T16:36:07.226256"
  }
  ```

- **PUT** `/api/v1/admin/alerts/{alert_id}`  
  _Update alert_
  ```json
  {
    "title": "Updated Alert Title",
    "body": "Updated alert message",
    "severity": "CRITICAL"
  }
  ```

- **POST** `/api/v1/admin/alerts/{alert_id}/archive`  
  _Archive alert_  
  _No body required_

- **DELETE** `/api/v1/admin/alerts/{alert_id}`  
  _Delete alert_  
  _No body required_

---

#### User Management (`/api/v1/admin/users`)

- **POST** `/api/v1/admin/users/`  
  _Create new user_
  ```json
  {
    "name": "John Doe",
    "team_id": "<engineering_team_uuid>"
  }
  ```

- **PUT** `/api/v1/admin/users/{user_id}`  
  _Update user_
  ```json
  {
    "name": "John Smith"
  }
  ```

- **PUT** `/api/v1/admin/users/{user_id}/team`  
  _Assign user to team_
  ```json
  {
    "team_id": "<marketing_team_uuid>"
  }
  ```

- **DELETE** `/api/v1/admin/users/{user_id}`  
  _Delete user_  
  _No body required_

---

#### Team Management (`/api/v1/admin/teams`)

- **POST** `/api/v1/admin/teams/`  
  _Create new team_
  ```json
  {
    "name": "Engineering"
  }
  ```

- **PUT** `/api/v1/admin/teams/{team_id}`  
  _Update team_
  ```json
  {
    "name": "Engineering & DevOps"
  }
  ```

- **DELETE** `/api/v1/admin/teams/{team_id}`  
  _Delete team_  
  _No body required_

---

#### System Management (`/api/v1/admin/system`)

- **POST** `/api/v1/admin/system/channels/test`  
  _Test channel configuration_
  ```json
  {
    "type": "email",
    "config": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "alerts@company.com",
      "password": "yourpassword",
      "from_address": "alerts@company.com"
    }
  }
  ```

- **POST** `/api/v1/admin/system/scheduler/start`  
  _No body required_

- **POST** `/api/v1/admin/system/scheduler/stop`  
  _No body required_

- **POST** `/api/v1/admin/system/scheduler/jobs/{job_id}/trigger`  
  _No body required_

- **POST** `/api/v1/admin/system/scheduler/reminders/trigger`  
  _No body required_

- **POST** `/api/v1/admin/system/scheduler/snooze/reset`  
  _No body required_

- **POST** `/api/v1/admin/system/maintenance/cleanup`  
  _No body required_

---

### User Endpoints

#### Alert Feed (`/api/v1/user/alerts`)

- **POST** `/api/v1/user/alerts/{alert_id}/read/{user_id}`  
  _Mark alert as read_  
  _No body required_

- **POST** `/api/v1/user/alerts/{alert_id}/unread/{user_id}`  
  _Mark alert as unread_  
  _No body required_

- **POST** `/api/v1/user/alerts/{alert_id}/snooze/{user_id}`  
  _Snooze alert for today_  
  _No body required_

---

#### Notifications (`/api/v1/user/notifications`)

- **POST** `/api/v1/user/notifications/deliveries/{delivery_id}/read`  
  _Mark delivery as read_  
  _No body required_

- **POST** `/api/v1/user/notifications/reminders`  
  _Trigger reminders manually_  
  _No body required_

- **POST** `/api/v1/user/notifications/alerts/{alert_id}/deliver/{user_id}`  
  _Deliver specific alert to user_  
  _No body required_

- **POST** `/api/v1/user/notifications/alerts/{alert_id}/deliver/{user_id}/channels`  
  _Deliver alert with specific channels_
  ```json
  {
    "channel_types": ["in_app", "email", "sms"]
  }
  ```

---

**Note:**  
Replace `<engineering_team_uuid>`, `<marketing_team_uuid>`, and other UUIDs with actual values from your database or seed data.

---



## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin APIs    │    │   User APIs     │    │  System APIs    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ Alert CRUD      │    │ Alert Feed      │    │ Scheduler Mgmt  │
│ User Management │    │ Read/Unread     │    │ System Health   │
│ Analytics       │    │ Snooze Control  │    │ Channel Config  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Service Layer  │
                    ├─────────────────┤
                    │ NotificationSvc │
                    │ AlertService    │
                    │ AnalyticsSvc    │
                    │ SchedulerSvc    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Repository Layer│
                    ├─────────────────┤
                    │ AlertRepo       │
                    │ UserRepo        │
                    │ DeliveryRepo    │
                    │ PreferenceRepo  │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │   (Supabase)    │
                    └─────────────────┘
```

## Technology Stack

- **Framework**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL (via Supabase)
- **ORM**: SQLAlchemy
- **Scheduler**: APScheduler
- **Documentation**: OpenAPI/Swagger

### Entity Relationships
- Users belong to Teams (many-to-one)
- Alerts can target Users, Teams, or Organization (flexible visibility)
- NotificationDeliveries track each alert sent to each user
- UserAlertPreferences manage read/snooze state per user-alert pair

## Design Patterns

### 1. Repository Pattern
```python
class AlertRepository:
    def create_alert(self, alert_data): pass
    def get_alert_by_id(self, alert_id): pass
    def get_active_alerts(self): pass
```

### 2. Service Layer Pattern
```python
class NotificationService:
    def trigger_reminders(self): pass
    def deliver(self, alert, user): pass
    def should_deliver(self, alert, user): pass
```

### 3. Strategy Pattern (Channels)
```python
class NotificationChannel:
    def send(self, alert, user): pass

class InAppChannel(NotificationChannel): pass
class EmailChannel(NotificationChannel): pass
```

## Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Verify DATABASE_URL format in .env
python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL'))
print('Connection successful!' if engine.connect() else 'Connection failed')
"
```

**Table Creation Issues**
```bash
python -m app.db.create_tables
```

**Scheduler Not Working**
```bash
# Check status
curl http://localhost:8000/api/v1/admin/system/scheduler/status

# Manual start
curl -X POST http://localhost:8000/api/v1/admin/system/scheduler/start
```

**Missing Dependencies**
```bash
pip install -r requirements.txt --force-reinstall
```

## Key Features Implementation

### 2-Hour Reminder System
Automated via APScheduler running every 2 hours, checks user preferences and snooze status, respects per-alert reminder frequency settings.

### Daily Snooze Reset
Runs automatically at midnight via cron trigger, clears previous day's snooze flags, ensures alerts resume delivery the next day.

### Flexible Visibility System
```json
{
  "visibility": {
    "org": true,
    "teams": ["eng", "ops"],
    "users": ["user1"]
  }
}
```

### Comprehensive Analytics
Real-time delivery and read metrics, severity-based breakdowns, user engagement tracking, system health monitoring.

### Extensible Architecture
Plugin-based notification channels, configurable reminder frequencies, future-ready for new features.

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Follow PEP 8 style guidelines, add type hints, include docstrings
4. Submit pull request

## Support

- GitHub issues for bugs and feature requests
- Email: zunxii.2210@gmail.com
- API documentation at `/docs` endpoint

---

Built with ❤️ using FastAPI, SQLAlchemy, and modern Python practices.