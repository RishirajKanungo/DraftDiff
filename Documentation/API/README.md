# DraftDiff Backend API

Base URL (local): `http://localhost:8000/api/v1`

## Health

- `GET /health`
- Response example:

```json
{ "status": "ok", "version": "0.1.0" }
```

## Riot endpoints

- `GET /riot/account/by-riot-id?game_name={name}&tag_line={tag}`

  - Returns Account-V1 object `{ puuid, gameName, tagLine }`

- `GET /riot/summoner/by-puuid/{puuid}`

  - Returns Summoner-V4 object `{ id, accountId, puuid, name, summonerLevel, ... }`

- `GET /riot/matches/by-puuid/{puuid}?start=0&count=20&queue=420`

  - Returns an array of match IDs `string[]`

- `GET /riot/match/{match_id}`

  - Returns match-v5 JSON `{ metadata, info }`

- `GET /riot/match/{match_id}/timeline`

  - Returns timeline JSON `{ metadata, info }`

- `GET /riot/league/entries/by-summoner/{encrypted_summoner_id}`

  - Returns ranked entries array

- `GET /riot/static/champions`

  - Returns DDragon champions JSON `{ type, data, ... }`

- `GET /riot/static/runes`
  - Returns DDragon runes array

For ready-to-use requests, import the Postman collection in `Documentation/Postman/`.
