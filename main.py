from fastapi import FastAPI
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

@app.get("/")
def root():
    return {"name": "Game Backlog Tracker", "version": "1.0"}

@app.get("/games")
def get_games():
    conn = get_db()
    games = conn.execute("SELECT * FROM games").fetchall()
    conn.close()
    return [dict(g) for g in games]