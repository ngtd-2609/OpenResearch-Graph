from data_pipeline.processing import deduplicate_papers
from data_pipeline.validation import require_valid_paper_record, validate_paper_record


def test_validation_sanitizes_identity_and_doi() -> None:
    row = require_valid_paper_record(
        {
            "openalex_id": " W1 ",
            "title": " Paper ",
            "doi": " HTTPS://DOI.ORG/10.1/ABC ",
            "publication_year": 2025,
            "cited_by_count": 0,
        }
    )
    assert row["openalex_id"] == "W1"
    assert row["title"] == "Paper"
    assert row["doi"] == "https://doi.org/10.1/abc"


def test_validation_reports_multiple_quality_issues() -> None:
    issues = validate_paper_record(
        {"openalex_id": "", "title": "", "publication_year": 1200, "cited_by_count": -1}
    )
    assert {issue.field for issue in issues} == {
        "openalex_id",
        "title",
        "publication_year",
        "cited_by_count",
    }


def test_deduplication_is_stable_and_merges_richer_fields() -> None:
    rows = [
        {"openalex_id": "W1", "title": "First", "abstract": None},
        {"openalex_id": "W2", "title": "Second"},
        {"openalex_id": "W1", "title": "First", "abstract": "Richer"},
        {"openalex_id": "", "title": "Invalid"},
    ]
    result = deduplicate_papers(rows)
    assert [row["openalex_id"] for row in result] == ["W1", "W2"]
    assert result[0]["abstract"] == "Richer"
