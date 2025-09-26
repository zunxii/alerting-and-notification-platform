# app/services/analytics_service.py
from datetime import datetime, timedelta, date
from typing import Dict, List, Any
from collections import defaultdict

class AnalyticsService:
    """Service for generating analytics and metrics for the alerting platform."""

    def __init__(self, alert_repo, delivery_repo, preference_repo, user_repo):
        self.alert_repo = alert_repo
        self.delivery_repo = delivery_repo
        self.preference_repo = preference_repo
        self.user_repo = user_repo

    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get comprehensive dashboard analytics as specified in PRD."""
        all_alerts = self.alert_repo.get_all_alerts()
        all_deliveries = self.delivery_repo.get_all_deliveries()
        all_users = self.user_repo.get_all_users()
        
        # Basic counts
        total_alerts = len(all_alerts)
        total_users = len(all_users)
        active_alerts = len(self.alert_repo.get_active_alerts())
        
        # Delivery metrics
        total_delivered = len(all_deliveries)
        total_read = len([d for d in all_deliveries if d.read_at is not None])
        read_rate = (total_read / total_delivered * 100) if total_delivered > 0 else 0
        
        # Severity breakdown
        severity_counts = {"Info": 0, "Warning": 0, "Critical": 0}
        for alert in all_alerts:
            severity = alert.severity.title() if alert.severity else "Info"
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Snooze analytics
        snooze_data = self._get_snooze_analytics()
        
        # Recent activity (last 7 days)
        recent_activity = self._get_recent_activity(7)
        
        return {
            "overview": {
                "total_alerts_created": total_alerts,
                "active_alerts": active_alerts,
                "total_users": total_users,
                "alerts_delivered": total_delivered,
                "alerts_read": total_read,
                "read_rate_percentage": round(read_rate, 2)
            },
            "severity_breakdown": severity_counts,
            "snooze_metrics": snooze_data,
            "recent_activity": recent_activity,
            "generated_at": datetime.utcnow()
        }

    def get_alert_analytics(self, alert_id: str) -> Dict[str, Any]:
        """Get detailed analytics for a specific alert."""
        alert = self.alert_repo.get_alert_by_id(alert_id)
        if not alert:
            return None
            
        deliveries = self.delivery_repo.get_alert_deliveries(alert_id)
        
        # Calculate metrics
        total_delivered = len(deliveries)
        total_read = len([d for d in deliveries if d.read_at is not None])
        unique_users = len(set(d.user_id for d in deliveries))
        
        # Get snooze count for this alert
        snooze_count = self._get_alert_snooze_count(alert_id)
        
        # Calculate engagement rate
        read_rate = (total_read / total_delivered * 100) if total_delivered > 0 else 0
        
        return {
            "alert": {
                "id": alert.id,
                "title": alert.title,
                "severity": alert.severity,
                "created_at": alert.created_at,
                "is_active": not alert.is_archived and (not alert.expiry_time or alert.expiry_time > datetime.utcnow())
            },
            "delivery_metrics": {
                "total_deliveries": total_delivered,
                "unique_users_reached": unique_users,
                "total_read": total_read,
                "read_rate_percentage": round(read_rate, 2)
            },
            "engagement": {
                "snooze_count": snooze_count,
                "avg_deliveries_per_user": round(total_delivered / unique_users, 2) if unique_users > 0 else 0
            },
            "generated_at": datetime.utcnow()
        }

    def get_alert_performance_metrics(self, alert_id: str) -> Dict[str, Any]:
        """Get performance metrics for alert delivery and engagement."""
        alert = self.alert_repo.get_alert_by_id(alert_id)
        if not alert:
            return None
            
        deliveries = self.delivery_repo.get_alert_deliveries(alert_id)
        
        # Time-based analysis
        delivery_times = []
        read_times = []
        
        for delivery in deliveries:
            delivery_times.append(delivery.delivered_at)
            if delivery.read_at:
                time_to_read = (delivery.read_at - delivery.delivered_at).total_seconds() / 60  # minutes
                read_times.append(time_to_read)
        
        # Calculate averages
        avg_time_to_read = sum(read_times) / len(read_times) if read_times else 0
        
        return {
            "alert_id": alert_id,
            "performance": {
                "average_time_to_read_minutes": round(avg_time_to_read, 2),
                "fastest_read_minutes": round(min(read_times), 2) if read_times else 0,
                "slowest_read_minutes": round(max(read_times), 2) if read_times else 0,
                "total_deliveries": len(deliveries),
                "delivery_success_rate": 100.0  # Assuming all deliveries succeed for MVP
            },
            "timeline": {
                "first_delivered": min(delivery_times) if delivery_times else None,
                "last_delivered": max(delivery_times) if delivery_times else None
            }
        }

    def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        # Recent deliveries
        all_deliveries = self.delivery_repo.get_all_deliveries()
        recent_deliveries = [d for d in all_deliveries if d.delivered_at >= last_24h]
        
        # Active vs inactive alerts
        all_alerts = self.alert_repo.get_all_alerts()
        active_alerts = self.alert_repo.get_active_alerts()
        
        # Calculate health score (simplified)
        total_alerts = len(all_alerts)
        active_ratio = len(active_alerts) / total_alerts if total_alerts > 0 else 0
        recent_activity_ratio = len(recent_deliveries) / len(all_deliveries) if all_deliveries else 0
        
        health_score = (active_ratio * 50) + (recent_activity_ratio * 50)
        
        return {
            "health_score": round(health_score, 2),
            "status": "healthy" if health_score > 70 else "warning" if health_score > 40 else "critical",
            "metrics": {
                "total_alerts": total_alerts,
                "active_alerts": len(active_alerts),
                "deliveries_last_24h": len(recent_deliveries),
                "active_alerts_ratio": round(active_ratio * 100, 2),
                "recent_activity_ratio": round(recent_activity_ratio * 100, 2)
            },
            "checked_at": now
        }

    def get_trend_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get trending analytics over specified time period."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        all_deliveries = self.delivery_repo.get_all_deliveries()
        period_deliveries = [d for d in all_deliveries if d.delivered_at >= start_date]
        
        # Group by day
        daily_stats = defaultdict(lambda: {"delivered": 0, "read": 0})
        
        for delivery in period_deliveries:
            day = delivery.delivered_at.date()
            daily_stats[day]["delivered"] += 1
            if delivery.read_at:
                daily_stats[day]["read"] += 1
        
        # Convert to sorted list
        trend_data = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            stats = daily_stats[current_date]
            trend_data.append({
                "date": current_date.isoformat(),
                "delivered": stats["delivered"],
                "read": stats["read"],
                "read_rate": (stats["read"] / stats["delivered"] * 100) if stats["delivered"] > 0 else 0
            })
            current_date += timedelta(days=1)
        
        return {
            "period": f"{days} days",
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "trends": trend_data,
            "summary": {
                "total_delivered": sum(d["delivered"] for d in trend_data),
                "total_read": sum(d["read"] for d in trend_data),
                "average_daily_delivered": round(sum(d["delivered"] for d in trend_data) / len(trend_data), 2),
                "average_daily_read": round(sum(d["read"] for d in trend_data) / len(trend_data), 2)
            }
        }

    def get_severity_breakdown(self) -> Dict[str, Any]:
        """Get detailed breakdown by severity as required by PRD."""
        all_alerts = self.alert_repo.get_all_alerts()
        all_deliveries = self.delivery_repo.get_all_deliveries()
        
        severity_stats = {
            "Info": {"alerts": 0, "deliveries": 0, "read": 0},
            "Warning": {"alerts": 0, "deliveries": 0, "read": 0},
            "Critical": {"alerts": 0, "deliveries": 0, "read": 0}
        }
        
        # Count alerts by severity
        for alert in all_alerts:
            severity = alert.severity.title() if alert.severity else "Info"
            if severity in severity_stats:
                severity_stats[severity]["alerts"] += 1
        
        # Count deliveries and reads by alert severity
        for delivery in all_deliveries:
            alert = self.alert_repo.get_alert_by_id(delivery.alert_id)
            if alert:
                severity = alert.severity.title() if alert.severity else "Info"
                if severity in severity_stats:
                    severity_stats[severity]["deliveries"] += 1
                    if delivery.read_at:
                        severity_stats[severity]["read"] += 1
        
        # Calculate read rates
        for severity in severity_stats:
            stats = severity_stats[severity]
            stats["read_rate"] = (stats["read"] / stats["deliveries"] * 100) if stats["deliveries"] > 0 else 0
        
        return {
            "breakdown": severity_stats,
            "totals": {
                "total_alerts": sum(s["alerts"] for s in severity_stats.values()),
                "total_deliveries": sum(s["deliveries"] for s in severity_stats.values()),
                "total_read": sum(s["read"] for s in severity_stats.values())
            }
        }

    def get_engagement_summary(self) -> Dict[str, Any]:
        """Get user engagement summary."""
        all_users = self.user_repo.get_all_users()
        all_deliveries = self.delivery_repo.get_all_deliveries()
        all_prefs = self.preference_repo.get_all_preferences()
        
        # User engagement metrics
        user_stats = defaultdict(lambda: {"delivered": 0, "read": 0, "snoozed": 0})
        
        for delivery in all_deliveries:
            user_stats[delivery.user_id]["delivered"] += 1
            if delivery.read_at:
                user_stats[delivery.user_id]["read"] += 1
        
        for pref in all_prefs:
            if pref.snoozed_date:
                user_stats[pref.user_id]["snoozed"] += 1
        
        # Calculate engagement tiers
        highly_engaged = sum(1 for stats in user_stats.values() if stats["read"] / max(stats["delivered"], 1) > 0.8)
        moderately_engaged = sum(1 for stats in user_stats.values() if 0.4 <= stats["read"] / max(stats["delivered"], 1) <= 0.8)
        low_engaged = sum(1 for stats in user_stats.values() if stats["read"] / max(stats["delivered"], 1) < 0.4)
        
        return {
            "total_users": len(all_users),
            "engaged_users": len(user_stats),  # Users who received at least one alert
            "engagement_tiers": {
                "highly_engaged": highly_engaged,  # >80% read rate
                "moderately_engaged": moderately_engaged,  # 40-80% read rate  
                "low_engaged": low_engaged  # <40% read rate
            },
            "overall_metrics": {
                "avg_deliveries_per_user": round(len(all_deliveries) / len(all_users), 2) if all_users else 0,
                "avg_read_rate": round(sum(stats["read"] / max(stats["delivered"], 1) for stats in user_stats.values()) / len(user_stats) * 100, 2) if user_stats else 0
            }
        }

    def _get_snooze_analytics(self) -> Dict[str, Any]:
        """Helper method to get snooze analytics."""
        all_prefs = self.preference_repo.get_all_preferences()
        
        # Count snoozes
        total_snoozes = sum(1 for pref in all_prefs if pref.snoozed_date)
        today_snoozes = sum(1 for pref in all_prefs if pref.snoozed_date == date.today())
        
        # Snoozes by alert
        alert_snoozes = defaultdict(int)
        for pref in all_prefs:
            if pref.snoozed_date:
                alert_snoozes[pref.alert_id] += 1
        
        # Most snoozed alert
        most_snoozed = max(alert_snoozes.items(), key=lambda x: x[1]) if alert_snoozes else (None, 0)
        
        return {
            "total_snoozes": total_snoozes,
            "active_snoozes_today": today_snoozes,
            "most_snoozed_alert_id": most_snoozed[0],
            "most_snoozed_count": most_snoozed[1],
            "snoozes_per_alert": dict(alert_snoozes)
        }

    def _get_alert_snooze_count(self, alert_id: str) -> int:
        """Helper method to get snooze count for specific alert."""
        all_prefs = self.preference_repo.get_all_preferences()
        return sum(1 for pref in all_prefs if pref.alert_id == alert_id and pref.snoozed_date)

    def _get_recent_activity(self, days: int) -> Dict[str, Any]:
        """Helper method to get recent activity."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        all_deliveries = self.delivery_repo.get_all_deliveries()
        recent_deliveries = [d for d in all_deliveries if d.delivered_at >= start_date]
        
        all_alerts = self.alert_repo.get_all_alerts()
        recent_alerts = [a for a in all_alerts if a.created_at >= start_date]
        
        return {
            "period_days": days,
            "new_alerts": len(recent_alerts),
            "total_deliveries": len(recent_deliveries),
            "daily_average_deliveries": round(len(recent_deliveries) / days, 2)
        }