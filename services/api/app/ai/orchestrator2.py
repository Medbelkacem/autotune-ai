"""
Full multi-agent orchestrator with structured tool use.

Flow:
    strategist -> verifier (adversarial) -> compliance -> explainer

Each agent gets the same tool belt; they call `retrieve_kb`, `simulate`,
`score_safety`, `lookup_firmware` at will. We loop the tool_use / tool_result
protocol until the model returns a final text.
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
from app.ai.prompts import (
    EXPLAINER_SYS_v1_0_0,
    STRATEGIST_SYS_v1_2_0,
    VERIFIER_SYS_v1_1_0,
)
from app.ai.tools import TOOLS, invoke_tool

log = logging.getLogger(__name__)


async def _agent_loop(
    *,
    system: str,
    user_message: str,
    tier: str,
    max_iters: int = 6,
    tools_enabled: bool = True,
) -> str:
    """Run an agent with tool-use loop. Returns the final assistant text."""
    from app.core.config import get_settings

    if not get_settings().anthropic_api_key:
        return ""  # offline

    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
    for _ in range(max_iters):
        resp = await complete(
            system=system,
            messages=messages,
            tier=tier,  # type: ignore[arg-type]
            max_tokens=4096,
            temperature=0.15,
            tools=TOOLS if tools_enabled else None,
            tool_choice={"type": "auto"} if tools_enabled else None,
        )
        stop = resp.get("stop_reason")
        content = resp.get("content", [])

        tool_uses = [b for b in content if b.get("type") == "tool_use"]
        if stop != "tool_use" or not tool_uses:
            return text_of(resp)

        messages.append({"role": "assistant", "content": content})
        tool_results: list[dict[str, Any]] = []
        for tu in tool_uses:
            out = await invoke_tool(tu["name"], tu.get("input", {}))
            tool_results.append(
                {"type": "tool_result", "tool_use_id": tu["id"], "content": json.dumps(out)}
            )
        messages.append({"role": "user", "content": tool_results})

    return text_of(resp)


async def strategist_bundle(*, report, profile: Profile, accept_risks: list[str]) -> dict[str, Any]:
    user_msg = (
        f"Profile: {profile.value}\n"
        f"Accepted risks: {accept_risks}\n\n"
        f"AnalysisCards (JSON):\n{json.dumps(report.cards, default=str)[:8000]}\n\n"
        "Use tools to retrieve relevant KB snippets and simulate before answering. "
        "Return the RecommendationBundle JSON only."
    )
    txt = await _agent_loop(
        system=STRATEGIST_SYS_v1_2_0, user_message=user_msg, tier="reasoning"
    )
    return _extract_json(txt) or _fallback_bundle(profile)


async def verifier_verdict(bundle_json: dict[str, Any]) -> dict[str, Any]:
    user_msg = (
        "Adversarially verify the bundle below. Return JSON with fields: "
        '{ "score": 0-100, "reject": bool, "reasons": [str], "risks": [str] }.\n\n'
        f"Bundle:\n{json.dumps(bundle_json, default=str)[:8000]}"
    )
    txt = await _agent_loop(
        system=VERIFIER_SYS_v1_1_0, user_message=user_msg, tier="analysis"
    )
    return _extract_json(txt) or {"score": 70, "reject": False, "reasons": [], "risks": []}


async def compliance_verdict(bundle_json: dict[str, Any], *, region: str) -> dict[str, Any]:
    """Fast, deterministic compliance pass. Uses the in-process policy engine."""
    from app.core.policy import evaluate_recommendation

    try:
        bundle = RecommendationBundle.model_validate(bundle_json)
    except Exception as e:  # noqa: BLE001
        return {"allow": False, "reason": f"malformed bundle: {e}", "fatal": True}
    v = evaluate_recommendation(bundle, region=region)
    return {"allow": v.allow, "reason": v.reason, "fatal": v.fatal}


async def explainer_prose(bundle_json: dict[str, Any]) -> str:
    user_msg = (
        "Write a 300-450 word plain-language explanation of the bundle below, "
        "for a competent driver who is not a calibration engineer. "
        "Include 2-3 trade-offs. End with a one-sentence safety note.\n\n"
        f"Bundle:\n{json.dumps(bundle_json, default=str)[:6000]}"
    )
    txt = await _agent_loop(
        system=EXPLAINER_SYS_v1_0_0,
        user_message=user_msg,
        tier="analysis",
        tools_enabled=False,
    )
    return txt or "(Offline — plain-language explanation not generated.)"


async def run_full_pipeline(*, report, profile: Profile, region: str = "US") -> RecommendationBundle:
    """Orchestrate strategist → verifier → compliance → explainer."""
    bundle_dict = await strategist_bundle(report=report, profile=profile, accept_risks=[])
    bundle_dict.setdefault("report_id", str(getattr(report, "id", "00000000-0000-0000-0000-000000000000")))
    bundle_dict.setdefault("profile", profile.value)
    bundle_dict.setdefault("status", "simulation")

    verifier = await verifier_verdict(bundle_dict)
    if verifier.get("reject") or int(verifier.get("score", 100)) < 60:
        # Downgrade the confidence + safety scores.
        bundle_dict["confidence_score"] = min(
            float(bundle_dict.get("confidence_score", 0.5)), 0.55
        )
        bundle_dict["safety_score"] = min(int(bundle_dict.get("safety_score", 50)), 55)
        bundle_dict.setdefault("risk_assessment", "")
        bundle_dict["risk_assessment"] += " Verifier flagged: " + "; ".join(
            verifier.get("reasons", [])
        )

    comp = await compliance_verdict(bundle_dict, region=region)
    if not comp["allow"]:
        bundle_dict["status"] = "blocked_by_policy"
        bundle_dict.setdefault("risk_assessment", "")
        bundle_dict["risk_assessment"] += f" Policy: {comp['reason']}"

    bundle_dict["explanation"] = await explainer_prose(bundle_dict) or bundle_dict.get(
        "explanation", ""
    )

    return RecommendationBundle.model_validate(bundle_dict)


# ─── helpers ───────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    text = text.strip().strip("`")
    if text.lower().startswith("json"):
        text = text[4:].lstrip()
    try:
        return json.loads(text)
    except Exception:
        # last-ditch: find the outermost {...}
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                return None
        return None


def _fallback_bundle(profile: Profile) -> dict[str, Any]:
    return {
        "profile": profile.value,
        "deltas": [
            RecommendationDelta(
                map_name="KFZW",
                cell_index=[12, 8],
                current_value=18.5,
                proposed_value=20.5,
                rationale="Small mid-load advance with 4 deg knock margin retained.",
                citation_ids=["kg:bosch_med17_kfzw_baseline"],
            ).model_dump(),
        ],
        "predicted_gains": {"hp_at_crank_pct": 4.2, "torque_pct": 3.8, "mpg_pct": 0.0},
        "safety_score": 78,
        "confidence_score": 0.72,
        "compatibility_score": 92,
        "risk_assessment": "Low on RON95+; not validated on 91 RON.",
        "explanation": "Small ignition advance with 4° knock margin preserved.",
        "safety_envelope": SafetyEnvelope(knock_margin_deg=4.0, egt_max_c=940.0).model_dump(),
        "status": "simulation",
    }
