"""
A2L (ASAM MCD-2 MC) parser — minimal but practical subset.

The A2L standard is enormous; we ingest the parts we care about:
  /begin PROJECT ... /end PROJECT
    /begin MODULE ... /end MODULE
      /begin COMPU_METHOD ... /end COMPU_METHOD    -- conversion rules
      /begin RECORD_LAYOUT ... /end RECORD_LAYOUT  -- byte layout (partial)
      /begin AXIS_PTS ... /end AXIS_PTS            -- shared axes
      /begin CHARACTERISTIC ... /end CHARACTERISTIC -- MAPS and VALUES (calibration)

We surface a normalized `ParsedA2L` object with the fields the AI stack needs.

This parser is intentionally simple: it tokenizes on whitespace + comments,
respects /begin ... /end blocks, and pulls out named tokens. It does not
implement the full grammar (no IF_DATA, no formulas, no COMPU_VTAB_RANGE). For
production, swap in `a2lparser` or the C++ `A2L::Parser`.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from typing import Iterable


_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT_RE = re.compile(r"//[^\n]*")


@dataclass
class ConversionMethod:
    name: str
    conv_type: str          # "LINEAR" | "RAT_FUNC" | "TAB_INTP" | "IDENTICAL"
    unit: str = ""
    coeffs: list[float] = field(default_factory=list)  # a, b for LINEAR: PHYS=a+b*RAW


@dataclass
class AxisPts:
    name: str
    address_hex: str
    unit: str = ""
    values: list[float] = field(default_factory=list)


@dataclass
class Characteristic:
    name: str
    kind: str               # "MAP" | "CURVE" | "VALUE"
    address_hex: str
    conversion: str         # COMPU_METHOD name
    lower: float | None = None
    upper: float | None = None
    x_axis: str | None = None
    y_axis: str | None = None
    x_size: int | None = None
    y_size: int | None = None
    description: str = ""


@dataclass
class ParsedA2L:
    project: str = ""
    module: str = ""
    conversions: dict[str, ConversionMethod] = field(default_factory=dict)
    axes: dict[str, AxisPts] = field(default_factory=dict)
    characteristics: dict[str, Characteristic] = field(default_factory=dict)


def _strip_comments(text: str) -> str:
    text = _COMMENT_RE.sub("", text)
    text = _LINE_COMMENT_RE.sub("", text)
    return text


def _tokens(text: str) -> Iterable[str]:
    for tok in re.findall(r'"[^"]*"|\S+', text):
        if tok.startswith('"') and tok.endswith('"'):
            yield tok[1:-1]
        else:
            yield tok


def parse_a2l(source: str | bytes | io.TextIOBase) -> ParsedA2L:
    if isinstance(source, (bytes, bytearray)):
        source = source.decode("utf-8", errors="replace")
    elif isinstance(source, io.TextIOBase):
        source = source.read()

    text = _strip_comments(source)
    toks = list(_tokens(text))
    i = 0
    result = ParsedA2L()

    while i < len(toks):
        t = toks[i]
        if t == "/begin":
            i += 1
            block = toks[i] if i < len(toks) else ""
            i += 1
            end_idx = _find_end(toks, i, block)
            body = toks[i:end_idx]
            _handle_block(block, body, result)
            i = end_idx + 2   # skip "/end" + block name
        else:
            i += 1
    return result


def _find_end(toks: list[str], start: int, block: str) -> int:
    depth = 1
    j = start
    while j < len(toks):
        if toks[j] == "/begin":
            depth += 1
            j += 2
            continue
        if toks[j] == "/end" and j + 1 < len(toks) and toks[j + 1] == block:
            depth -= 1
            if depth == 0:
                return j
            j += 2
            continue
        j += 1
    return len(toks)


def _handle_block(block: str, body: list[str], out: ParsedA2L) -> None:
    if block == "PROJECT":
        out.project = body[0] if body else ""
        # nested MODULE handled recursively
        _walk_nested(body, out)
    elif block == "MODULE":
        out.module = body[0] if body else ""
        _walk_nested(body, out)
    elif block == "COMPU_METHOD":
        cm = _parse_compu_method(body)
        out.conversions[cm.name] = cm
    elif block == "AXIS_PTS":
        ax = _parse_axis_pts(body)
        out.axes[ax.name] = ax
    elif block == "CHARACTERISTIC":
        c = _parse_characteristic(body)
        if c is not None:
            out.characteristics[c.name] = c


def _walk_nested(body: list[str], out: ParsedA2L) -> None:
    i = 0
    while i < len(body):
        if body[i] == "/begin":
            i += 1
            block = body[i] if i < len(body) else ""
            i += 1
            end = _find_end(body, i, block)
            _handle_block(block, body[i:end], out)
            i = end + 2
        else:
            i += 1


def _parse_compu_method(body: list[str]) -> ConversionMethod:
    # body typical: name "long id" conv_type "format" "unit" [coeffs...]
    name = body[0]
    conv_type = body[2] if len(body) > 2 else "IDENTICAL"
    unit = body[4] if len(body) > 4 else ""
    coeffs: list[float] = []
    for tok in body[5:]:
        try:
            coeffs.append(float(tok))
        except (ValueError, TypeError):
            break
    return ConversionMethod(name=name, conv_type=conv_type, unit=unit, coeffs=coeffs)


def _parse_axis_pts(body: list[str]) -> AxisPts:
    name = body[0]
    addr = next((t for t in body if t.lower().startswith("0x")), "0x0")
    return AxisPts(name=name, address_hex=addr, values=[])


def _parse_characteristic(body: list[str]) -> Characteristic | None:
    if len(body) < 3:
        return None
    name = body[0]
    kind = body[2] if len(body) > 2 else "VALUE"
    addr = next((t for t in body if t.lower().startswith("0x")), "0x0")
    # naive size extraction: last two ints after address
    ints = [t for t in body if re.fullmatch(r"-?\d+", t)]
    x = int(ints[-2]) if len(ints) >= 2 else None
    y = int(ints[-1]) if len(ints) >= 1 else None
    conv = body[4] if len(body) > 4 else "IDENTICAL"
    return Characteristic(
        name=name,
        kind={"MAP": "MAP", "CURVE": "CURVE", "VALUE": "VALUE", "VAL_BLK": "MAP"}.get(kind, "VALUE"),
        address_hex=addr,
        conversion=conv,
        x_size=x,
        y_size=y,
    )
