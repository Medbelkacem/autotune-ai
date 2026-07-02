"""
Checksum modules for ECU calibration pages.

Each vendor has a proprietary scheme; this registry holds the ones we've
observed and validated. Recompute before any virtual write; refuse any
operation whose checksum can't be verified.
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass
from typing import Callable, Protocol


class ChecksumFn(Protocol):
    def __call__(self, page_bytes: bytes) -> bytes: ...


@dataclass(frozen=True)
class ChecksumModule:
    vendor: str
    ecu_family: str
    name: str
    fn: Callable[[bytes], bytes]


def _bosch_med17_crc32(page_bytes: bytes) -> bytes:
    """Bosch MED17 data-flash page: CRC-32 (little-endian) over the region minus
    the last 4 bytes (which hold the CRC itself)."""
    body = page_bytes[:-4]
    crc = zlib.crc32(body) & 0xFFFFFFFF
    return crc.to_bytes(4, "little")


def _continental_sim_sha1_stub(page_bytes: bytes) -> bytes:
    import hashlib
    return hashlib.sha1(page_bytes[:-20]).digest()  # last 20 = signature slot


REGISTRY: list[ChecksumModule] = [
    ChecksumModule("Bosch", "MED17", "med17_crc32", _bosch_med17_crc32),
    ChecksumModule("Continental", "SIMOS18", "simos18_sha1", _continental_sim_sha1_stub),
]


def lookup(vendor: str, ecu_family: str) -> ChecksumModule | None:
    for m in REGISTRY:
        if m.vendor.lower() == vendor.lower() and m.ecu_family.lower() in ecu_family.lower():
            return m
    return None


def recompute_and_verify(page_bytes: bytes, module: ChecksumModule) -> bool:
    computed = module.fn(page_bytes)
    stored = page_bytes[-len(computed):]
    return computed == stored
