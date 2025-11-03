# =============================================================================
# Dynamic Compression Algorithms Frontend - Production Dockerfile
# Optimized for production with proper static file serving
# =============================================================================

# Use Node.js 18 slim image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package.json package-lock.json* ./

# Install all dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Create non-root user for security
RUN groupadd -r nextjs && useradd -r -g nextjs nextjs

# Change ownership of the app directory
RUN chown -R nextjs:nextjs /app

# Switch to non-root user
USER nextjs

# Expose port (matching nginx configuration)
EXPOSE 3000

# Set environment variables for runtime
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start the application
CMD ["npm", "start"]
