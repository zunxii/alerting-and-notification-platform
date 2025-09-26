from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.v1.admin import admin_alert_routes, admin_user_routes, admin_team_routes
from app.api.v1.user import user_alert_routes, user_notification_routes
from app.core.config import config

app = FastAPI(
    title="Alerting & Notification Platform",
    description="API platform to create, manage, and deliver alerts to users.",
    version="1.0.0",
    contact={
        "name": "Junaid",
        "email": "zunxii.2210@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Include Admin API routers
app.include_router(admin_alert_routes.router, prefix="/api/v1/admin", tags=["Admin - Alerts"])
app.include_router(admin_user_routes.router, prefix="/api/v1/admin", tags=["Admin - Users"])
app.include_router(admin_team_routes.router, prefix="/api/v1/admin", tags=["Admin - Teams"])

# Include User API routers
app.include_router(user_alert_routes.router, prefix="/api/v1/user", tags=["User - Alerts"])
app.include_router(user_notification_routes.router, prefix="/api/v1/user", tags=["User - Notifications"])

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Simple health check endpoint.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "database_url": config.DATABASE_URL.split("@")[1].split("/")[0],  # mask credentials
            "version": app.version
        }
    )

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the Alerting & Notification Platform API!"}