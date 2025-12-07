# storage.py

import sqlite3
from contextlib import closing
from pathlib import Path
import datetime

DB_PATH = Path(__file__).with_name("hangman_scores.db")


def init_db():
    """Create the games table if it doesn't exist."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                word TEXT NOT NULL,
                word_length INTEGER NOT NULL,
                won INTEGER NOT NULL,
                attempts_used INTEGER NOT NULL,
                wrong_guesses INTEGER NOT NULL,
                max_lives INTEGER NOT NULL,
                remaining_lives INTEGER NOT NULL,
                duration_sec REAL,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.commit()


def log_game(
    username: str,
    word: str,
    won: bool,
    attempts_used: int,
    wrong_guesses: int,
    max_lives: int,
    remaining_lives: int,
    duration_sec: float | None = None,
):
    """Insert a finished game into the database."""
    timestamp = datetime.datetime.utcnow().isoformat()

    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO games (
                username, word, word_length, won, attempts_used,
                wrong_guesses, max_lives, remaining_lives,
                duration_sec, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                word,
                len(word),
                1 if won else 0,
                attempts_used,
                wrong_guesses,
                max_lives,
                remaining_lives,
                duration_sec,
                timestamp,
            ),
        )
        conn.commit()


def fetch_all_games():
    """Return all games as a list of dicts."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM games ORDER BY timestamp ASC").fetchall()
        return [dict(r) for r in rows]
