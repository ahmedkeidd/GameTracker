import sqlite3

conn = sqlite3.connect("games.db")
conn.row_factory = sqlite3.Row

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

count = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
if count == 0:
    conn.execute("INSERT INTO games (title, status) VALUES (?, ?)", ("Elden Ring", "playing"))
    conn.execute("INSERT INTO games (title, status) VALUES (?, ?)", ("Hollow Knight", "not_yet"))
    conn.execute("INSERT INTO games (title, status) VALUES (?, ?)", ("God of War", "played"))
    conn.commit()
    print("Seeded 3 demo games.")
else:
    print("Games already exist, skipping seed.")

conn.close()