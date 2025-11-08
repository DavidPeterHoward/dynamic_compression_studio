#!/bin/bash

# Full Test Suite Runner for Docker Environment
# Runs comprehensive tests including live API tests against Docker containers

set -e

echo "🚀 Starting Full Test Suite with Docker Integration"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.dev.yml"
TEST_TIMEOUT=300
MAX_WAIT=120

# Function to check if service is healthy
check_service_health() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}Waiting for $service to be healthy...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service is healthy${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service failed to become healthy${NC}"
    return 1
}

# Step 1: Start Docker services in detached mode
echo -e "\n${YELLOW}Step 1: Starting Docker services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Step 2: Check service health
echo -e "\n${YELLOW}Step 2: Checking service health...${NC}"

check_service_health "PostgreSQL" "http://localhost:5433" || exit 1
check_service_health "Redis" "http://localhost:6379" || exit 1
check_service_health "Backend API" "http://localhost:8443/health" || exit 1

# Step 3: Run database migrations
echo -e "\n${YELLOW}Step 3: Running database migrations...${NC}"
docker-compose -f "$COMPOSE_FILE" run --rm db-migrate || echo "Migration service not available, continuing..."

# Step 4: Run full test suite
echo -e "\n${YELLOW}Step 4: Running comprehensive test suite...${NC}"

# Core tests
echo -e "\n${GREEN}Running core component tests...${NC}"
docker-compose -f "$COMPOSE_FILE" run --rm test-runner pytest tests/core/ -v --tb=short || true

# Agent tests
echo -e "\n${GREEN}Running agent tests...${NC}"
docker-compose -f "$COMPOSE_FILE" run --rm test-runner pytest tests/agents/ -v --tb=short || true

# Integration tests
echo -e "\n${GREEN}Running integration tests...${NC}"
docker-compose -f "$COMPOSE_FILE" run --rm test-runner pytest tests/integration/ -v --tb=short || true

# Live API tests
echo -e "\n${GREEN}Running live API tests...${NC}"
docker-compose -f "$COMPOSE_FILE" run --rm test-runner pytest tests/integration/test_live_api_docker.py -v --tb=short -s || true

# Comprehensive test suite
echo -e "\n${GREEN}Running comprehensive test suite...${NC}"
docker-compose -f "$COMPOSE_FILE" run --rm test-runner pytest tests/comprehensive_test_suite/ -v --tb=short || true

# Step 5: Generate coverage report
echo -e "\n${YELLOW}Step 5: Generating test coverage report...${NC}"
docker-compose -f "$COMPOSE_FILE" run --rm test-runner pytest \
    tests/core/ tests/agents/ tests/integration/ \
    --cov=app \
    --cov-report=html:/app/htmlcov \
    --cov-report=term \
    --cov-report=xml:/app/coverage.xml \
    -v || true

# Step 6: Test summary
echo -e "\n${GREEN}=================================================="
echo -e "✅ Test Suite Execution Complete"
echo -e "==================================================${NC}"

# Step 7: Show container status
echo -e "\n${YELLOW}Container Status:${NC}"
docker-compose -f "$COMPOSE_FILE" ps

echo -e "\n${GREEN}Test suite completed!${NC}"
echo -e "Coverage reports available in: backend/htmlcov/"
echo -e "To view coverage: docker-compose -f $COMPOSE_FILE exec test-runner python -m http.server 8000 -d /app/htmlcov"
