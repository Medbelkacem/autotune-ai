from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models._mixins import Timestamps, UUIDPk

if TYPE_CHECKING:
    from app.models.vehicle import EcuProfile


class CalibrationDocument(Base, UUIDPk, Timestamps):
    __tablename__ = "calibration_document"

    ecu_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ecu_profile.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    a2l_version: Mapped[str | None] = mapped_column(Text)
    page_checksums: Mapped[dict] = mapped_column(JSONB, default=dict)
    provenance: Mapped[dict] = mapped_column(JSONB, default=dict)
    s3_uri: Mapped[str | None] = mapped_column(Text)  # raw blob in object store

    ecu_profile: Mapped["EcuProfile"] = relationship(back_populates="calibration_documents")
    maps: Mapped[List["MapRecord"]] = relationship(
        back_populates="document", cascade="all,delete-orphan"
    )


class MapRecord(Base, UUIDPk, Timestamps):
    __tablename__ = "map_record"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("calibration_document.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    address_hex: Mapped[str] = mapped_column(Text, nullable=False)
    datatype: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str | None] = mapped_column(Text)
    phys_min: Mapped[float | None] = mapped_column(Numeric)
    phys_max: Mapped[float | None] = mapped_column(Numeric)
    rows: Mapped[int] = mapped_column(Integer, default=1)
    cols: Mapped[int] = mapped_column(Integer, default=1)
    values: Mapped[dict] = mapped_column(JSONB, nullable=False)  # encoded matrix
    axes: Mapped[dict] = mapped_column(JSONB, default=dict)
    description: Mapped[str | None] = mapped_column(Text)
    page_hash_sha256: Mapped[str | None] = mapped_column(Text)

    document: Mapped["CalibrationDocument"] = relationship(back_populates="maps")
