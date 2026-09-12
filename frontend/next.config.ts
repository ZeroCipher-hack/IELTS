import type { NextConfig } from "next";
const backend = process.env.BACKEND_URL?.replace(/\/$/, "");
const nextConfig: NextConfig = {
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return backend ? [{source:"/api/:path*",destination:`${backend}/api/:path*`}] : [];
  },
};
export default nextConfig;
