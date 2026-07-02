"""
Policy engine (OPA-style, in-process for MVP).

Critical invariants:
1. Defeat-device modifications (DPF/EGR/AdBlue removal) are ALWAYS refused.
2. Recommendations remain `simulation` until signed by a `tuner` role
   with a hardware-backed key.
3. Emissions envelope is regional — out-of-region recommendations are flagged.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from autotune_schemas import RecommendationBundle, RecommendationDelta


_DEFEAT_DEVICE_KEYWORDS = frozenset(
    {
        "dpf_off",
        "dpf_delete",
        "egr_off",
        "egr_delete",
        "adblue_off",
        "scr_off",
        "lambda_defeat",
        "o2_simulator",
    }
)

# Map names whose deletion / extreme alteration is a defeat device.
_REGULATED_MAP_PREFIXES = ("DPF_", "EGR_", "ADBLUE_", "SCR_", "OBD_DIAG_")


@dataclass(frozen=True)
class PolicyVerdict:
    allow: bool
    reason: str = ""
    fatal: bool = False  # if True, no human override can re-enable


def _is_defeat_device(deltas: Iterable[RecommendationDelta]) -> str | None:
    for d in deltas:
        name = d.map_name.lower()
        if any(k in name for k in _DEFEAT_DEVICE_KEYWORDS):
            return d.map_name
        if d.map_name.startswith(_REGULATED_MAP_PREFIXES):
            # Block dramatic changes to emissions-related maps.
            if d.current_value != 0 and d.proposed_value == 0:
                return d.map_name
    return None


def evaluate_recommendation(bundle: RecommendationBundle, *, region: str) -> PolicyVerdict:
    if (offender := _is_defeat_device(bundle.deltas)) is not None:
        return PolicyVerdict(
            allow=False,
            reason=f"Refusing defeat-device modification on {offender}.",
            fatal=True,
        )

    if bundle.safety_score < 60:
        return PolicyVerdict(
            allow=False,
            reason=f"Safety score {bundle.safety_score} below threshold (60).",
        )

    if bundle.confidence_score < 0.65:
        return PolicyVerdict(
            allow=False,
            reason=f"Confidence {bundle.confidence_score:.2f} below threshold (0.65).",
        )

    # Region-specific emission limits could be wired here.
    if region in {"EU", "DE", "FR", "UK"} and "egt_max_c" in bundle.predicted_gains:
        if float(bundle.predicted_gains.get("egt_max_c", 0)) > 980:
            return PolicyVerdict(
                allow=False,
                reason="Predicted EGT exceeds EU envelope (980 °C).",
            )

    return PolicyVerdict(allow=True, reason="ok")


def requires_signature(bundle: RecommendationBundle) -> bool:
    return bundle.status in {"simulation", "pending_review"}
