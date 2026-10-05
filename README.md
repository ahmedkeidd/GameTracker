# Game Backlog Tracker — My 10x Solution

A backend API that tracks your PlayStation game backlog — what you own, what
you're playing, what you've finished — and suggests what to play next using AI.

## The problem

I own a large backlog of games and constantly lose track of what I've played,
what I'm playing, and what I still want to try. This turns that into a simple,
queryable API instead of scrolling through a PS5 library with no organization.

## Concepts implemented

| Concept | Where it lives |
|---|---|
| API endpoints | All routes in `main.py` — CRUD for games, auth, suggestions |
| Database | SQLite (`games.db`), games persist across restarts |
| Authentication | Supabase Auth, all game routes require a valid bearer token |
| Caching | `rawg_cache` table — game metadata from RAWG API fetched once, reused after |
| LLM integration | `GET /games/suggest` — picks a game from your backlog with a one-sentence reason |

## Run it

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload --port 8001
```

Then visit `http://localhost:8001/docs` for Swagger UI.

## Demo path (5 minutes)

1. Open `http://localhost:8001/docs`
2. `POST /auth/signup` with any email/password
3. Copy the `access_token` from the response
4. Click **Authorize** (top right), paste the token
5. `GET /games` — see the 3 seeded demo games
6. `POST /games` with `{"title": "Celeste"}` — watch cover/genre/rating get fetched from RAWG automatically
7. `POST /games` with the same title again — check the terminal, see `CACHE HIT` instead of a new API call
8. `GET /games/suggest` — get an AI pick from your "not yet" backlog with a reason

## Environment variables

See `.env.example`:
- `SUPABASE_URL`, `SUPABASE_KEY` — your Supabase project
- `RAWG_API_KEY` — free key from rawg.io
- `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` — OpenRouter free tier

## Non-goal

No multiplayer, no mobile app, no frontend UI, single-user only.

## Future ideas

A PDF monthly report of games played, rate limiting on the suggest endpoint.