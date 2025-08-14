# DraftDiff ML Documentation

This document describes the v1 feature set, data artifacts, training pipeline, and how to run it locally.

## Scope (v1)

Predict blue-side win probability from draft-only features:

- Champions by role (blue/red)
- Lane matchup win rate (per role, per patch), counter-pick advantage
- Team composition archetypes: engage, poke, siege, dive, split-push
- Crowd control totals (hard/soft), engage tools
- Damage mix (AD/AP/True)
- Scaling (early/mid/late)
- Patch id, side
- Optional later: runes, summoner spells, bans, pick order, player comfort

## Data inputs

- `matches.parquet` (rows = matches)

  - `match_id: str`
  - `patch: str`
  - `blue_win: bool`
  - `blue_team: Dict[str, str]` — mapping role -> champion key
  - `red_team: Dict[str, str]`

- `lane_wr.parquet`

  - columns: `patch, role, blue, red, wr_blue` (float in [0,1])

- `champ_info.parquet`
  - index: `champion`
  - columns: `ad_weight, ap_weight, true_weight, hard_cc, soft_cc, engage, poke, siege, dive, split, early, mid, late`

## Pipeline

1. Feature build: `ml/src/pipelines/build_training_set.py`

   - Computes blue-minus-red deltas for composition/CC/damage/scaling
   - Adds per-lane matchup WR and counter advantage
   - Outputs `artifacts/training.parquet`

2. Training: `ml/src/train/train_lightgbm.py`
   - LightGBM classifier; outputs `artifacts/model.joblib`
   - Metrics on validation: AUC and Brier score

## How to run

1. Install ML deps:
   - `cd ml && poetry install`
2. Collect raw data and write `ml/data/raw/{patch}/*.json` and `ml/data/processed/matches.parquet`:
   - `poetry run python src/cli/collect_and_build.py --game-name <name> --tag-line <tag> --count 100 --with-timeline`
3. Build features (if you already have the required `matches.parquet`, `champ_info.parquet`, and `lane_wr.parquet`):
   - `python -c "from src.pipelines.build_training_set import build_training_frame, save_parquet; import pandas as pd; from pathlib import Path; df=build_training_frame(pd.read_parquet('matches.parquet'), pd.read_parquet('champ_info.parquet').set_index('champion'), pd.read_parquet('lane_wr.parquet')); save_parquet(df, Path('artifacts/training.parquet'))"`
4. Train:
   - `poetry run python src/train/train_lightgbm.py --input artifacts/training.parquet --output artifacts/model.joblib`
5. Serve:
   - copy `ml/artifacts/model.joblib` to `backend/models/model.joblib`
   - update `backend/app/services/prediction_service.py` to load and score

## Backend endpoints (examples)

- `GET /api/v1/health` → `{ "status": "ok", "version": "0.1.0" }`
- `POST /api/v1/predict` (planned real model)
  - Request: `{ champions: string[], lanes: string[], runes: object, patch: string, blue_side: boolean }`
  - Response: `{ win_probability: number (0..1), model_version: string, details?: object }`

## Cloud and scaling

- Object storage for raw JSON and parquet artifacts; lightweight DB for metadata
- Batch training via CI or a scheduled VM; orchestrate with simple scripts/cron initially
- Keep costs low: sample per patch/elo; compress Parquet; cache feature tables
