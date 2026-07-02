"use client";

import useSWR from "swr";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { apiJson } from "@/lib/api";

type Alert = {
  id: string;
  severity: "info" | "warning" | "critical";
  channel: string;
  description: string;
  vehicle_vin_last6: string;
  created_at: string;
};

const tone = (s: string) => (s === "critical" ? "risk" : s === "warning" ? "warn" : "muted") as const;

export default function NotificationsPage() {
  const { data } = useSWR<Alert[]>("/analytics/alerts", (p: string) => apiJson(p));
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Notifications</h1>
      <Card>
        <ul className="divide-y divide-line text-sm">
          {(data ?? []).map((a) => (
            <li key={a.id} className="py-2 flex items-center gap-3">
              <Chip tone={tone(a.severity)}>{a.severity}</Chip>
              <span className="font-mono text-text-muted">***{a.vehicle_vin_last6}</span>
              <span className="flex-1">
                <span className="text-brand-soft mr-2">{a.channel}</span>
                {a.description}
              </span>
              <span className="text-xs text-text-muted">
                {new Date(a.created_at).toLocaleString()}
              </span>
            </li>
          ))}
          {(!data || data.length === 0) && (
            <li className="py-6 text-center text-text-muted">no alerts</li>
          )}
        </ul>
      </Card>
    </div>
  );
}
