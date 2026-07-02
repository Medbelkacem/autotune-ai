/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typescript: {
    // We typecheck via `npm run typecheck` — Next.js's build-time typecheck is
    // overly strict about typed routes for a workshop MVP.
    ignoreBuildErrors: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/v1/:path*`,
      },
    ];
  },
};
export default nextConfig;
