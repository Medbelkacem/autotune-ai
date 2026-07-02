from __future__ import annotations

import logging

from celery import Celery
from celery.signals import setup_logging

from worker.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "autotune-analysis-worker",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_result_backend,
    include=[
        "worker.tasks.scan",
        "worker.tasks.embed",
        "worker.tasks.sim",
    ],
)

celery_app.conf.update(
    task_default_queue="analysis",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_transport_options={"visibility_timeout": 3600},
    task_routes={
        "worker.tasks.scan.*": {"queue": "analysis"},
        "worker.tasks.embed.*": {"queue": "embedding"},
        "worker.tasks.sim.*": {"queue": "simulation"},
    },
    task_time_limit=15 * 60,
    task_soft_time_limit=10 * 60,
)


@setup_logging.connect
def _configure_logging(**_kwargs) -> None:
    logging.basicConfig(
        level=getattr(logging, _settings.log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
