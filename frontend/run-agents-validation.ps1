# PowerShell script to run Agents Tab validation tests
$env:SKIP_WEBSERVER = "true"
$env:BASE_URL = "http://localhost:8443"
$env:API_URL = "http://localhost:8441"

Write-Host "Running Agents Tab Validation Tests..."
Write-Host "BASE_URL: $env:BASE_URL"
Write-Host "API_URL: $env:API_URL"
Write-Host ""

npx playwright test tests/agents-tab-validation.spec.ts --project=chromium --reporter=list --timeout=120000

