from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ScanStartRequest(BaseModel):
    vehicle_id: UUID
    bridge_serial: str | None = None
    fast_mode: bool = Field(default=False, description="Skip deep memory reads, ~5 s scan")


class ScanOut(BaseModel):
    id: UUID
    vehicle_id: UUID
    status: str
    started_at: datetime
    ended_at: datetime | None
    bridge_id: str | None
    details: dict = {}

    class Config:
        from_attributes = True
