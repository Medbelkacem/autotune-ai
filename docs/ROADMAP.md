# AutoTune AI — Product Roadmap

Version 1.0 · Confidential · 2026-07-02

---

## Guiding metrics

| Metric | Baseline | 12-mo target | 36-mo target |
|---|---|---|---|
| Approved recommendations / mo | 0 | 8,000 | 250,000 |
| Vehicles under service | 0 | 15k | 500k |
| Workshops enrolled | 0 | 400 | 4,500 |
| Time from scan → signed bundle | n/a | < 90 s p95 | < 45 s p95 |
| Safety-violation rate (per 1k approvals) | 0 | ≤ 0.5 | ≤ 0.05 |
| Gross margin (SaaS + hardware blend) | n/a | 68% | 78% |
| ARR | 0 | $6.4M | $84M |

---

## Phase M0 — Foundations (T0..+3 months) ✅ complete

- Monorepo, CI, containerization
- FastAPI + Celery + Postgres + Redis + RabbitMQ + pgvector + Neo4j + MinIO local stack
- Shared Pydantic + Zod schemas
- Auth (JWT + refresh), RBAC, org multi-tenancy
- Alembic initial schema (users, roles, vehicles, ECU profiles, calibrations, scans, reports, recommendations, telemetry streams, KB, audit, bridges)
- Policy engine with defeat-device refusal (hard fatal)
- ed25519 recommendation signing
- Analyst fan-out (8 domains), report writer, health score
- Multi-agent orchestrator with tool use (strategist → verifier → compliance → explainer)
- A2L parser, checksum module registry, ECU protocol simulator
- KB ingestion (chunker + embedder + upsert to pgvector + Qdrant)
- Web dashboard: garage, vehicle, reports, recommendations, monitor
- Mobile app: login, garage, vehicle, monitor
- K8s manifests + Helm-shaped kustomization + Terraform for AWS (VPC, EKS, Aurora, MSK, ElastiCache, S3, Grafana/Prom)
- TOTP MFA, audit log foundation
- Docker images signed with cosign, SBOM published

## Phase M1 — Beta with 5 lighthouse workshops (+3..+9 months)

**Product**
- Bridge v0 hardware (J2534 + DoIP + BLE) — off-the-shelf ODM + firmware
- 40 supported ECUs (Bosch MED17.x, EDC17.x, Continental SIMOS18.x, Delphi DCM, Denso)
- Full A2L ingestion for OEM-published files; reverse fingerprinting for missing A2Ls
- 1D engine simulator integration (open-source `engsim` + calibration adapters)
- WLTC + track + towing simulation modes
- OTA bridge firmware updates with signed images

**AI**
- Golden-set eval expanded to 500 cases across 12 domains
- Preference-pair fine-tuning of small models on tuner corrections (DPO)
- Retrieval evaluator (context-precision + citation-precision > 0.85)
- Latency: full pipeline p95 < 35 s

**Compliance**
- SOC 2 Type I audit initiated
- GDPR DPIA published
- CCPA + EU AI Act (Annex III) risk register

## Phase M2 — GA in EU + US (+9..+18 months)

- 250 supported ECUs
- Fleet operator SKU (multi-vehicle rollup, cost-per-mile analytics)
- OEM sandbox tier (calibrations remain on customer's tenant)
- Marketplace: 3rd-party map catalogs (Cobb, HPTuners, JB4 imports)
- SOC 2 Type II + ISO 27001 certification
- API partnerships (Bosch DEV, Delphi Diagnostics, Snap-on)

## Phase M3 — Fleet analytics + predictive maintenance (+18..+27 months)

- Time-series lake (Iceberg on S3) with 5-yr retention
- Predictive RUL models per component (injectors, MAF, O₂, turbo, coil)
- Fleet dashboards (uptime, TCO, cost/km)
- Insurance integrations (Root, Progressive, Zurich)
- ISO 21434 (automotive cybersecurity) certification

## Phase M4 — OEM + regulator platform (+27..+42 months)

- OEM co-development mode (calibration diffs against certified baseline)
- Regulator submission mode (signed lineage: baseline → mod → recomputed emissions)
- On-prem OEM install (air-gapped)
- White-label workshop portal

## Phase M5 — International + hybrid/EV (+42..+60 months)

- CN6b / Bharat Stage VI / Japanese emission-standard support
- Hybrid + BEV powertrain calibration (torque split, regen strategy, battery thermal)
- FSD/ADAS calibration analysis
- Public API for AV testbed integrators

---

## Hiring plan

| Phase | Eng | ML | DevOps | Automotive | GTM | Total |
|---|---|---|---|---|---|---|
| M0 | 4 | 2 | 1 | 1 | 1 | **9** |
| M1 | 8 | 4 | 2 | 3 | 3 | **20** |
| M2 | 14 | 7 | 4 | 6 | 8 | **39** |
| M3 | 22 | 12 | 6 | 10 | 14 | **64** |
| M4 | 32 | 16 | 8 | 16 | 22 | **94** |

## Budget (indicative)

| Phase | Duration | Burn rate | Total spend |
|---|---|---|---|
| M0 | Q3 2026 → Q4 2026 | $180k/mo | $0.9M |
| M1 | Q1 2027 → Q3 2027 | $420k/mo | $2.5M |
| M2 | Q4 2027 → Q2 2028 | $850k/mo | $7.7M |
| M3 | Q3 2028 → Q4 2028 | $1.5M/mo | $9.0M |
| M4 | 2029 | $2.4M/mo | $28.8M |

## Risks & mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| OEM lockout via signed OTA | High | Existential | Focus M1 on pre-signing-mandate vehicle years; pursue OEM partnerships early. |
| Regulator classification as "tampering device" | Medium | High | Simulation-first, defeat-device refusal, cryptographic provenance, engagement with KBA / EPA / DfT. |
| LLM cost inflation | Medium | Medium | Multi-provider routing, prompt caching, small-model fine-tuning for the analyst tier. |
| Safety incident linked to a signed bundle | Low | Existential | Adversarial verifier, mandatory 1D sim gate, per-bundle liability insurance. |
| Talent (calibration engineers rare) | High | Medium | Partner with tuning academies, bring-your-own-mentor apprentice program. |
