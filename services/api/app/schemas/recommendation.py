from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from autotune_schemas import Profile


class RecommendationRequest(BaseModel):
    report_id: UUID
    profile: Profile
    target_octane: int | None = Field(default=None, ge=87, le=110)
    accept_risks: list[str] = Field(default_factory=list)


class RecommendationOut(BaseModel):
    id: UUID
    report_id: UUID
    safety_score: int
    confidence_score: float
    compat_score: int
    predicted_gains: dict[str, Any]
    status: str
    created_at: datetime
    bundle: dict[str, Any]

    class Config:
        from_attributes = True


class ApprovalRequest(BaseModel):
    """Tuner signs the bundle off-device with their hardware key."""

    signature_b64: str
    key_fingerprint: str
