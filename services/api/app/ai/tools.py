"""
Claude tool-use registry. Every tool is:
  - defined by a JSON schema (goes into the LLM request)
  - implemented by an async Python function (invoked when the LLM calls it)

Tool routing lives in `orchestrator2.py`.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from app.ai.rag import retrieve_relevant


ToolFn = Callable[[dict[str, Any]], Awaitable[Any]]


# ─── Tool implementations ──────────────────────────────────────────────

async def _tool_retrieve_kb(args: dict[str, Any]) -> dict[str, Any]:
    query = str(args.get("query", ""))
    k = int(args.get("k", 6))
    hits = await retrieve_relevant(query, k=k)
    return {
        "hits": [
            {"source_id": h["source_id"], "text": h["text"][:1200], "score": h["score"]}
            for h in hits
        ],
    }


async def _tool_lookup_firmware(args: dict[str, Any]) -> dict[str, Any]:
    sw_pn = args.get("software_pn", "")
    # In production: query firmware_registry
    return {
        "software_pn": sw_pn,
        "vendor": "Bosch",
        "family": "MED17",
        "known": bool(sw_pn),
    }


async def _tool_score_safety(args: dict[str, Any]) -> dict[str, Any]:
    """Deterministic monotonic score used by the strategist to self-check bundles."""
    knock_margin = float(args.get("knock_margin_deg", 0.0))
    egt_c = float(args.get("egt_c_p95", 950.0))
    lambda_min = float(args.get("lambda_min", 0.86))
    oil_temp_c = float(args.get("oil_temp_c_p95", 120.0))

    score = 100
    if knock_margin < 4.0:
        score -= int((4.0 - knock_margin) * 12)
    if egt_c > 940:
        score -= int((egt_c - 940) * 0.4)
    if lambda_min < 0.80:
        score -= int((0.80 - lambda_min) * 60)
    if oil_temp_c > 125:
        score -= int((oil_temp_c - 125) * 1.2)
    score = max(0, min(100, score))
    return {"safety_score": score}


async def _tool_simulate(args: dict[str, Any]) -> dict[str, Any]:
    """Placeholder to a 1-D engine sim. In production this hits a worker task."""
    n_deltas = int(args.get("n_deltas", 0))
    return {
        "hp_at_crank_pct": round(3.2 + 0.4 * n_deltas, 1),
        "torque_pct": round(2.8 + 0.4 * n_deltas, 1),
        "mpg_pct": round(1.0 - 0.05 * n_deltas, 1),
        "knock_margin_deg_min": 4.6,
        "egt_c_p95": 906.0,
    }


# ─── Tool schemas (Claude's function-calling format) ───────────────────

TOOLS: list[dict[str, Any]] = [
    {
        "name": "retrieve_kb",
        "description": "Retrieve relevant knowledge base snippets by semantic search.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search query."},
                "k": {"type": "integer", "default": 6, "description": "Number of results."},
            },
            "required": ["query"],
        },
    },
    {
        "name": "lookup_firmware",
        "description": "Resolve an ECU software part-number to its vendor / family.",
        "input_schema": {
            "type": "object",
            "properties": {"software_pn": {"type": "string"}},
            "required": ["software_pn"],
        },
    },
    {
        "name": "score_safety",
        "description": "Deterministically score a bundle against the safety envelope.",
        "input_schema": {
            "type": "object",
            "properties": {
                "knock_margin_deg": {"type": "number"},
                "egt_c_p95": {"type": "number"},
                "lambda_min": {"type": "number"},
                "oil_temp_c_p95": {"type": "number"},
            },
            "required": ["knock_margin_deg", "egt_c_p95"],
        },
    },
    {
        "name": "simulate",
        "description": "Run a lightweight simulation. Returns predicted gains and safety metrics.",
        "input_schema": {
            "type": "object",
            "properties": {"n_deltas": {"type": "integer"}},
            "required": ["n_deltas"],
        },
    },
]

TOOL_FNS: dict[str, ToolFn] = {
    "retrieve_kb": _tool_retrieve_kb,
    "lookup_firmware": _tool_lookup_firmware,
    "score_safety": _tool_score_safety,
    "simulate": _tool_simulate,
}


async def invoke_tool(name: str, args: dict[str, Any]) -> Any:
    fn = TOOL_FNS.get(name)
    if not fn:
        return {"error": f"unknown tool: {name}"}
    try:
        return await fn(args)
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
