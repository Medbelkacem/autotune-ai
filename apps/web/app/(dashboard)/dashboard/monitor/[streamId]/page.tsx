"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardValue } from "@/components/ui/Card";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";

type Point = { ts: string; channel: string; value: number };

export default function MonitorPage() {
  const { streamId } = useParams<{ streamId: string }>();
  const [series, setSeries] = useState<Record<string, { t: number; v: number }[]>>({});

  useEffect(() => {
    const base = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
      /^http/,
      "ws",
    );
    const token = (typeof document !== "undefined"
      ? document.cookie.match(/(?:^| )atk=([^;]+)/)?.[1]
      : null) ?? "";
    const ws = new WebSocket(`${base}/v1/telemetry/ws/${streamId}?token=${encodeURIComponent(token)}`);
    ws.onmessage = (e) => {
      try {
        const pt: Point = JSON.parse(e.data);
        setSeries((prev) => {
          const arr = prev[pt.channel] ?? [];
          const next = arr.length > 200 ? arr.slice(-200) : arr;
          return {
            ...prev,
            [pt.channel]: [...next, { t: new Date(pt.ts).getTime(), v: pt.value }],
          };
        });
      } catch {}
    };
    return () => ws.close();
  }, [streamId]);

  const kpis = [
    { key: "rpm", label: "RPM" },
    { key: "boost", label: "Boost (bar)" },
    { key: "afr", label: "AFR" },
    { key: "timing", label: "Timing (°)" },
    { key: "coolant_temp", label: "Coolant (°C)" },
    { key: "knock", label: "Knock" },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Live monitor</h1>
      <section className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {kpis.map((k) => {
          const arr = series[k.key] ?? [];
          const last = arr.at(-1)?.v;
          return (
            <Card key={k.key}>
              <CardHeader>
                <CardTitle>{k.label}</CardTitle>
              </CardHeader>
              <CardValue>{last?.toFixed(1) ?? "—"}</CardValue>
              <div className="h-16 mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={arr}>
                    <Line
                      type="monotone"
                      dataKey="v"
                      stroke="#a78bfa"
                      dot={false}
                      strokeWidth={1.5}
                    />
                    <XAxis dataKey="t" hide />
                    <YAxis hide domain={["auto", "auto"]} />
                    <Tooltip contentStyle={{ background: "#161d2b", border: "none" }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          );
        })}
      </section>
    </div>
  );
}
