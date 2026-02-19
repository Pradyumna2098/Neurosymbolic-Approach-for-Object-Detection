$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvActivate = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"

if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Warning "Virtual environment not found at $venvActivate"
}

$backendDir = Join-Path $repoRoot "backend"
Set-Location $backendDir
python -m uvicorn app.main:app --reload
