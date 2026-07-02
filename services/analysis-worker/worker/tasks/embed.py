"""Embedding + telemetry persistence tasks."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text

from worker.celery_app import celery_app
from worker.db import db_session

log = logging.getLogger(__name__)


@celery_app.task(name="worker.tasks.embed.persist_telemetry")
def persist_telemetry(batch: dict[str, Any]) -> dict:
    """Persist a TelemetryBatch dict to timescale (or timescale-shaped hypertable)."""
    stream_id = batch["stream_id"]
    points = batch["points"]
    log.info("telemetry.persist stream=%s n=%d", stream_id, len(points))
    with db_session() as s:
        # In production this is a COPY into a hypertable.
        # For skeleton we use a wide insert into a landing table.
        for pt in points:
            s.execute(
                text(
                    "INSERT INTO telemetry_landing (stream_id, ts, channel, value) "
                    "VALUES (:sid, :ts, :ch, :v) ON CONFLICT DO NOTHING"
                ),
                {"sid": stream_id, "ts": pt["ts"], "ch": pt["channel"], "v": pt["value"]},
            )
    return {"stream_id": stream_id, "persisted": len(points)}


@celery_app.task(name="worker.tasks.embed.embed_document")
def embed_document(doc_id: str) -> dict:
    """Chunk a KB doc + generate embeddings + upsert to pgvector + Qdrant."""
    log.info("embed.doc %s", doc_id)
    # placeholder — real path splits text and calls voyage / bge and upserts.
    return {"doc_id": doc_id, "chunks": 0}
