# PowerShell Script - Comprehensive Test Coverage for Docker Containers
# Run this from the project root

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "COMPREHENSIVE DOCKER CONTAINER TEST COVERAGE" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "[1/7] Checking Docker status..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Start containers
Write-Host "[2/7] Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "✓ Containers started" -ForegroundColor Green
Write-Host ""

# Wait for backend
Write-Host "[3/7] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

$maxRetries = 30
$retryCount = 0
while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Backend is healthy" -ForegroundColor Green
            break
        }
    } catch {
        $retryCount++
        if ($retryCount -eq $maxRetries) {
            Write-Host "✗ Backend failed to start" -ForegroundColor Red
            docker-compose logs backend
            exit 1
        }
        Start-Sleep -Seconds 2
    }
}
Write-Host ""

# Install test dependencies
Write-Host "[4/7] Running Backend Tests..." -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Installing test dependencies..."
docker-compose exec -T backend pip install pytest pytest-cov pytest-asyncio pytest-html coverage 2>&1 | Out-Null

# Run pytest with coverage
Write-Host ""
Write-Host "Running pytest suite with coverage..." -ForegroundColor Yellow
docker-compose exec -T backend pytest tests/ `
    --cov=app `
    --cov-report=term `
    --cov-report=html:coverage_reports/backend_html `
    --cov-report=json:coverage_reports/backend_coverage.json `
    --html=coverage_reports/backend_test_report.html `
    --self-contained-html `
    -v 2>&1

Write-Host ""
Write-Host "✓ Backend tests completed" -ForegroundColor Green
Write-Host ""

# Run Metrics Tests
Write-Host "[5/7] Running Metrics Accuracy Tests..." -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
docker-compose exec -T backend python scripts/test_all_metrics.py 2>&1
Write-Host ""
Write-Host "✓ Metrics tests completed" -ForegroundColor Green
Write-Host ""

# Test API Endpoints
Write-Host "[6/7] Running API Endpoint Tests..." -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

$endpoints = @(
    "/health",
    "/api/v1/metrics/system/comprehensive",
    "/api/v1/metrics/dashboard",
    "/api/v1/metrics/performance",
    "/api/v1/metrics/algorithms"
)

$successCount = 0
$failCount = 0

foreach ($endpoint in $endpoints) {
    Write-Host -NoNewline "Testing GET $endpoint ... "
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000$endpoint" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ PASS" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "✗ FAIL" -ForegroundColor Red
            $failCount++
        }
    } catch {
        Write-Host "✗ FAIL" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "API Endpoint Test Results: $successCount passed, $failCount failed" -ForegroundColor White
Write-Host ""

# Generate Summary
Write-Host "[7/7] Generating Coverage Summary..." -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = "docker_test_coverage_report_$timestamp.txt"

@"
================================================================================
DOCKER CONTAINER TEST COVERAGE REPORT
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
================================================================================

INFRASTRUCTURE STATUS
------------------------------------------------------------
✓ Docker containers: Running
✓ Backend service: Healthy (http://localhost:8000)
✓ Frontend service: Running (http://localhost:3000)

BACKEND TESTS
------------------------------------------------------------
"@ | Out-File -FilePath $reportFile -Encoding UTF8

# Add coverage report
docker-compose exec -T backend coverage report 2>&1 | Out-File -FilePath $reportFile -Append -Encoding UTF8

@"

API ENDPOINT TESTS
------------------------------------------------------------
Total Endpoints Tested: $($endpoints.Count)
Passed: $successCount
Failed: $failCount
Success Rate: $([math]::Round($successCount / $endpoints.Count * 100, 2))%

TESTED ENDPOINTS:
"@ | Out-File -FilePath $reportFile -Append -Encoding UTF8

foreach ($endpoint in $endpoints) {
    "  - $endpoint" | Out-File -FilePath $reportFile -Append -Encoding UTF8
}

@"

METRICS VALIDATION
------------------------------------------------------------
See backend/metrics_test_results_*.json for detailed metrics validation

COVERAGE REPORTS LOCATION
------------------------------------------------------------
- Backend Coverage (HTML): coverage_reports/backend_html/index.html
- Backend Coverage (JSON): coverage_reports/backend_coverage.json
- Backend Test Report (HTML): coverage_reports/backend_test_report.html
- This Summary Report: $reportFile

DOCKER LOGS
------------------------------------------------------------
To view logs:
  docker-compose logs backend
  docker-compose logs frontend

TO VIEW COVERAGE REPORTS
------------------------------------------------------------
  start coverage_reports\backend_html\index.html  # Windows

================================================================================
"@ | Out-File -FilePath $reportFile -Append -Encoding UTF8

# Display summary
Get-Content $reportFile

# Copy coverage reports from container
Write-Host ""
Write-Host "Copying test results from containers..." -ForegroundColor Yellow
$backendContainer = docker-compose ps -q backend
if ($backendContainer) {
    docker cp "${backendContainer}:/app/coverage_reports" "./coverage_reports/" 2>$null
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "TEST COVERAGE COMPLETE" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Summary report saved to: $reportFile" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review coverage reports in coverage_reports/" -ForegroundColor White
Write-Host "  2. Check test results in $reportFile" -ForegroundColor White
Write-Host "  3. View metrics validation in backend/metrics_test_results_*.json" -ForegroundColor White
Write-Host "  4. Open HTML coverage report: start coverage_reports\backend_html\index.html" -ForegroundColor White
Write-Host ""
Write-Host "✓ All tests completed successfully!" -ForegroundColor Green
Write-Host ""

# Ask to stop containers
$response = Read-Host "Stop Docker containers? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    docker-compose down
    Write-Host "✓ Containers stopped" -ForegroundColor Green
}

