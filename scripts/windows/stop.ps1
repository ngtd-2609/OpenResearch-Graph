param([switch]$RemoveOrphans)
$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
$args = @("compose", "down")
if ($RemoveOrphans) { $args += "--remove-orphans" }
& docker @args
if ($LASTEXITCODE -ne 0) { throw "Failed to stop containers" }
Write-Host "Containers stopped. Named volumes were preserved." -ForegroundColor Green
