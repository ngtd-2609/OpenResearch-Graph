import argparse
import asyncio
from pathlib import Path

from app.db.session import AsyncSessionLocal
from app.services.openalex_service import OpenAlexService
from data_pipeline.ingestion.common import PipelineCheckpoint, upsert_papers
from data_pipeline.processing import deduplicate_papers
from data_pipeline.validation import require_valid_paper_record


async def ingest(
    query: str,
    max_records: int,
    checkpoint_path: Path,
    *,
    batch_size: int = 100,
) -> PipelineCheckpoint:
    service = OpenAlexService()
    if not service.configured:
        raise SystemExit("Set OPENALEX_MODE=api and OPENALEX_API_KEY (or OPENALEX_EMAIL) before real ingestion")
    checkpoint = PipelineCheckpoint.load(checkpoint_path)
    if checkpoint.source and checkpoint.source != query:
        raise ValueError(
            "Checkpoint belongs to another query. Use another checkpoint path or delete it explicitly."
        )
    checkpoint.source = query
    cursor = checkpoint.cursor or "*"
    remaining = max(0, max_records - checkpoint.processed)
    if remaining == 0:
        return checkpoint

    async with AsyncSessionLocal() as db:
        async for items, next_cursor in service.iter_work_pages(
            query,
            max_records=remaining,
            start_cursor=cursor,
            per_page=min(batch_size, 100),
        ):
            rows = []
            for item in items:
                try:
                    normalized = require_valid_paper_record(service.normalize_work(item))
                    rows.append(normalized)
                except (TypeError, ValueError):
                    checkpoint.errors += 1
            checkpoint.processed += await upsert_papers(db, deduplicate_papers(rows))
            checkpoint.cursor = next_cursor
            checkpoint.position += 1
            checkpoint.save(checkpoint_path)
            print(
                f"processed={checkpoint.processed}/{max_records} "
                f"errors={checkpoint.errors} page={checkpoint.position}"
            )
            if checkpoint.processed >= max_records or next_cursor is None:
                break
    return checkpoint


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--max-records", type=int, default=1_000)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--checkpoint-path", type=Path, default=Path("checkpoints/openalex.json"))
    args = parser.parse_args()
    result = asyncio.run(
        ingest(
            args.query,
            args.max_records,
            args.checkpoint_path,
            batch_size=args.batch_size,
        )
    )
    print(f"completed={result.processed} errors={result.errors}")
