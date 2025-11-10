/** @type {import('next').NextConfig} */
const nextConfig = {
  // Optimize for Docker deployment (standalone only for production)
  ...(process.env.NODE_ENV === 'production' && {
    output: 'standalone',
  }),

  images: {
    domains: ['localhost', '127.0.0.1'],
    unoptimized: process.env.NODE_ENV === 'development', // Optimize images in development
  },

  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8443',
    NEXT_PUBLIC_GRAPHQL_URL: process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8443/graphql',
  },

  async rewrites() {
    // API proxy configuration optimized for Docker
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

  // Optimize for development and production
  trailingSlash: false,

  // Enhanced experimental features for better Docker performance
  experimental: {
    outputFileTracingRoot: undefined,
  },

  // Optimize webpack for memory efficiency
  webpack: (config, { dev, isServer }) => {
    // Add path aliases for cleaner imports
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname, 'src'),
    };

    // Optimize for memory usage in development
    if (dev && !isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };

      // Use efficient source maps in development (don't disable them completely)
      // Let Next.js handle the devtool configuration for optimal performance
    }

    // Enhanced bundle splitting for better memory management
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        ...config.optimization.splitChunks,
        chunks: 'all',
        cacheGroups: {
          ...config.optimization.splitChunks?.cacheGroups,
          // Separate vendor chunks for better caching
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10,
            enforce: true,
          },
          // Separate React and related libraries
          react: {
            test: /[\\/]node_modules[\\/](react|react-dom|@mui|@emotion)[\\/]/,
            name: 'react',
            chunks: 'all',
            priority: 20,
            enforce: true,
          },
          // UI library chunks
          ui: {
            test: /[\\/]node_modules[\\/](@radix-ui|lucide-react|tailwindcss)[\\/]/,
            name: 'ui',
            chunks: 'all',
            priority: 15,
            enforce: true,
          },
        },
      },
    };

    // Add memory optimizations
    if (dev) {
      // Reduce webpack watcher memory usage
      config.watchOptions = {
        ...config.watchOptions,
        ignored: [
          '**/node_modules/**',
          '**/.next/**',
          '**/*.log',
          '**/coverage/**',
          '**/test-results/**',
        ],
        aggregateTimeout: 300,
        poll: false,
      };
    }

    return config;
  },

  // Optimize build output directory
  distDir: '.next',

  // Development optimizations
  ...(process.env.NODE_ENV === 'development' && {
    // Disable type checking in development for faster builds
    typescript: {
      ignoreBuildErrors: true,
    },
    eslint: {
      ignoreDuringBuilds: true,
    },
    // Optimize static file serving
    assetPrefix: '',
  }),

  // Production optimizations
  ...(process.env.NODE_ENV === 'production' && {
    // Enable compression
    compress: true,
    // Optimize CSS
    optimizeCss: true,
  }),
};

module.exports = nextConfig;
