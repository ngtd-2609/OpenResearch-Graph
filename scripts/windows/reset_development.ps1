$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
Write-Host "WARNING: This deletes PostgreSQL, Redis state and uploaded PDFs." -ForegroundColor Red
$answer = Read-Host "Type DELETE-OPENRESEARCH to continue"
if ($answer -ne "DELETE-OPENRESEARCH") {
    Write-Host "Cancelled; no data was removed."
    exit 0
}
docker compose down -v --remove-orphans
if ($LASTEXITCODE -ne 0) { throw "Reset failed" }
Write-Host "Development volumes deleted. Run setup.ps1 to recreate them." -ForegroundColor Yellow
