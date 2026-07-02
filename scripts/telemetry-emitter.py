#!/usr/bin/env python3
"""
Synthetic drive-cycle telemetry emitter.

Publishes a realistic RPM / boost / AFR / knock waveform to the API's
/telemetry/ingest endpoint so the live monitor pages have something to draw.

Usage:
    python scripts/telemetry-emitter.py \
        --api http://localhost:8000 \
        --token $ACCESS_TOKEN \
        --stream-id 00000000-0000-0000-0000-000000000000 \
        --rate 25 --duration 120
"""

from __future__ import annotations

import argparse
import asyncio
import math
import random
import time
from datetime import datetime, timezone

import httpx


CHANNELS = ("rpm", "boost", "afr", "lambda", "timing", "coolant_temp",
            "knock", "stft", "ltft", "iat", "map", "throttle",
            "vehicle_speed", "gear", "torque_est", "battery_v")


def _sample(t: float) -> dict[str, float]:
    """Fake a moderate acceleration + cruise."""
    phase = (math.sin(t / 12.0) + 1) / 2   # 0..1
    rpm = 900 + phase * 4600 + random.gauss(0, 30)
    load = phase
    boost = max(0.0, load * 1.6 + random.gauss(0, 0.02))    # bar
    lam = 1.00 - load * 0.18 + random.gauss(0, 0.005)
    timing = 26 - load * 12 + random.gauss(0, 0.4)
    knock = max(0, random.gauss(0.05 + load * 0.3, 0.3))
    return {
        "rpm": rpm,
        "boost": boost,
        "afr": lam * 14.7,
        "lambda": lam,
        "timing": timing,
        "coolant_temp": 88 + random.gauss(0, 0.5),
        "knock": knock,
        "stft": random.gauss(0, 2),
        "ltft": -1.2 + random.gauss(0, 0.4),
        "iat": 32 + random.gauss(0, 0.5),
        "map": 1.0 + boost,
        "throttle": load * 100,
        "vehicle_speed": phase * 180,
        "gear": min(6, max(1, int(phase * 6) + 1)),
        "torque_est": load * 380,
        "battery_v": 14.1 + random.gauss(0, 0.05),
    }


async def _post(cx: httpx.AsyncClient, api: str, token: str, stream_id: str, batch: list[dict]) -> None:
    r = await cx.post(
        f"{api}/v1/telemetry/ingest",
        headers={"Authorization": f"Bearer {token}"},
        json={"stream_id": stream_id, "points": batch},
        timeout=10,
    )
    if r.status_code >= 300:
        print("ingest failed:", r.status_code, r.text[:200])


async def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--api", default="http://localhost:8000")
    p.add_argument("--token", required=True)
    p.add_argument("--stream-id", required=True)
    p.add_argument("--rate", type=int, default=25, help="Hz")
    p.add_argument("--duration", type=int, default=60, help="seconds")
    a = p.parse_args()

    period = 1.0 / a.rate
    t0 = time.time()
    async with httpx.AsyncClient() as cx:
        batch: list[dict] = []
        while time.time() - t0 < a.duration:
            t = time.time() - t0
            s = _sample(t)
            now = datetime.now(timezone.utc).isoformat()
            for ch, val in s.items():
                batch.append({"ts": now, "channel": ch, "value": float(val)})
            if len(batch) >= 200:
                await _post(cx, a.api, a.token, a.stream_id, batch)
                batch = []
            await asyncio.sleep(period)
        if batch:
            await _post(cx, a.api, a.token, a.stream_id, batch)
    print(f"done — sent {a.duration}s of telemetry at {a.rate} Hz across {len(CHANNELS)} channels")


if __name__ == "__main__":
    asyncio.run(main())
