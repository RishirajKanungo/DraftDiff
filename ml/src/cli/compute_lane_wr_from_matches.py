from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

from src.utils.jsonio import parse_jsonish


ROLES = ["top", "jg", "mid", "adc", "sup"]


def compute_lane_wr(matches: pd.DataFrame) -> pd.DataFrame:
    counts: Dict[Tuple[str, str, str, str], int] = defaultdict(int)
    wins: Dict[Tuple[str, str, str, str], int] = defaultdict(int)

    for _, row in matches.iterrows():
        patch = str(row["patch"])
        blue_team = row["blue_team"]
        red_team = row["red_team"]
        # Handle JSON-serialized dicts
        blue_team = parse_jsonish(blue_team)
        red_team = parse_jsonish(red_team)

        blue_win = bool(row["blue_win"])

        for role in ROLES:
            b = blue_team.get(role)
            r = red_team.get(role)
            if not b or not r:
                continue
            key = (patch, role, str(b), str(r))
            counts[key] += 1
            if blue_win:
                wins[key] += 1

    records = []
    for key, n in counts.items():
        w = wins.get(key, 0)
        patch, role, blue, red = key
        wr_blue = w / n
        records.append({
            "patch": patch,
            "role": role,
            "blue": blue,
            "red": red,
            "n": n,
            "wr_blue": wr_blue,
        })
    df = pd.DataFrame.from_records(records)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute per-role lane matchup win rates (blue vs red) from matches.parquet"
    )
    parser.add_argument("--matches", type=Path, required=True, help="Path to matches.parquet")
    parser.add_argument("--output", type=Path, required=True, help="Path to write lane_wr.parquet")
    args = parser.parse_args()

    mdf = pd.read_parquet(args.matches)
    out = compute_lane_wr(mdf)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(args.output, index=False)
    print({"rows": int(len(out)), "output": str(args.output)})


if __name__ == "__main__":
    main()


