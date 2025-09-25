from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.v1 import alert_routes, notification_routes, user_routes
from app.core.config import config

app = FastAPI(
    title="Alerting & Notification Platform",
    description="API platform to create, manage, and deliver alerts to users.",
    version="1.0.0",
    contact={
        "name": "Your Name / Team",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Include API routers
app.include_router(alert_routes.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(notification_routes.router)

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
