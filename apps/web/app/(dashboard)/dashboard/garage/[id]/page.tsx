"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import useSWR from "swr";
import { Card, CardHeader, CardTitle, CardValue } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { apiFetch, apiJson } from "@/lib/api";

export default function VehiclePage() {
  const { id } = useParams<{ id: string }>();
  const { data: vehicle } = useSWR(`/vehicles/${id}`, (p: string) => apiJson<Record<string, unknown>>(p));
  const [scanning, setScanning] = useState(false);
  const [scanId, setScanId] = useState<string | null>(null);

  async function startScan() {
    setScanning(true);
    const r = await apiFetch("/scans", {
      method: "POST",
      body: JSON.stringify({ vehicle_id: id }),
    });
    if (r.ok) {
      const j = await r.json();
      setScanId(j.id);
    }
    setScanning(false);
  }

  return (
    <div className="space-y-6">
      <header className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold">
          {(vehicle as any)?.manufacturer} {(vehicle as any)?.model}
          <span className="text-text-muted"> · {(vehicle as any)?.year}</span>
        </h1>
        <Chip tone="brand">Bosch MED17.5.20</Chip>
      </header>

      <section className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Health score</CardTitle>
          </CardHeader>
          <CardValue className="text-ok">88/100</CardValue>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Firmware</CardTitle>
          </CardHeader>
          <div className="text-sm">
            <div>SW-PN 8K2907115AF_0010</div>
            <div className="text-text-muted mt-1">SHA-256 ****cafe</div>
          </div>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Modification</CardTitle>
          </CardHeader>
          <div className="text-sm">
            <div>Stage 1 (suspected)</div>
            <div className="text-text-muted mt-1">confidence 0.78</div>
          </div>
        </Card>
      </section>

      <section className="flex gap-3">
        <button
          onClick={startScan}
          disabled={scanning}
          className="rounded-xl bg-brand px-5 py-2.5 text-white hover:bg-brand-soft disabled:opacity-50"
        >
          {scanning ? "Starting…" : "Start scan"}
        </button>
        <button className="rounded-xl border border-line px-5 py-2.5 hover:bg-bg-soft">
          Live monitor
        </button>
        <button className="rounded-xl border border-line px-5 py-2.5 hover:bg-bg-soft">
          Reports
        </button>
      </section>

      {scanId && (
        <Card>
          <CardHeader>
            <CardTitle>Scan {scanId.slice(0, 8)}…</CardTitle>
            <Chip tone="brand">queued</Chip>
          </CardHeader>
          <p className="text-sm text-text-muted">
            The bridge is negotiating protocol and reading calibration. This typically takes 15–35s.
          </p>
        </Card>
      )}
    </div>
  );
}
