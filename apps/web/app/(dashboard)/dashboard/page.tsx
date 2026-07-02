import { Card, CardHeader, CardTitle, CardValue } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";

export default function OverviewPage() {
  return (
    <div className="space-y-6">
      <header className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold">Workshop overview</h1>
        <span className="text-sm text-text-muted">Live · demo workspace</span>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Vehicles</CardTitle>
            <Chip tone="brand">+2 this wk</Chip>
          </CardHeader>
          <CardValue>128</CardValue>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Active scans</CardTitle>
            <Chip tone="ok">healthy</Chip>
          </CardHeader>
          <CardValue>3</CardValue>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Avg. health</CardTitle>
            <Chip tone="ok">↑ 4</Chip>
          </CardHeader>
          <CardValue className="text-ok">86/100</CardValue>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Approvals pending</CardTitle>
            <Chip tone="warn">tuner review</Chip>
          </CardHeader>
          <CardValue>2</CardValue>
        </Card>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent scans</CardTitle>
            <a href="/dashboard/reports" className="text-xs text-brand-soft">
              view all →
            </a>
          </CardHeader>
          <ul className="divide-y divide-line text-sm">
            {["Audi A4 1.8T · WAUZZZ8K9BA…456 · balanced · 88/100",
              "BMW M3 F80 · WBSWD9C50BE…457 · performance · 72/100",
              "Ford F-150 3.0L PS · 1FT8W3BT9NEB…345 · towing · 91/100"].map((line) => (
              <li key={line} className="py-2 flex items-center justify-between gap-4">
                <span className="truncate">{line}</span>
                <Chip tone="muted">2h ago</Chip>
              </li>
            ))}
          </ul>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Alerts</CardTitle>
            <Chip tone="risk">1 critical</Chip>
          </CardHeader>
          <ul className="text-sm space-y-2">
            <li>
              <Chip tone="risk">critical</Chip> Overboost 3400 rpm — F80 M3
            </li>
            <li>
              <Chip tone="warn">warning</Chip> LTFT drift +12% — A4
            </li>
            <li>
              <Chip tone="ok">info</Chip> Bridge SN-A19 firmware up-to-date
            </li>
          </ul>
        </Card>
      </section>
    </div>
  );
}
