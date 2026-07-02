import { twMerge } from "tailwind-merge";
import clsx, { type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatScore(n: number | null | undefined): string {
  if (n === null || n === undefined) return "—";
  return `${Math.round(n)}/100`;
}

export function healthColor(n: number | null | undefined): string {
  if (n === null || n === undefined) return "text-text-muted";
  if (n >= 85) return "text-ok";
  if (n >= 65) return "text-warn";
  return "text-risk";
}
