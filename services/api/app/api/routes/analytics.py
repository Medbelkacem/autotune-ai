from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import func, select

from app.core.deps import CurrentUserDep, DbSession
from app.models import (
    AnalysisReport,
    HealthEvent,
    Recommendation,
    ScanSession,
    Vehicle,
)

router = APIRouter()


@router.get("/summary")
async def summary(user: CurrentUserDep, db: DbSession) -> dict:
    """Workshop-level rollup for the overview dashboard."""
    total_vehicles = (
        await db.execute(
            select(func.count(Vehicle.id)).where(
                Vehicle.org_id == user.org_id, Vehicle.deleted_at.is_(None)
            )
        )
    ).scalar_one()

    active_scans = (
        await db.execute(
            select(func.count(ScanSession.id))
            .join(Vehicle, Vehicle.id == ScanSession.vehicle_id)
            .where(Vehicle.org_id == user.org_id, ScanSession.status.in_(["queued", "running"]))
        )
    ).scalar_one()

    avg_health = (
        await db.execute(
            select(func.avg(AnalysisReport.health_score))
            .join(ScanSession, ScanSession.id == AnalysisReport.scan_id)
            .join(Vehicle, Vehicle.id == ScanSession.vehicle_id)
            .where(Vehicle.org_id == user.org_id)
        )
    ).scalar()

    pending_approvals = (
        await db.execute(
            select(func.count(Recommendation.id))
            .join(AnalysisReport, AnalysisReport.id == Recommendation.report_id)
            .join(ScanSession, ScanSession.id == AnalysisReport.scan_id)
            .join(Vehicle, Vehicle.id == ScanSession.vehicle_id)
            .where(
                Vehicle.org_id == user.org_id,
                Recommendation.status.in_(["simulation", "pending_review"]),
            )
        )
    ).scalar_one()

    return {
        "total_vehicles": int(total_vehicles or 0),
        "active_scans": int(active_scans or 0),
        "avg_health_score": round(float(avg_health), 1) if avg_health is not None else None,
        "pending_approvals": int(pending_approvals or 0),
    }


@router.get("/alerts")
async def alerts(user: CurrentUserDep, db: DbSession, limit: int = 20) -> list[dict]:
    res = await db.execute(
        select(HealthEvent, Vehicle)
        .join(Vehicle, Vehicle.id == HealthEvent.stream_id)  # NB: join on stream in prod
        .where(Vehicle.org_id == user.org_id)
        .order_by(HealthEvent.created_at.desc())
        .limit(limit)
    )
    out = []
    for ev, veh in res.all():
        out.append(
            {
                "id": str(ev.id),
                "severity": ev.severity,
                "channel": ev.channel,
                "description": ev.description,
                "vehicle_vin_last6": veh.vin[-6:],
                "created_at": ev.created_at,
            }
        )
    return out
