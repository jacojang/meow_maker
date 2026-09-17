from __future__ import annotations

import os
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "meow_maker.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS player (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS game (
    player_id TEXT PRIMARY KEY REFERENCES player(id),
    state_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def get_db_path() -> str:
    return os.environ.get("MEOW_DB_PATH", str(DEFAULT_DB_PATH))


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


_initialized_paths: set[str] = set()


def ensure_initialized(db_path: str) -> None:
    """Lazily run init_db at most once per path.

    Called from the default provider functions rather than at import time,
    so importing app.main for tests that override those providers never
    touches disk.
    """
    if db_path not in _initialized_paths:
        init_db(db_path)
        _initialized_paths.add(db_path)


@contextmanager
def connect(db_path: str) -> Generator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
