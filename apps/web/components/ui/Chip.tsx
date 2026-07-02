import { cn } from "@/lib/utils";
import type { HTMLAttributes } from "react";

type Tone = "ok" | "warn" | "risk" | "muted" | "brand";

const tones: Record<Tone, string> = {
  ok: "bg-ok/15 text-ok",
  warn: "bg-warn/15 text-warn",
  risk: "bg-risk/15 text-risk",
  muted: "bg-line text-text-muted",
  brand: "bg-brand/15 text-brand-soft",
};

export function Chip({
  tone = "muted",
  className,
  children,
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span className={cn("chip", tones[tone], className)} {...props}>
      {children}
    </span>
  );
}
