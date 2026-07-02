from fastapi import APIRouter

from app.api.routes import (
    auth,
    health,
    vehicles,
    scans,
    reports,
    recommendations,
    telemetry,
    bridges,
    ai,
    billing,
    mfa,
    analytics,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(mfa.router, prefix="/mfa", tags=["mfa"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
api_router.include_router(bridges.router, prefix="/bridges", tags=["bridges"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
