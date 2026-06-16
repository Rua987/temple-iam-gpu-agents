# Offline agent validation gate (no GPU / no games required).
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$checkPy = Join-Path $PSScriptRoot "check_offline.py"

python $checkPy
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "check_offline: OK"
