"""
Per-domain Analyst agents. Each agent runs concurrently and produces one AnalysisCard.
The worker fan-outs these via asyncio.gather.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from autotune_schemas import AnalysisCard, Confidence, Domain

from app.ai.llm import complete, text_of
from app.ai.prompts import ANALYST_SYS_v1_3_0
from app.ai.rag import retrieve_relevant

_log = logging.getLogger(__name__)


DOMAIN_BRIEF: dict[Domain, str] = {
    Domain.FUEL: "Volumetric efficiency / MAF-based fueling, injector PW, lambda targeting.",
    Domain.IGNITION: "Spark advance maps (KFZW/SPK), knock retard, cold-advance.",
    Domain.TORQUE_REQUEST: "Driver-demand torque, engine-torque-coordinated control.",
    Domain.THROTTLE: "Electronic throttle pedal mapping.",
    Domain.BOOST: "Wastegate/VGT duty, boost requests vs altitude/IAT.",
    Domain.AFR_LAMBDA: "Lambda setpoint vs load/RPM; lean cruise; full-load enrichment.",
    Domain.SPEED_LIMITER: "Vehicle-speed torque cap.",
    Domain.REV_LIMITER: "RPM-cut and fuel-cut strategy.",
    Domain.CAM_TIMING: "Intake/exhaust VVT phasing.",
    Domain.TEMP_COMPENSATION: "Fuel/timing trims vs coolant + IAT.",
    Domain.KNOCK: "Knock sensor calibration; retard/recovery dynamics.",
    Domain.DRIVER_DEMAND: "Pedal-to-torque-request curves per gear.",
    Domain.GEAR_STRATEGY: "Per-gear torque and shift behavior (DSG/AT).",
}


async def analyze_domain(
    *,
    domain: Domain,
    calibration_doc: dict[str, Any],
    vehicle_identity: dict[str, Any],
) -> AnalysisCard:
    brief = DOMAIN_BRIEF[domain]
    snippets = await retrieve_relevant(
        f"{domain.value} {vehicle_identity.get('manufacturer','')} {vehicle_identity.get('engine',{}).get('code','')}",
        k=6,
    )
    ctx = "\n\n".join(
        f"[{i+1}] id={s['source_id']} loc={s.get('locator')}: {s['text'][:800]}"
        for i, s in enumerate(snippets)
    )

    relevant_maps = [
        m for m in calibration_doc.get("maps", []) if _map_matches_domain(m["name"], domain)
    ]

    user_msg = (
        f"Domain: {domain.value}\nBrief: {brief}\n\n"
        f"Vehicle: {json.dumps(vehicle_identity, default=str)[:1200]}\n\n"
        f"Relevant maps (first 12 shown):\n{json.dumps(relevant_maps[:12], default=str)[:4000]}\n\n"
        f"KB snippets:\n{ctx}\n\n"
        "Return the AnalysisCard JSON only."
    )

    from app.ai.llm import complete  # noqa: F811

    if not _llm_available():
        return _offline_card(domain)

    resp = await complete(
        system=ANALYST_SYS_v1_3_0,
        messages=[{"role": "user", "content": user_msg}],
        tier="analysis",
        max_tokens=3072,
        temperature=0.2,
    )
    try:
        data = _extract_json(text_of(resp))
        return AnalysisCard.model_validate(data)
    except Exception as e:  # noqa: BLE001
        _log.warning("Analyst[%s] returned non-conforming JSON: %s", domain.value, e)
        return _offline_card(domain)


def _map_matches_domain(name: str, domain: Domain) -> bool:
    name_l = name.lower()
    table: dict[Domain, list[str]] = {
        Domain.FUEL: ["fuel", "lambda", "afr", "fn_inj", "fkr", "ve", "kfve"],
        Domain.IGNITION: ["kfzw", "spk", "ign", "spark"],
        Domain.BOOST: ["boost", "kfldimx", "ldimx", "wg"],
        Domain.AFR_LAMBDA: ["lambda", "kflam", "lammax", "fkalsl"],
        Domain.KNOCK: ["knock", "kfk", "klr"],
        Domain.CAM_TIMING: ["nws", "vvt", "cam", "kfns"],
        Domain.SPEED_LIMITER: ["vmax", "speed_lim"],
        Domain.REV_LIMITER: ["nmax", "rev_lim", "drz"],
        Domain.TEMP_COMPENSATION: ["temp", "tmot", "tans", "ect"],
        Domain.TORQUE_REQUEST: ["kfmirl", "torque", "mreq"],
        Domain.DRIVER_DEMAND: ["pedal", "kfpe", "ped_to_trq"],
        Domain.THROTTLE: ["dk", "throttle", "etb"],
        Domain.GEAR_STRATEGY: ["gear", "shift", "kfgang"],
    }
    return any(t in name_l for t in table.get(domain, []))


def _llm_available() -> bool:
    from app.core.config import get_settings

    return bool(get_settings().anthropic_api_key)


def _extract_json(s: str) -> dict[str, Any]:
    s = s.strip().strip("`")
    if s.lower().startswith("json"):
        s = s[4:].lstrip()
    return json.loads(s)


def _offline_card(domain: Domain) -> AnalysisCard:
    return AnalysisCard(
        domain=domain,
        title=f"{domain.value} — offline placeholder",
        purpose=DOMAIN_BRIEF[domain],
        inputs=["RPM", "load"],
        outputs=["control variable"],
        observed_summary="No LLM key configured; calibration parsed but not analyzed.",
        risks=[],
        optimization_opportunities=[],
        explanation="Offline mode — set ANTHROPIC_API_KEY to enable analysis.",
        confidence=Confidence(value=0.0, calibrated=False, method="offline"),
    )
