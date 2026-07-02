import Link from "next/link";
import { Car, Gauge, FileText, Wrench, Users, Settings } from "lucide-react";

const nav = [
  { href: "/dashboard", label: "Overview", Icon: Gauge },
  { href: "/dashboard/garage", label: "Garage", Icon: Car },
  { href: "/dashboard/reports", label: "Reports", Icon: FileText },
  { href: "/dashboard/tuners", label: "Tuners", Icon: Wrench },
  { href: "/dashboard/customers", label: "Customers", Icon: Users },
  { href: "/dashboard/settings", label: "Settings", Icon: Settings },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen grid grid-cols-[240px_1fr]">
      <aside className="border-r border-line px-3 py-5 bg-bg-soft">
        <div className="mb-6 px-2">
          <span className="text-lg font-semibold">
            <span className="text-brand">Auto</span>Tune
          </span>
        </div>
        <nav className="flex flex-col gap-1">
          {nav.map(({ href, label, Icon }) => (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-text-muted hover:bg-bg-card hover:text-text transition"
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="p-6">{children}</main>
    </div>
  );
}
