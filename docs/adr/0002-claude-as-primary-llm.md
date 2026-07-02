# ADR 0002 — Claude as primary LLM

Date: 2026-01-22  ·  Status: Accepted

## Context
Recommendation quality is the product. The reasoning stack must handle multi-step calibration analysis with citations, tool use, and hard refusal on defeat-device requests.

## Decision
Use **Anthropic Claude** as the primary LLM, with tiered routing:

| Task class | Model | Reason |
|---|---|---|
| Deep reasoning (strategist, verifier) | `claude-opus-4-8` | Best at long-context multi-step reasoning. |
| Per-domain analyst | `claude-sonnet-4-6` | Cost/latency balance for parallel fan-out. |
| Routing / classification | `claude-haiku-4-5-20251001` | Sub-second latency. |

Use prompt caching on the ~18k-token system prompt (calibration ontology) to reduce steady-state token cost by ~85%.

## Alternatives
- OpenAI GPT-4o class — comparable quality, but Claude's refusal semantics and long-context recall have been more reliable in our internal evals for the safety-critical strategist role.
- Open-source (Llama-3.3-70B, Mixtral) — kept as a fallback for on-prem OEM installs.

## Consequences
- Vendor risk mitigated by prompt/tool abstractions so we can multi-source.
- Every prompt is versioned + evaluated on the golden set in CI.
- Sensitive data (VINs, customer names) is redacted at the tokenizer boundary.
