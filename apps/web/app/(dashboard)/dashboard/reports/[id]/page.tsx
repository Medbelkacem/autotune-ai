"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import { Card, CardHeader, CardTitle, CardValue } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { apiFetch, apiJson } from "@/lib/api";
import { healthColor } from "@/lib/utils";

type Report = {
  id: string;
  profile: string;
  health_score: number;
  summary: string;
  cards: Array<{
    domain: string;
    title: string;
    risks: string[];
    optimization_opportunities: string[];
    confidence: { value: number };
  }>;
};

const PROFILES = ["fuel_economy", "balanced", "performance", "track", "towing", "fleet"] as const;

export default function ReportDetail() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data } = useSWR<Report>(`/reports/${id}`, (p: string) => apiJson(p));
  const [profile, setProfile] = useState<(typeof PROFILES)[number]>("balanced");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function generate() {
    setErr(null);
    setBusy(true);
    try {
      const r = await apiFetch(`/recommendations`, {
        method: "POST",
        body: JSON.stringify({ report_id: id, profile }),
      });
      if (!r.ok) throw new Error((await r.json()).detail ?? "generate failed");
      const rec = await r.json();
      router.push(`/dashboard/recommendations/${rec.id}`);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  if (!data) return <p className="text-text-muted">Loading…</p>;

  return (
    <div className="space-y-6">
      <header className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold">Report</h1>
        <Chip tone={data.health_score >= 85 ? "ok" : data.health_score >= 65 ? "warn" : "risk"}>
          health {data.health_score}/100
        </Chip>
      </header>

      <Card>
        <p className="text-sm">{data.summary}</p>
      </Card>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.cards.map((c) => (
          <Card key={c.domain}>
            <CardHeader>
              <CardTitle>{c.title}</CardTitle>
              <Chip tone="brand">{c.domain}</Chip>
            </CardHeader>
            {c.risks.length > 0 && (
              <div className="mb-2">
                <div className="text-xs text-text-muted mb-1">Risks</div>
                <ul className="text-sm text-warn list-disc pl-4 space-y-0.5">
                  {c.risks.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
            {c.optimization_opportunities.length > 0 && (
              <div>
                <div className="text-xs text-text-muted mb-1">Opportunities</div>
                <ul className="text-sm text-ok list-disc pl-4 space-y-0.5">
                  {c.optimization_opportunities.map((o, i) => (
                    <li key={i}>{o}</li>
                  ))}
                </ul>
              </div>
            )}
            <p className="text-xs text-text-muted mt-2">
              confidence {(c.confidence.value * 100).toFixed(0)}%
            </p>
          </Card>
        ))}
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Generate recommendation</CardTitle>
        </CardHeader>
        <div className="flex items-center gap-3">
          <select
            className="rounded-lg bg-bg-soft border border-line px-3 py-2 text-sm"
            value={profile}
            onChange={(e) => setProfile(e.target.value as (typeof PROFILES)[number])}
          >
            {PROFILES.map((p) => (
              <option key={p} value={p}>
                {p.replace("_", " ")}
              </option>
            ))}
          </select>
          <button
            onClick={generate}
            disabled={busy}
            className="rounded-xl bg-brand px-4 py-2 text-white hover:bg-brand-soft disabled:opacity-50"
          >
            {busy ? "Generating…" : "Generate →"}
          </button>
          {err && <p className="text-risk text-sm">{err}</p>}
        </div>
      </Card>
    </div>
  );
}
