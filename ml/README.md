# DraftDiff ML Workspace

This workspace is for data ingestion, feature engineering, training, evaluation, and model packaging for runtime inference.

## Suggested stack

- Python 3.11
- Notebooks via Jupyter / Quarto
- DataFrames: Polars or pandas
- Modeling: scikit-learn, LightGBM, optional PyTorch
- Experiment tracking: Weights & Biases (optional)

## Layout

- `data/`: raw and processed data (gitignored)
- `notebooks/`: exploratory and report notebooks
- `src/`: reusable pipelines and training code
- `artifacts/`: exported models, metrics, plots

## Packaging models

Export models as Joblib to `artifacts/` and copy the chosen production model to `backend/models/model.joblib` for serving.

## Components added

- `src/data/schemas.py`: Pydantic models for draft and match records.
- `src/data/riot_fetch.py`: Async Riot API client for data collection (matches, timelines, summoner/league).
- `src/features/featurize.py`: Team-level features (damage mix, CC, archetypes, scaling) and blue-vs-red deltas.
- `src/features/matchup_features.py`: Lane matchup features by role and patch using empirical lane winrates.
- `src/pipelines/build_training_set.py`: Builds a tabular dataset from match JSON + feature sources, outputs Parquet.
- `src/train/train_lightgbm.py`: LightGBM classifier training pipeline, saves `model.joblib` with feature names.

## Recommended v1 feature set (implemented)

- Champions by role (blue/red), side-aware features
- Lane matchup WR (per role, patch) and counter-pick advantage
- Synergy via archetype/CC/waveclear proxies (extendable)
- Damage mix (AD/AP/True), scaling curve (early/mid/late)
- Patch id, side
- Runes/summoners can be appended as categorical/numeric features in a follow-up step

## Example workflow

1. Collect data with your own script/notebooks using `src/data/riot_fetch.py` and persist raw JSON.
2. Build lane WR table (per patch, role, champ vs champ). Save as Parquet `lane_wr.parquet` with columns `[patch, role, blue, red, wr_blue]`.
3. Prepare `champ_info.parquet` with per-champion numeric attributes: `ad_weight, ap_weight, true_weight, hard_cc, soft_cc, engage, poke, siege, dive, split, early, mid, late`.
4. Assemble `matches.parquet` with columns: `[match_id, patch, blue_win, blue_team, red_team]` where teams are dicts like `{role: champion_key}` (use pandas `object` dtype with JSON-serializable dicts).
5. Build features:
   - Python: `python -c "from src.pipelines.build_training_set import build_training_frame, save_parquet; import pandas as pd; from pathlib import Path; df=build_training_frame(pd.read_parquet('matches.parquet'), pd.read_parquet('champ_info.parquet').set_index('champion'), pd.read_parquet('lane_wr.parquet')); save_parquet(df, Path('artifacts/training.parquet'))"`
6. Train model:
   - `poetry run python src/train/train_lightgbm.py --input artifacts/training.parquet --output artifacts/model.joblib`
7. Copy model to backend:
   - `cp ml/artifacts/model.joblib backend/models/model.joblib`

## Serving

Backend loads `backend/models/model.joblib`. Update `app/services/prediction_service.py` to load and score the real model using incoming payload features.

## Cloud considerations

- For continuous training or large-scale data, use object storage (S3/GCS/Azure Blob) for raw and processed data, and a small Postgres for metadata.
- Compute: GitHub Actions or a cloud VM can run batch training. For big workloads, consider managed notebooks or simple Airflow/Prefect flows.
- Cost control: Keep artifacts in compressed Parquet, sample matches per patch/elo for fast iteration.
