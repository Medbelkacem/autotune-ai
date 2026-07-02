from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Datatype(str, Enum):
    UBYTE = "ubyte"
    SBYTE = "sbyte"
    UWORD = "uword"
    SWORD = "sword"
    ULONG = "ulong"
    SLONG = "slong"
    FLOAT32 = "float32"
    FLOAT64 = "float64"


class ConversionRule(BaseModel):
    formula: str = "PHYS = a + b*RAW"      # ASAM CONV_TYPE LINEAR formula
    a: float = 0.0
    b: float = 1.0
    unit: str = ""
    n_decimals: int = 2


class AxisDef(BaseModel):
    name: str
    unit: str
    values: List[float]
    breakpoints: int = Field(ge=2, le=64)


class MapRecord(BaseModel):
    """A single calibration map (or scalar — values is 1×1)."""

    map_id: UUID = Field(default_factory=uuid4)
    name: str                                  # e.g. KFMIRL, KFZW, FN_INJ_BASE
    address_hex: str
    datatype: Datatype
    conversion: ConversionRule
    x_axis: Optional[AxisDef] = None
    y_axis: Optional[AxisDef] = None
    values: List[List[float]]                  # row-major; scalar = [[x]]
    unit: str = ""
    phys_min: Optional[float] = None
    phys_max: Optional[float] = None
    description: Optional[str] = None
    page_hash_sha256: Optional[str] = None     # checksum of memory page

    @property
    def shape(self) -> Tuple[int, int]:
        return (len(self.values), len(self.values[0]) if self.values else 0)


class CalibrationDocument(BaseModel):
    document_id: UUID = Field(default_factory=uuid4)
    ecu_firmware_sha256: str
    a2l_version: Optional[str] = None
    maps: List[MapRecord]
    page_checksums: dict[str, str] = Field(default_factory=dict)
    # cell-level provenance lets us diff across firmware versions
    provenance: dict[str, str] = Field(default_factory=dict)
