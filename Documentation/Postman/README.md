# DraftDiff Riot API Postman Collection

Use this collection to exercise the Riot-related endpoints exposed by the DraftDiff backend running locally.

Prerequisites:

- Backend running locally on http://localhost:8000 (FastAPI)
- `RIOT_API_KEY` set in `backend/.env` (copy from `.env.example` and fill in your key)
- Frontend optional, not required for API testing

How to import:

1. Open Postman
2. File → Import → select `DraftDiff-Riot-API.postman_collection.json`
3. After import, in the collection variables set:
   - `baseUrl` if your API is not on `http://localhost:8000/api/v1`
   - `game_name` and `tag_line` for an account you want to test
   - Fill `puuid`, `encrypted_summoner_id`, and `match_id` after retrieving them via earlier calls

Workflow suggestions:

1. Health: `GET {{baseUrl}}/health` should return `{ "status": "ok" }`
2. Account by Riot ID: `GET {{baseUrl}}/riot/account/by-riot-id?game_name={{game_name}}&tag_line={{tag_line}}`
   - Copy `puuid` from response to the collection variable `puuid`
3. Summoner by PUUID: `GET {{baseUrl}}/riot/summoner/by-puuid/{{puuid}}`
   - Copy `id` to `encrypted_summoner_id`
4. Matches by PUUID: `GET {{baseUrl}}/riot/matches/by-puuid/{{puuid}}?start={{start}}&count={{count}}&queue={{queue}}`
   - Copy a value (e.g., `KR_123...`) into `match_id`
5. Match by ID: `GET {{baseUrl}}/riot/match/{{match_id}}`
6. Match timeline: `GET {{baseUrl}}/riot/match/{{match_id}}/timeline`
7. League entries: `GET {{baseUrl}}/riot/league/entries/by-summoner/{{encrypted_summoner_id}}`
8. Static champions: `GET {{baseUrl}}/riot/static/champions`
9. Static runes: `GET {{baseUrl}}/riot/static/runes`

Notes:

- The Riot endpoints require a valid `RIOT_API_KEY` and correct `RIOT_PLATFORM`/`RIOT_REGION`. Defaults are `na1` and `americas` and can be changed via environment variables or `backend/.env`.
- If you receive `429 Too Many Requests`, wait and retry (the backend retries a few times automatically but will surface rate limits).
- Timeouts are ~15–20s upstream; consider narrowing `count` in match queries if needed.
