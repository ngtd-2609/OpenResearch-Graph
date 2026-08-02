$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

function Assert-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found. Install it and open a new PowerShell window."
    }
}

Assert-Command "docker"
docker info | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Docker Engine is not running. Open Docker Desktop." }

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[CREATED] .env from .env.example" -ForegroundColor Yellow
}

Write-Host "[1/4] Starting PostgreSQL and Redis..." -ForegroundColor Cyan
docker compose up -d postgres redis
if ($LASTEXITCODE -ne 0) { throw "Infrastructure startup failed." }

Write-Host "[2/4] Applying Alembic migrations..." -ForegroundColor Cyan
docker compose run --rm backend alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw "Migration failed. Read backend/postgres logs." }

Write-Host "[3/4] Seeding development data..." -ForegroundColor Cyan
docker compose run --rm backend python -m app.scripts.seed
if ($LASTEXITCODE -ne 0) { throw "Seed failed." }

Write-Host "[4/4] Running system doctor..." -ForegroundColor Cyan
python scripts/system_doctor.py

Write-Host "Setup complete. Run .\scripts\windows\start.ps1" -ForegroundColor Green
Write-Host "Before production, replace demo credentials and JWT/database secrets." -ForegroundColor Yellow
