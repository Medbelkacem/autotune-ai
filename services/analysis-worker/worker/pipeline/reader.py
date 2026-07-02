"""
Step 2 — ECU Reading.

Production: streams UDS 0x23 ReadMemoryByAddress with security-access unlock.
Skeleton: returns a canonical fixture calibration for MED17.5.20 so the pipeline
can run end-to-end without hardware.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

log = logging.getLogger(__name__)


def _fixture_maps() -> list[dict]:
    """A tiny but realistic subset of a MED17 calibration."""
    return [
        {
            "name": "KFZW",
            "address_hex": "0x8010F000",
            "datatype": "uword",
            "conversion": {"formula": "PHYS=a+b*RAW", "a": -20.0, "b": 0.75, "unit": "deg"},
            "x_axis": {
                "name": "RPM",
                "unit": "rpm",
                "values": [800, 1200, 1600, 2000, 2500, 3000, 3500, 4000, 5000, 6000],
                "breakpoints": 10,
            },
            "y_axis": {
                "name": "rel_load",
                "unit": "-",
                "values": [0.2, 0.35, 0.5, 0.65, 0.8, 1.0, 1.2],
                "breakpoints": 7,
            },
            "values": [
                [30, 28, 26, 24, 22, 18, 12],
                [30, 28, 26, 24, 22, 18, 12],
                [28, 27, 25, 22, 20, 16, 10],
                [26, 25, 23, 20, 18, 14, 8],
                [25, 24, 22, 19, 17, 13, 7],
                [24, 22, 20, 17, 15, 11, 6],
                [22, 20, 18, 16, 14, 10, 4],
                [20, 18, 17, 14, 12, 9, 3],
                [17, 16, 14, 12, 10, 7, 2],
                [15, 13, 12, 10, 8, 5, 1],
            ],
            "unit": "deg",
        },
        {
            "name": "KFLDIMX",
            "address_hex": "0x8010F800",
            "datatype": "uword",
            "conversion": {"formula": "PHYS=a+b*RAW", "a": 0, "b": 0.005, "unit": "bar_abs"},
            "x_axis": {
                "name": "RPM", "unit": "rpm",
                "values": [1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000],
                "breakpoints": 9,
            },
            "y_axis": {"name": "IAT", "unit": "C", "values": [-10, 10, 25, 40, 60], "breakpoints": 5},
            "values": [
                [1.30, 1.30, 1.28, 1.24, 1.18],
                [1.55, 1.55, 1.52, 1.46, 1.36],
                [1.72, 1.72, 1.68, 1.60, 1.48],
                [1.80, 1.80, 1.76, 1.66, 1.52],
                [1.80, 1.80, 1.76, 1.66, 1.52],
                [1.76, 1.76, 1.72, 1.60, 1.44],
                [1.66, 1.66, 1.60, 1.50, 1.34],
                [1.50, 1.50, 1.44, 1.34, 1.20],
                [1.36, 1.36, 1.30, 1.20, 1.08],
            ],
            "unit": "bar_abs",
        },
        {
            "name": "KFLAMKR",
            "address_hex": "0x8010FA80",
            "datatype": "uword",
            "conversion": {"formula": "PHYS=a+b*RAW", "a": 0.5, "b": 0.001, "unit": "-"},
            "x_axis": {"name": "RPM", "unit": "rpm",
                       "values": [1000, 2000, 3000, 4000, 5000, 6000], "breakpoints": 6},
            "y_axis": {"name": "rel_load", "unit": "-",
                       "values": [0.4, 0.6, 0.8, 1.0, 1.2], "breakpoints": 5},
            "values": [
                [1.00, 1.00, 0.98, 0.94, 0.90],
                [1.00, 0.99, 0.94, 0.90, 0.86],
                [1.00, 0.96, 0.90, 0.86, 0.82],
                [0.98, 0.92, 0.86, 0.82, 0.80],
                [0.96, 0.88, 0.84, 0.82, 0.80],
                [0.92, 0.86, 0.84, 0.82, 0.80],
            ],
            "unit": "-",
        },
        {
            "name": "NMAX_RVL",
            "address_hex": "0x8010FF00",
            "datatype": "uword",
            "conversion": {"formula": "PHYS=a+b*RAW", "a": 0, "b": 1, "unit": "rpm"},
            "values": [[6700]],
            "unit": "rpm",
        },
        {
            "name": "VMAX_SPD",
            "address_hex": "0x8010FF04",
            "datatype": "uword",
            "conversion": {"formula": "PHYS=a+b*RAW", "a": 0, "b": 1, "unit": "kmh"},
            "values": [[250]],
            "unit": "kmh",
        },
    ]


async def read_calibration(scan_id: UUID, vehicle_identity: dict[str, Any]) -> dict[str, Any]:
    log.info("reader.calibration ecu=%s", vehicle_identity["ecu"]["model"])
    doc = {
        "document_id": str(scan_id),  # not a UUID validation error since consumers don't validate
        "ecu_firmware_sha256": vehicle_identity["ecu"]["firmware_sha256"],
        "a2l_version": "1.7.1",
        "maps": _fixture_maps(),
        "page_checksums": {},
        "provenance": {},
    }
    return doc
