"""
Multi-agent orchestrator. The flow:
   detector -> reader -> [analyst-N parallel] -> strategist -> verifier -> compliance -> explainer

For MVP this file orchestrates the Strategist + Explainer steps used by the
recommendations endpoint. The full agentic pipeline runs in the Celery worker.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from autotune_schemas import (
    Profile,
    RecommendationBundle,
    RecommendationDelta,
    SafetyEnvelope,
)

from app.ai.llm import complete, model_for, text_of
from app.ai.prompts import EXPLAINER_SYS_v1_0_0, STRATEGIST_SYS_v1_2_0

_log = logging.getLogger(__name__)


async def generate_recommendation_bundle(
    *,
    report,  # AnalysisReport ORM
    profile: Profile,
    accept_risks: list[str],
) -> RecommendationBundle:
    cards_json = json.dumps(report.cards, default=str)

    user_msg = (
        f"Profile: {profile.value}\n"
        f"Accepted risks: {accept_risks}\n\n"
        f"Cards (JSON array):\n{cards_json}\n\n"
        "Produce the bundle JSON."
    )

    if _llm_available():
        resp = await complete(
            system=STRATEGIST_SYS_v1_2_0,
            messages=[{"role": "user", "content": user_msg}],
            tier="reasoning",
            max_tokens=4096,
            temperature=0.1,
        )
        raw = text_of(resp)
        try:
            data = _extract_json(raw)
        except Exception:
            _log.warning("Strategist returned non-JSON; falling back to safe stub.")
            data = _stub_bundle(profile, accept_risks)
    else:
        data = _stub_bundle(profile, accept_risks)

    data["report_id"] = str(report.id)
    bundle = RecommendationBundle.model_validate(data)

    # Always start in simulation status.
    if bundle.status != "simulation":
        bundle = bundle.model_copy(update={"status": "simulation"})
    return bundle


async def explain_concept(question: str, *, snippets: list[dict]) -> tuple[str, str]:
    if not _llm_available():
        return ("(Offline) " + question + " — no LLM key configured.", "offline")
    ctx = "\n\n".join(
        f"[{i+1}] (source_id={s['source_id']}): {s['text'][:1200]}"
        for i, s in enumerate(snippets)
    )
    user_msg = (
        f"Q: {question}\n\nContext:\n{ctx}\n\n"
        "Answer concisely with inline citations like [1], [2]."
    )
    resp = await complete(
        system=EXPLAINER_SYS_v1_0_0,
        messages=[{"role": "user", "content": user_msg}],
        tier="analysis",
        max_tokens=1024,
        temperature=0.3,
    )
    return text_of(resp), model_for("analysis")


# ─── Helpers ────────────────────────────────────────────────────────────

def _llm_available() -> bool:
    from app.core.config import get_settings

    return bool(get_settings().anthropic_api_key)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("` \n")
        # remove optional leading 'json\n'
        if text.lower().startswith("json"):
            text = text[4:].lstrip()
    return json.loads(text)


def _stub_bundle(profile: Profile, accept_risks: list[str]) -> dict[str, Any]:
    """Offline fallback used by tests and CI."""
    return {
        "report_id": "00000000-0000-0000-0000-000000000000",
        "profile": profile.value,
        "deltas": [
            RecommendationDelta(
                map_name="KFZW",
                cell_index=[12, 8],
                current_value=18.5,
                proposed_value=20.5,
                rationale="Modest spark advance in mid-load, mid-rpm region with retained 4° knock margin.",
                citation_ids=["kg:bosch_med17_kfzw_baseline"],
            ).model_dump(),
        ],
        "predicted_gains": {"hp_at_crank_pct": 4.2, "torque_pct": 3.8, "mpg_pct": 0.0},
        "safety_score": 78,
        "confidence_score": 0.72,
        "compatibility_score": 92,
        "risk_assessment": "Low risk on RON95+; not validated on 91 RON.",
        "explanation": (
            "Slightly advances ignition timing in the most-used cruise region while keeping a "
            "4-degree knock margin. Expect a small power bump; fuel economy unchanged."
        ),
        "safety_envelope": SafetyEnvelope(knock_margin_deg=4.0, egt_max_c=940.0).model_dump(),
        "status": "simulation",
    }
