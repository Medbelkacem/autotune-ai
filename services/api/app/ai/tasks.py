"""
Celery task stubs that mirror what the analysis-worker exposes.
The API uses .delay() to enqueue; the worker module owns the actual implementations.
"""

from __future__ import annotations

from celery import Celery

from app.core.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "autotune-api-tasks",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_result_backend,
)
celery_app.conf.task_default_queue = "analysis"
celery_app.conf.task_routes = {
    "worker.tasks.scan.*": {"queue": "analysis"},
    "worker.tasks.embed.*": {"queue": "embedding"},
    "worker.tasks.sim.*": {"queue": "simulation"},
}


# Sender-side stubs — the actual task bodies live in the worker.
@celery_app.task(name="worker.tasks.scan.run_scan_pipeline")
def run_scan_pipeline(scan_id: str) -> None: ...


@celery_app.task(name="worker.tasks.embed.persist_telemetry")
def persist_telemetry(batch: dict) -> None: ...
