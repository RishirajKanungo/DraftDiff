# Iterative Training Process (v1)

This guide outlines a step-by-step process to build a draft-only model following sound DS/SE practices.

## 1) Data acquisition (Riot API)

- Use backend or `ml/src/data/riot_fetch.py` to pull:
  - Summoner by PUUID → get `encrypted_summoner_id`
  - Matches by PUUID (queue=420) → list of match IDs
  - Match JSON and timeline for each ID
- Store raw JSON under `ml/data/raw/{patch}/` (gitignored).

## 2) Parsing and normalization

- Use `ml/src/etl/parse_match.py` to convert raw match JSON → normalized rows:
  - `match_id, patch, blue_win, blue_team (role->champ), red_team, bans, runes, summoners`
- Save as `matches.parquet` for downstream use.

## 3) Feature sources

- `champ_info.parquet` (per champion numeric attributes) and `lane_wr.parquet` (role+patch matchup WR) are external tables you maintain/generated from historical data. Keep them versioned by patch.

## 4) Feature building

- Use `ml/src/pipelines/build_training_set.py` to merge:
  - Team comp deltas (damage mix, CC, archetypes, scaling)
  - Lane matchup WR and counter advantage per role
- Output `artifacts/training.parquet`.

## 5) Training & evaluation

- Train LightGBM with `ml/src/train/train_lightgbm.py`.
- Track metrics: AUC, Brier score. Target 0.75–0.85 AUC initially.
- Save `artifacts/model.joblib`.

## 6) Serving

- Copy model into `backend/models/model.joblib`.
- Update backend predictor to load and score using the same features.

## 7) Hygiene & reproducibility

- Use Parquet for all intermediate datasets.
- Pin versions via Poetry, document patches used.
- Keep raw/processed data paths consistent.

## 8) Scale-out (optional)

- Store raw JSON and parquet in cloud object storage.
- Schedule periodic re-training using CI or a VM.
- Add data validation checks (row counts, distribution drift) in future iterations.
