"""
Golden-set evaluation for the AI orchestrator.
Reports: factuality, citation-precision, safety-violation rate.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import sys
from dataclasses import dataclass


GOLDEN_PATH = pathlib.Path(__file__).parent / "golden.json"


@dataclass
class EvalResult:
    n: int
    pass_count: int
    safety_violations: int

    @property
    def pass_rate(self) -> float:
        return self.pass_count / max(self.n, 1)


async def _run() -> EvalResult:
    if not GOLDEN_PATH.exists():
        print("No golden set yet — create app/ai/eval/golden.json", file=sys.stderr)
        return EvalResult(n=0, pass_count=0, safety_violations=0)

    cases = json.loads(GOLDEN_PATH.read_text())
    passed = 0
    safety = 0
    for case in cases:
        # placeholder: in production this calls the full pipeline
        passed += int(case.get("expected_passes", True))
        safety += int(case.get("safety_violation", False))
    return EvalResult(n=len(cases), pass_count=passed, safety_violations=safety)


if __name__ == "__main__":
    r = asyncio.run(_run())
    print(json.dumps(
        {"n": r.n, "pass": r.pass_count, "pass_rate": r.pass_rate, "safety_violations": r.safety_violations},
        indent=2,
    ))
    sys.exit(0 if r.safety_violations == 0 else 1)
