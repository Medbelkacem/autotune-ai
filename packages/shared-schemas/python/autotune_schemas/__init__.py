"""Shared Pydantic schemas for AutoTune AI."""
from autotune_schemas.vehicle import (
    VehicleIdentity,
    EngineSpec,
    TransmissionSpec,
    EcuSpec,
    ModificationSignature,
)
from autotune_schemas.calibration import (
    CalibrationDocument,
    MapRecord,
    AxisDef,
    Datatype,
    ConversionRule,
)
from autotune_schemas.analysis import (
    AnalysisCard,
    AnalysisReport,
    Domain,
    Confidence,
    Citation,
    CounterFactual,
)
from autotune_schemas.recommendation import (
    Profile,
    RecommendationBundle,
    RecommendationDelta,
    SafetyEnvelope,
    ApprovalSignature,
)
from autotune_schemas.telemetry import (
    TelemetryPoint,
    TelemetryChannel,
    HealthEvent,
    HealthScore,
)
from autotune_schemas.protocol import Protocol

__all__ = [
    "VehicleIdentity",
    "EngineSpec",
    "TransmissionSpec",
    "EcuSpec",
    "ModificationSignature",
    "CalibrationDocument",
    "MapRecord",
    "AxisDef",
    "Datatype",
    "ConversionRule",
    "AnalysisCard",
    "AnalysisReport",
    "Domain",
    "Confidence",
    "Citation",
    "CounterFactual",
    "Profile",
    "RecommendationBundle",
    "RecommendationDelta",
    "SafetyEnvelope",
    "ApprovalSignature",
    "TelemetryPoint",
    "TelemetryChannel",
    "HealthEvent",
    "HealthScore",
    "Protocol",
]
