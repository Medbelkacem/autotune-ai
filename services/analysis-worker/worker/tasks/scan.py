"""
Long-running scan pipeline:
   1. detect vehicle identity (from bridge / VIN decode)
   2. read ECU calibration (via bridge or synthesized fixture)
   3. run per-domain Analyst agents (fan-out)
   4. write AnalysisReport
"""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from sqlalchemy import text

from worker.celery_app import celery_app
from worker.db import db_session

log = logging.getLogger(__name__)


@celery_app.task(name="worker.tasks.scan.run_scan_pipeline", bind=True)
def run_scan_pipeline(self, scan_id: str) -> dict:
    log.info("scan.pipeline.start scan_id=%s", scan_id)
    with db_session() as s:
        s.execute(
            text("UPDATE scan_session SET status='running' WHERE id=:sid"),
            {"sid": scan_id},
        )

    try:
        asyncio.run(_run(UUID(scan_id)))
        with db_session() as s:
            s.execute(
                text("UPDATE scan_session SET status='completed', ended_at=now() WHERE id=:sid"),
                {"sid": scan_id},
            )
        return {"scan_id": scan_id, "status": "completed"}
    except Exception as e:
        log.exception("scan.pipeline.failed")
        with db_session() as s:
            s.execute(
                text(
                    "UPDATE scan_session SET status='failed', ended_at=now(), "
                    "details = details || jsonb_build_object('error', :err) WHERE id=:sid"
                ),
                {"sid": scan_id, "err": str(e)[:500]},
            )
        raise


async def _run(scan_id: UUID) -> None:
    """
    Full scan pipeline. Uses fixture data if no bridge is attached.
    In production, this would drive the AutoTune Bridge over WebSocket to read the ECU.
    """
    from worker.pipeline.detector import detect_vehicle
    from worker.pipeline.reader import read_calibration
    from worker.pipeline.analyst_fanout import run_analysts
    from worker.pipeline.report_writer import write_report

    vehicle_ident = await detect_vehicle(scan_id)
    calib_doc = await read_calibration(scan_id, vehicle_ident)
    cards = await run_analysts(calibration_doc=calib_doc, vehicle_identity=vehicle_ident)
    await write_report(scan_id, cards=cards, vehicle_identity=vehicle_ident, calibration_doc=calib_doc)
