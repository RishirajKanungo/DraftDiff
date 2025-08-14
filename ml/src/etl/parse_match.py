from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from ..utils.roles import normalize_role

ROLES = ["top", "jg", "mid", "adc", "sup"]


def _extract_patch(game_version: str) -> str:
    # Riot gameVersion like "14.7.456.1234" → "14.7"
    parts = (game_version or "").split(".")
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return game_version


def _extract_keystone(participant: Dict[str, Any]) -> Optional[int]:
    try:
        styles = participant.get("perks", {}).get("styles", [])
        if styles and styles[0].get("selections"):
            return int(styles[0]["selections"][0]["perk"])  # type: ignore
    except Exception:
        return None
    return None


def parse_match_to_record(match: Dict[str, Any]) -> Dict[str, Any]:
    info = match.get("info", {})
    teams_info = {t.get("teamId"): t for t in info.get("teams", [])}
    blue_win = bool(teams_info.get(100, {}).get("win", False))
    patch = _extract_patch(info.get("gameVersion", ""))

    blue_team: Dict[str, str] = {}
    red_team: Dict[str, str] = {}
    blue_runes: Dict[str, Dict[str, str]] = {}
    red_runes: Dict[str, Dict[str, str]] = {}
    blue_summ: Dict[str, List[str]] = {}
    red_summ: Dict[str, List[str]] = {}

    for p in info.get("participants", []):
        team_id = p.get("teamId")
        role = normalize_role(p.get("teamPosition"), p.get("individualPosition"))
        if role not in ROLES:
            continue
        champ = p.get("championName")
        rune = _extract_keystone(p)
        s1 = p.get("summoner1Id")
        s2 = p.get("summoner2Id")

        if team_id == 100:
            if role not in blue_team:
                blue_team[role] = champ
                if rune is not None:
                    blue_runes[role] = {"keystone": str(rune)}
                blue_summ[role] = [str(s1), str(s2)]
        elif team_id == 200:
            if role not in red_team:
                red_team[role] = champ
                if rune is not None:
                    red_runes[role] = {"keystone": str(rune)}
                red_summ[role] = [str(s1), str(s2)]

    # Bans (optional)
    bans_blue: List[str] = []
    bans_red: List[str] = []
    for tid, t in teams_info.items():
        bans = t.get("bans", []) or []
        ids = [str(b.get("championId")) for b in bans if b.get("championId") is not None]
        if tid == 100:
            bans_blue = ids
        elif tid == 200:
            bans_red = ids

    return {
        "match_id": match.get("metadata", {}).get("matchId"),
        "patch": patch,
        "blue_win": blue_win,
        "blue_team": blue_team,
        "red_team": red_team,
        "blue_runes": blue_runes,
        "red_runes": red_runes,
        "blue_summoners": blue_summ,
        "red_summoners": red_summ,
        "bans_blue": bans_blue,
        "bans_red": bans_red,
    }


