from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from autotune_schemas import TelemetryChannel


class TelemetryPointIn(BaseModel):
    channel: TelemetryChannel
    ts: datetime = Field(default_factory=datetime.utcnow)
    value: float


class TelemetryBatch(BaseModel):
    stream_id: UUID
    points: list[TelemetryPointIn] = Field(min_length=1, max_length=5000)
