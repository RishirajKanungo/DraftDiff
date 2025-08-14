from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel


class RiotClient(BaseModel):
    api_key: str
    platform: str = "na1"
    region: str = "americas"
    timeout: float = 15.0

    @property
    def platform_base(self) -> str:
        return f"https://{self.platform}.api.riotgames.com"

    @property
    def region_base(self) -> str:
        return f"https://{self.region}.api.riotgames.com"

    async def _request(self, method: str, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        headers = {"X-Riot-Token": self.api_key}
        retries = 3
        backoff = 0.8
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    r = await client.request(method, url, params=params, headers=headers)
                if r.status_code == 429:
                    retry_after = float(r.headers.get("Retry-After", backoff * (2 ** attempt)))
                    await asyncio.sleep(retry_after)
                    continue
                if 200 <= r.status_code < 300:
                    return r.json()
                if 500 <= r.status_code < 600:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                raise RuntimeError(f"Riot error {r.status_code}: {r.text}")
            except (httpx.RequestError, httpx.TimeoutException):
                await asyncio.sleep(backoff * (2 ** attempt))
                continue
        raise RuntimeError("Upstream request failed after retries")

    async def account_by_riot_id(self, game_name: str, tag_line: str) -> Dict[str, Any]:
        url = f"{self.region_base}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        return await self._request("GET", url)

    # Regional routing
    async def matches_by_puuid(self, puuid: str, start: int = 0, count: int = 20, queue: Optional[int] = None) -> List[str]:
        params: Dict[str, Any] = {"start": start, "count": count}
        if queue is not None:
            params["queue"] = queue
        url = f"{self.region_base}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        return await self._request("GET", url, params=params)

    async def match(self, match_id: str) -> Dict[str, Any]:
        url = f"{self.region_base}/lol/match/v5/matches/{match_id}"
        return await self._request("GET", url)

    async def match_timeline(self, match_id: str) -> Dict[str, Any]:
        url = f"{self.region_base}/lol/match/v5/matches/{match_id}/timeline"
        return await self._request("GET", url)

    # Platform routing
    async def summoner_by_puuid(self, puuid: str) -> Dict[str, Any]:
        url = f"{self.platform_base}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return await self._request("GET", url)

    async def league_entries_by_summoner(self, encrypted_summoner_id: str) -> List[Dict[str, Any]]:
        url = f"{self.platform_base}/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
        return await self._request("GET", url)


