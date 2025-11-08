# Comprehensive Test Suite Execution Guide

## Overview

This guide provides instructions for executing the comprehensive test suite with fail-pass bootstrap methodology using Playwright E2E testing (Chromium only) in Docker containers.

## Prerequisites

1. **Docker Desktop** installed and running
2. **Node.js** (v18+) and npm installed
3. **Python** (v3.11+) with pip installed
4. **Git** for version control

## Quick Start

### Method 1: Direct PowerShell Execution (Recommended for Windows)

```powershell
cd scripts
.\execute_comprehensive_tests.ps1
```

This script will:
- ✅ Validate all dependencies
- ✅ Run backend tests with coverage
- ✅ Run Playwright E2E tests (Chromium only)
- ✅ Run integration tests
- ✅ Generate comprehensive reports

### Method 2: Docker Compose Execution

```bash
# Build and run all test containers
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# View logs
docker-compose -f docker-compose.test.yml logs -f

# Clean up
docker-compose -f docker-compose.test.yml down -v
```

### Method 3: Individual Component Testing

#### Backend Tests Only
```bash
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term
```

#### Playwright E2E Tests Only
```bash
cd frontend
npx playwright test --project=chromium --reporter=html,list
```

#### Integration Tests Only
```bash
python scripts/test_full_system_integration.py
```

## Test Structure

### 1. Bootstrap Validation Phase
- ✅ Dependency checks (Python, Node.js, npm)
- ✅ Service health checks (Backend, Frontend)
- ✅ Environment validation

### 2. Backend Test Phase
- **Location**: `backend/tests/`
- **Coverage Target**: >70%
- **Output**: `backend/htmlcov/index.html`

### 3. Playwright E2E Test Phase
- **Location**: `frontend/tests/e2e/comprehensive.spec.ts`
- **Browser**: Chromium only
- **Test Count**: 13 comprehensive test suites
- **Output**: `frontend/playwright-report/index.html`

### 4. Integration Test Phase
- **Location**: `scripts/test_full_system_integration.py`
- **Scope**: End-to-end system validation
- **Output**: `integration_test_results.json`

## Test Coverage

### E2E Tests (Playwright)
1. ✅ Application loading and interface
2. ✅ Agent Dashboard functionality
3. ✅ Task Submission workflow
4. ✅ Compression functionality
5. ✅ Metrics and monitoring
6. ✅ System health and status
7. ✅ Navigation and routing
8. ✅ Responsive design
9. ✅ Error handling and validation
10. ✅ Performance metrics
11. ✅ API integration
12. ✅ Bootstrap validation

### Backend Tests (Pytest)
- Unit tests for all agents
- API endpoint tests
- Database connectivity tests
- Agent communication tests
- Compression engine tests

## Fail-Pass Bootstrap Methodology

The test suite implements fail-pass bootstrap methodology:

1. **Bootstrap Validation**: All prerequisites must pass
2. **Graceful Degradation**: Tests continue even if some checks fail
3. **Auto-Fix Attempts**: Common errors are automatically fixed
4. **Comprehensive Reporting**: All results documented regardless of pass/fail

## Expected Results

### Success Indicators
- ✅ All bootstrap validations pass
- ✅ Backend test coverage > 70%
- ✅ All Playwright tests pass in Chromium
- ✅ Integration tests validate workflows
- ✅ No critical console errors

### Reports Generated
1. **Backend Coverage**: `backend/htmlcov/index.html`
2. **Playwright Report**: `frontend/playwright-report/index.html`
3. **Integration Results**: `integration_test_results.json`
4. **Comprehensive Summary**: `test-results/comprehensive_test_results.json`

## Troubleshooting

### Issue: Docker containers fail to start
**Solution**: Ensure Docker Desktop is running and has sufficient resources allocated

### Issue: Playwright browser not found
**Solution**: Run `npx playwright install chromium` in the frontend directory

### Issue: Backend tests fail with import errors
**Solution**: Run `pip install -r backend/requirements.txt` and ensure all dependencies are installed

### Issue: Frontend not accessible
**Solution**: 
1. Start frontend: `cd frontend && npm run dev`
2. Verify it's running on `http://localhost:8449`
3. Check for port conflicts

### Issue: API endpoints not accessible
**Solution**:
1. Start backend: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Verify it's running on `http://localhost:8000`
3. Check database connection

## Performance Benchmarks

- **Page Load Time**: < 10 seconds (target)
- **Navigation Response**: < 3 seconds (target)
- **Full Test Suite**: ~5-10 minutes (typical)

## Next Steps After Testing

1. Review test reports in generated HTML files
2. Address any failing tests
3. Improve coverage for areas below threshold
4. Fix critical errors identified in bootstrap validation
5. Re-run tests until all pass

## Continuous Integration

For CI/CD pipelines, use:

```yaml
# Example GitHub Actions workflow
- name: Run Comprehensive Tests
  run: |
    cd scripts
    bash execute_comprehensive_tests.sh
```

---

**Last Updated**: 2025-11-02  
**Test Suite Version**: 1.0.0  
**Status**: ✅ Ready for Execution
