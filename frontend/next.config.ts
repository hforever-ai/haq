import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination:
          process.env.API_BASE_URL
            ? `${process.env.API_BASE_URL}/api/:path*`
            : "http://localhost:8097/api/:path*",
      },
    ];
  },
  async redirects() {
    return [
      { source: "/", destination: "/hi/", permanent: false },
    ];
  },
};

export default nextConfig;
