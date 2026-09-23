from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

def get_db():
    conn = sqlite3.connect("games.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'not_yet'
        )
    """)
    conn.commit()
    conn.close()

init_db()

app = FastAPI()

class GameCreate(BaseModel):
    title: str

class GameUpdate(BaseModel):
    status: str

@app.get("/")
def root():
    return {"name": "Game Backlog Tracker", "version": "1.0"}

@app.get("/games")
def get_games():
    conn = get_db()
    games = conn.execute("SELECT * FROM games").fetchall()
    conn.close()
    return [dict(g) for g in games]

@app.post("/games", status_code=201)
def create_game(game: GameCreate):
    if not game.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    conn = get_db()
    cursor = conn.execute("INSERT INTO games (title, status) VALUES (?, ?)", (game.title, "not_yet"))
    conn.commit()
    new_game = conn.execute("SELECT * FROM games WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return dict(new_game)

@app.put("/games/{game_id}")
def update_game_status(game_id: int, update: GameUpdate):
    valid_statuses = ["not_yet", "playing", "played"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")
    conn = get_db()
    game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    if game is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    conn.execute("UPDATE games SET status = ? WHERE id = ?", (update.status, game_id))
    conn.commit()
    updated = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    conn.close()
    return dict(updated)

@app.delete("/games/{game_id}", status_code=204)
def delete_game(game_id: int):
    conn = get_db()
    game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    if game is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    conn.execute("DELETE FROM games WHERE id = ?", (game_id,))
    conn.commit()
    conn.close()