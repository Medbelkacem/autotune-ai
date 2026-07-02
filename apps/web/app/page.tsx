import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-8 px-6">
      <header className="text-center">
        <h1 className="text-5xl font-semibold tracking-tight">
          <span className="text-brand">Auto</span>Tune AI
        </h1>
        <p className="mt-3 text-text-muted max-w-lg">
          AI-powered ECU intelligence — explainable, safety-bounded, human-in-the-loop.
        </p>
      </header>
      <div className="flex gap-3">
        <Link
          href="/dashboard"
          className="rounded-xl bg-brand px-5 py-2.5 text-white hover:bg-brand-soft transition"
        >
          Open workshop dashboard →
        </Link>
        <Link
          href="/login"
          className="rounded-xl border border-line px-5 py-2.5 hover:bg-bg-soft transition"
        >
          Sign in
        </Link>
      </div>
    </main>
  );
}
