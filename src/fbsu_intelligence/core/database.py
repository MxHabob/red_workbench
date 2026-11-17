from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS domains (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    source TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    added_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    asset TEXT NOT NULL,
    source TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    first_observed_at TEXT NOT NULL,
    last_observed_at TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    confidence TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    evidence_reference TEXT NOT NULL,
    details_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metadata_resources (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    status_code INTEGER,
    availability TEXT NOT NULL,
    content_type TEXT NOT NULL,
    response_size INTEGER,
    observed_at TEXT NOT NULL,
    source_url TEXT NOT NULL,
    notes TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS collection_events (
    id TEXT PRIMARY KEY,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    source TEXT NOT NULL,
    message TEXT NOT NULL
);
"""

TABLES = {
    "domains": ("id", "name", "status", "source", "source_reference", "added_at"),
    "observations": (
        "id", "category", "asset", "source", "source_reference", "first_observed_at",
        "last_observed_at", "collected_at", "confidence", "verification_status",
        "evidence_reference", "details_json",
    ),
    "metadata_resources": (
        "id", "url", "category", "status_code", "availability", "content_type",
        "response_size", "observed_at", "source_url", "notes",
    ),
    "collection_events": (
        "id", "stage", "status", "started_at", "completed_at", "source", "message",
    ),
}


class Repository:
    """Small SQLite repository with an allow-listed table/column surface."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def insert(self, table: str, values: dict[str, Any], *, replace: bool = False) -> None:
        if table not in TABLES:
            raise ValueError(f"Unsupported repository table: {table}")
        columns = TABLES[table]
        if set(values) != set(columns):
            raise ValueError(f"Invalid fields for {table}; expected {', '.join(columns)}.")
        marks = ", ".join("?" for _ in columns)
        verb = "INSERT OR REPLACE" if replace else "INSERT"
        with self.connect() as connection:
            connection.execute(
                f"{verb} INTO {table} ({', '.join(columns)}) VALUES ({marks})",
                [values[column] for column in columns],
            )

    def list(self, table: str) -> list[dict[str, Any]]:
        if table not in TABLES:
            raise ValueError(f"Unsupported repository table: {table}")
        with self.connect() as connection:
            rows = connection.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
        records = [dict(row) for row in rows]
        for item in records:
            if "details_json" in item:
                item["details"] = json.loads(item.pop("details_json"))
        return records
