from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenPair,
    RefreshRequest,
    MeResponse,
)
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehiclePatch
from app.schemas.scan import ScanStartRequest, ScanOut
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationOut,
    ApprovalRequest,
)
from app.schemas.telemetry import TelemetryBatch

__all__ = [
    "LoginRequest",
    "SignupRequest",
    "TokenPair",
    "RefreshRequest",
    "MeResponse",
    "VehicleCreate",
    "VehicleOut",
    "VehiclePatch",
    "ScanStartRequest",
    "ScanOut",
    "RecommendationRequest",
    "RecommendationOut",
    "ApprovalRequest",
    "TelemetryBatch",
]
