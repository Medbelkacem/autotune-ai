from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUserDep, DbSession
from app.models import AnalysisReport, ScanSession, Vehicle

router = APIRouter()


@router.get("/{report_id}")
async def get_report(report_id: UUID, user: CurrentUserDep, db: DbSession) -> dict:
    res = await db.execute(
        select(AnalysisReport, Vehicle)
        .join(ScanSession, ScanSession.id == AnalysisReport.scan_id)
        .join(Vehicle, Vehicle.id == ScanSession.vehicle_id)
        .where(AnalysisReport.id == report_id, Vehicle.org_id == user.org_id)
    )
    row = res.first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "report not found")
    r: AnalysisReport = row[0]
    return {
        "id": str(r.id),
        "scan_id": str(r.scan_id),
        "profile": r.profile,
        "cards": r.cards,
        "health_score": r.health_score,
        "summary": r.summary,
        "created_at": r.created_at,
    }


@router.get("/scan/{scan_id}/latest")
async def get_latest_report_for_scan(
    scan_id: UUID, user: CurrentUserDep, db: DbSession
) -> dict:
    res = await db.execute(
        select(AnalysisReport, Vehicle)
        .join(ScanSession, ScanSession.id == AnalysisReport.scan_id)
        .join(Vehicle, Vehicle.id == ScanSession.vehicle_id)
        .where(ScanSession.id == scan_id, Vehicle.org_id == user.org_id)
        .order_by(AnalysisReport.created_at.desc())
        .limit(1)
    )
    row = res.first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no report for scan")
    r: AnalysisReport = row[0]
    return {
        "id": str(r.id),
        "profile": r.profile,
        "cards": r.cards,
        "health_score": r.health_score,
        "summary": r.summary,
        "created_at": r.created_at,
    }
