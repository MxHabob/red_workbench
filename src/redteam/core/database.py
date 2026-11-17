import sqlite3
from pathlib import Path
from contextlib import contextmanager

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS assets (
 id TEXT PRIMARY KEY, kind TEXT NOT NULL, value TEXT NOT NULL, source TEXT NOT NULL,
 notes TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(kind, value));
CREATE TABLE IF NOT EXISTS endpoints (
 id TEXT PRIMARY KEY, method TEXT NOT NULL, url TEXT NOT NULL, source TEXT NOT NULL,
 notes TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(method, url));
CREATE TABLE IF NOT EXISTS findings (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, severity TEXT NOT NULL, status TEXT NOT NULL,
 description TEXT NOT NULL, impact TEXT NOT NULL, recommendation TEXT NOT NULL,
 asset_id TEXT, created_at TEXT NOT NULL,
 FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE SET NULL);
CREATE TABLE IF NOT EXISTS evidence (
 id TEXT PRIMARY KEY, finding_id TEXT NOT NULL, file_path TEXT NOT NULL,
 description TEXT NOT NULL, sha256 TEXT NOT NULL, created_at TEXT NOT NULL,
 FOREIGN KEY(finding_id) REFERENCES findings(id) ON DELETE CASCADE);
"""

class Database:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.executescript(SCHEMA)

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def insert(self, table: str, data: dict):
        allowed = {"assets", "endpoints", "findings", "evidence"}
        if table not in allowed:
            raise ValueError("Unsupported table")
        keys = list(data)
        cols = ", ".join(keys)
        marks = ", ".join("?" for _ in keys)
        with self.connect() as con:
            con.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})", [data[k] for k in keys])

    def rows(self, table: str):
        if table not in {"assets", "endpoints", "findings", "evidence"}:
            raise ValueError("Unsupported table")
        with self.connect() as con:
            return [dict(r) for r in con.execute(f"SELECT * FROM {table} ORDER BY created_at DESC")]
