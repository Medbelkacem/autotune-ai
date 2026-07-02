"use client";

import useSWR from "swr";
import Link from "next/link";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { apiJson } from "@/lib/api";
import { healthColor } from "@/lib/utils";

type Vehicle = {
  id: string;
  vin: string;
  manufacturer: string | null;
  model: string | null;
  year: number | null;
  fuel_type: string | null;
};

export default function GaragePage() {
  const fetcher = (p: string) => apiJson<Vehicle[]>(p);
  const { data, isLoading, error } = useSWR<Vehicle[]>("/vehicles", fetcher);

  return (
    <div className="space-y-6">
      <header className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold">Garage</h1>
        <Link
          href="/dashboard/garage/new"
          className="rounded-xl bg-brand px-4 py-2 text-sm text-white hover:bg-brand-soft"
        >
          + Add vehicle
        </Link>
      </header>

      {isLoading && <p className="text-text-muted">Loading…</p>}
      {error && <p className="text-risk">{String(error)}</p>}

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(data ?? []).map((v) => {
          const health = 88; // placeholder — real value from latest report
          return (
            <Link key={v.id} href={`/dashboard/garage/${v.id}`}>
              <Card className="hover:border-brand transition">
                <CardHeader>
                  <CardTitle>
                    {v.manufacturer} {v.model} {v.year ? `· ${v.year}` : ""}
                  </CardTitle>
                  <Chip tone={health >= 85 ? "ok" : health >= 65 ? "warn" : "risk"}>
                    {health >= 85 ? "healthy" : health >= 65 ? "caution" : "at risk"}
                  </Chip>
                </CardHeader>
                <div className="flex items-center justify-between text-sm">
                  <code className="text-text-muted">
                    VIN {"***"}
                    {v.vin.slice(-6)}
                  </code>
                  <span className={healthColor(health)}>{health}/100</span>
                </div>
                <div className="mt-2 text-xs text-text-muted">{v.fuel_type ?? "—"}</div>
              </Card>
            </Link>
          );
        })}
      </section>
    </div>
  );
}
