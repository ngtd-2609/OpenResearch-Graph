"""Stable in-batch deduplication for normalized paper records."""

from __future__ import annotations

from typing import Any


def deduplicate_papers(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep one record per OpenAlex ID while preserving first-seen ordering.

    Later copies merge non-null fields into the first record. This prevents a
    PostgreSQL `ON CONFLICT DO UPDATE` statement from affecting the same row
    twice in one batch while retaining richer metadata from duplicate records.
    """
    ordered_ids: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        identity = str(row.get("openalex_id") or "").strip()
        if not identity:
            continue
        if identity not in by_id:
            ordered_ids.append(identity)
            by_id[identity] = dict(row)
            continue
        existing = by_id[identity]
        for key, value in row.items():
            if value not in (None, "", [], {}) or key not in existing:
                existing[key] = value
    return [by_id[identity] for identity in ordered_ids]
