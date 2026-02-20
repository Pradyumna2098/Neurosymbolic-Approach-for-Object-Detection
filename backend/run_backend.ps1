$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvActivate = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"

if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Warning "Virtual environment not found at $venvActivate"
}

# Ensure repo root is on PYTHONPATH so the 'pipeline' module can be imported
$env:PYTHONPATH = $repoRoot

$backendDir = Join-Path $repoRoot "backend"
Set-Location $backendDir
python -m uvicorn app.main:app --reload
