from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.data.riot_fetch import RiotClient
from src.etl.parse_match import parse_match_to_record


@dataclass
class CollectionConfig:
    api_key: str
    game_name: str
    tag_line: str
    platform: str = "na1"
    region: str = "americas"
    queue: Optional[int] = 420
    start: int = 0
    count: int = 50
    concurrency: int = 5
    output_parquet: Path = Path("ml/data/processed/matches.parquet")
    raw_dir: Path = Path("ml/data/raw")
    with_timeline: bool = False


async def collect_matches(config: CollectionConfig) -> pd.DataFrame:
    client = RiotClient(api_key=config.api_key, platform=config.platform, region=config.region)

    account = await client.account_by_riot_id(config.game_name, config.tag_line)
    puuid = account["puuid"]

    match_ids = await client.matches_by_puuid(
        puuid=puuid, start=config.start, count=config.count, queue=config.queue
    )

    semaphore = asyncio.Semaphore(config.concurrency)
    records: List[Dict[str, Any]] = []

    async def fetch_one(match_id: str) -> None:
        async with semaphore:
            match = await client.match(match_id)
            record = parse_match_to_record(match)
            patch = record.get("patch") or "unknown"
            patch_dir = (config.raw_dir / patch)
            patch_dir.mkdir(parents=True, exist_ok=True)
            # Save raw match JSON
            with (patch_dir / f"{match_id}.json").open("w", encoding="utf-8") as f:
                json.dump(match, f, ensure_ascii=False)
            # Optionally save timeline JSON
            if config.with_timeline:
                timeline = await client.match_timeline(match_id)
                with (patch_dir / f"{match_id}.timeline.json").open("w", encoding="utf-8") as f:
                    json.dump(timeline, f, ensure_ascii=False)
            records.append({
                "match_id": record["match_id"],
                "patch": record["patch"],
                "blue_win": record["blue_win"],
                "blue_team": record["blue_team"],
                "red_team": record["red_team"],
            })

    await asyncio.gather(*(fetch_one(m) for m in match_ids))

    df = pd.DataFrame.from_records(records)
    return df


def parse_args() -> CollectionConfig:
    parser = argparse.ArgumentParser(
        description="Collect Riot matches for a Riot ID and build v1 matches.parquet"
    )
    parser.add_argument("--game-name", required=True, help="Riot game name (e.g., Faker)")
    parser.add_argument("--tag-line", required=True, help="Riot tag line (e.g., KR1)")
    parser.add_argument("--api-key", required=False, help="Riot API key (or set RIOT_API_KEY)")
    parser.add_argument("--platform", default="na1", help="Platform routing (default: na1)")
    parser.add_argument("--region", default="americas", help="Region routing (default: americas)")
    parser.add_argument("--queue", type=int, default=420, help="Queue ID (default: 420 SoloQ)")
    parser.add_argument("--start", type=int, default=0, help="Start offset for match history")
    parser.add_argument("--count", type=int, default=50, help="Number of matches to fetch")
    parser.add_argument(
        "--output-parquet",
        type=Path,
        default=Path("ml/data/processed/matches.parquet"),
        help="Where to write the v1 matches parquet",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("ml/data/raw"),
        help="Directory to store raw match JSON under {patch}/",
    )
    parser.add_argument(
        "--with-timeline",
        action="store_true",
        help="Also fetch and store timeline JSON",
    )
    parser.add_argument("--concurrency", type=int, default=5, help="Max concurrent match fetches")

    args = parser.parse_args()
    api_key = args.api_key or os.getenv("RIOT_API_KEY")
    if not api_key:
        raise SystemExit("RIOT_API_KEY is required (pass --api-key or set env var)")

    return CollectionConfig(
        api_key=api_key,
        game_name=args.game_name,
        tag_line=args.tag_line,
        platform=args.platform,
        region=args.region,
        queue=args.queue,
        start=args.start,
        count=args.count,
        concurrency=args.concurrency,
        output_parquet=args.output_parquet,
        raw_dir=args.raw_dir,
        with_timeline=bool(args.with_timeline),
    )


def main_sync() -> None:
    config = parse_args()
    df = asyncio.run(collect_matches(config))
    config.output_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(config.output_parquet, index=False)
    print(
        {
            "rows": int(len(df)),
            "patches": sorted(df["patch"].dropna().unique().tolist()) if not df.empty else [],
            "output": str(config.output_parquet),
            "raw_dir": str(config.raw_dir),
        }
    )


if __name__ == "__main__":
    main_sync()


