from __future__ import annotations

import asyncio
import json
from uuid import UUID

import redis.asyncio as redis_async
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select

from app.core.config import get_settings
from app.core.deps import CurrentUserDep, DbSession, get_current_user
from app.models import TelemetryStream, Vehicle
from app.schemas.telemetry import TelemetryBatch

router = APIRouter()
_settings = get_settings()


def _stream_channel(stream_id: UUID) -> str:
    return f"telemetry:{stream_id}"


@router.post("/streams")
async def create_stream(
    vehicle_id: UUID,
    bridge_serial: str | None = None,
    user: CurrentUserDep = None,  # type: ignore[assignment]
    db: DbSession = None,  # type: ignore[assignment]
) -> dict:
    v = (
        await db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.org_id == user.org_id)
        )
    ).scalar_one_or_none()
    if not v:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "vehicle not found")
    s = TelemetryStream(vehicle_id=v.id, bridge_id=bridge_serial)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return {"stream_id": str(s.id)}


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest(payload: TelemetryBatch, user: CurrentUserDep, db: DbSession) -> dict:
    # tenant guard
    row = (
        await db.execute(
            select(TelemetryStream, Vehicle)
            .join(Vehicle, Vehicle.id == TelemetryStream.vehicle_id)
            .where(TelemetryStream.id == payload.stream_id, Vehicle.org_id == user.org_id)
        )
    ).first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "stream not found")

    # Fan-out to Redis pub/sub for live dashboards; long-term store handled by worker.
    r = redis_async.from_url(str(_settings.redis_url))
    try:
        ch = _stream_channel(payload.stream_id)
        for pt in payload.points:
            await r.publish(
                ch,
                json.dumps(
                    {
                        "ts": pt.ts.isoformat(),
                        "channel": pt.channel.value,
                        "value": pt.value,
                    }
                ),
            )
    finally:
        await r.aclose()

    # Enqueue persistence to timescale
    from app.ai.tasks import persist_telemetry  # local import

    persist_telemetry.delay(payload.model_dump(mode="json"))
    return {"accepted": len(payload.points)}


@router.websocket("/ws/{stream_id}")
async def ws_stream(
    websocket: WebSocket,
    stream_id: UUID,
    token: str = Query(...),  # access token over ws query, since headers are awkward in browsers
) -> None:
    """Real-time fan-out from Redis pub/sub. Tokens are short-lived (5 min)."""
    # auth
    try:
        await get_current_user(authorization=f"Bearer {token}")
    except HTTPException:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    r = redis_async.from_url(str(_settings.redis_url))
    pubsub = r.pubsub()
    await pubsub.subscribe(_stream_channel(stream_id))

    try:
        async for msg in pubsub.listen():
            if msg["type"] != "message":
                continue
            await websocket.send_text(msg["data"].decode() if isinstance(msg["data"], bytes) else msg["data"])
    except WebSocketDisconnect:
        pass
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe(_stream_channel(stream_id))
        await pubsub.aclose()
        await r.aclose()
