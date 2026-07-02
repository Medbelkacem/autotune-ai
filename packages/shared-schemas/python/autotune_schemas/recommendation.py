from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Profile(str, Enum):
    FUEL_ECONOMY = "fuel_economy"
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    TRACK = "track"
    TOWING = "towing"
    FLEET = "fleet"


class SafetyEnvelope(BaseModel):
    knock_margin_deg: float = Field(ge=0.0)
    egt_max_c: float = Field(le=1100.0)
    lambda_min: float = 0.78
    lambda_max: float = 1.10
    oil_temp_max_c: float = 130.0
    trans_temp_max_c: float = 110.0
    boost_max_overshoot_pct: float = 5.0


class RecommendationDelta(BaseModel):
    """A proposed change to a single map / scalar."""

    map_name: str
    cell_index: Optional[List[int]] = None   # None = scalar
    current_value: float
    proposed_value: float
    rationale: str
    citation_ids: List[str] = []


class ApprovalSignature(BaseModel):
    signer_user_id: UUID
    signer_role: str
    algorithm: str = "ed25519"
    signed_at: datetime = Field(default_factory=datetime.utcnow)
    signature_b64: str
    key_fingerprint: str


class RecommendationBundle(BaseModel):
    bundle_id: UUID = Field(default_factory=uuid4)
    report_id: UUID
    profile: Profile
    deltas: List[RecommendationDelta]
    predicted_gains: Dict[str, Any]          # e.g. {"hp_at_crank_pct": 8.2, "mpg_pct": 4.1}
    safety_score: int = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0.0, le=1.0)
    compatibility_score: int = Field(ge=0, le=100)
    risk_assessment: str
    explanation: str
    safety_envelope: SafetyEnvelope
    status: str = "simulation"               # 'simulation' | 'pending_review' | 'approved' | 'rejected' | 'flashed'
    approval: Optional[ApprovalSignature] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
