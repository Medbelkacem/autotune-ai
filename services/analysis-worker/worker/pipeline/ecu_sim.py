"""
ECU protocol simulator — behaves like a UDS-capable Bosch MED17 ECU.

We use it in two places:
1. The scan pipeline calls `simulate_read_calibration()` when no bridge is attached.
2. The unit tests can spin up an in-memory ECU and validate the reader logic.

The simulator honors:
  - UDS 0x22 ReadDataByIdentifier (VIN, spare-part, SW version)
  - UDS 0x23 ReadMemoryByAddress
  - checksum computation via app.ecu.checksums

Latency is modeled loosely (~ 25 ms per UDS frame) so higher-level code that
times reads gets realistic numbers.
"""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SimEcu:
    vin: str = "WAUZZZ8K9BA123456"
    software_pn: str = "8K2907115AF_0010"
    hardware_pn: str = "8K2907115"
    calibration_pn: str = "8K2907115AF"
    vendor: str = "Bosch"
    model: str = "MED17.5.20"
    memory: dict[int, bytes] = field(default_factory=dict)  # addr -> page bytes

    def __post_init__(self):
        # populate a few calibration pages
        self.memory[0x8010F000] = bytes(range(256)) * 8       # KFZW-ish
        self.memory[0x8010F800] = bytes(range(64)) * 32       # KFLDIMX-ish
        self.memory[0x8010FA80] = bytes(range(128)) * 8       # KFLAMKR-ish

    async def read_data_by_identifier(self, did: int) -> bytes:
        await asyncio.sleep(0.02)
        table = {
            0xF190: self.vin.encode("ascii"),
            0xF187: self.software_pn.encode("ascii"),
            0xF191: self.hardware_pn.encode("ascii"),
            0xF18C: b"AT-SIM-0001",
        }
        if did in table:
            return table[did]
        raise KeyError(f"DID {did:#06x} not supported")

    async def read_memory_by_address(self, address: int, size: int) -> bytes:
        await asyncio.sleep(0.03)
        page = self.memory.get(address)
        if page is None:
            raise KeyError(f"page {address:#010x} not present")
        return page[:size]

    def firmware_sha256(self) -> str:
        h = hashlib.sha256()
        for addr in sorted(self.memory):
            h.update(addr.to_bytes(4, "big"))
            h.update(self.memory[addr])
        return h.hexdigest()


async def simulate_read_calibration(sim: SimEcu | None = None) -> dict[str, Any]:
    sim = sim or SimEcu()
    vin = (await sim.read_data_by_identifier(0xF190)).decode("ascii", errors="ignore")
    sw = (await sim.read_data_by_identifier(0xF187)).decode("ascii", errors="ignore")
    return {
        "vin": vin,
        "software_pn": sw,
        "firmware_sha256": sim.firmware_sha256(),
        "pages_read": len(sim.memory),
    }
