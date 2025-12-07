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
                username TEXT,
                word TEXT,
                word_length INTEGER NOT NULL,
                category TEXT,
                won INTEGER,
                attempts_used INTEGER,
                wrong_guesses INTEGER,
                max_lives INTEGER,
                remaining_lives INTEGER,
                duration_sec REAL,
                timestamp TEXT
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
    category: str | None = None,
):
    """
    Insert a finished game into the database.

    Handles different schemas gracefully:
    - with word_length + category
    - with word_length only
    - with neither (oldest schema)
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    word_length = len(word) if word else 0

    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()

        # 1) Try full modern schema: word_length + category
        try:
            cur.execute(
                """
                INSERT INTO games (
                    username, word, word_length, category, won,
                    attempts_used, wrong_guesses,
                    max_lives, remaining_lives, duration_sec, timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    username,
                    word,
                    word_length,
                    category,
                    won,
                    attempts_used,
                    wrong_guesses,
                    max_lives,
                    remaining_lives,
                    duration_sec,
                    timestamp,
                ),
            )
        except Exception:
            # 2) Try schema with word_length but no category
            try:
                cur.execute(
                    """
                    INSERT INTO games (
                        username, word, word_length, won,
                        attempts_used, wrong_guesses,
                        max_lives, remaining_lives, duration_sec, timestamp
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    ,
                    (
                        username,
                        word,
                        word_length,
                        won,
                        attempts_used,
                        wrong_guesses,
                        max_lives,
                        remaining_lives,
                        duration_sec,
                        timestamp,
                    ),
                )
            except Exception:
                # 3) Oldest schema: no word_length, no category
                cur.execute(
                    """
                    INSERT INTO games (
                        username, word, won,
                        attempts_used, wrong_guesses,
                        max_lives, remaining_lives, duration_sec, timestamp
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        username,
                        word,
                        won,
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
