# DraftDiff

Web application that details the win percentage of both blue and red side teams in a game of League of Legends using features such as: Champions being played, lane matchups, champion loadouts (runes), champion synergies, what patch the game is being played on, etc.

The application utilizes machine learning techniques on the champion data and Solo Queue match data from the Riot API to help garner these predictions utilizing different set of algorithms such as Neural Networks, LightGBM, etc.

---

## Plan: Modern stack, ML-driven predictions

- **Backend (Python/FastAPI)**: Typed REST API for health, predictions, and future endpoints (auth, data ETL triggers). Production-ready with Pydantic v2, async-first I/O, and Docker.
- **Frontend (Next.js 14, App Router, TypeScript)**: Modern React UX, form to submit draft context, calls FastAPI, deployable on Vercel or containers.
- **ML Workspace (Python)**: Reproducible training with scikit-learn/LightGBM, joblib packaging, optional PyTorch for deep models. Clear separation between training and serving.
- **Data & Storage**: PostgreSQL for persistent data, Redis for caching (e.g., model metadata, feature caches). Optional object storage for large artifacts.
- **Infra & DevX**: Docker Compose for local dev, Poetry for Python deps, ESLint/TS for frontend, basic CI-ready structure.

### Initial milestones

1. Scaffold API and FE with an end-to-end prediction flow using a stub model.
2. Build ML pipelines to train a first baseline model (LightGBM) and export to Joblib.
3. Wire real model into the backend, add input validation and feature processing.
4. Add caching, metrics, and simple A/B model versioning.

---

## First-time setup (Poetry and Node)

- **Prerequisites**:

  - Python 3.12 recommended (3.10–3.12 supported)
  - Node.js 20 (see `.nvmrc`)

- **Install Poetry**
  - macOS/Linux:

```bash
curl -sSL https://install.python-poetry.org | python3 -
# add to PATH for current shell session
export PATH="$HOME/.local/bin:$PATH"
poetry --version
```

- Windows (PowerShell):

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
# reopen terminal, then
poetry --version
# If not found, try: py -m poetry --version
```

- **Python virtual environment (created in-project)**

```bash
cd backend
poetry config virtualenvs.in-project true
poetry env use 3.12  # choose a 3.10–3.12 Python available on your system
poetry install
```

- **Activating the virtualenv**
  - macOS/Linux:

```bash
source backend/.venv/bin/activate
# ... work ...
deactivate
```

- Windows (PowerShell):

```powershell
backend\.venv\Scripts\Activate.ps1
# If blocked by execution policy, run once:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- **Frontend Node setup**
  - macOS/Linux (with nvm):

```bash
nvm install 20 && nvm use 20
cd frontend
npm install
npm run dev
```

- Windows (with nvm-windows):

```powershell
nvm install 20
nvm use 20
cd frontend
npm install
npm run dev
```

- **Environment variables**

  - Backend: `cd backend && cp .env.example .env`
  - Frontend: set `NEXT_PUBLIC_API_BASE_URL` if not using default `http://localhost:8000/api/v1`

- **Troubleshooting**
  - Poetry complains about Python 3.13: use `poetry env use 3.12` and ensure Python 3.12 is installed (via pyenv, asdf, or system installer).
  - If `poetry` is not found after install: add `~/.local/bin` (macOS/Linux) to PATH or reopen terminal; on Windows, use the full path printed by the installer or `py -m poetry`.
  - Node install errors: ensure Node 20 is active (`node -v` prints `v20.x`).

---

## Scripts (one-shot setup)

Run these after cloning the repo to auto-install backend and frontend dependencies and create the Python venv.

- macOS/Linux:

```bash
bash Scripts/setup_macos_linux.sh
```

- Windows (PowerShell):

```powershell
Scripts\setup_windows.ps1
```

After the script completes:

- Backend: `cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Frontend: `cd frontend && npm run dev`

Remember to add your `RIOT_API_KEY` to `backend/.env`.

---

## Riot API configuration and data endpoints

- Set in `backend/.env`:

```env
RIOT_API_KEY=your_api_key_here
RIOT_PLATFORM=na1        # e.g., na1, euw1, kr
RIOT_REGION=americas     # americas, europe, asia
DDRAGON_VERSION=          # optional, leave empty for latest
```

- Endpoints (all prefixed by `/api/v1/riot`):
  - `GET /account/by-riot-id?game_name=Faker&tag_line=KR1`
  - `GET /summoner/by-puuid/{puuid}`
  - `GET /matches/by-puuid/{puuid}?start=0&count=20&queue=420`
  - `GET /match/{match_id}`
  - `GET /match/{match_id}/timeline`
  - `GET /league/entries/by-summoner/{encrypted_summoner_id}`
  - `GET /static/champions`
  - `GET /static/runes`

These give us Solo Queue match IDs, detailed match + timeline data, player rank data, and static metadata (champions, runes) for feature engineering.

---

## Repository structure

```
DraftDiff/
  backend/
    app/
      api/
        routes/
          __init__.py
          predictions.py
          riot.py
        __init__.py
      core/
        __init__.py
        config.py
      services/
        __init__.py
        prediction_service.py
        riot_client.py
      __init__.py
    Dockerfile
    README.md
    pyproject.toml
    .env.example
  frontend/
    app/
      globals.css
      layout.tsx
      page.tsx
    Dockerfile
    next.config.mjs
    package.json
    tsconfig.json
  ml/
    README.md
    # notebooks/, src/, data/, artifacts/ (create as needed)
  Scripts/
    setup_macos_linux.sh
    setup_windows.ps1
  docker-compose.yml
  .gitignore
  README.md (this file)
```

---

## Backend

- **Framework**: FastAPI + Uvicorn
- **Config**: Pydantic settings via env, CORS enabled for FE
- **ML runtime**: scikit-learn/LightGBM via Joblib model artifact
- **DB/Caching**: SQLAlchemy/Postgres, Redis (ready to wire)

Run locally:

```bash
cd backend
cp .env.example .env
# add RIOT_API_KEY, RIOT_PLATFORM, RIOT_REGION
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health: `GET http://localhost:8000/api/v1/health`

Predict: `POST http://localhost:8000/api/v1/predict`

Riot: see section above for endpoints

---

## Frontend

- **Framework**: Next.js 14 (App Router) + TypeScript
- **Dev**:

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` (defaults to `http://localhost:8000/api/v1`).

---

## ML Workspace

- Train baseline models using scikit-learn/LightGBM.
- Save candidate model to `ml/artifacts/` and copy release model to `backend/models/model.joblib`.
- Future: feature store, W&B tracking, batch evaluation.

---

## Docker (optional local orchestration)

```bash
docker compose up --build
```

- Services: `api` (FastAPI), `db` (Postgres), `redis`, `web` (Next.js)

---

## Dependencies

- **Backend runtime**: FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, Redis, httpx, scikit-learn, LightGBM, joblib
- **Backend dev**: pytest, pytest-asyncio, ruff, black, isort
- **Frontend**: Next.js, React, TypeScript, ESLint

---

## Next steps

- Implement real feature extraction/parsing from payload to model vector.
- Add model registry/versioning and simple canary release.
- Integrate Riot API ETL and persistence (scheduled jobs).
- Add auth/rate limiting if needed for public release.
