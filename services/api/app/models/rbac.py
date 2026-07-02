from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._mixins import UUIDPk


class Role(Base, UUIDPk):
    __tablename__ = "role"
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class Permission(Base, UUIDPk):
    __tablename__ = "permission"
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)


class RolePermission(Base):
    __tablename__ = "role_permission"
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE")
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("permission.id", ondelete="CASCADE")
    )
    __table_args__ = (PrimaryKeyConstraint("role_id", "permission_id"),)


class RoleAssignment(Base):
    __tablename__ = "role_assignment"
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE")
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE")
    )
    scope: Mapped[str] = mapped_column(Text, nullable=False, default="org")
    __table_args__ = (PrimaryKeyConstraint("user_id", "role_id", "scope"),)
