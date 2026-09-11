"""A small, content-free log of what the app did.

One JSON line per event in ``data/logs/runs.jsonl``: when, which person, which
model, how long it took, whether it worked, and if not, why, in the app's own
words. Never the brief, never the generated text, never a key, never a raw provider
error. Only the fields in ``ALLOWED_FIELDS`` can be written, so nothing sensitive
gets in by accident.

It exists so an operator can answer "how often does writing fail, and how long does
it take" without reading anyone's content.
"""
from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_LOG_PATH = Path(__file__).resolve().parents[1] / "data" / "logs" / "runs.jsonl"

# The evaluation harness switches this off and the tests point it at a temporary
# file, so replays and fakes never end up in the operator's real log.
ENABLED = True
LOG_PATH = DEFAULT_LOG_PATH

ALLOWED_FIELDS = frozenset({
    "persona", "output_type", "provider", "model", "success", "attempts", "error",
    "seconds", "package_id", "output_types",
})


def log_event(event: str, **fields: Any) -> None:
    """Append one event. Never raises: a logging problem must not break the app."""
    if not ENABLED:
        return
    record: dict[str, Any] = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event": event,
    }
    record.update({k: v for k, v in fields.items() if k in ALLOWED_FIELDS})
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def read_events(limit: int = 500) -> list[dict[str, Any]]:
    """The most recent events, oldest first. Unreadable lines are skipped."""
    try:
        lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    events = []
    for line in lines[-limit:]:
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    return events


def summary(limit: int = 50) -> dict[str, Any]:
    """Success rate and typical time for the most recent writing runs."""
    runs = [e for e in read_events() if e.get("event") == "generate"][-limit:]
    if not runs:
        return {"runs": 0, "worked": 0, "median_seconds": None}
    seconds = [e["seconds"] for e in runs if isinstance(e.get("seconds"), (int, float))]
    return {
        "runs": len(runs),
        "worked": sum(1 for e in runs if e.get("success")),
        "median_seconds": round(statistics.median(seconds), 1) if seconds else None,
    }
