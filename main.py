from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
import sqlite3
import os
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

RAWG_API_KEY = os.getenv("RAWG_API_KEY")

security = HTTPBearer()

def verify_token(credentials = Depends(security)):
    token = credentials.credentials
    try:
        response = supabase.auth.get_user(token)
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return response.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

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
            status TEXT NOT NULL DEFAULT 'not_yet',
            cover_url TEXT,
            genre TEXT,
            rating REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rawg_cache (
            title TEXT PRIMARY KEY,
            cover_url TEXT,
            genre TEXT,
            rating REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_game_metadata(title: str):
    conn = get_db()
    cached = conn.execute("SELECT * FROM rawg_cache WHERE title = ?", (title,)).fetchone()
    if cached:
        conn.close()
        print(f"CACHE HIT: {title}")
        return dict(cached)

    print(f"FETCHING FROM RAWG: {title}")
    response = requests.get(
        "https://api.rawg.io/api/games",
        params={"key": RAWG_API_KEY, "search": title, "page_size": 1},
        timeout=10
    )
    data = response.json()

    if not data.get("results"):
        conn.close()
        return {"cover_url": None, "genre": None, "rating": None}

    result = data["results"][0]
    cover_url = result.get("background_image")
    genre = result["genres"][0]["name"] if result.get("genres") else None
    rating = result.get("rating")

    conn.execute(
        "INSERT INTO rawg_cache (title, cover_url, genre, rating) VALUES (?, ?, ?, ?)",
        (title, cover_url, genre, rating)
    )
    conn.commit()
    conn.close()

    return {"cover_url": cover_url, "genre": genre, "rating": rating}

app = FastAPI()

class GameCreate(BaseModel):
    title: str

class GameUpdate(BaseModel):
    status: str

@app.get("/")
def root():
    return {"name": "Game Backlog Tracker", "version": "1.0"}

@app.post("/auth/signup", status_code=201)
def signup(data: dict):
    if "email" not in data or "password" not in data:
        raise HTTPException(status_code=400, detail="Email and password are required")
    try:
        response = supabase.auth.sign_up({
            "email": data["email"],
            "password": data["password"]
        })
        return {"user": response.user}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Auth provider error: {str(e)}")

@app.post("/auth/login")
def login(data: dict):
    if "email" not in data or "password" not in data:
        raise HTTPException(status_code=400, detail="Email and password are required")
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data["email"],
            "password": data["password"]
        })
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid login credentials")
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

@app.get("/games")
def get_games(user=Depends(verify_token)):
    conn = get_db()
    games = conn.execute("SELECT * FROM games").fetchall()
    conn.close()
    return [dict(g) for g in games]

@app.post("/games", status_code=201)
def create_game(game: GameCreate, user=Depends(verify_token)):
    if not game.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    metadata = get_game_metadata(game.title)

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO games (title, status, cover_url, genre, rating) VALUES (?, ?, ?, ?, ?)",
        (game.title, "not_yet", metadata["cover_url"], metadata["genre"], metadata["rating"])
    )
    conn.commit()
    new_game = conn.execute("SELECT * FROM games WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return dict(new_game)

@app.put("/games/{game_id}")
def update_game_status(game_id: int, update: GameUpdate, user=Depends(verify_token)):
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
def delete_game(game_id: int, user=Depends(verify_token)):
    conn = get_db()
    game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    if game is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    conn.execute("DELETE FROM games WHERE id = ?", (game_id,))
    conn.commit()
    conn.close()