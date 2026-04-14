/** @type {import('next').NextConfig} */
const apiBase = (process.env.FINLAB_API_URL || "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);

const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
