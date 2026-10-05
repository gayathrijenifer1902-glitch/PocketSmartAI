import sqlite3
from pathlib import Path
from .config import settings

def db_path():
    return settings.database_url.replace("sqlite:///", "")
def connection():
    con = sqlite3.connect(db_path(), check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con
def init_db():
    Path(db_path()).parent.mkdir(parents=True, exist_ok=True) if Path(db_path()).parent != Path('.') else None
    with connection() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, planner TEXT NOT NULL, request_json TEXT NOT NULL, response_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id));
        ''')
