# My 10x Solution — Game Backlog Tracker

## The problem (3 sentences)
I own a large backlog of PlayStation games and constantly lose track of what
I've played, what I'm currently playing, and what I still want to try. Scrolling
through my PS5 library doesn't tell me this — it's just a grid of icons with no
organization by status. I end up re-deciding what to play from scratch every time.

## Who has this problem
Anyone with a large, unsorted game backlog — applies to me directly, and to
most gamers with more games than time.

## The 10x claim
Instead of scrolling through my PS5 library trying to remember what I own and
what mood I'm in, I get an instant categorized list and an AI suggestion for
what to play next, in one request.

## Concepts (5, no swaps)
1. **API endpoints** — CRUD for games (add, update status, delete, list)
2. **Database** — SQLite, persists my game list across restarts
3. **Authentication** — Supabase Auth, so it's actually my list
4. **Caching** — game metadata (cover, genre, rating) fetched from RAWG API once, cached, never re-fetched for the same game
5. **LLM integration** — "what should I play next" endpoint, reasons over my backlog and picks one

## Non-goal
No multiplayer, no mobile app, no frontend UI, single-user only (just me).