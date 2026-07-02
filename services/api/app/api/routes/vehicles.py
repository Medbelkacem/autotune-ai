from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.deps import CurrentUserDep, DbSession
from app.models import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehiclePatch

router = APIRouter()


@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    payload: VehicleCreate, user: CurrentUserDep, db: DbSession
) -> VehicleOut:
    v = Vehicle(
        org_id=user.org_id,
        vin=payload.vin,
        manufacturer=payload.manufacturer,
        model=payload.model,
        year=payload.year,
        engine_code=payload.engine_code,
        transmission_code=payload.transmission_code,
        fuel_type=payload.fuel_type,
        emission_standard=payload.emission_standard,
    )
    db.add(v)
    try:
        await db.commit()
    except IntegrityError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, "VIN already exists in org") from e
    await db.refresh(v)
    return VehicleOut.model_validate(v)


@router.get("", response_model=list[VehicleOut])
async def list_vehicles(
    user: CurrentUserDep,
    db: DbSession,
    limit: int = Query(50, le=200),
    cursor: str | None = None,  # opaque base64; not implemented in skeleton
) -> list[VehicleOut]:
    res = await db.execute(
        select(Vehicle)
        .where(Vehicle.org_id == user.org_id, Vehicle.deleted_at.is_(None))
        .order_by(Vehicle.created_at.desc())
        .limit(limit)
    )
    return [VehicleOut.model_validate(v) for v in res.scalars().all()]


@router.get("/{vehicle_id}", response_model=VehicleOut)
async def get_vehicle(vehicle_id: UUID, user: CurrentUserDep, db: DbSession) -> VehicleOut:
    res = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.org_id == user.org_id)
    )
    v = res.scalar_one_or_none()
    if not v:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "vehicle not found")
    return VehicleOut.model_validate(v)


@router.patch("/{vehicle_id}", response_model=VehicleOut)
async def patch_vehicle(
    vehicle_id: UUID, payload: VehiclePatch, user: CurrentUserDep, db: DbSession
) -> VehicleOut:
    res = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.org_id == user.org_id)
    )
    v = res.scalar_one_or_none()
    if not v:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "vehicle not found")
    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(v, field, val)
    await db.commit()
    await db.refresh(v)
    return VehicleOut.model_validate(v)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(vehicle_id: UUID, user: CurrentUserDep, db: DbSession) -> None:
    res = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.org_id == user.org_id)
    )
    v = res.scalar_one_or_none()
    if not v:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "vehicle not found")
    from datetime import datetime, timezone

    v.deleted_at = datetime.now(timezone.utc)
    await db.commit()
