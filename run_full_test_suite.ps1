# Full Test Suite Execution Script
# Runs comprehensive tests against Docker environment

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "FULL TEST SUITE EXECUTION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker containers
Write-Host "[1/5] Checking Docker containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml ps

Write-Host ""
Write-Host "[2/5] Checking backend health..." -ForegroundColor Yellow
$health = docker exec compression_backend curl -s http://localhost:8000/health 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend is healthy" -ForegroundColor Green
} else {
    Write-Host "⚠️  Backend health check failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/5] Running core framework tests..." -ForegroundColor Yellow
cd backend
python -m pytest tests/core/test_task_decomposer.py tests/agents/test_orchestrator_agent.py tests/integration/test_data_pipeline_live.py -v --tb=short -q

Write-Host ""
Write-Host "[4/5] Running live API tests..." -ForegroundColor Yellow
python -m pytest tests/integration/test_full_api_suite.py -v --tb=short -q

Write-Host ""
Write-Host "[5/5] Generating coverage report..." -ForegroundColor Yellow
python -m pytest tests/core/ tests/agents/ tests/integration/ --cov=app --cov-report=term-missing --cov-report=html -q

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "TEST SUITE COMPLETE" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Coverage report: backend/htmlcov/index.html" -ForegroundColor Green

