from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ARRAY, DateTime, ForeignKey, Integer, LargeBinary, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models._mixins import Timestamps, UUIDPk

if TYPE_CHECKING:
    from app.models.calibration import CalibrationDocument
    from app.models.organization import Organization
    from app.models.scan import ScanSession


class Vehicle(Base, UUIDPk, Timestamps):
    __tablename__ = "vehicle"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vin: Mapped[str] = mapped_column(Text, nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None] = mapped_column(Integer)
    engine_code: Mapped[str | None] = mapped_column(Text)
    transmission_code: Mapped[str | None] = mapped_column(Text)
    fuel_type: Mapped[str | None] = mapped_column(Text)
    emission_standard: Mapped[str | None] = mapped_column(Text)
    modification: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    signed_identity: Mapped[bytes | None] = mapped_column(LargeBinary)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    org: Mapped["Organization"] = relationship(back_populates="vehicles")
    ecu_profiles: Mapped[List["EcuProfile"]] = relationship(
        back_populates="vehicle", cascade="all,delete-orphan"
    )
    scans: Mapped[List["ScanSession"]] = relationship(back_populates="vehicle")

    __table_args__ = (UniqueConstraint("org_id", "vin", name="uq_vehicle_vin_org"),)


class EcuProfile(Base, UUIDPk, Timestamps):
    __tablename__ = "ecu_profile"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicle.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(Text)
    hardware_pn: Mapped[str | None] = mapped_column(Text)
    software_pn: Mapped[str | None] = mapped_column(Text)
    calibration_pn: Mapped[str | None] = mapped_column(Text)
    firmware_sha256: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    protocols: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    vehicle: Mapped["Vehicle"] = relationship(back_populates="ecu_profiles")
    calibration_documents: Mapped[List["CalibrationDocument"]] = relationship(
        back_populates="ecu_profile"
    )
