param([switch]$IncludeDatabase, [switch]$IncludeE2E)
$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

Write-Host "Running backend tests with 80% coverage gate..." -ForegroundColor Cyan
docker compose run --rm backend sh -lc "PYTHONPATH=.:.. pytest tests --ignore=tests/integration --cov=app --cov-fail-under=80"
if ($LASTEXITCODE -ne 0) { throw "Backend tests failed" }

if ($IncludeDatabase) {
    Write-Host "Running PostgreSQL integration tests..." -ForegroundColor Cyan
    docker compose up -d postgres redis
    docker compose run --rm -e RUN_DB_TESTS=1 backend sh -lc "PYTHONPATH=.:.. pytest tests/integration -q"
    if ($LASTEXITCODE -ne 0) { throw "Database integration tests failed" }
}

Write-Host "Running frontend lint, typecheck, unit tests and build..." -ForegroundColor Cyan
docker compose run --rm frontend sh -lc "npm run lint && npm run typecheck && npm run test:run && npm run build"
if ($LASTEXITCODE -ne 0) { throw "Frontend quality checks failed" }

if ($IncludeE2E) {
    docker compose up -d frontend backend
    docker compose exec frontend npm run e2e
    if ($LASTEXITCODE -ne 0) { throw "Playwright tests failed" }
}
Write-Host "All requested checks passed." -ForegroundColor Green
