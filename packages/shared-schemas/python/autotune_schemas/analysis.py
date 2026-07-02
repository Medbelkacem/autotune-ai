from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Domain(str, Enum):
    FUEL = "fuel"
    IGNITION = "ignition"
    TORQUE_REQUEST = "torque_request"
    THROTTLE = "throttle"
    BOOST = "boost"
    AFR_LAMBDA = "afr_lambda"
    SPEED_LIMITER = "speed_limiter"
    REV_LIMITER = "rev_limiter"
    CAM_TIMING = "cam_timing"
    TEMP_COMPENSATION = "temp_compensation"
    KNOCK = "knock"
    DRIVER_DEMAND = "driver_demand"
    GEAR_STRATEGY = "gear_strategy"


class Citation(BaseModel):
    source_id: str                                 # KG node id or doc anchor
    source_kind: str                               # "kg" | "doc" | "oem_manual" | "fleet_data"
    snippet: Optional[str] = None
    locator: Optional[str] = None                  # page / line / map name
    score: float = Field(ge=0.0, le=1.0)


class CounterFactual(BaseModel):
    if_changed: str                                # natural-language condition
    then_conclusion_changes: str
    affected_metrics: List[str] = []


class Confidence(BaseModel):
    value: float = Field(ge=0.0, le=1.0)
    calibrated: bool = False                       # True if temperature-scaled
    method: str = "ensemble_vote"


class AnalysisCard(BaseModel):
    card_id: UUID = Field(default_factory=uuid4)
    domain: Domain
    title: str
    purpose: str
    inputs: List[str]
    outputs: List[str]
    relationships: List[str] = []
    observed_summary: str
    oem_expected_envelope: Optional[str] = None
    deviation_summary: Optional[str] = None
    risks: List[str] = []
    optimization_opportunities: List[str] = []
    explanation: str
    citations: List[Citation] = []
    counter_factuals: List[CounterFactual] = []
    confidence: Confidence


class AnalysisReport(BaseModel):
    report_id: UUID = Field(default_factory=uuid4)
    vehicle_identity_id: UUID
    calibration_document_id: UUID
    profile_hint: Optional[str] = None
    cards: List[AnalysisCard]
    health_score: int = Field(ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
