$ErrorActionPreference = "Continue"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
python scripts/system_doctor.py
exit $LASTEXITCODE
