from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class VehicleCreate(BaseModel):
    vin: str = Field(min_length=17, max_length=17)
    manufacturer: str | None = None
    model: str | None = None
    year: int | None = Field(default=None, ge=1980, le=2100)
    engine_code: str | None = None
    transmission_code: str | None = None
    fuel_type: str | None = None
    emission_standard: str | None = None
    notes: str | None = None

    @field_validator("vin")
    @classmethod
    def _check_vin(cls, v: str) -> str:
        v = v.strip().upper()
        if any(ch in "IOQ" for ch in v):
            raise ValueError("VIN cannot contain I, O, Q")
        return v


class VehiclePatch(BaseModel):
    manufacturer: str | None = None
    model: str | None = None
    year: int | None = None
    engine_code: str | None = None
    transmission_code: str | None = None
    fuel_type: str | None = None
    emission_standard: str | None = None


class VehicleOut(BaseModel):
    id: UUID
    org_id: UUID
    vin: str
    manufacturer: str | None
    model: str | None
    year: int | None
    engine_code: str | None
    transmission_code: str | None
    fuel_type: str | None
    emission_standard: str | None
    modification: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
