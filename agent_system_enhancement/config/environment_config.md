# Environment Configuration Guide

## Overview

The Agent System supports environment-based configuration for flexible deployment across different environments (development, staging, production).

## Environment Variables

### API Configuration

```bash
# API URLs
AGENT_API_URL=http://localhost:8441          # Backend API URL
FRONTEND_URL=http://localhost:8443           # Frontend application URL
OLLAMA_API_URL=http://localhost:11434       # Ollama service URL

# WebSocket URLs are automatically derived from API URLs
# HTTP URLs are converted to WS/WSS protocols
```

### Test Configuration

```bash
# Test timeouts and retry settings
TEST_TIMEOUT=30                              # API request timeout (seconds)
WEBSOCKET_TIMEOUT=5.0                        # WebSocket connection timeout
MAX_RETRIES=3                                # Maximum retry attempts for failed requests
```

### Database Configuration

```bash
# PostgreSQL connection string
DATABASE_URL=postgresql://user:password@localhost:5432/agent_system
```

### Monitoring Configuration

```bash
# Prometheus and Grafana URLs (for advanced monitoring)
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3001
```

### Security Configuration

```bash
# JWT settings (for advanced security features)
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Logging Configuration

```bash
# Logging settings
LOG_LEVEL=INFO                               # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json                              # json or text
```

### Feature Flags

```bash
# Feature toggles
ENABLE_ADVANCED_MONITORING=false            # Enable Prometheus/Grafana monitoring
ENABLE_SECURITY_FEATURES=false              # Enable JWT authentication
ENABLE_CIRCUIT_BREAKERS=false               # Enable circuit breaker patterns
```

## Configuration Files

### Development (.env.development)

```bash
AGENT_API_URL=http://localhost:8441
FRONTEND_URL=http://localhost:8443
OLLAMA_API_URL=http://localhost:11434
TEST_TIMEOUT=30
WEBSOCKET_TIMEOUT=5.0
MAX_RETRIES=3
LOG_LEVEL=DEBUG
ENABLE_ADVANCED_MONITORING=false
ENABLE_SECURITY_FEATURES=false
```

### Production (.env.production)

```bash
AGENT_API_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com
OLLAMA_API_URL=http://ollama-service:11434
TEST_TIMEOUT=60
WEBSOCKET_TIMEOUT=10.0
MAX_RETRIES=5
LOG_LEVEL=INFO
LOG_FORMAT=json
DATABASE_URL=postgresql://user:password@db-host:5432/agent_system
JWT_SECRET_KEY=production-secret-key
ENABLE_ADVANCED_MONITORING=true
ENABLE_SECURITY_FEATURES=true
ENABLE_CIRCUIT_BREAKERS=true
```

## Usage in Code

### Python Configuration

```python
import os

# Get configuration with fallbacks
api_url = os.getenv('AGENT_API_URL', 'http://localhost:8441')
timeout = int(os.getenv('TEST_TIMEOUT', '30'))
debug_mode = os.getenv('LOG_LEVEL', 'INFO') == 'DEBUG'
```

### Test Configuration

```python
# Environment-aware test configuration
BASE_URL = os.getenv('AGENT_API_URL', 'http://localhost:8441')
TEST_TIMEOUT = int(os.getenv('TEST_TIMEOUT', '30'))
WEBSOCKET_TIMEOUT = float(os.getenv('WEBSOCKET_TIMEOUT', '5.0'))
```

## Docker Configuration

### docker-compose.yml

```yaml
version: '3.8'
services:
  backend:
    environment:
      - AGENT_API_URL=${AGENT_API_URL}
      - DATABASE_URL=${DATABASE_URL}
      - LOG_LEVEL=${LOG_LEVEL}
    env_file:
      - .env

  frontend:
    environment:
      - REACT_APP_API_URL=${AGENT_API_URL}
    env_file:
      - .env
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-system-config
data:
  AGENT_API_URL: "https://api.production.com"
  DATABASE_URL: "postgresql://user:password@db:5432/agent_system"
  LOG_LEVEL: "INFO"
  ENABLE_ADVANCED_MONITORING: "true"
```

## Validation

The system validates configuration on startup:

1. **Required Variables**: API URLs must be provided
2. **URL Format**: URLs must include protocol (http/https)
3. **Numeric Values**: Timeouts must be valid numbers
4. **Database URLs**: Must follow PostgreSQL connection string format

## Security Considerations

1. **Secret Management**: Use Kubernetes secrets for production credentials
2. **Environment Separation**: Different configurations for dev/staging/prod
3. **Access Control**: Limit who can modify environment variables
4. **Audit Logging**: Log configuration changes in production

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failures**
   - Check if AGENT_API_URL is accessible
   - Verify WebSocket URL derivation logic

2. **Database Connection Issues**
   - Validate DATABASE_URL format
   - Check network connectivity to database

3. **Test Timeouts**
   - Increase TEST_TIMEOUT for slow networks
   - Check service availability before running tests
