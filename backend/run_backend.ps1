$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvActivate = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"

if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Warning "Virtual environment not found at $venvActivate"
}

$env:PYTHONPATH = $repoRoot
Set-Location $repoRoot
python -m uvicorn backend.app.main:app --reload
