# AutoTune AI — Pitch Deck

Confidential · Series Seed · 2026-07

---

## 1. One-liner

> AutoTune AI turns ECU tuning from a hands-on craft into a **verifiable, explainable, and regulator-ready** software workflow — so professional workshops can service 10× more vehicles at 3× the safety.

## 2. The problem

- **200M+ vehicles** get post-purchase calibration changes each year (performance, fuel economy, fleet cost, EV motor mapping).
- The current market is 90% craft: a tuner opens a `.bin` file in HP Tuners / WinOLS / Cobb ATR, edits maps by intuition, flashes, road-tests, iterates.
- **Failure modes**: bricked ECUs, blown turbos, voided warranties, illegal emissions, insurance denial. Estimated $2B/year in preventable damage in NA + EU alone.
- **Regulatory turn**: UNECE R155/R156 (2024) require signed calibration provenance. Aftermarket without provenance is being pushed toward criminal liability in DE, FR, IT, NL.

## 3. The solution

An **AI reasoning layer** between the tuner and the ECU:

1. **Connect** — supports J2534, DoIP, UDS, KWP2000, CAN-FD.
2. **Read** — identifies vehicle, reads calibration, computes checksums.
3. **Analyze** — multi-agent Claude reasoning explains what each map does, cites OEM references, flags risks.
4. **Recommend** — safety-scored, simulation-vetted deltas per user profile (economy / balanced / performance / track / towing / fleet).
5. **Approve** — credentialed tuner signs with hardware key; every write is logged, reversible, and provenance-preserving.

## 4. Why now

| Force | Signal |
|---|---|
| LLM reasoning maturity | First time an AI can reliably reason over multi-modal calibration data with citations. |
| UNECE R155/R156 | 100+ OEMs must ship cryptographically-signed calibrations; aftermarket must match. |
| EV / hybrid complexity | 5-10× more calibration parameters than ICE; craft doesn't scale. |
| Right-to-Repair (EU) | Aftermarket gains protected diagnostic access; demand for tooling rises. |
| Fleet telematics | 1-10 GB/vehicle/day → analytics becomes a service, not a workshop event. |

## 5. Market

| Segment | Global TAM | Serviceable (SAM) | Obtainable (SOM, 5-yr) |
|---|---|---|---|
| Professional tuning shops | $18B | $6.4B | $420M |
| Fleet fuel/maintenance opt. | $54B | $9.1B | $780M |
| OEM co-development sandboxes | $11B | $2.2B | $180M |
| Regulator / homologation | $2.7B | $0.9B | $60M |
| **Total** | **$85.7B** | **$18.6B** | **$1.44B** |

## 6. Product moat

1. **Calibration knowledge graph** — proprietary, curated, growing with every scan.
2. **Hardware bridge** — J2534 / DoIP / BLE reference design with OTA + attestation.
3. **Human feedback flywheel** — each tuner correction improves models.
4. **Regulatory posture** — first mover on provenance-signed calibrations positions us as the compliance layer for the industry.
5. **Safety layer patents** — pending on adversarial verifier + policy-as-code gate.

## 7. Business model

| Tier | Price | Included |
|---|---|---|
| Free | $0 | 3 scans/mo, read-only |
| Pro | $49/mo | 30 scans, 5 recommendations |
| Workshop | $349/mo/tech | Unlimited scans, 200 recommendations, telemetry retention 90d |
| Enterprise | $9,900/mo min. | SSO, dedicated tenant, custom SLAs |
| OEM sandbox | $250k/yr | On-prem or dedicated cloud |
| Government/regulator | $600k/yr | Audit access, evidence chain |
| Bridge hardware | $499 (Pro) / $1,299 (Workshop) | One-time, includes 1yr firmware |
| API licensing | $0.02 per recommendation | Fleet integrators, insurance |

## 8. Traction (as of Q3 2026)

- **12** design-partner workshops (2× in DE, 3× in UK, 4× in US, 3× in AE).
- **3** OEM LOIs for M2 pilot (1 European premium, 1 US truck, 1 Asian mass-market).
- **50** curated ECU firmware SKUs supported end-to-end.
- **500** golden-set eval cases; **96.1%** factuality; **0** safety violations in eval.

## 9. Competition

| Player | Category | Weakness vs. AutoTune |
|---|---|---|
| HP Tuners | Editor | No reasoning; no provenance; craft workflow. |
| Cobb ATR | Editor + tune library | Fixed-catalog tunes; no per-vehicle reasoning. |
| Alientech KESSv3 | Reader/writer hardware | Hardware without AI or safety layer. |
| Bosch DEV | OEM diag | OEM-only; not aftermarket-facing. |
| Snap-on Zeus | Workshop diag | DTC-focused; no calibration reasoning. |
| Cloud OEMs (SDV platforms) | OEM only | Locked to a single OEM. |

## 10. Team (target)

- **CEO**: ex-Bosch calibration lead + startup exit.
- **CTO**: ex-Google Brain / Waymo perception.
- **VP AI**: ex-Anthropic applied research.
- **VP Safety**: ex-VW compliance officer (post-Dieselgate ombudsman).
- **VP Sales**: ex-HP Tuners channel director.

## 11. The ask

**Series Seed — $12M.**

- **60%** engineering + AI (M0–M1 hiring plan)
- **20%** bridge hardware NRE + first 5k units
- **10%** SOC 2 / ISO 27001 / regulatory legal
- **10%** design-partner GTM

**24-month runway** into a metrics-driven Series A at $8M ARR, 500 workshops, 1st OEM contract in flight.

## 12. Exit lens

- **Strategic** — Bosch, Continental, Cummins, Snap-on, Denso.
- **Financial** — public compliance/analytics comps trade at 12-18× ARR (Cerence, Palantir Foundry adjacencies).
- **Timing** — 5-7 yr, aligned with UNECE R156 SUMS enforcement wave.
