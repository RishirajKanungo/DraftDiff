from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd

ROLES = ["top", "jg", "mid", "adc", "sup"]


def lane_pair_key(ch_blue: str, ch_red: str, patch: str, role: str) -> Tuple[str, str, str, str]:
    return (patch, role, ch_blue, ch_red)


def compute_lane_matchup_features(
    blue_team: Dict[str, str], red_team: Dict[str, str], patch: str, lane_wr: pd.DataFrame
) -> Dict[str, float]:
    """
    lane_wr columns expected: [patch, role, blue, red, wr_blue]
    wr_blue = empirical win rate for blue champ vs red champ within role+patch.
    """
    features: Dict[str, float] = {}
    for role in ROLES:
        b = blue_team.get(role)
        r = red_team.get(role)
        if not b or not r:
            continue
        row = lane_wr[(lane_wr["patch"] == patch) & (lane_wr["role"] == role) & (lane_wr["blue"] == b) & (lane_wr["red"] == r)]
        if row.empty:
            wr = 0.5
        else:
            wr = float(row.iloc[0]["wr_blue"])  # between 0 and 1
        features[f"lane_{role}_blue_wr"] = wr
        features[f"lane_{role}_counter_adv"] = wr - 0.5
    return features


