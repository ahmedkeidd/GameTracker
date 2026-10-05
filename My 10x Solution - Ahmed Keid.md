# My 10x Solution — Ahmed Keid

## What is the problem you are solving?

I own a large backlog of PlayStation games and constantly lose track of what
I've played, what I'm currently playing, and what I still want to try.
Scrolling through my PS5 library doesn't help — it's just a grid of icons
with no way to organize by status or get a recommendation. I end up
re-deciding what to play from scratch every single time, which wastes time
and often means I just replay something familiar instead of touching my
backlog at all.

Anyone with a large, unsorted game backlog has this same problem.

## How did you implement your solution?

I built a backend API (FastAPI + Python) that lets me track games across
three states — not yet played, playing, played — and automatically enriches
each game with cover art, genre, and rating pulled from the RAWG game
database. It also has an AI-powered "what should I play next" endpoint that
looks at my backlog and picks one game with a reason.

### Concepts implemented (5, no swaps)

1. **API endpoints** — Full CRUD for games (`GET/POST/PUT/DELETE /games`),
   with correct status codes (200/201/204/400/404) and input validation via
   Pydantic.

2. **Database** — SQLite (`games.db`), two tables: `games` (the backlog
   itself) and `rawg_cache` (cached external lookups). Data survives a
   server restart.

3. **Authentication** — Supabase Auth. Every game route requires a valid
   bearer token; missing or invalid tokens get a 401, verified via a reusable
   FastAPI dependency.

4. **Caching** — When a game is added, its title is first checked against
   the `rawg_cache` table. If already cached, no external call is made. If
   not, the RAWG API is queried once and the result is saved for every future
   lookup of that same title — this is the "expensive to compute, store and
   reuse" caching concept.

5. **LLM integration** — `GET /games/suggest` sends my current "not yet
   played" backlog (titles + genres) to an LLM via OpenRouter, which picks
   one game and returns a one-sentence reason as structured JSON.

### How to run it

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload --port 8001
```

Then visit `http://localhost:8001/docs` for interactive Swagger UI testing.
Full demo path is in the README.

### What I'd do with another day

Add a PDF monthly report summarizing games finished, and rate-limit the
`/games/suggest` endpoint since it costs an LLM call per request.