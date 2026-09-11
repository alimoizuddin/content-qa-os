"""Local history of approved packages.

SQLite, on this machine, gitignored. Only approved, sanitised text is stored: the
brief, the raw model output, any provider diagnostics, and every key are all
deliberately absent. ``CHECK (approved = 1)`` makes storing an unapproved package
structurally impossible rather than merely discouraged.

The previous version had a write path and no read path, so nothing that was saved
was ever shown again. Reading it back is what makes the history worth writing.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_HISTORY_PATH = Path(__file__).resolve().parents[1] / "data" / "history.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS approved_packages (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    persona TEXT NOT NULL,
    output_types TEXT NOT NULL,
    outputs TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    approved INTEGER NOT NULL CHECK (approved = 1)
)
"""


def _connect(database_path: Path | str) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(SCHEMA)
    return connection


def save_approved_package(
    database_path: Path | str = DEFAULT_HISTORY_PATH,
    *,
    persona: str,
    outputs: dict[str, str],
    provider: str,
    model: str,
    output_types: list[str] | None = None,
) -> int:
    with _connect(database_path) as connection:
        cursor = connection.execute(
            "INSERT INTO approved_packages "
            "(persona, output_types, outputs, provider, model, approved) "
            "VALUES (?, ?, ?, ?, ?, 1)",
            (
                persona,
                ", ".join(output_types or []),
                json.dumps(outputs, ensure_ascii=False),
                provider,
                model,
            ),
        )
        return int(cursor.lastrowid)


def list_approved_packages(
    database_path: Path | str = DEFAULT_HISTORY_PATH,
    *,
    persona: str = "",
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Most recent first. Returns an empty list when nothing has been approved yet."""
    try:
        with _connect(database_path) as connection:
            if persona:
                rows = connection.execute(
                    "SELECT * FROM approved_packages WHERE persona = ? "
                    "ORDER BY id DESC LIMIT ?",
                    (persona, limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM approved_packages ORDER BY id DESC LIMIT ?", (limit,)
                ).fetchall()
    except sqlite3.DatabaseError:
        return []

    packages = []
    for row in rows:
        try:
            outputs = json.loads(row["outputs"])
        except (TypeError, ValueError):
            outputs = {}
        packages.append(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "persona": row["persona"],
                "output_types": row["output_types"],
                "outputs": outputs,
                "provider": row["provider"],
                "model": row["model"],
            }
        )
    return packages


def delete_package(database_path: Path | str = DEFAULT_HISTORY_PATH, *, package_id: int) -> bool:
    with _connect(database_path) as connection:
        cursor = connection.execute(
            "DELETE FROM approved_packages WHERE id = ?", (package_id,)
        )
        return cursor.rowcount > 0


def package_as_text(entry: dict[str, Any]) -> str:
    """One saved package as a plain text file a person can open, keep, or paste from.

    The database is the right place to keep approved work and the wrong thing to
    hand a person. Ali approved a post and then could not find where it had gone.
    """
    lines = [
        f"{entry['persona']}, saved package #{entry['id']}, {entry.get('created_at', '')}",
        f"Written with {entry.get('model', '')}",
        "",
    ]
    for key, value in entry["outputs"].items():
        lines += [f"[{key}]", str(value).strip(), ""]
    return "\n".join(lines).rstrip() + "\n"
