/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: 'standalone', // Disabled for better static file support
  images: {
    domains: ['localhost', '127.0.0.1'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8441',
    NEXT_PUBLIC_GRAPHQL_URL: process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8441/graphql',
  },
  async rewrites() {
    // API proxy configuration
    // Next.js rewrites run server-side, so we use Docker service name
    // For client-side requests, the browser will use NEXT_PUBLIC_API_URL directly
    // Server-side rewrites (SSR/getServerSideProps) use backend service in Docker
    const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';

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
  // Reduce webpack memory usage
  webpack: (config, { isServer }) => {
    // Add path aliases
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname, 'src'),
    };

    // Optimize for memory usage
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }

    // Reduce bundle size and memory usage
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        ...config.optimization.splitChunks,
        cacheGroups: {
          ...config.optimization.splitChunks?.cacheGroups,
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10,
          },
        },
      },
    };

    return config;
  },
  // Ensure static files are included in standalone build
  distDir: '.next',
};

module.exports = nextConfig;
