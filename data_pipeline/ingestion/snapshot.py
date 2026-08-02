import argparse
import asyncio
import gzip
import json
from pathlib import Path
from typing import TextIO

from app.db.session import AsyncSessionLocal
from app.services.openalex_service import OpenAlexService
from data_pipeline.ingestion.common import PipelineCheckpoint, upsert_papers
from data_pipeline.processing import deduplicate_papers
from data_pipeline.validation import require_valid_paper_record


def iter_snapshot_files(path: Path):
    if path.is_file():
        yield path
        return
    yield from sorted((*path.rglob("*.gz"), *path.rglob("*.jsonl")))


def open_text(path: Path) -> TextIO:
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open("r", encoding="utf-8")


async def ingest(
    input_path: Path,
    batch_size: int,
    checkpoint_path: Path,
    dead_letter_path: Path,
    *,
    max_records: int | None = None,
    dry_run: bool = False,
) -> PipelineCheckpoint:
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    checkpoint = PipelineCheckpoint.load(checkpoint_path)
    dead_letter_path.parent.mkdir(parents=True, exist_ok=True)
    files = list(iter_snapshot_files(input_path))
    if not files:
        raise FileNotFoundError(f"No .gz or .jsonl files found under {input_path}")

    resume_source = checkpoint.source
    async with AsyncSessionLocal() as db, dead_letter_path.open("a", encoding="utf-8") as dead:
        for source_file in files:
            source_name = str(source_file.resolve())
            if resume_source and source_name != resume_source:
                continue
            start_line = checkpoint.position if source_name == resume_source else 0
            resume_source = ""
            batch: list[dict] = []
            last_line = start_line
            with open_text(source_file) as stream:
                for line_number, line in enumerate(stream):
                    if line_number < start_line:
                        continue
                    last_line = line_number + 1
                    try:
                        item = json.loads(line)
                        normalized = require_valid_paper_record(OpenAlexService.normalize_work(item))
                        batch.append(normalized)
                    except (json.JSONDecodeError, TypeError, ValueError) as exc:
                        checkpoint.errors += 1
                        dead.write(
                            json.dumps(
                                {
                                    "source": source_name,
                                    "line": line_number,
                                    "error": str(exc),
                                    "raw": line[:2_000],
                                },
                                ensure_ascii=False,
                            )
                            + "\n"
                        )
                    if len(batch) >= batch_size:
                        if not dry_run:
                            checkpoint.processed += await upsert_papers(db, deduplicate_papers(batch))
                        else:
                            checkpoint.processed += len(deduplicate_papers(batch))
                        batch.clear()
                        checkpoint.source = source_name
                        checkpoint.position = last_line
                        checkpoint.save(checkpoint_path)
                        print(
                            f"processed={checkpoint.processed} errors={checkpoint.errors} "
                            f"source={source_file.name} line={last_line}"
                        )
                    if max_records and checkpoint.processed + len(batch) >= max_records:
                        break
            if batch:
                if not dry_run:
                    checkpoint.processed += await upsert_papers(db, deduplicate_papers(batch))
                else:
                    checkpoint.processed += len(deduplicate_papers(batch))
            checkpoint.source = source_name
            checkpoint.position = last_line
            checkpoint.save(checkpoint_path)
            if max_records and checkpoint.processed >= max_records:
                break
    return checkpoint


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-path", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=5_000)
    parser.add_argument("--checkpoint-path", type=Path, default=Path("checkpoints/snapshot.json"))
    parser.add_argument("--dead-letter-path", type=Path, default=Path("checkpoints/snapshot-errors.jsonl"))
    parser.add_argument("--max-records", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = asyncio.run(
        ingest(
            args.input_path,
            args.batch_size,
            args.checkpoint_path,
            args.dead_letter_path,
            max_records=args.max_records,
            dry_run=args.dry_run,
        )
    )
    print(f"completed={result.processed} errors={result.errors}")
