from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException

from ..core.config import settings


class RiotApiClient:
    def __init__(self, api_key: Optional[str], platform: str, region: str) -> None:
        self.api_key = api_key
        self.platform = platform
        self.region = region
        self.platform_base = f"https://{platform}.api.riotgames.com"
        self.region_base = f"https://{region}.api.riotgames.com"
        self.headers = {"X-Riot-Token": api_key} if api_key else {}

    async def _request(self, method: str, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="RIOT_API_KEY is not configured")
        retries = 3
        backoff = 0.8
        last_exc: Optional[Exception] = None
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    r = await client.request(method, url, params=params, headers=self.headers)
                if r.status_code == 429:
                    # rate limited; respect retry-after if present
                    retry_after = float(r.headers.get("Retry-After", backoff * (2 ** attempt)))
                    await asyncio.sleep(retry_after)
                    continue
                if 200 <= r.status_code < 300:
                    return r.json()
                if 500 <= r.status_code < 600:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                # Other errors
                raise HTTPException(status_code=r.status_code, detail=r.text)
            except (httpx.RequestError, httpx.TimeoutException) as exc:
                last_exc = exc
                await asyncio.sleep(backoff * (2 ** attempt))
                continue
        if last_exc:
            raise HTTPException(status_code=502, detail=f"Upstream error: {last_exc}")
        raise HTTPException(status_code=502, detail="Upstream request failed after retries")

    # Account-V1 / Summoner-V4
    async def get_by_riot_id(self, game_name: str, tag_line: str) -> Any:
        # Account-V1 uses regional routing
        url = f"{self.region_base}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        return await self._request("GET", url)

    async def get_by_puuid(self, puuid: str) -> Any:
        # Summoner-V4 uses platform routing
        url = f"{self.platform_base}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return await self._request("GET", url)

    async def get_matches_by_puuid(self, puuid: str, start: int = 0, count: int = 20, queue: Optional[int] = None) -> Any:
        params: Dict[str, Any] = {"start": start, "count": count}
        if queue is not None:
            params["queue"] = queue
        url = f"{self.region_base}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        return await self._request("GET", url, params=params)

    async def get_match(self, match_id: str) -> Any:
        url = f"{self.region_base}/lol/match/v5/matches/{match_id}"
        return await self._request("GET", url)

    async def get_match_timeline(self, match_id: str) -> Any:
        url = f"{self.region_base}/lol/match/v5/matches/{match_id}/timeline"
        return await self._request("GET", url)

    async def get_league_entries_by_summoner(self, encrypted_summoner_id: str) -> Any:
        url = f"{self.platform_base}/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
        return await self._request("GET", url)

    # DDragon static data
    async def get_ddragon_version(self) -> str:
        if settings.ddragon_version:
            return settings.ddragon_version
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get("https://ddragon.leagueoflegends.com/api/versions.json")
        r.raise_for_status()
        versions = r.json()
        return versions[0]

    async def get_champions(self) -> Any:
        version = await self.get_ddragon_version()
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(url)
        r.raise_for_status()
        return r.json()

    async def get_runes(self) -> Any:
        version = await self.get_ddragon_version()
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/runesReforged.json"
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(url)
        r.raise_for_status()
        return r.json()


client = RiotApiClient(
    api_key=settings.riot_api_key,
    platform=settings.riot_platform,
    region=settings.riot_region,
)
