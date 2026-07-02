"""
Load a small seed knowledge base into pgvector + Qdrant, so /v1/ai/ask has
something to retrieve from on day one.

Content includes:
  - Bosch MED17 KFZW / KFLDIMX / KFLAMKR overview
  - Generic knock-control theory
  - AFR / lambda safety envelopes
  - EU / EPA emissions guardrails
"""

from __future__ import annotations

import asyncio

from app.core.db import session_factory
from app.kb.chunker import chunk_prose
from app.kb.ingest import ingest_chunks, upsert_doc


SEED = [
    (
        "Bosch MED17 KFZW overview",
        "kg:bosch_med17_kfzw_baseline",
        """\
KFZW is the primary ignition timing map in Bosch MED17 family ECUs (MED17.5.x, MED17.1.x).
X-axis is engine RPM; Y-axis is relative filling (rel_load). Output is base spark advance in
degrees BTDC. KFZW is combined with additive maps for knock retard (KFZWK), cold-advance
corrections vs coolant temp (KFZWT), and IAT-based reductions to produce the final commanded
advance. Typical OEM values on RON95 range from 30 deg at low load / low rpm to 6-12 deg at
full load / high rpm. Aggressive tuning past +3 deg over OEM at full load usually requires
higher-octane fuel and reduced boost target to preserve at least 4 deg of knock margin.
""",
    ),
    (
        "Bosch MED17 KFLDIMX boost limit",
        "kg:bosch_med17_kfldimx",
        """\
KFLDIMX is the boost target maximum map in Bosch MED17. X-axis: RPM. Y-axis: intake air
temperature (IAT). Output: absolute manifold pressure limit in bar_abs. It caps the boost
requested by KLDLLKR (the primary boost request map). Reducing KFLDIMX values at low IAT is
the usual OEM strategy to prevent turbo overspeed at cold ambient. Overboost fault codes
are set when observed boost exceeds KFLDIMX by more than a vendor-specific tolerance
(commonly 100-200 mbar for ~2s).
""",
    ),
    (
        "AFR and lambda safety envelope",
        "kg:afr_lambda_envelope",
        """\
Under load, gasoline engines require lambda enrichment to control combustion temperature
and protect the catalyst. Typical safe full-load lambda ranges are 0.78-0.86 for turbo
gasoline engines and 0.85-0.92 for naturally aspirated. Running leaner than 0.82 at full
load raises exhaust gas temperature (EGT) into ranges that damage turbo turbines and
catalyst substrates within seconds. Cruise/part-load lambda is typically 0.98-1.02 for
three-way catalyst efficiency; some strategies allow lean-burn pockets around 1.05-1.15
in narrow rpm/load windows for fuel economy.
""",
    ),
    (
        "Knock control fundamentals",
        "kg:knock_control_fundamentals",
        """\
Detonation (knock) is auto-ignition of end-gas ahead of the flame front, producing pressure
oscillations at 6-8 kHz. Modern ECUs use structure-borne knock sensors coupled to the block
and a windowed FFT/energy calculation gated by crank angle. On detection, the ECU applies
per-cylinder spark retard (typically 1-3 deg) and, if sustained, requests fuel enrichment
and boost reduction. Knock margin is defined as the difference between commanded spark and
the borderline knock spark; production calibrations target 4-8 deg of margin at full load
to tolerate variability in fuel octane, IAT, humidity, and combustion chamber deposits.
""",
    ),
    (
        "EU regulatory guardrails for aftermarket tuning",
        "kg:eu_reg_guardrails",
        """\
UNECE R83 (emissions) and R51 (noise) bound aftermarket calibrations sold in the EU. Any
change that increases certified NOx, CO, HC or PM emissions requires re-homologation
(section 8 of R83). Removal or defeat of emission control devices (DPF, EGR, AdBlue/SCR)
is prohibited under EU Directive 2018/858 and mirrored in national type-approval regimes.
Post-R155 (2024), OEM software integrity is protected by cryptographic signing;
aftermarket flashers who bypass those signatures may face criminal liability in DE, FR, IT
and NL. Recommendations that modify DPF, EGR, AdBlue, or lambda-defeat maps must be
categorically refused.
""",
    ),
]


async def main() -> None:
    async with session_factory()() as db:
        for title, sid, text in SEED:
            doc = await upsert_doc(db, title=title, source="seed", text=text)
            chunks = chunk_prose(text, source_id=sid)
            await ingest_chunks(db, doc, chunks)
        await db.commit()
    print(f"Ingested {len(SEED)} seed KB documents.")


if __name__ == "__main__":
    asyncio.run(main())
