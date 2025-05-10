import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  eslint: {
    ignoreDuringBuilds: true,
  },
  webpack: (config) => {
    config.externals.push("pino-pretty");
    return config;
  },
};

export default nextConfig;
