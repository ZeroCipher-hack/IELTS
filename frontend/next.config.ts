import type { NextConfig } from "next";
const backend = process.env.BACKEND_URL?.replace(/\/$/, "");
const nextConfig: NextConfig = {
  skipTrailingSlashRedirect: true,
  output: 'standalone',
  async rewrites() {
    return backend ? [{source:"/api/:path*",destination:`${backend}/api/:path*/`},{source:"/admin/:path*",destination:`${backend}/admin/:path*/`},{source:"/static/:path*",destination:`${backend}/static/:path*`}] : [];
  },
};
export default nextConfig;
