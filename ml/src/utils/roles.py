from __future__ import annotations

from typing import Optional


_TEAM_POSITION_MAP = {
    "TOP": "top",
    "JUNGLE": "jg",
    "MIDDLE": "mid",
    "BOTTOM": "adc",
    "SUPPORT": "sup",
}


def normalize_role(team_position: Optional[str], individual_position: Optional[str]) -> Optional[str]:
    if team_position and team_position in _TEAM_POSITION_MAP:
        return _TEAM_POSITION_MAP[team_position]
    if individual_position and individual_position in _TEAM_POSITION_MAP:
        return _TEAM_POSITION_MAP[individual_position]
    return None


