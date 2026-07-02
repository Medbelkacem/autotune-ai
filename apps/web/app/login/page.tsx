"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("owner@demo.autotune.ai");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      const r = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      if (!r.ok) throw new Error((await r.json()).detail ?? "login failed");
      const tokens = await r.json();
      document.cookie = `atk=${tokens.access_token}; path=/; SameSite=Lax; max-age=${tokens.expires_in}`;
      router.push("/dashboard");
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <form onSubmit={onSubmit} className="card w-full max-w-md space-y-4">
        <h1 className="text-2xl font-semibold">Sign in</h1>
        <label className="block text-sm">
          <span className="text-text-muted">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg bg-bg-soft border border-line px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="text-text-muted">Password</span>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg bg-bg-soft border border-line px-3 py-2"
          />
        </label>
        {err && <p className="text-risk text-sm">{err}</p>}
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-xl bg-brand py-2.5 text-white hover:bg-brand-soft disabled:opacity-50 transition"
        >
          {busy ? "Signing in…" : "Continue →"}
        </button>
      </form>
    </main>
  );
}
