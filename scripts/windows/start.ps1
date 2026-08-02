param(
    [switch]$Detached,
    [switch]$NoBuild
)
$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

$args = @("compose", "up")
if ($Detached) { $args += "-d" }
if (-not $NoBuild) { $args += "--build" }

Write-Host "Starting OpenResearch Graph..." -ForegroundColor Cyan
& docker @args
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

if ($Detached) {
    docker compose ps
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
    Write-Host "Swagger:  http://localhost:8000/docs" -ForegroundColor Green
}
