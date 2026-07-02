from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUserDep, DbSession
from app.models import ScanSession, Vehicle
from app.schemas.scan import ScanOut, ScanStartRequest

router = APIRouter()


@router.post("", response_model=ScanOut, status_code=status.HTTP_202_ACCEPTED)
async def start_scan(
    payload: ScanStartRequest, user: CurrentUserDep, db: DbSession
) -> ScanOut:
    v = (
        await db.execute(
            select(Vehicle).where(
                Vehicle.id == payload.vehicle_id,
                Vehicle.org_id == user.org_id,
            )
        )
    ).scalar_one_or_none()
    if not v:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "vehicle not found")

    scan = ScanSession(
        vehicle_id=v.id,
        user_id=user.user_id,
        bridge_id=payload.bridge_serial,
        status="queued",
        details={"fast_mode": payload.fast_mode},
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # Dispatch to the analysis worker (Celery)
    from app.ai.tasks import run_scan_pipeline  # local import to avoid circular

    run_scan_pipeline.delay(str(scan.id))

    return ScanOut.model_validate(scan)


@router.get("/{scan_id}", response_model=ScanOut)
async def get_scan(scan_id: UUID, user: CurrentUserDep, db: DbSession) -> ScanOut:
    res = await db.execute(
        select(ScanSession, Vehicle)
        .join(Vehicle, Vehicle.id == ScanSession.vehicle_id)
        .where(ScanSession.id == scan_id, Vehicle.org_id == user.org_id)
    )
    row = res.first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "scan not found")
    return ScanOut.model_validate(row[0])


@router.post("/{scan_id}/cancel", response_model=ScanOut)
async def cancel_scan(scan_id: UUID, user: CurrentUserDep, db: DbSession) -> ScanOut:
    res = await db.execute(
        select(ScanSession, Vehicle)
        .join(Vehicle, Vehicle.id == ScanSession.vehicle_id)
        .where(ScanSession.id == scan_id, Vehicle.org_id == user.org_id)
    )
    row = res.first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "scan not found")
    scan: ScanSession = row[0]
    if scan.status in {"completed", "failed", "cancelled"}:
        return ScanOut.model_validate(scan)
    scan.status = "cancelled"
    scan.ended_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(scan)
    return ScanOut.model_validate(scan)
