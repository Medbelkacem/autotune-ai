from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models._mixins import Timestamps, UUIDPk

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle


class ScanSession(Base, UUIDPk, Timestamps):
    __tablename__ = "scan_session"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicle.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="SET NULL"),
        nullable=True,
    )
    bridge_id: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="running")
    details: Mapped[dict] = mapped_column(JSONB, default=dict)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="scans")
    reports: Mapped[List["AnalysisReport"]] = relationship(back_populates="scan")


class AnalysisReport(Base, UUIDPk, Timestamps):
    __tablename__ = "analysis_report"

    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scan_session.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    profile: Mapped[str] = mapped_column(Text, nullable=False)
    cards: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    health_score: Mapped[int | None] = mapped_column(Integer)
    summary: Mapped[str | None] = mapped_column(Text)

    scan: Mapped["ScanSession"] = relationship(back_populates="reports")
    recommendations: Mapped[List["Recommendation"]] = relationship(back_populates="report")


class Recommendation(Base, UUIDPk, Timestamps):
    __tablename__ = "recommendation"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_report.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    safety_score: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    compat_score: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_gains: Mapped[dict] = mapped_column(JSONB, default=dict)
    bundle: Mapped[dict] = mapped_column(JSONB, nullable=False)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="SET NULL"),
    )
    signed_blob: Mapped[bytes | None] = mapped_column(LargeBinary)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="simulation")

    report: Mapped["AnalysisReport"] = relationship(back_populates="recommendations")
