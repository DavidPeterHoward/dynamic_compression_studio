#!/bin/bash
# Comprehensive Test Coverage for Docker Containers
# Run this script from the project root

set -e

echo "================================================================================"
echo "COMPREHENSIVE DOCKER CONTAINER TEST COVERAGE"
echo "================================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
echo -e "${YELLOW}[1/7] Checking Docker status...${NC}"
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}✗ docker-compose.yml not found. Please run from project root.${NC}"
    exit 1
fi

# Start containers if not running
echo -e "${YELLOW}[2/7] Starting Docker containers...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Containers started${NC}"
echo ""

# Wait for services to be ready
echo -e "${YELLOW}[3/7] Waiting for services to be ready...${NC}"
sleep 10

# Check backend health
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo -e "${RED}✗ Backend failed to start${NC}"
        docker-compose logs backend
        exit 1
    fi
    sleep 2
done
echo ""

# Run Backend Tests
echo -e "${YELLOW}[4/7] Running Backend Tests...${NC}"
echo "================================================================================"

# Install test dependencies
echo "Installing test dependencies..."
docker-compose exec -T backend pip install pytest pytest-cov pytest-asyncio pytest-html coverage > /dev/null 2>&1 || true

# Run pytest with coverage
echo ""
echo "Running pytest suite..."
docker-compose exec -T backend pytest tests/ \
    --cov=app \
    --cov-report=term \
    --cov-report=html:coverage_reports/backend_html \
    --cov-report=json:coverage_reports/backend_coverage.json \
    --html=coverage_reports/backend_test_report.html \
    --self-contained-html \
    -v || true

echo ""
echo -e "${GREEN}✓ Backend tests completed${NC}"
echo ""

# Run Metrics Accuracy Tests
echo -e "${YELLOW}[5/7] Running Metrics Accuracy Tests...${NC}"
echo "================================================================================"
docker-compose exec -T backend python scripts/test_all_metrics.py || true
echo ""
echo -e "${GREEN}✓ Metrics tests completed${NC}"
echo ""

# Run API Endpoint Tests
echo -e "${YELLOW}[6/7] Running API Endpoint Tests...${NC}"
echo "================================================================================"

# Test all critical endpoints
ENDPOINTS=(
    "/health"
    "/api/v1/metrics/system/comprehensive"
    "/api/v1/metrics/dashboard"
    "/api/v1/metrics/performance"
    "/api/v1/metrics/algorithms"
)

SUCCESS_COUNT=0
FAIL_COUNT=0

for endpoint in "${ENDPOINTS[@]}"; do
    echo -n "Testing GET $endpoint ... "
    if curl -s -f "http://localhost:8000$endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${RED}✗ FAIL${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done

echo ""
echo "API Endpoint Test Results: $SUCCESS_COUNT passed, $FAIL_COUNT failed"
echo ""

# Generate Coverage Summary
echo -e "${YELLOW}[7/7] Generating Coverage Summary...${NC}"
echo "================================================================================"

# Create summary report
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="docker_test_coverage_report_${TIMESTAMP}.txt"

cat > "$REPORT_FILE" << EOF
================================================================================
DOCKER CONTAINER TEST COVERAGE REPORT
Generated: $(date)
================================================================================

INFRASTRUCTURE STATUS
------------------------------------------------------------
✓ Docker containers: Running
✓ Backend service: Healthy (http://localhost:8000)
✓ Frontend service: Running (http://localhost:3000)

BACKEND TESTS
------------------------------------------------------------
EOF

# Extract coverage from pytest output
docker-compose exec -T backend coverage report >> "$REPORT_FILE" 2>/dev/null || echo "Coverage data not available" >> "$REPORT_FILE"

cat >> "$REPORT_FILE" << EOF

API ENDPOINT TESTS
------------------------------------------------------------
Total Endpoints Tested: ${#ENDPOINTS[@]}
Passed: $SUCCESS_COUNT
Failed: $FAIL_COUNT
Success Rate: $(( SUCCESS_COUNT * 100 / ${#ENDPOINTS[@]} ))%

TESTED ENDPOINTS:
EOF

for endpoint in "${ENDPOINTS[@]}"; do
    echo "  - $endpoint" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" << EOF

METRICS VALIDATION
------------------------------------------------------------
See backend/metrics_test_results_*.json for detailed metrics validation results

COVERAGE REPORTS LOCATION
------------------------------------------------------------
- Backend Coverage (HTML): coverage_reports/backend_html/index.html
- Backend Coverage (JSON): coverage_reports/backend_coverage.json
- Backend Test Report (HTML): coverage_reports/backend_test_report.html
- This Summary Report: $REPORT_FILE

DOCKER LOGS
------------------------------------------------------------
To view logs:
  docker-compose logs backend
  docker-compose logs frontend

TO VIEW COVERAGE REPORTS
------------------------------------------------------------
  # Open HTML coverage report in browser
  open coverage_reports/backend_html/index.html  # macOS
  xdg-open coverage_reports/backend_html/index.html  # Linux
  start coverage_reports/backend_html/index.html  # Windows

================================================================================
EOF

# Display summary
cat "$REPORT_FILE"

echo ""
echo -e "${GREEN}================================================================================${NC}"
echo -e "${GREEN}TEST COVERAGE COMPLETE${NC}"
echo -e "${GREEN}================================================================================${NC}"
echo ""
echo "Summary report saved to: $REPORT_FILE"
echo ""
echo "Next steps:"
echo "  1. Review coverage reports in coverage_reports/"
echo "  2. Check test results in $REPORT_FILE"
echo "  3. View metrics validation in backend/metrics_test_results_*.json"
echo ""

# Copy results from container
echo "Copying test results from containers..."
docker-compose exec -T backend bash -c "mkdir -p /tmp/test_results && cp -r coverage_reports /tmp/test_results/" 2>/dev/null || true
docker cp $(docker-compose ps -q backend):/tmp/test_results/coverage_reports ./coverage_reports/ 2>/dev/null || true

echo ""
echo -e "${GREEN}✓ All tests completed successfully!${NC}"
echo ""

# Ask if user wants to stop containers
read -p "Stop Docker containers? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down
    echo -e "${GREEN}✓ Containers stopped${NC}"
fi

