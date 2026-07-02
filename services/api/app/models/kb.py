from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector  # type: ignore[import-not-found]
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._mixins import Timestamps, UUIDPk

# Embedding dimensions (voyage-3 = 1024, bge-large = 1024, openai-3-large = 3072).
EMBED_DIM = 1024


class KbDoc(Base, UUIDPk, Timestamps):
    __tablename__ = "kb_doc"

    title: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)  # oem_manual | fleet_report | sae_paper | a2l
    uri: Mapped[str | None] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)


class KbChunk(Base, UUIDPk, Timestamps):
    __tablename__ = "kb_chunk"

    doc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("kb_doc.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ord: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    locator: Mapped[str | None] = mapped_column(Text)  # page / section / map name


class Embedding(Base, UUIDPk, Timestamps):
    __tablename__ = "embedding"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("kb_chunk.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model: Mapped[str] = mapped_column(Text, nullable=False)
    vec: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM), nullable=False)
