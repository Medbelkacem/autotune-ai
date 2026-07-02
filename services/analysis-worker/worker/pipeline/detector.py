"""
Step 1 — Vehicle Detection.

In production, this drives the AutoTune Bridge to issue:
    Mode 09 PID 02 (OBD-II VIN)
    UDS 0x22 F190 (VIN by DID)
    UDS 0x22 F187 (spare part)
    UDS 0x22 F189 (software version)
and fuses evidence via Dempster–Shafer.

The skeleton loads the vehicle row and produces a VehicleIdentity from it.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import text

from worker.db import db_session

log = logging.getLogger(__name__)


async def detect_vehicle(scan_id: UUID) -> dict[str, Any]:
    with db_session() as s:
        row = s.execute(
            text(
                """
                SELECT v.id, v.vin, v.manufacturer, v.model, v.year,
                       v.engine_code, v.transmission_code, v.fuel_type, v.emission_standard
                FROM scan_session ss
                JOIN vehicle v ON v.id = ss.vehicle_id
                WHERE ss.id = :sid
                """
            ),
            {"sid": str(scan_id)},
        ).one()

    identity = {
        "vehicle_identity_id": str(row.id),
        "vin": row.vin,
        "vin_confidence": 0.99,
        "manufacturer": row.manufacturer or "Unknown",
        "model": row.model or "Unknown",
        "model_year": row.year or 2020,
        "engine": {
            "code": row.engine_code or "UNKNOWN",
            "displacement_cc": 2000,
            "config": "I4",
            "induction": "Turbo",
        },
        "transmission": {"type": row.transmission_code or "MT", "gears": 6},
        "ecu": {
            "vendor": "Bosch",
            "model": "MED17.5.20",
            "hardware_pn": "8K2907115",
            "software_pn": "8K2907115AF_0010",
            "firmware_sha256": "0" * 64,
        },
        "emission_standard": row.emission_standard,
        "fuel_type": row.fuel_type or "Gasoline_RON95",
        "supported_protocols": ["UDS", "ISO15765-4", "DoIP"],
        "modification_history": [],
    }
    log.info("detector.identity vin=%s ecu=%s", "***" + identity["vin"][-6:], identity["ecu"]["model"])
    return identity
