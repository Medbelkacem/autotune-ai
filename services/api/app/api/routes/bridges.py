from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.core.deps import CurrentUserDep, DbSession, require_role
from app.models import Bridge

router = APIRouter()


class EnrollRequest(BaseModel):
    serial: str
    model: str
    firmware_version: str
    public_key_b64: str
    attestation_blob_b64: str


class EnrollResponse(BaseModel):
    bridge_id: str
    enrollment_token: str


@router.post("/enroll", response_model=EnrollResponse, status_code=status.HTTP_201_CREATED)
async def enroll(
    payload: EnrollRequest,
    user: CurrentUserDep = require_role("owner", "admin"),  # noqa: B008
    db: DbSession = None,  # type: ignore[assignment]
) -> EnrollResponse:
    # In production: verify TPM/SE attestation_blob against the manufacturer root.
    existing = (
        await db.execute(select(Bridge).where(Bridge.serial == payload.serial))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "bridge already enrolled")
    b = Bridge(
        org_id=user.org_id,
        serial=payload.serial,
        model=payload.model,
        firmware_version=payload.firmware_version,
        public_key_b64=payload.public_key_b64,
        attested=True,
    )
    db.add(b)
    await db.commit()
    await db.refresh(b)
    return EnrollResponse(bridge_id=str(b.id), enrollment_token=f"bridge_{b.id}")


@router.post("/{serial}/heartbeat", status_code=status.HTTP_204_NO_CONTENT)
async def heartbeat(serial: str, db: DbSession) -> None:
    res = await db.execute(select(Bridge).where(Bridge.serial == serial))
    b = res.scalar_one_or_none()
    if b is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "bridge not enrolled")
    b.last_seen_at = datetime.now(timezone.utc)
    await db.commit()


@router.get("")
async def list_bridges(user: CurrentUserDep, db: DbSession) -> list[dict]:
    res = await db.execute(select(Bridge).where(Bridge.org_id == user.org_id))
    return [
        {
            "id": str(b.id),
            "serial": b.serial,
            "model": b.model,
            "firmware_version": b.firmware_version,
            "last_seen_at": b.last_seen_at,
            "attested": b.attested,
        }
        for b in res.scalars().all()
    ]
