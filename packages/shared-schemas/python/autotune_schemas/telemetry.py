from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TelemetryChannel(str, Enum):
    RPM = "rpm"
    BOOST = "boost"
    AFR = "afr"
    LAMBDA = "lambda"
    TIMING = "timing"
    COOLANT_TEMP = "coolant_temp"
    OIL_TEMP = "oil_temp"
    KNOCK = "knock"
    STFT = "stft"
    LTFT = "ltft"
    BATTERY_V = "battery_v"
    TURBO_EFF = "turbo_eff"
    INJ_DUTY = "inj_duty"
    IAT = "iat"
    MAF = "maf"
    MAP = "map"
    THROTTLE = "throttle"
    VEHICLE_SPEED = "vehicle_speed"
    GEAR = "gear"
    TORQUE_EST = "torque_est"


class TelemetryPoint(BaseModel):
    stream_id: UUID
    ts: datetime = Field(default_factory=datetime.utcnow)
    channel: TelemetryChannel
    value: float


class HealthEvent(BaseModel):
    stream_id: UUID
    ts: datetime = Field(default_factory=datetime.utcnow)
    severity: str   # 'info' | 'warning' | 'critical'
    channel: TelemetryChannel
    description: str
    value: Optional[float] = None
    threshold: Optional[float] = None


class HealthScore(BaseModel):
    vehicle_id: UUID
    score: int = Field(ge=0, le=100)
    sub_scores: dict[str, float] = Field(default_factory=dict)
    computed_at: datetime = Field(default_factory=datetime.utcnow)
