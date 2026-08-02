"""Validation rules for normalized OpenAlex paper records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class ValidationIssue:
    field: str
    message: str


def validate_paper_record(record: dict[str, Any]) -> list[ValidationIssue]:
    """Return deterministic data-quality issues without mutating the input record."""
    issues: list[ValidationIssue] = []
    openalex_id = str(record.get("openalex_id") or "").strip()
    title = str(record.get("title") or "").strip()
    year = record.get("publication_year")
    citations = record.get("cited_by_count", 0)

    if not openalex_id:
        issues.append(ValidationIssue("openalex_id", "OpenAlex work ID is required"))
    if not title:
        issues.append(ValidationIssue("title", "Paper title is required"))
    if year is not None and (not isinstance(year, int) or year < 1400 or year > 2200):
        issues.append(ValidationIssue("publication_year", "Publication year is outside the accepted range"))
    if not isinstance(citations, int) or citations < 0:
        issues.append(ValidationIssue("cited_by_count", "Citation count must be a non-negative integer"))
    embedding = record.get("embedding")
    if embedding is not None and not isinstance(embedding, list):
        issues.append(ValidationIssue("embedding", "Embedding must be a list or null"))
    return issues


def require_valid_paper_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return a sanitized copy or raise a concise validation error."""
    sanitized = dict(record)
    sanitized["openalex_id"] = str(sanitized.get("openalex_id") or "").strip()
    sanitized["title"] = str(sanitized.get("title") or "").strip()
    if sanitized.get("doi"):
        sanitized["doi"] = str(sanitized["doi"]).strip().lower()
    issues = validate_paper_record(sanitized)
    if issues:
        detail = "; ".join(f"{issue.field}: {issue.message}" for issue in issues)
        raise ValueError(detail)
    return sanitized
