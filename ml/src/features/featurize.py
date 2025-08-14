from __future__ import annotations

from typing import Dict, List, Tuple
import math

import pandas as pd


ROLES = ["top", "jg", "mid", "adc", "sup"]


def compute_damage_profile(team: Dict[str, str], champ_info: pd.DataFrame) -> Tuple[float, float, float]:
    ad = ap = true = 0.0
    for role, champ in team.items():
        row = champ_info.loc[champ] if champ in champ_info.index else None
        if row is None:
            continue
        ad += float(row.get("ad_weight", 0.0))
        ap += float(row.get("ap_weight", 0.0))
        true += float(row.get("true_weight", 0.0))
    total = ad + ap + true
    if total == 0:
        return 0.0, 0.0, 0.0
    return ad / total, ap / total, true / total


def compute_cc_metrics(team: Dict[str, str], champ_info: pd.DataFrame) -> Dict[str, float]:
    hard_cc = soft_cc = engage_tools = 0.0
    for champ in team.values():
        row = champ_info.loc[champ] if champ in champ_info.index else None
        if row is None:
            continue
        hard_cc += float(row.get("hard_cc", 0.0))
        soft_cc += float(row.get("soft_cc", 0.0))
        engage_tools += float(row.get("engage", 0.0))
    return {"hard_cc": hard_cc, "soft_cc": soft_cc, "engage_tools": engage_tools}


def compute_comp_archetypes(team: Dict[str, str], champ_info: pd.DataFrame) -> Dict[str, float]:
    keys = ["engage", "poke", "siege", "dive", "split"]
    scores = {k: 0.0 for k in keys}
    for champ in team.values():
        row = champ_info.loc[champ] if champ in champ_info.index else None
        if row is None:
            continue
        for k in keys:
            scores[k] += float(row.get(k, 0.0))
    return scores


def compute_scaling(team: Dict[str, str], champ_info: pd.DataFrame) -> Dict[str, float]:
    early = mid = late = 0.0
    for champ in team.values():
        row = champ_info.loc[champ] if champ in champ_info.index else None
        if row is None:
            continue
        early += float(row.get("early", 0.0))
        mid += float(row.get("mid", 0.0))
        late += float(row.get("late", 0.0))
    return {"early": early, "mid": mid, "late": late}


def aggregate_side_features(blue_team: Dict[str, str], red_team: Dict[str, str], champ_info: pd.DataFrame) -> Dict[str, float]:
    # Damage profile
    b_ad, b_ap, b_true = compute_damage_profile(blue_team, champ_info)
    r_ad, r_ap, r_true = compute_damage_profile(red_team, champ_info)

    # CC and archetypes
    b_cc = compute_cc_metrics(blue_team, champ_info)
    r_cc = compute_cc_metrics(red_team, champ_info)
    b_arch = compute_comp_archetypes(blue_team, champ_info)
    r_arch = compute_comp_archetypes(red_team, champ_info)

    # Scaling
    b_scale = compute_scaling(blue_team, champ_info)
    r_scale = compute_scaling(red_team, champ_info)

    # Differences (blue minus red)
    features: Dict[str, float] = {
        "ad_share_diff": b_ad - r_ad,
        "ap_share_diff": b_ap - r_ap,
        "true_share_diff": b_true - r_true,
        "hard_cc_diff": b_cc["hard_cc"] - r_cc["hard_cc"],
        "soft_cc_diff": b_cc["soft_cc"] - r_cc["soft_cc"],
        "engage_tools_diff": b_cc["engage_tools"] - r_cc["engage_tools"],
        "early_diff": b_scale["early"] - r_scale["early"],
        "mid_diff": b_scale["mid"] - r_scale["mid"],
        "late_diff": b_scale["late"] - r_scale["late"],
    }
    for key in ["engage", "poke", "siege", "dive", "split"]:
        features[f"{key}_diff"] = b_arch[key] - r_arch[key]
    return features


