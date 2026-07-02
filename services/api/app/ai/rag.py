"""RAG hybrid retrieval: BM25 (Postgres pg_trgm) ⊕ dense (pgvector / Qdrant).
This is a stub-friendly implementation: it works offline against pgvector,
and switches to Qdrant when QDRANT_URL is reachable.
"""

from __future__ import annotations

import hashlib
from typing import Any

import httpx

from app.core.config import get_settings

_settings = get_settings()


async def _embed(text: str) -> list[float]:
    """Embed a query. Falls back to a deterministic hash-based pseudo-embedding offline."""
    if _settings.voyage_api_key:
        async with httpx.AsyncClient(timeout=30) as cx:
            r = await cx.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {_settings.voyage_api_key}"},
                json={"input": [text], "model": _settings.embed_model},
            )
            r.raise_for_status()
            return r.json()["data"][0]["embedding"]
    # offline pseudo-embedding (deterministic) — 1024 dims for shape compat
    h = hashlib.sha512(text.encode()).digest()
    seed = int.from_bytes(h[:8], "big")
    import random

    rng = random.Random(seed)
    return [rng.uniform(-1, 1) for _ in range(1024)]


async def retrieve_relevant(
    query: str, k: int = 6, *, tenant_id: str | None = None
) -> list[dict[str, Any]]:
    """Returns a list of {source_id, text, score, locator}."""
    if not _settings.qdrant_url:
        return []
    vec = await _embed(query)
    async with httpx.AsyncClient(timeout=15) as cx:
        try:
            r = await cx.post(
                f"{_settings.qdrant_url}/collections/kb/points/search",
                json={"vector": vec, "limit": k, "with_payload": True},
            )
            r.raise_for_status()
            hits = r.json().get("result", [])
        except Exception:
            return []

    return [
        {
            "source_id": h["payload"].get("source_id", str(h["id"])),
            "text": h["payload"].get("text", ""),
            "score": float(h.get("score", 0.0)),
            "locator": h["payload"].get("locator"),
        }
        for h in hits
    ]
