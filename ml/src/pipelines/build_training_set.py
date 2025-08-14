from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd
from tqdm import tqdm

from ..features.featurize import aggregate_side_features
from ..features.matchup_features import compute_lane_matchup_features


def build_training_frame(
    matches: pd.DataFrame,
    champ_info: pd.DataFrame,
    lane_wr: pd.DataFrame,
) -> pd.DataFrame:
    """
    matches: rows with [match_id, patch, blue_win, blue_team, red_team]
    champ_info: per-champion numeric attributes used by featurize module
    lane_wr: per-role, per-patch lane matchup winrates
    """
    records: List[Dict] = []
    for _, row in tqdm(matches.iterrows(), total=len(matches)):
        blue_team = row["blue_team"]
        red_team = row["red_team"]
        patch = row["patch"]

        side_feats = aggregate_side_features(blue_team, red_team, champ_info)
        lane_feats = compute_lane_matchup_features(blue_team, red_team, patch, lane_wr)

        features: Dict = {**side_feats, **lane_feats}
        features["patch"] = patch
        features["blue_win"] = bool(row["blue_win"])
        features["match_id"] = row["match_id"]
        records.append(features)
    return pd.DataFrame.from_records(records)


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


