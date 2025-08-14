#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

Write-Host "`n==> DraftDiff setup (Windows PowerShell)" -ForegroundColor Cyan

# Resolve repo root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir '..')
Set-Location $RepoRoot

function Get-PoetryExe {
  # Try PATH first
  $cmd = (Get-Command poetry -ErrorAction SilentlyContinue)
  if ($cmd) { return $cmd.Source }
  # Common install locations (installer >= 2.x)
  $candidates = @(
    (Join-Path $env:APPDATA 'pypoetry/venv/Scripts/poetry.exe'),
    (Join-Path $env:LOCALAPPDATA 'pypoetry/venv/Scripts/poetry.exe'),
    (Join-Path $env:USERPROFILE '.poetry/bin/poetry.exe')
  )
  foreach ($path in $candidates) {
    if ($path -and (Test-Path $path)) { return $path }
  }
  # where.exe as last PATH probe
  try {
    $where = (where.exe poetry 2>$null | Select-Object -First 1)
    if ($where) { return $where }
  } catch {}
  return $null
}

# Install Poetry if missing
$poetryBefore = Get-PoetryExe
if (-not $poetryBefore) {
  Write-Host "`n-> Installing Poetry..." -ForegroundColor Yellow
  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
}

$PoetryExe = Get-PoetryExe
if ($PoetryExe) {
  Write-Host "Using Poetry at: $PoetryExe" -ForegroundColor DarkGray
  $script:PoetryExe = $PoetryExe
} else {
  Write-Host "Poetry not found on PATH yet; will try 'py -m poetry' as a fallback." -ForegroundColor Yellow
  $script:PoetryExe = $null
}

function Run-Poetry {
  param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Args
  )
  if ($script:PoetryExe) { & $script:PoetryExe @Args }
  else { & py -m poetry @Args }
}

function Get-PythonExe {
  $versions = @('3.12','3.11','3.10')
  foreach ($v in $versions) {
    try {
      $exe = (& py -$v -c "import sys; print(sys.executable)" 2>$null)
      if ($exe) { return $exe.Trim() }
    } catch {}
  }
  try {
    $exe = (& py -3 -c "import sys; print(sys.executable)" 2>$null)
    if ($exe) { return $exe.Trim() }
  } catch {}
  $cmd = (Get-Command python -ErrorAction SilentlyContinue)
  if ($cmd) { return $cmd.Source }
  return $null
}

# Make sure a supported Python version exists
Write-Host "`n-> Setting up backend (Python)" -ForegroundColor Cyan
Set-Location (Join-Path $RepoRoot 'backend')

if (-not (Test-Path .env) -and (Test-Path .env.example)) {
  Copy-Item .env.example .env
  Write-Host "Created backend/.env from .env.example (remember to add RIOT_API_KEY)." -ForegroundColor Yellow
}

# Ensure in-project venv
Run-Poetry config virtualenvs.in-project true | Out-Null

# Prefer a working Python (3.12/3.11/3.10) discovered via py launcher
$pythonExe = Get-PythonExe
if (-not $pythonExe) {
  throw "No suitable Python 3.10-3.12 found. Please install Python 3.12 and re-run."
}

# Create venv and install deps
Run-Poetry env use $pythonExe | Out-Null
Run-Poetry install --no-interaction --no-ansi

# Frontend setup
Write-Host "`n-> Setting up frontend (Node)" -ForegroundColor Cyan
Set-Location (Join-Path $RepoRoot 'frontend')

# nvm-windows if available
$nvmCmd = (Get-Command nvm -ErrorAction SilentlyContinue)
if ($nvmCmd) {
  & nvm install 20 | Out-Null
  & nvm use 20 | Out-Null
} else {
  Write-Host "Warning: nvm-windows not found. Ensure Node 20 is installed. Current: " -NoNewline
  try { node -v } catch { Write-Host 'not found' }
}

# Install node deps (prefer pnpm/yarn if installed)
$pnpmCmd = (Get-Command pnpm -ErrorAction SilentlyContinue)
$yarnCmd = (Get-Command yarn -ErrorAction SilentlyContinue)
if ($pnpmCmd) {
  pnpm install --frozen-lockfile 2>$null; if ($LASTEXITCODE -ne 0) { pnpm install }
} elseif ($yarnCmd) {
  yarn install --frozen-lockfile 2>$null; if ($LASTEXITCODE -ne 0) { yarn install }
} else {
  npm install --legacy-peer-deps 2>$null; if ($LASTEXITCODE -ne 0) { npm install }
}

Set-Location $RepoRoot

@"

==> Setup complete

Next steps:
- Start backend:
  cd backend; poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

- Start frontend:
  cd frontend; npm run dev

Notes:
- If Poetry isn't found after install, open a new terminal or run:  py -m poetry --version
- Update backend/.env with RIOT_API_KEY.
"@ | Write-Host
