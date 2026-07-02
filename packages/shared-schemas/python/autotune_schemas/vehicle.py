from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from autotune_schemas.protocol import Protocol


class EngineSpec(BaseModel):
    code: str
    displacement_cc: int = Field(ge=50, le=20_000)
    config: str  # I3, I4, I6, V6, V8, F4, ...
    induction: str  # NA, Turbo, TwinTurbo, Supercharged, Electric
    cylinders: Optional[int] = None
    valves_per_cylinder: Optional[int] = None
    compression_ratio: Optional[float] = None


class TransmissionSpec(BaseModel):
    type: str  # MT, AT, DCT, DSG, CVT, eCVT
    code: Optional[str] = None
    gears: Optional[int] = Field(default=None, ge=1, le=12)


class EcuSpec(BaseModel):
    vendor: str
    model: str
    hardware_pn: Optional[str] = None
    software_pn: Optional[str] = None
    calibration_pn: Optional[str] = None
    boot_loader: Optional[str] = None
    firmware_sha256: Optional[str] = Field(default=None, min_length=64, max_length=64)


class ModificationSignature(BaseModel):
    detected_signature: str
    family: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    is_known_tune: bool = False
    is_defeat_device_suspect: bool = False


class VehicleIdentity(BaseModel):
    vehicle_identity_id: UUID = Field(default_factory=uuid4)
    vin: str
    vin_confidence: float = Field(ge=0.0, le=1.0)
    manufacturer: str
    model: str
    model_year: int = Field(ge=1980, le=2100)
    engine: EngineSpec
    transmission: TransmissionSpec
    ecu: EcuSpec
    emission_standard: Optional[str] = None  # EU3..EU7, Tier3, LEV-III, CN6b
    fuel_type: str  # Gasoline_RON95, Diesel, E85, LPG, CNG, Hybrid, Electric
    supported_protocols: List[Protocol] = []
    modification_history: List[ModificationSignature] = []
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    signature: Optional[str] = None  # ed25519 base64

    @field_validator("vin")
    @classmethod
    def _validate_vin(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 17:
            raise ValueError("VIN must be 17 characters")
        if any(ch in "IOQ" for ch in v):
            raise ValueError("VIN cannot contain I, O, or Q")
        return v
