from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DraftContext(BaseModel):
    patch: str
    blue_side: bool
    champions_by_role: Dict[str, str] = Field(
        description="Mapping of role -> champion key (e.g., top, jg, mid, adc, sup)"
    )
    runes_by_role: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Mapping of role -> rune selections (keystone + shards)",
    )
    summoners_by_role: Dict[str, List[str]] = Field(
        default_factory=dict, description="Mapping of role -> [spell1, spell2]"
    )


class MatchRecord(BaseModel):
    match_id: str
    patch: str
    blue_win: bool
    blue_team: Dict[str, str]
    red_team: Dict[str, str]
    blue_runes: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    red_runes: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    blue_summoners: Dict[str, List[str]] = Field(default_factory=dict)
    red_summoners: Dict[str, List[str]] = Field(default_factory=dict)
    bans_blue: List[str] = Field(default_factory=list)
    bans_red: List[str] = Field(default_factory=list)
    region: Optional[str] = None
    queue: Optional[int] = None


