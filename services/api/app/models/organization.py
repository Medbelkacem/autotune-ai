from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models._mixins import Timestamps, UUIDPk

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vehicle import Vehicle


class Organization(Base, UUIDPk, Timestamps):
    __tablename__ = "organization"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    plan: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="free",
    )
    region: Mapped[str] = mapped_column(String(8), nullable=False, default="US")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    users: Mapped[List["User"]] = relationship(back_populates="org", cascade="all,delete-orphan")
    vehicles: Mapped[List["Vehicle"]] = relationship(back_populates="org")
    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="org")

    __table_args__ = (
        CheckConstraint(
            "plan IN ('free','pro','workshop','enterprise','oem','gov')",
            name="organization_plan_check",
        ),
    )


class Subscription(Base, UUIDPk, Timestamps):
    __tablename__ = "subscription"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stripe_subscription_id: Mapped[str | None] = mapped_column(Text)
    plan: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    seats: Mapped[int] = mapped_column(nullable=False, default=1)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")

    org: Mapped["Organization"] = relationship(back_populates="subscriptions")
