"""
Chunker with two strategies:

1. `chunk_prose`   — section-aware for OEM manuals / SAE papers / bulletins.
2. `chunk_a2l`    — one chunk per calibration map (name + axes + description).

Both return `(text, locator)` tuples where `locator` is a stable pointer back
to the source (e.g. "manual:section-3.2" or "a2l:KFZW").
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TARGET = 800
OVERLAP = 100


@dataclass
class Chunk:
    text: str
    locator: str


_PARA_SPLIT = re.compile(r"\n\s*\n")


def chunk_prose(text: str, source_id: str, *, target: int = TARGET, overlap: int = OVERLAP) -> list[Chunk]:
    """Greedy sliding-window over paragraph boundaries."""
    paragraphs = _PARA_SPLIT.split(text.strip())
    chunks: list[Chunk] = []
    buf: list[str] = []
    buf_len = 0
    idx = 0

    def flush():
        nonlocal buf, buf_len, idx
        if not buf:
            return
        chunks.append(Chunk(text="\n\n".join(buf).strip(), locator=f"{source_id}#chunk{idx}"))
        idx += 1

    for p in paragraphs:
        if buf_len + len(p) > target and buf_len > 0:
            flush()
            # keep last paragraph as overlap
            keep = buf[-1] if buf else ""
            buf = [keep] if len(keep) < overlap * 2 else []
            buf_len = len(buf[0]) if buf else 0
        buf.append(p)
        buf_len += len(p)
    flush()
    return chunks


def chunk_a2l(parsed, source_id: str) -> list[Chunk]:
    """One chunk per map: name + kind + address + axes + description."""
    out: list[Chunk] = []
    for name, c in parsed.characteristics.items():
        conv = parsed.conversions.get(c.conversion)
        unit = conv.unit if conv else ""
        text = (
            f"Map {name} ({c.kind}) at {c.address_hex}. "
            f"Unit: {unit or 'unknown'}. "
            f"Size: {c.x_size}x{c.y_size}. "
            f"Description: {c.description or 'n/a'}."
        )
        out.append(Chunk(text=text, locator=f"a2l:{source_id}:{name}"))
    return out
