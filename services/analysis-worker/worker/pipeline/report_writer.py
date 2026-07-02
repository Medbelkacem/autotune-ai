"""
Step 3 (write) — persist AnalysisReport to Postgres, compute health score.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import text

from worker.db import db_session

log = logging.getLogger(__name__)


def _health_score(cards: list[Any]) -> int:
    if not cards:
        return 50
    # weight risk count against confidence
    penalties = 0
    total_conf = 0.0
    for c in cards:
        # c is either an AnalysisCard model or a raw dict
        risks = getattr(c, "risks", None) if hasattr(c, "risks") else c.get("risks", [])
        conf = getattr(c, "confidence", None) if hasattr(c, "confidence") else c.get("confidence", {})
        conf_val = getattr(conf, "value", None) if hasattr(conf, "value") else conf.get("value", 0.5)
        penalties += min(15, 5 * len(risks or []))
        total_conf += float(conf_val)
    avg_conf = total_conf / len(cards)
    return max(0, min(100, int(round(90 - penalties + (avg_conf - 0.5) * 20))))


async def write_report(
    scan_id: UUID,
    *,
    cards: list[Any],
    vehicle_identity: dict[str, Any],
    calibration_doc: dict[str, Any],
) -> None:
    cards_json = [
        (c.model_dump(mode="json") if hasattr(c, "model_dump") else c)
        for c in cards
    ]
    score = _health_score(cards)
    summary = _summarize(cards_json)
    with db_session() as s:
        s.execute(
            text(
                """
                INSERT INTO analysis_report (scan_id, profile, cards, health_score, summary)
                VALUES (:sid, :prof, CAST(:cards AS JSONB), :score, :summ)
                """
            ),
            {
                "sid": str(scan_id),
                "prof": "balanced",
                "cards": json.dumps(cards_json),
                "score": score,
                "summ": summary,
            },
        )
    log.info("report.written scan=%s score=%d", scan_id, score)


def _summarize(cards_json: list[dict]) -> str:
    risks = [r for c in cards_json for r in c.get("risks", [])]
    opps = [o for c in cards_json for o in c.get("optimization_opportunities", [])]
    return (
        f"{len(cards_json)} domains analyzed. "
        f"{len(risks)} risks flagged, {len(opps)} optimization opportunities."
    )
