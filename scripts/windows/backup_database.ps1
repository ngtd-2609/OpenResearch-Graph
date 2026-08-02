param([string]$OutputDirectory = "backups")

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

New-Item -ItemType Directory -Force $OutputDirectory | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$path = Join-Path $OutputDirectory "openresearch-$stamp.sql"
$containerPath = "/tmp/openresearch-$stamp.sql"

$containerId = (docker compose ps -q postgres).Trim()
if (-not $containerId) {
    throw "The postgres container is not running. Start it with: docker compose up -d postgres"
}

Write-Host "Creating a plain-SQL PostgreSQL backup..." -ForegroundColor Cyan
docker compose exec -T postgres sh -c "pg_dump --no-owner --no-privileges --clean --if-exists -U openresearch_user -d openresearch > '$containerPath'"
if ($LASTEXITCODE -ne 0) {
    throw "pg_dump failed. Check: docker compose logs postgres"
}

try {
    docker cp "${containerId}:${containerPath}" $path
    if ($LASTEXITCODE -ne 0) {
        throw "docker cp failed while copying the backup to the host."
    }
}
finally {
    docker compose exec -T postgres rm -f $containerPath | Out-Null
}

if (-not (Test-Path $path) -or (Get-Item $path).Length -eq 0) {
    Remove-Item $path -ErrorAction SilentlyContinue
    throw "Backup file is empty."
}

Write-Host "Backup written: $path" -ForegroundColor Green
Write-Host "Verify it by restoring into a disposable database before relying on it." -ForegroundColor Yellow
