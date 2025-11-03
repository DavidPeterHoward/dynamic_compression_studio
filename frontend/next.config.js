/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: 'standalone', // Disabled for better static file support
  images: {
    domains: ['localhost', '127.0.0.1'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8443',
    NEXT_PUBLIC_GRAPHQL_URL: process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8443/graphql',
  },
  async rewrites() {
    // Use localhost for browser access (frontend is already in Docker)
    // The browser needs to access the backend on localhost:8443
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8443';

    // In Docker, use backend service name
    const backendUrl = process.env.NODE_ENV === 'production'
      ? 'http://backend:8000'
      : apiUrl;

    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
      {
        source: '/media/:path*',
        destination: `${backendUrl}/media/:path*`,
      },
    ];
  },
  // Ensure static files are properly served
  trailingSlash: false,
  // Optimize for Docker deployment
  experimental: {
    outputFileTracingRoot: undefined,
  },
  // Ensure static files are included in standalone build
  distDir: '.next',
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
