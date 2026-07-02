import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AutoTune AI — Workshop",
  description: "AI-powered ECU intelligence platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased font-sans">{children}</body>
    </html>
  );
}
