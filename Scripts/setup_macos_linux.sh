#!/usr/bin/env bash
set -euo pipefail

# Resolve repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

printf "\n==> DraftDiff setup (macOS/Linux)\n"

# Ensure curl
if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required. Please install curl and re-run." >&2
  exit 1
fi

# Install Poetry if missing
if ! command -v poetry >/dev/null 2>&1; then
  echo "\n-> Installing Poetry..."
  curl -sSL https://install.python-poetry.org | python3 -
else
  echo "\n-> Poetry already installed"
fi

# Ensure Poetry in PATH for this session
export PATH="$HOME/.local/bin:$PATH"
poetry --version || true

# Backend setup
echo "\n-> Setting up backend (Python)"
cd "$REPO_ROOT/backend"

# Create .env if missing
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "Created backend/.env from .env.example (remember to add RIOT_API_KEY)."
fi

# Use in-project venv
poetry config virtualenvs.in-project true

# Prefer Python 3.12 if available
PY="python3"
if command -v python3.12 >/dev/null 2>&1; then
  PY="python3.12"
fi
poetry env use "$PY" || true

# Install deps
poetry install --no-interaction --no-ansi

# Frontend setup
echo "\n-> Setting up frontend (Node)"
cd "$REPO_ROOT/frontend"

# Use Node 20 with nvm if available
if command -v nvm >/dev/null 2>&1; then
  nvm install 20 >/dev/null
  nvm use 20 >/dev/null
elif [ -s "$HOME/.nvm/nvm.sh" ]; then
  # shellcheck disable=SC1090
  . "$HOME/.nvm/nvm.sh"
  nvm install 20 >/dev/null
  nvm use 20 >/dev/null
else
  echo "Warning: nvm not found. Ensure Node 20 is installed. Current: $(node -v 2>/dev/null || echo 'not found')"
fi

# Install node deps
if command -v pnpm >/dev/null 2>&1; then
  pnpm install --frozen-lockfile || pnpm install
elif command -v yarn >/dev/null 2>&1; then
  yarn install --frozen-lockfile || yarn install
else
  npm install --legacy-peer-deps || npm install
fi

cd "$REPO_ROOT"

cat << 'EON'

==> Setup complete

Next steps:
- Start backend:
  cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

- Start frontend:
  cd frontend && npm run dev

Notes:
- Add Poetry to PATH permanently by appending to your shell rc:
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc  # or ~/.bashrc
- Update backend/.env with RIOT_API_KEY.
EON
