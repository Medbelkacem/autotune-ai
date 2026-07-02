"""1-D engine simulation tasks — used to score recommendations offline."""

from __future__ import annotations

import logging
from typing import Any

from worker.celery_app import celery_app

log = logging.getLogger(__name__)


@celery_app.task(name="worker.tasks.sim.simulate_wltc")
def simulate_wltc(bundle: dict[str, Any]) -> dict:
    """
    Run a WLTC cycle simulation against a proposed calibration bundle.
    Returns per-cycle BSFC, EGT model peaks, knock margin, and predicted gains.

    Real implementation shells out to a 1D solver (GT-Power-style / open-source
    engsim). This stub returns a plausible envelope.
    """
    n_deltas = len(bundle.get("deltas", []))
    return {
        "bsfc_pct_delta": -0.4 * n_deltas,
        "knock_margin_deg_min": 4.6,
        "egt_c_p95": 906.0,
        "hp_at_crank_pct": 3.2 + 0.6 * n_deltas,
        "mpg_pct": 1.1,
    }


@celery_app.task(name="worker.tasks.sim.simulate_track")
def simulate_track(bundle: dict[str, Any]) -> dict:
    return {
        "power_top_pct": 6.8,
        "oil_temp_c_p95": 128.0,
        "trans_temp_c_p95": 108.0,
    }
