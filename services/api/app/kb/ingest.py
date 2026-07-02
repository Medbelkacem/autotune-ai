"""
End-to-end ingestion:
    text/A2L → chunks → embeddings → (pgvector + Qdrant) → knowledge graph edge.

Idempotent: content-hashed IDs.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Sequence
from uuid import UUID, uuid4

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.kb.chunker import Chunk
from app.kb.embedder import get_embedder
from app.models import Embedding, KbChunk, KbDoc

log = logging.getLogger(__name__)
_settings = get_settings()


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


async def upsert_doc(db: AsyncSession, *, title: str, source: str, text: str, meta: dict | None = None) -> KbDoc:
    sha = content_hash(text)
    existing = (await db.execute(select(KbDoc).where(KbDoc.sha256 == sha))).scalar_one_or_none()
    if existing:
        return existing
    doc = KbDoc(id=uuid4(), title=title, source=source, sha256=sha, meta=meta or {})
    db.add(doc)
    await db.flush()
    return doc


async def ingest_chunks(
    db: AsyncSession,
    doc: KbDoc,
    chunks: Sequence[Chunk],
) -> list[UUID]:
    embedder = get_embedder()
    texts = [c.text for c in chunks]
    vecs = await embedder.embed(texts)

    chunk_ids: list[UUID] = []
    for ord_, (chunk, vec) in enumerate(zip(chunks, vecs)):
        kc = KbChunk(
            id=uuid4(),
            doc_id=doc.id,
            ord=ord_,
            text=chunk.text,
            locator=chunk.locator,
        )
        db.add(kc)
        await db.flush()
        db.add(Embedding(id=uuid4(), chunk_id=kc.id, model=_settings.embed_model, vec=vec))
        chunk_ids.append(kc.id)

    await _mirror_to_qdrant(chunks, vecs, doc.title)
    return chunk_ids


async def _mirror_to_qdrant(chunks: Sequence[Chunk], vecs: Sequence[list[float]], title: str) -> None:
    if not _settings.qdrant_url:
        return
    points = [
        {
            "id": ord_,
            "vector": vec,
            "payload": {"text": chunk.text, "locator": chunk.locator, "source_id": chunk.locator, "title": title},
        }
        for ord_, (chunk, vec) in enumerate(zip(chunks, vecs))
    ]
    try:
        async with httpx.AsyncClient(timeout=30) as cx:
            # ensure collection
            await cx.put(
                f"{_settings.qdrant_url}/collections/kb",
                json={"vectors": {"size": len(vecs[0]), "distance": "Cosine"}},
            )
            await cx.put(f"{_settings.qdrant_url}/collections/kb/points", json={"points": points})
    except Exception as e:  # noqa: BLE001
        log.warning("qdrant.mirror.failed: %s", e)
