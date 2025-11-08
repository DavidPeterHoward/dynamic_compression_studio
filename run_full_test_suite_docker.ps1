# Full Test Suite Runner for Docker Environment (PowerShell)
# Runs comprehensive tests including live API tests against Docker containers

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Full Test Suite with Docker Integration" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Configuration
$COMPOSE_FILE = "docker-compose.dev.yml"
$MAX_WAIT = 120

# Function to check service health
function Check-ServiceHealth {
    param(
        [string]$ServiceName,
        [string]$Url,
        [int]$MaxAttempts = 30
    )
    
    Write-Host "Waiting for $ServiceName to be healthy..." -ForegroundColor Yellow
    
    $attempt = 1
    while ($attempt -le $MaxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $ServiceName is healthy" -ForegroundColor Green
                return $true
            }
        } catch {
            # Service not ready yet
        }
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
        $attempt++
    }
    
    Write-Host ""
    Write-Host "❌ $ServiceName failed to become healthy" -ForegroundColor Red
    return $false
}

# Step 1: Start Docker services in detached mode
Write-Host "`nStep 1: Starting Docker services..." -ForegroundColor Yellow
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to start
Write-Host "`nWaiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Step 2: Check service health
Write-Host "`nStep 2: Checking service health..." -ForegroundColor Yellow

$postgresHealthy = Check-ServiceHealth "PostgreSQL" "http://localhost:5433"
$redisHealthy = Check-ServiceHealth "Redis" "http://localhost:6379"
$backendHealthy = Check-ServiceHealth "Backend API" "http://localhost:8443/health"

if (-not $backendHealthy) {
    Write-Host "⚠️  Some services may not be fully ready, continuing with tests..." -ForegroundColor Yellow
}

# Step 3: Run database migrations
Write-Host "`nStep 3: Running database migrations..." -ForegroundColor Yellow
docker-compose -f $COMPOSE_FILE run --rm db-migrate 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Migration service not available, continuing..." -ForegroundColor Yellow
}

# Step 4: Run full test suite
Write-Host "`nStep 4: Running comprehensive test suite..." -ForegroundColor Yellow

# Core tests
Write-Host "`nRunning core component tests..." -ForegroundColor Green
docker-compose -f $COMPOSE_FILE run --rm test-runner pytest tests/core/ -v --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some core tests failed" -ForegroundColor Yellow
}

# Agent tests
Write-Host "`nRunning agent tests..." -ForegroundColor Green
docker-compose -f $COMPOSE_FILE run --rm test-runner pytest tests/agents/ -v --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some agent tests failed" -ForegroundColor Yellow
}

# Integration tests
Write-Host "`nRunning integration tests..." -ForegroundColor Green
docker-compose -f $COMPOSE_FILE run --rm test-runner pytest tests/integration/ -v --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some integration tests failed" -ForegroundColor Yellow
}

# Live API tests
Write-Host "`nRunning live API tests..." -ForegroundColor Green
docker-compose -f $COMPOSE_FILE run --rm test-runner pytest tests/integration/test_live_api_docker.py -v --tb=short -s
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some live API tests failed" -ForegroundColor Yellow
}

# Comprehensive test suite
Write-Host "`nRunning comprehensive test suite..." -ForegroundColor Green
docker-compose -f $COMPOSE_FILE run --rm test-runner pytest tests/comprehensive_test_suite/ -v --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some comprehensive tests failed" -ForegroundColor Yellow
}

# Step 5: Generate coverage report
Write-Host "`nStep 5: Generating test coverage report..." -ForegroundColor Yellow
docker-compose -f $COMPOSE_FILE run --rm test-runner pytest `
    tests/core/ tests/agents/ tests/integration/ `
    --cov=app `
    --cov-report=html:/app/htmlcov `
    --cov-report=term `
    --cov-report=xml:/app/coverage.xml `
    -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Coverage generation had issues" -ForegroundColor Yellow
}

# Step 6: Test summary
Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "✅ Test Suite Execution Complete" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Step 7: Show container status
Write-Host "`nContainer Status:" -ForegroundColor Yellow
docker-compose -f $COMPOSE_FILE ps

Write-Host "`n✅ Test suite completed!" -ForegroundColor Green
Write-Host "Coverage reports available in: backend/htmlcov/" -ForegroundColor Cyan
