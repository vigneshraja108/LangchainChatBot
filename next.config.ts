
// const nextConfig: NextConfig = {
//   /* config options here */
// };

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    turbo: false, // ✅ Disable Turbopack
  },
  reactStrictMode: false,
};

export default nextConfig; // ✅ Correct way in TypeScript ESM

