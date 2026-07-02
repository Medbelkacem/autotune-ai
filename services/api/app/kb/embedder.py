"""
Embedding provider abstraction. Providers:

  - voyage-3 (recommended, 1024 dims)
  - openai-3-large (3072 dims)
  - local hash-based fallback (deterministic, offline; 1024 dims)

The local fallback lets CI + offline dev exercise the whole ingest path
without external API dependencies.
"""

from __future__ import annotations

import hashlib
import random
from typing import Sequence

import httpx

from app.core.config import get_settings

_settings = get_settings()
EMBED_DIM = 1024


class LocalHashEmbedder:
    """Deterministic offline embedder. Uses SHA-512 of text to seed a PRNG."""

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for t in texts:
            h = hashlib.sha512(t.encode()).digest()
            seed = int.from_bytes(h[:8], "big")
            rng = random.Random(seed)
            vec = [rng.gauss(0, 1) for _ in range(EMBED_DIM)]
            n = (sum(x * x for x in vec)) ** 0.5 or 1.0
            out.append([x / n for x in vec])
        return out


class VoyageEmbedder:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=60) as cx:
            r = await cx.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"input": list(texts), "model": self.model},
            )
            r.raise_for_status()
            return [d["embedding"] for d in r.json()["data"]]


def get_embedder():
    if _settings.embed_provider == "voyage" and _settings.voyage_api_key:
        return VoyageEmbedder(_settings.voyage_api_key, _settings.embed_model)
    return LocalHashEmbedder()
