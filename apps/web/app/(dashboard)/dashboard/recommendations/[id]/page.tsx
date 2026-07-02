"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import { Card, CardHeader, CardTitle, CardValue } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { apiFetch, apiJson } from "@/lib/api";
import { healthColor } from "@/lib/utils";

type Rec = {
  id: string;
  safety_score: number;
  confidence_score: number;
  compat_score: number;
  status: string;
  predicted_gains: Record<string, number>;
  bundle: {
    profile: string;
    explanation: string;
    risk_assessment: string;
    deltas: Array<{
      map_name: string;
      cell_index: number[] | null;
      current_value: number;
      proposed_value: number;
      rationale: string;
      citation_ids: string[];
    }>;
  };
};

export default function RecommendationPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data, mutate } = useSWR<Rec>(`/recommendations/${id}`, (p: string) => apiJson(p));
  const [signature, setSignature] = useState("");
  const [fingerprint, setFingerprint] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function approve() {
    setErr(null);
    setBusy(true);
    try {
      const r = await apiFetch(`/recommendations/${id}/approve`, {
        method: "POST",
        body: JSON.stringify({ signature_b64: signature, key_fingerprint: fingerprint }),
      });
      if (!r.ok) throw new Error((await r.json()).detail ?? "approval failed");
      await mutate();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  if (!data) return <p className="text-text-muted">Loading…</p>;

  const isFinal = data.status === "approved" || data.status === "rejected" || data.status === "blocked_by_policy";
  const blocked = data.status === "blocked_by_policy";

  return (
    <div className="space-y-6">
      <header className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold">Recommendation</h1>
        <Chip tone={data.status === "approved" ? "ok" : blocked ? "risk" : "warn"}>
          {data.status}
        </Chip>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Safety</CardTitle>
          </CardHeader>
          <CardValue className={healthColor(data.safety_score)}>{data.safety_score}/100</CardValue>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Confidence</CardTitle>
          </CardHeader>
          <CardValue>{(data.confidence_score * 100).toFixed(0)}%</CardValue>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Compatibility</CardTitle>
          </CardHeader>
          <CardValue>{data.compat_score}/100</CardValue>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
          </CardHeader>
          <CardValue className="text-brand-soft capitalize">{data.bundle.profile.replace("_", " ")}</CardValue>
        </Card>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Proposed changes</CardTitle>
            <Chip tone="brand">{data.bundle.deltas.length} deltas</Chip>
          </CardHeader>
          <table className="w-full text-sm">
            <thead className="text-text-muted">
              <tr className="text-left">
                <th className="py-2">Map</th>
                <th>Cell</th>
                <th className="text-right">From</th>
                <th className="text-right">To</th>
                <th>Rationale</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {data.bundle.deltas.map((d, i) => (
                <tr key={i} className="align-top">
                  <td className="py-2 font-mono text-brand-soft">{d.map_name}</td>
                  <td className="text-text-muted">{d.cell_index?.join(",") ?? "scalar"}</td>
                  <td className="text-right">{d.current_value.toFixed(2)}</td>
                  <td className="text-right text-ok">{d.proposed_value.toFixed(2)}</td>
                  <td className="text-text-muted">{d.rationale}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Predicted gains</CardTitle>
          </CardHeader>
          <ul className="text-sm space-y-1">
            {Object.entries(data.predicted_gains).map(([k, v]) => (
              <li key={k} className="flex justify-between">
                <span className="text-text-muted">{k}</span>
                <span>{typeof v === "number" ? v.toFixed(1) : String(v)}</span>
              </li>
            ))}
          </ul>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Explanation</CardTitle>
        </CardHeader>
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{data.bundle.explanation}</p>
        {data.bundle.risk_assessment && (
          <p className="mt-3 text-sm text-warn">Risk: {data.bundle.risk_assessment}</p>
        )}
      </Card>

      {!isFinal && (
        <Card>
          <CardHeader>
            <CardTitle>Tuner approval</CardTitle>
            <Chip tone="warn">signature required</Chip>
          </CardHeader>
          <p className="text-sm text-text-muted mb-3">
            Paste the ed25519 signature of the canonical bundle JSON, computed offline
            with your hardware key. See <code className="font-mono">scripts/sign-recommendation.py</code>.
          </p>
          <label className="block text-xs text-text-muted">Signature (base64)</label>
          <input
            className="w-full mt-1 mb-3 rounded-lg bg-bg-soft border border-line px-3 py-2 font-mono text-xs"
            value={signature}
            onChange={(e) => setSignature(e.target.value)}
            placeholder="MEUCIQD…"
          />
          <label className="block text-xs text-text-muted">Key fingerprint</label>
          <input
            className="w-full mt-1 mb-3 rounded-lg bg-bg-soft border border-line px-3 py-2 font-mono text-xs"
            value={fingerprint}
            onChange={(e) => setFingerprint(e.target.value)}
            placeholder="e.g. 3f9e2c…"
          />
          {err && <p className="text-risk text-sm mb-2">{err}</p>}
          <div className="flex gap-2">
            <button
              onClick={approve}
              disabled={busy || !signature || !fingerprint}
              className="rounded-xl bg-brand px-4 py-2 text-white hover:bg-brand-soft disabled:opacity-50"
            >
              {busy ? "Signing…" : "Approve & sign"}
            </button>
            <button
              onClick={() => router.back()}
              className="rounded-xl border border-line px-4 py-2 hover:bg-bg-soft"
            >
              Cancel
            </button>
          </div>
        </Card>
      )}

      {blocked && (
        <Card className="border-risk/50">
          <CardHeader>
            <CardTitle className="text-risk">Blocked by policy</CardTitle>
          </CardHeader>
          <p className="text-sm">
            This bundle triggers a hard policy refusal (defeat-device, safety floor, or region
            regulation). It cannot be approved. Adjust the input and regenerate.
          </p>
        </Card>
      )}
    </div>
  );
}
