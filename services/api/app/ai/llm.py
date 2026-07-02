"""Anthropic Claude wrapper with tiered model routing + prompt caching."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Literal

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam

from app.core.config import get_settings

_log = logging.getLogger(__name__)
_settings = get_settings()
_client: AsyncAnthropic | None = None


def client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=_settings.anthropic_api_key)
    return _client


Tier = Literal["routing", "analysis", "reasoning"]


def model_for(tier: Tier) -> str:
    return {
        "routing": _settings.anthropic_model_routing,
        "analysis": _settings.anthropic_model_analysis,
        "reasoning": _settings.anthropic_model_reasoning,
    }[tier]


async def complete(
    *,
    system: str,
    messages: list[MessageParam],
    tier: Tier = "analysis",
    max_tokens: int = 4096,
    temperature: float = 0.2,
    tools: list[dict[str, Any]] | None = None,
    tool_choice: dict[str, Any] | None = None,
    cache_system: bool = True,
) -> dict[str, Any]:
    """Call Claude with retry + token accounting. Returns raw response dict."""
    sys_blocks: list[dict[str, Any]] = (
        [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
        if cache_system
        else [{"type": "text", "text": system}]
    )

    attempts = 3
    last_err: Exception | None = None
    for n in range(attempts):
        try:
            resp = await client().messages.create(
                model=model_for(tier),
                system=sys_blocks,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                tools=tools or [],
                tool_choice=tool_choice or {"type": "auto"} if tools else {"type": "none"},
            )
            return resp.model_dump()
        except Exception as e:  # noqa: BLE001
            last_err = e
            backoff = 1.5**n
            _log.warning("Claude call failed (attempt %d): %s; retry in %.1fs", n + 1, e, backoff)
            await asyncio.sleep(backoff)
    raise RuntimeError(f"LLM call failed after {attempts} attempts: {last_err}")


def text_of(resp: dict[str, Any]) -> str:
    parts = []
    for blk in resp.get("content", []):
        if blk.get("type") == "text":
            parts.append(blk.get("text", ""))
    return "".join(parts).strip()
