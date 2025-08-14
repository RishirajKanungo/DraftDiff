#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

Write-Host "`n==> DraftDiff setup (Windows PowerShell)" -ForegroundColor Cyan

# Resolve repo root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir '..')
Set-Location $RepoRoot

# Install Poetry if missing
$poetryCmd = (Get-Command poetry -ErrorAction SilentlyContinue)
if (-not $poetryCmd) {
  Write-Host "`n-> Installing Poetry..." -ForegroundColor Yellow
  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
} else {
  Write-Host "`n-> Poetry already installed" -ForegroundColor Green
}

# Make sure a supported Python version exists
Write-Host "`n-> Setting up backend (Python)" -ForegroundColor Cyan
Set-Location (Join-Path $RepoRoot 'backend')

if (-not (Test-Path .env) -and (Test-Path .env.example)) {
  Copy-Item .env.example .env
  Write-Host "Created backend/.env from .env.example (remember to add RIOT_API_KEY)." -ForegroundColor Yellow
}

# Ensure in-project venv
poetry config virtualenvs.in-project true | Out-Null

# Prefer Python 3.12 if available
$python = 'py -3.12'
try {
  & py -3.12 -V | Out-Null
} catch {
  $python = 'py -3'
}

# Create venv and install deps
& poetry env use $python | Out-Null
& poetry install --no-interaction --no-ansi

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
