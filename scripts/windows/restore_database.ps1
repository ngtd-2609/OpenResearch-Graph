param(
    [Parameter(Mandatory = $true)]
    [Alias("Path")]
    [string]$BackupFile
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

$resolvedBackup = (Resolve-Path $BackupFile).Path
if ([System.IO.Path]::GetExtension($resolvedBackup).ToLowerInvariant() -ne ".sql") {
    throw "Expected a .sql backup created by backup_database.ps1."
}

$containerId = (docker compose ps -q postgres).Trim()
if (-not $containerId) {
    throw "The postgres container is not running. Start it with: docker compose up -d postgres"
}

Write-Host "This operation can overwrite objects in the development database." -ForegroundColor Yellow
$answer = Read-Host "Type RESTORE to continue"
if ($answer -ne "RESTORE") {
    Write-Host "Cancelled"
    exit 0
}

$containerPath = "/tmp/openresearch-restore.sql"
Write-Host "Copying and restoring the PostgreSQL backup..." -ForegroundColor Cyan

docker cp $resolvedBackup "${containerId}:${containerPath}"
if ($LASTEXITCODE -ne 0) {
    throw "docker cp failed while copying the backup into PostgreSQL."
}

try {
    docker compose exec -T postgres psql `
        -v ON_ERROR_STOP=1 `
        -U openresearch_user `
        -d openresearch `
        -f $containerPath

    if ($LASTEXITCODE -ne 0) {
        throw "psql restore failed. Review: docker compose logs postgres"
    }
}
finally {
    docker compose exec -T postgres rm -f $containerPath | Out-Null
}

Write-Host "Restore completed." -ForegroundColor Green
Write-Host "Next: run migrations and .\scripts\windows\doctor.ps1" -ForegroundColor Cyan
