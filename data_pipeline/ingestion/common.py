import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Paper


@dataclass(slots=True)
class PipelineCheckpoint:
    source: str = ""
    position: int = 0
    processed: int = 0
    errors: int = 0
    cursor: str | None = None

    @classmethod
    def load(cls, path: Path) -> "PipelineCheckpoint":
        if not path.exists():
            return cls()
        return cls(**json.loads(path.read_text(encoding="utf-8")))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporary, path)


async def upsert_papers(db: AsyncSession, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    # Pass 1: upsert by openalex_id (authoritative key from OpenAlex)
    stmt = insert(Paper).values(rows)
    excluded = stmt.excluded
    update_columns = {
        column.name: getattr(excluded, column.name)
        for column in Paper.__table__.columns
        if column.name not in {"id", "openalex_id", "created_at"}
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=[Paper.openalex_id],
        set_=update_columns,
    )
    try:
        await db.execute(stmt)
        await db.commit()
        return len(rows)
    except Exception:
        await db.rollback()

    # Pass 2: fallback — insert row-by-row, skip any that conflict on doi or openalex_id
    inserted = 0
    for row in rows:
        single = insert(Paper).values([row])
        single = single.on_conflict_do_nothing()
        try:
            result = await db.execute(single)
            await db.commit()
            inserted += result.rowcount
        except Exception:
            await db.rollback()
    return inserted
