import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";

const demo = [
  { id: "rep_01", vehicle: "Audi A4 · WAUZZZ8K9BA…456", profile: "balanced", score: 88 },
  { id: "rep_02", vehicle: "BMW M3 F80 · WBSWD9C50BE…457", profile: "performance", score: 72 },
  { id: "rep_03", vehicle: "Ford F-150 · 1FT8W3BT9NEB…345", profile: "towing", score: 91 },
];

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Reports</h1>
      <Card>
        <table className="w-full text-sm">
          <thead className="text-text-muted">
            <tr className="text-left">
              <th className="py-2">Report</th>
              <th>Vehicle</th>
              <th>Profile</th>
              <th className="text-right">Health</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {demo.map((r) => (
              <tr key={r.id} className="hover:bg-bg-soft">
                <td className="py-2 font-mono text-brand-soft">{r.id}</td>
                <td>{r.vehicle}</td>
                <td>
                  <Chip tone="brand">{r.profile}</Chip>
                </td>
                <td className="text-right">
                  <span
                    className={
                      r.score >= 85 ? "text-ok" : r.score >= 65 ? "text-warn" : "text-risk"
                    }
                  >
                    {r.score}/100
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
