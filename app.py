"""
Hangman Analytics Arcade — Enhanced Streamlit app 

This file is a modified version of your app. Changes:
 - Replaced emoji usage with inline SVG icons / neutral text
 - Updated theme to a colorful gradient (not black)
 - Kept functionality: gameplay, hint system, analytics, leaderboard, export
"""

from pathlib import Path
import random
import time
from datetime import datetime
from collections import Counter

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import storage

# --------------------------
# ASCII Art from hangman_art.py 
# --------------------------
STAGES = ['''
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========
''', '''
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========
''', '''
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========
''', '''
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========
''', '''
  +---+
  |   |
  O   |
  |   |
      |
      |
=========
''', '''
  +---+
  |   |
  O   |
      |
      |
      |
=========
''', '''
  +---+
  |   |
      |
      |
      |
      |
=========
''']

LOGO_MAIN = '''
██╗░░██╗░█████╗░███╗░░██╗░██████╗░███╗░░░███╗░█████╗░███╗░░██╗
██║░░██║██╔══██╗████╗░██║██╔════╝░████╗░████║██╔══██╗████╗░██║
███████║███████║██╔██╗██║██║░░██╗░██╔████╔██║███████║██╔██╗██║
██╔══██║██╔══██║██║╚████║██║░░╚██╗██║╚██╔╝██║██╔══██║██║╚████║
██║░░██║██║░░██║██║░╚███║╚██████╔╝██║░╚═╝░██║██║░░██║██║░╚███║
╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝░╚═════╝░╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝'''

LOGO_GOOD_WORK = "GOOD WORK"
LOGO_WELCOME = "WELCOME"

# --------------------------
# Word lists with categories
# --------------------------
WORD_CATEGORIES = {
    "Programming": [
        "python", "javascript", "algorithm", "database", "function",
        "variable", "compiler", "debugging", "software", "hardware"
    ],
    "Technology": [
        "computer", "internet", "smartphone", "software", "keyboard",
        "monitor", "browser", "network", "digital", "automation"
    ],
    "Science": [
        "biology", "chemistry", "physics", "astronomy", "molecule",
        "electron", "gravity", "evolution", "experiment", "research"
    ],
    "General": [
        "elephant", "butterfly", "mountain", "adventure", "treasure",
        "happiness", "wisdom", "mystery", "journey", "champion"
    ],
}

WORD_HINTS = {
    "python": "A very popular programming language often used for data tasks",
    "javascript": "The primary language used in web browsers for interactivity",
    "streamlit": "A Python framework for building simple data apps",
    "algorithm": "A step-by-step procedure for solving computational problems",
    "database": "Structured storage that holds data for applications",
    "computer": "An electronic device for executing programs and processing data",
    "keyboard": "An input device used to type text",
    "elephant": "Large land mammal known for its trunk and memory",
    "butterfly": "An insect with colorful patterned wings",
    "mountain": "A large natural elevation of the Earth's surface",
}

# --------------------------
# App configuration
# --------------------------
st.set_page_config(page_title="Hangman Analytics Arcade", page_icon="🎯", layout="wide")
storage.init_db()

# --------------------------
# SVG Icons
# --------------------------
ICON_PLAY = "<svg width='16' height='16' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'><path d='M5 3v18l15-9L5 3z' stroke='currentColor' stroke-width='1.2' stroke-linejoin='round' stroke-linecap='round'/></svg>"

# --------------------------
# CSS Theme
# --------------------------
APP_CSS = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0b1a14 0%, #0f251c 40%, #0a1c14 100%);
    color: #c8f7df;
    min-height: 100vh;
    font-family: Inter, sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1f18 !important;
    color: #c9f3e2 !important;
    border-right: 1px solid rgba(100,255,180,0.05);
}
[data-testid="stSidebar"] * {
    color: #c9f3e2 !important;
}

/* Radio buttons */
div[role="radiogroup"] > label {
    color: #c9f3e2 !important;
    font-weight: 500;
}
div[role="radiogroup"] > label[data-checked="true"] {
    color: #72ffb7 !important;
    font-weight: 700;
}
div[role="radio"][aria-checked="true"] > div:first-child {
    border: 2px solid #34ff9a !important;
    background-color: #34ff9a !important;
}
div[role="radio"][aria-checked="false"] > div:first-child {
    border: 2px solid #4b6a5e !important;
}

/* Titles */
.gradient-title {
    font-size: 2.3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #4cffb1, #7affd1, #b5ffe8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ASCII logo box */
.ascii-logo {
    font-family: monospace;
    font-size: 0.8rem;
    padding: 1.2rem;
    color: #7fffd4 !important;
    background: rgba(0, 40, 25, 0.35);
    border: 1px solid rgba(125, 255, 200, 0.25);
    border-radius: 14px;
    text-align: center;
    white-space: pre;
}

/* Metric text */
div[data-testid="stMetric"],
div[data-testid="stMetricValue"],
div[data-testid="stMetricDelta"],
div[data-testid="stMetric"] span,
div[data-testid="stMetric"] label {
    color: #b9ffe5 !important;
}

/* Info / warning / success */
div[data-testid="stInfo"] {
    background: #19382a !important;
    color: #b9ffe5 !important;
    border-left: 4px solid #44ffb4 !important;
}
div[data-testid="stWarning"] {
    background: #382f14 !important;
    color: #ffe9b5 !important;
    border-left: 4px solid #ffcc44 !important;
}
div[data-testid="stError"] {
    background: #3a1414 !important;
    color: #ffb5b5 !important;
    border-left: 4px solid #ff4444 !important;
}
div[data-testid="stSuccess"] {
    background: #143826 !important;
    color: #afffd8 !important;
    border-left: 4px solid #44ff99 !important;
}

/* Buttons */
div.stButton > button,
div.stDownloadButton > button {
    background: linear-gradient(180deg, #1a3f31, #0e2b20) !important;
    color: #b9ffe5 !important;
    border: 1px solid rgba(100,255,180,0.25) !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    box-shadow: 0 4px 15px rgba(50,255,170,0.12) !important;
    font-weight: 700 !important;
}
div.stButton > button:hover {
    background: linear-gradient(180deg, #1f4d3c, #103729) !important;
    box-shadow: 0 6px 20px rgba(50,255,170,0.18) !important;
}

/* Word display */
.word-display {
    color: #7affbf !important;
    font-size: 2.8rem;
    letter-spacing: 0.25em;
    font-family: monospace;
}

/* Keyboard */
.keyboard-btn {
    background: #163427 !important;
    color: #85ffce !important;
    border: 1px solid rgba(100,255,180,0.2) !important;
}
.keyboard-btn-used {
    background: #2e463c !important;
    color: #6f9286 !important;
}

/* ------------------------------
   TABLES / DATAFRAMES (GREEN THEME)
   ------------------------------*/
.dataframe,
.stDataFrame td,
.stDataFrame th,
table td,
table th {
    background-color: #051710 !important;   /* deep green */
    color: #aefee4 !important;              /* mint text */
    border-color: rgba(120,255,200,0.35) !important;
}

/* Header row */
.stDataFrame th {
    background-color: #0b2219 !important;
    color: #cffff4 !important;
    font-weight: 700 !important;
    border-bottom: 2px solid rgba(140,255,210,0.7) !important;
}

/* Hover row */
.stDataFrame tbody tr:hover td {
    background-color: rgba(76,255,177,0.12) !important;
}

/* Zebra stripes (optional, but looks nice) */
.stDataFrame tbody tr:nth-child(even) td {
    background-color: #071d14 !important;
}


/* Plotly text */
.js-plotly-plot * text {
    fill: #c8f7df !important;
    color: #c8f7df !important;
}

/* Hint + stats boxes */
.hint-box {
    background: rgba(76,255,177,0.08);
    border-left: 4px solid #4cffb1;
    padding: 12px;
    border-radius: 10px;
    color: #c8f7df;
}
.stats-highlight {
    background: rgba(76,255,150,0.06);
    border-left: 4px solid #44ff99;
    padding: 14px;
    border-radius: 10px;
    color: #d7ffee;
}

/* Welcome pill */
.welcome-logo {
    font-size: 1.4rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: #aefee4;
    padding: 8px 48px;
    border-radius: 12px;
    border: 2px solid rgba(150,255,200,0.25);
    width: auto;
    display: inline-block;
}

/* Custom info on Play page */
.custom-info {
    background: linear-gradient(180deg, #1a3f31, #0e2b20);
    color: #7fffd4 !important;
    padding: 14px 20px;
    border-radius: 14px;
    border: 1px solid rgba(100,255,180,0.25);
    box-shadow: 0 4px 15px rgba(50,255,170,0.15);
    font-size: 18px;
    display: flex;
    align-items: center;
    width: 100%;
    height: 58px;
}

@media(max-width:800px){
    .keyboard-btn{
        padding: 6px!important;
        font-size: 0.8rem!important;
    }
}

</style>
"""

st.markdown(APP_CSS, unsafe_allow_html=True)

# --------------------------
# Difficulty configuration
# --------------------------
DIFFICULTY_CONFIG = {
    "Easy": {"lives": 8, "hint_cost": 1, "points_multiplier": 1.0},
    "Medium": {"lives": 6, "hint_cost": 1, "points_multiplier": 1.5},
    "Hard": {"lives": 4, "hint_cost": 2, "points_multiplier": 2.0},
}

# --------------------------
# Helper functions
# --------------------------
def _has_win_streak(games, streak_len=3) -> bool:
    if not games:
        return False
    sorted_games = sorted(games, key=lambda g: g.get("timestamp", ""))
    current = 0
    best = 0
    for g in sorted_games:
        if g.get("won") == 1:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best >= streak_len

ACHIEVEMENTS = [
    ("First Steps", "Play your first game", lambda df: len(df) >= 1),
    ("Getting Started", "Play 10 games", lambda df: len(df) >= 10),
    ("Dedicated Player", "Play 50 games", lambda df: len(df) >= 50),
    ("Perfect Victory", "Win without any wrong guesses",
     lambda df: any((g.get("won") == 1 and g.get("wrong_guesses") == 0) for g in df)),
    ("Perfectionist", "Get 5 perfect wins",
     lambda df: sum(1 for g in df if g.get("won") == 1 and g.get("wrong_guesses") == 0) >= 5),
    ("Win Streak 3", "Win 3 games in a row", lambda df: _has_win_streak(df, 3)),
    ("Win Streak 5", "Win 5 games in a row", lambda df: _has_win_streak(df, 5)),
    ("Speed Demon", "Win a game in under 60 seconds",
     lambda df: any((g.get("won") == 1 and g.get("duration_sec", float('inf')) < 60) for g in df)),
]

def format_seconds(sec: float) -> str:
    if pd.isna(sec) or sec is None:
        return "N/A"
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

def load_games_df():
    df = pd.DataFrame(storage.fetch_all_games())
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if "word_length" not in df.columns:
        df["word_length"] = df["word"].astype(str).str.len()
    return df

def category_stats(df: pd.DataFrame) -> pd.DataFrame:
    if "category" not in df.columns:
        return pd.DataFrame(columns=["category", "win_rate", "wrong", "duration"])
    out = df.groupby("category").agg(
        win_rate=("won", "mean"),
        wrong=("wrong_guesses", "mean"),
        duration=("duration_sec", "mean"),
    )
    out["win_rate"] = out["win_rate"] * 100
    return out.reset_index()

def difficulty_recommendation(user_df: pd.DataFrame):
    if len(user_df) < 10:
        return None
    wr = user_df["won"].mean() * 100
    if wr >= 70:
        return "Hard"
    elif wr >= 40:
        return "Medium"
    else:
        return "Easy"
def apply_green_theme(fig):
    """Give a bright-green theme to a Plotly figure."""
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#7affbf"),
        xaxis=dict(
            color="#7affbf",
            gridcolor="rgba(127,255,191,0.18)",
            zerolinecolor="rgba(127,255,191,0.3)",
        ),
        yaxis=dict(
            color="#7affbf",
            gridcolor="rgba(127,255,191,0.18)",
            zerolinecolor="rgba(127,255,191,0.3)",
        ),
        legend=dict(font=dict(color="#7affbf")),
    )
    return fig

def letter_heatmap(user_df: pd.DataFrame) -> pd.DataFrame:
    """
    Letter frequency table:
    how often each letter appears in words from games you won vs lost.
    """
    letters = list("abcdefghijklmnopqrstuvwxyz")
    stats = {l: {"won": 0, "lost": 0} for l in letters}

    for _, row in user_df.iterrows():
        word = str(row.get("word", "")).lower()
        if not word:
            continue
        unique_letters = {c for c in word if c.isalpha()}
        col = "won" if row.get("won", 0) == 1 else "lost"
        for l in unique_letters:
            if l in stats:
                stats[l][col] += 1

    hm = pd.DataFrame(stats).T
    hm = hm.sort_index()
    return hm

def get_hint(word: str) -> str:
    w = word.lower()
    if w in WORD_HINTS:
        return WORD_HINTS[w]
    vowels = set("aeiou")
    vowel_count = sum(1 for c in w if c in vowels)
    first = w[0].upper()
    last = w[-1].upper()
    hints = [
        f"Starts with {first}",
        f"Ends with {last}",
        f"Contains {vowel_count} vowel(s)",
    ]
    return random.choice(hints)

def get_all_words():
    all_words = []
    for words in WORD_CATEGORIES.values():
        all_words.extend(words)
    return all_words

# Master word list
try:
    from hangman_words import word_list as ORIGINAL_WORDS
    ALL_WORDS = [w.lower() for w in ORIGINAL_WORDS]
except Exception:
    ALL_WORDS = []
    for words in WORD_CATEGORIES.values():
        ALL_WORDS.extend(w.lower() for w in words)
ALL_WORDS = list(dict.fromkeys(ALL_WORDS))

# --------------------------
# Session state
# --------------------------
def init_session_state():
    defaults = dict(
        username="",
        difficulty="Medium",
        word_category="All Categories",
        game_active=False,
        secret_word="",
        display_word=[],
        guessed_letters=set(),
        wrong_letters=set(),
        remaining_lives=6,
        max_lives=6,
        attempts=0,
        start_time=None,
        game_over=False,
        game_won=False,
        result_logged=False,
        hint_shown=False,
        current_streak=0,
        best_streak=0,
        word_queue=[],
        last_word="",
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

def get_difficulty_config():
    diff = st.session_state.get("difficulty", "Medium")
    if isinstance(diff, str):
        if diff.startswith("Easy"):
            diff = "Easy"
        elif diff.startswith("Medium"):
            diff = "Medium"
        elif diff.startswith("Hard"):
            diff = "Hard"
        else:
            diff = "Medium"
    st.session_state.difficulty = diff
    return DIFFICULTY_CONFIG.get(diff, DIFFICULTY_CONFIG["Medium"])

# --------------------------
# Game control
# --------------------------
def start_new_game(difficulty=None, category=None):
    if difficulty:
        st.session_state.difficulty = difficulty
    if category:
        st.session_state.word_category = category

    cfg = get_difficulty_config()
    st.session_state.max_lives = cfg["lives"]
    st.session_state.remaining_lives = cfg["lives"]
    st.session_state.attempts = 0
    st.session_state.guessed_letters = set()
    st.session_state.wrong_letters = set()
    st.session_state.hint_shown = False
    st.session_state.game_over = False
    st.session_state.game_won = False
    st.session_state.result_logged = False
    st.session_state.start_time = time.time()

    if st.session_state.word_category == "All Categories":
        base_words = ALL_WORDS
    else:
        base_words = WORD_CATEGORIES.get(st.session_state.word_category, ALL_WORDS)
    base_words = list(dict.fromkeys(w.lower() for w in base_words))

    if not st.session_state.word_queue:
        queue = base_words[:]
        random.shuffle(queue)
        last = st.session_state.get("last_word")
        if last in queue and len(queue) > 1 and queue[-1] == last:
            random.shuffle(queue)
        st.session_state.word_queue = queue

    secret = st.session_state.word_queue.pop()
    last = st.session_state.get("last_word")
    if last and secret == last and st.session_state.word_queue:
        secret = st.session_state.word_queue.pop()

    st.session_state.secret_word = secret.lower()
    st.session_state.last_word = st.session_state.secret_word
    st.session_state.display_word = ["_"] * len(st.session_state.secret_word)
    st.session_state.game_active = True

def process_guess(letter: str):
    if not letter or not letter.isalpha() or len(letter) != 1:
        st.error("Please enter a single letter (A–Z).")
        return

    letter = letter.lower()
    if letter in st.session_state.guessed_letters:
        st.info(f"You already guessed {letter.upper()}")
        return

    st.session_state.guessed_letters.add(letter)
    st.session_state.attempts += 1

    if letter in st.session_state.secret_word:
        for i, ch in enumerate(st.session_state.secret_word):
            if ch == letter:
                st.session_state.display_word[i] = letter
        st.success(f"Good — {letter.upper()} is in the word.")
    else:
        st.session_state.wrong_letters.add(letter)
        st.session_state.remaining_lives -= 1
        st.error(f"Incorrect — {letter.upper()} is not in the word. Lives remaining: {st.session_state.remaining_lives}")

    if "_" not in st.session_state.display_word:
        st.session_state.game_over = True
        st.session_state.game_won = True
        st.session_state.current_streak = (st.session_state.current_streak or 0) + 1
        st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.current_streak)
        st.session_state.result_logged = False

    if st.session_state.remaining_lives <= 0:
        st.session_state.display_word = list(st.session_state.secret_word)
        st.session_state.game_over = True
        st.session_state.game_won = False
        st.session_state.current_streak = 0
        st.session_state.result_logged = False

def log_result_if_needed():
    if not st.session_state.game_over or st.session_state.result_logged:
        return
    if not st.session_state.username:
        return

    duration = None
    if st.session_state.start_time:
        duration = time.time() - st.session_state.start_time

    storage.log_game(
        username=st.session_state.username,
        word=st.session_state.secret_word,
        category=st.session_state.word_category,
        won=st.session_state.game_won,
        attempts_used=st.session_state.attempts,
        wrong_guesses=len(st.session_state.wrong_letters),
        max_lives=st.session_state.max_lives,
        remaining_lives=st.session_state.remaining_lives,
        duration_sec=duration,
    )
    st.session_state.result_logged = True
    
# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.markdown(
        "<div style='display:flex; justify-content:center; margin-top:20px;'>"
        "<div class='welcome-logo'>WELCOME</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='gradient-title'>{ICON_PLAY} HANGMAN ARCADE</div>", unsafe_allow_html=True)

    st.markdown("---")
    username = st.text_input("Enter username", value=st.session_state.username, placeholder="Your name...")
    if username != st.session_state.username:
        st.session_state.username = username

    st.markdown("### Player Stats")
    games_df = load_games_df()

    if not games_df.empty and st.session_state.username:
        user_df_sidebar = games_df[games_df["username"] == st.session_state.username]
        col1, col2, col3 = st.columns(3)
        total_games = len(user_df_sidebar)
        wins = int(user_df_sidebar["won"].sum()) if not user_df_sidebar.empty else 0
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        col1.metric("Games", total_games)
        col2.metric("Wins", wins)
        col3.metric("Win %", f"{win_rate:.0f}%")
        st.markdown(f"**Current Streak:** {st.session_state.current_streak}")
        st.markdown(f"**Best Streak:** {st.session_state.best_streak}")
    else:
        st.info("Play some games to see your stats.")

    st.markdown("---")
    st.markdown("Game Settings")

    diff = st.selectbox(
        "Difficulty Level",
        list(DIFFICULTY_CONFIG.keys()),
        index=list(DIFFICULTY_CONFIG.keys()).index(st.session_state.difficulty),
    )

    category = st.selectbox(
        "Word Category",
        ["All Categories"] + list(WORD_CATEGORIES.keys()),
        index=0,
    )

    if st.button("Start New Game with Settings", use_container_width=True):
        start_new_game(diff, category)

    st.markdown("---")
    st.markdown("Achievements")

    all_games = storage.fetch_all_games()
    for title, desc, check_fn in ACHIEVEMENTS:
        try:
            achieved = check_fn(all_games)
            marker = "●" if achieved else "○"
            st.markdown(f"{marker} **{title}**")
            if not achieved:
                st.caption(desc)
        except Exception:
            st.markdown("○ **{title}**")

    st.markdown("---")
    page = st.radio("Navigate", ["Play", "Analytics", "Leaderboard", "Data Export"])

# --------------------------
# Main header
# --------------------------
st.markdown(f"<div class='ascii-logo'>{LOGO_MAIN}</div>", unsafe_allow_html=True)

# --------------------------
# PLAY PAGE
# --------------------------
if page == "Play":
    col_left, col_right = st.columns([1, 2], gap="large")

    with col_left:
        st.markdown("### Game Controls")

        if not st.session_state.game_active or st.session_state.game_over:
            if st.button("Start New Game", use_container_width=True):
                start_new_game()
        else:
            if st.button("Give Up & Start New", use_container_width=True):
                st.session_state.game_over = True
                st.session_state.game_won = False
                st.session_state.display_word = list(st.session_state.secret_word)
                log_result_if_needed()
                start_new_game()

        st.markdown("---")
        st.markdown("Hangman State")
        lives_index = min(len(STAGES) - 1, st.session_state.max_lives - st.session_state.remaining_lives)
        st.code(STAGES[lives_index], language=None)

        st.markdown("---")
        st.markdown("Current Game")
        st.markdown("<div class='stats-highlight'>", unsafe_allow_html=True)
        st.markdown(f"**Lives:** {st.session_state.remaining_lives} / {st.session_state.max_lives}")
        st.markdown(f"**Attempts:** {st.session_state.attempts}")
        st.markdown(f"**Difficulty:** {st.session_state.difficulty}")
        if st.session_state.start_time and not st.session_state.game_over:
            elapsed = time.time() - st.session_state.start_time
            st.markdown(f"**Time:** {format_seconds(elapsed)}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("Word to Guess")

        if not st.session_state.game_active:
            st.markdown(
                "<div class='custom-info'>Click 'Start New Game' to begin playing.</div>",
                unsafe_allow_html=True,
            )
        else:
            display = " ".join(ch.upper() for ch in st.session_state.display_word)
            st.markdown(f"<div class='word-display'>{display}</div>", unsafe_allow_html=True)

            st.caption(
                f"Word length: {len(st.session_state.secret_word)} letters | "
                f"Category: {st.session_state.word_category}"
            )

            if st.session_state.wrong_letters:
                wrong_str = ", ".join(sorted(ch.upper() for ch in st.session_state.wrong_letters))
                st.markdown(f"Wrong guesses: {wrong_str}")

            st.markdown("---")

            if not st.session_state.game_over:
                st.markdown("Need a hint?")
                if not st.session_state.hint_shown:
                    hint_cost = get_difficulty_config()["hint_cost"]
                    if st.button(f"Show Hint (costs {hint_cost} life)", use_container_width=True):
                        if st.session_state.remaining_lives > hint_cost:
                            st.session_state.remaining_lives -= hint_cost
                            st.session_state.hint_shown = True
                            st.rerun()
                        else:
                            st.error("Not enough lives for a hint.")
                else:
                    st.markdown(
                        f"<div class='hint-box'>{get_hint(st.session_state.secret_word)}</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("---")
                st.markdown("Virtual Keyboard")

                rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
                for row in rows:
                    cols = st.columns(len(row))
                    st.write("")
                    for i, letter in enumerate(row):
                        with cols[i]:
                            letter_lower = letter.lower()
                            disabled = letter_lower in st.session_state.guessed_letters
                            if disabled:
                                st.button(letter, key=f"used_{letter}", disabled=True, use_container_width=True)
                            else:
                                if st.button(letter, key=f"key_{letter}", use_container_width=True):
                                    process_guess(letter_lower)
                                    st.rerun()

            if st.session_state.game_over:
                st.markdown("---")
                if st.session_state.game_won:
                    st.markdown(f"<div class='ascii-logo'>{LOGO_GOOD_WORK}</div>", unsafe_allow_html=True)
                    st.success(f"YOU WON! The word was {st.session_state.secret_word.upper()}")
                    st.balloons()
                    if st.session_state.start_time:
                        duration = time.time() - st.session_state.start_time
                        st.info(f"Time: {format_seconds(duration)} | Attempts: {st.session_state.attempts}")
                else:
                    st.error(f"GAME OVER. The word was {st.session_state.secret_word.upper()}")

                log_result_if_needed()

                if st.button("Play Again", use_container_width=True):
                    start_new_game()

# --------------------------
# ANALYTICS PAGE
# --------------------------
elif page == "Analytics":
    st.markdown("Player Analytics Dashboard")

    df = load_games_df()

    if df.empty:
        st.info("No games played yet. Start playing to see analytics.")
    elif not st.session_state.username:
        st.warning("Enter a username in the sidebar to view personal analytics.")
    else:
        user_df = df[df["username"] == st.session_state.username]

        if user_df.empty:
            st.info("You haven't played any games yet. Start playing!")
        else:
            # ===== Summary metrics =====
            col1, col2, col3, col4 = st.columns(4)

            total_games = len(user_df)
            wins = int(user_df["won"].sum())
            win_rate = (wins / total_games * 100) if total_games > 0 else 0
            avg_attempts = user_df["attempts_used"].mean()

            col1.metric("Total Games", total_games)

            # Difficulty suggestion after 10+ games
            suggested = difficulty_recommendation(user_df)
            if suggested:
                st.info(
                    f"We recommend trying **{suggested} difficulty** based on your performance."
                )

            col2.metric("Wins", wins)
            col3.metric("Win Rate", f"{win_rate:.1f}%")
            col4.metric("Avg Attempts", f"{avg_attempts:.1f}")

            st.markdown("---")

            # ===== Win / Loss bar =====
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                win_loss = user_df["won"].value_counts().rename({0: "Losses", 1: "Wins"})
                fig1 = px.bar(
                    y=win_loss.index,
                    x=win_loss.values,
                    orientation="h",
                    title="Win/Loss Distribution",
                    color=win_loss.index,
                    color_discrete_sequence=["#2ecc71", "#7affbf"],  # bright greens
                )
                fig1 = apply_green_theme(fig1)
                st.plotly_chart(fig1, use_container_width=True)

            # ===== Word length performance =====
            with chart_col2:
                length_perf = user_df.groupby("word_length").won.mean().reset_index()
                length_perf["Win Rate"] = length_perf["won"] * 100
                fig2 = px.bar(
                    length_perf,
                    x="word_length",
                    y="Win Rate",
                    color="Win Rate",
                    color_continuous_scale="Greens",
                    title="Win Rate by Word Length",
                )
                fig2 = apply_green_theme(fig2)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("---")

            # ===== Letter heatmap =====
            st.markdown("### Letter Usage Heatmap")
            hm = letter_heatmap(user_df)

            if hm[["won", "lost"]].values.sum() == 0:
                st.info("Not enough data yet to build a letter heatmap.")
            else:
                fig_hm = px.imshow(
                    hm[["won", "lost"]].T,
                    labels=dict(x="Letter", y="Outcome", color="Count"),
                    x=hm.index,
                    y=["won", "lost"],
                    color_continuous_scale="Greens",
                    aspect="auto",
                )
                fig_hm = apply_green_theme(fig_hm)
                st.plotly_chart(fig_hm, use_container_width=True)

            st.markdown("---")

            # ===== Time-of-day performance =====
            st.markdown("### Performance by Time of Day")
            user_df["hour"] = user_df["timestamp"].dt.hour
            tod = user_df.groupby("hour").won.mean().reset_index()
            tod["Win Rate"] = tod["won"] * 100
            fig_time = px.line(
                tod, x="hour", y="Win Rate", title="Win Rate by Hour"
            )
            fig_time.update_traces(line_color="#7affbf")
            fig_time = apply_green_theme(fig_time)
            st.plotly_chart(fig_time, use_container_width=True)

            st.markdown("---")

            # ===== Category difficulty =====
            st.markdown("### Category Difficulty Comparison")
            if "category" in user_df.columns:
                cat = category_stats(user_df)
                if not cat.empty:
                    fig_cat = px.bar(
                        cat,
                        x="category",
                        y="win_rate",
                        color="win_rate",
                        color_continuous_scale="Greens",
                    )
                    fig_cat = apply_green_theme(fig_cat)
                    st.plotly_chart(fig_cat, use_container_width=True)

            st.markdown("---")

            # ===== Achievement progress =====
            st.markdown("### Achievement Progress")
            ach_names, ach_value = [], []
            all_games = storage.fetch_all_games()
            for title, _, check in ACHIEVEMENTS:
                ach_names.append(title)
                ach_value.append(1 if check(all_games) else 0)

            apd = pd.DataFrame(
                {"Achievement": ach_names, "Completed": ach_value}
            )
            fig_ach = px.bar(
                apd,
                x="Achievement",
                y="Completed",
                title="Achievements",
                color="Completed",
                color_continuous_scale="Greens",
            )
            fig_ach = apply_green_theme(fig_ach)
            st.plotly_chart(fig_ach, use_container_width=True)

            # ===== Win-rate progress over time =====
            timeline = user_df.sort_values("timestamp").copy()
            timeline["game_number"] = range(1, len(timeline) + 1)
            timeline["cumulative_wins"] = timeline["won"].cumsum()
            timeline["cumulative_win_rate"] = (
                timeline["cumulative_wins"] / timeline["game_number"]
            ) * 100

            fig3 = px.line(
                timeline,
                x="game_number",
                y="cumulative_win_rate",
                title="Win Rate Progress Over Time",
                labels={
                    "game_number": "Game Number",
                    "cumulative_win_rate": "Win Rate (%)",
                },
            )
            fig3.update_traces(line_color="#7affbf")
            fig3 = apply_green_theme(fig3)
            st.plotly_chart(fig3, use_container_width=True)

            st.markdown("---")
            st.markdown("Recent Games")
            recent = (
                user_df.sort_values("timestamp", ascending=False)
                .head(10)
                .copy()
            )
            recent["timestamp"] = recent["timestamp"].dt.strftime(
                "%Y-%m-%d %H:%M"
            )
            recent["duration_sec"] = recent["duration_sec"].apply(
                lambda x: format_seconds(x)
            )
            recent["won"] = recent["won"].map({1: "Yes", 0: "No"})

            display_cols = [
                "timestamp",
                "word",
                "won",
                "attempts_used",
                "wrong_guesses",
                "duration_sec",
            ]
            recent_display = recent[display_cols].rename(
                columns={
                    "timestamp": "Time",
                    "word": "Word",
                    "won": "Result",
                    "attempts_used": "Attempts",
                    "wrong_guesses": "Wrong",
                    "duration_sec": "Duration",
                }
            )
            st.dataframe(recent_display, use_container_width=True)

# --------------------------
# LEADERBOARD PAGE
# --------------------------
elif page == "Leaderboard":
    st.markdown("Global Leaderboard")

    df = load_games_df()

    if df.empty:
        st.info("No games recorded yet.")
    else:
        stats = df.copy()
        stats["perfect"] = ((stats["won"] == 1) & (stats["wrong_guesses"] == 0)).astype(int)

        leaderboard = stats.groupby("username").agg(
            games=("id", "count"),
            wins=("won", "sum"),
            perfects=("perfect", "sum"),
            avg_attempts=("attempts_used", "mean"),
            avg_duration=("duration_sec", "mean"),
        )
        leaderboard["win_rate"] = (leaderboard["wins"] / leaderboard["games"]) * 100

        min_games = st.slider("Minimum games to show", 1, max(1, int(leaderboard["games"].max())), 1)
        filtered = leaderboard[leaderboard["games"] >= min_games].sort_values(
            ["win_rate", "games"], ascending=[False, False]
        )

        st.markdown("Top 3 Players")
        top3 = filtered.head(3).reset_index()
        if len(top3) >= 1:
            medal_cols = st.columns([1, 1, 1])
            medals = ["gold", "silver", "bronze"]
            for i in range(min(3, len(top3))):
                with medal_cols[i]:
                    player = top3.iloc[i]
                    st.markdown(
                        f"<div class='{medals[i]}'>"
                        f"<strong>{player['username']}</strong><br>"
                        f"Win Rate: {player['win_rate']:.1f}%<br>"
                        f"Games: {int(player['games'])}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        st.markdown("---")
        st.markdown("Full Rankings")

        display_lb = filtered.copy()
        display_lb["avg_duration"] = display_lb["avg_duration"].apply(format_seconds)
        display_lb = display_lb.reset_index()
        display_lb = display_lb[
            ["username", "games", "wins", "win_rate", "perfects", "avg_attempts", "avg_duration"]
        ]
        display_lb.columns = ["Player", "Games", "Wins", "Win Rate %", "Perfect Wins", "Avg Attempts", "Avg Time"]

        st.dataframe(
            display_lb.style.format(
                {
                    "Win Rate %": "{:.1f}",
                    "Avg Attempts": "{:.1f}",
                }
            ),
            use_container_width=True,
        )

# --------------------------
# DATA EXPORT PAGE
# --------------------------
elif page == "Data Export":
    st.markdown("Export Your Data")

    df = load_games_df()

    if df.empty:
        st.info("No data to export yet.")
    else:
        st.markdown("Database Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Games", len(df))
        col2.metric("Unique Players", df["username"].nunique())
        col3.metric("Total Wins", int(df["won"].sum()))

        st.markdown("---")

        st.markdown("Filter Data")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            selected_players = st.multiselect(
                "Select Players",
                options=["All"] + sorted(df["username"].unique().tolist()),
                default=["All"],
            )

        with col_f2:
            min_date = df["timestamp"].min() if not df.empty else datetime.now()
            max_date = df["timestamp"].max() if not df.empty else datetime.now()
            date_range = st.date_input(
                "Date Range",
                value=(min_date.date(), max_date.date()),
                max_value=datetime.now(),
            )

        filtered_df = df.copy()
        if "All" not in selected_players:
            filtered_df = filtered_df[filtered_df["username"].isin(selected_players)]

        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df["timestamp"] >= pd.Timestamp(date_range[0]))
                & (filtered_df["timestamp"] <= pd.Timestamp(date_range[1]))
            ]

        st.markdown(f"Filtered records: {len(filtered_df)}")

        st.markdown("Data Preview")
        preview = filtered_df.head(20).copy()
        preview["timestamp"] = preview["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(preview, use_container_width=True)

        st.markdown("---")
        csv = filtered_df.to_csv(index=False)

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"hangman_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col_e2:
            if st.button("Refresh Data", use_container_width=True):
                st.rerun()

# Auto-log results
if st.session_state.game_over and not st.session_state.result_logged:
    try:
        log_result_if_needed()
    except Exception:
        pass
