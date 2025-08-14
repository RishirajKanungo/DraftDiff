from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from ...services.riot_client import client as riot

router = APIRouter(prefix="/riot", tags=["riot"])


@router.get("/account/by-riot-id")
async def account_by_riot_id(game_name: str = Query(...), tag_line: str = Query(...)) -> Any:
    return await riot.get_by_riot_id(game_name=game_name, tag_line=tag_line)


@router.get("/summoner/by-puuid/{puuid}")
async def summoner_by_puuid(puuid: str) -> Any:
    return await riot.get_by_puuid(puuid)


@router.get("/matches/by-puuid/{puuid}")
async def matches_by_puuid(
    puuid: str,
    start: int = Query(0, ge=0),
    count: int = Query(20, ge=1, le=100),
    queue: Optional[int] = Query(None, description="Queue ID (e.g., 420 for Ranked Solo)")
) -> Any:
    return await riot.get_matches_by_puuid(puuid=puuid, start=start, count=count, queue=queue)


@router.get("/match/{match_id}")
async def match(match_id: str) -> Any:
    return await riot.get_match(match_id)


@router.get("/match/{match_id}/timeline")
async def match_timeline(match_id: str) -> Any:
    return await riot.get_match_timeline(match_id)


@router.get("/league/entries/by-summoner/{encrypted_summoner_id}")
async def league_entries_by_summoner(encrypted_summoner_id: str) -> Any:
    return await riot.get_league_entries_by_summoner(encrypted_summoner_id)


@router.get("/static/champions")
async def champions() -> Any:
    return await riot.get_champions()


@router.get("/static/runes")
async def runes() -> Any:
    return await riot.get_runes()
