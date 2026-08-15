"""Ensure all papers in database have stored embeddings."""
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.entities import Paper
from app.services.embedding_service import get_embedding_service
from sqlalchemy import select, update


async def main():
    async with AsyncSessionLocal() as db:
        missing_papers = list(
            (
                await db.scalars(
                    select(Paper).where(Paper.embedding.is_(None))
                )
            ).all()
        )
        print(f"Papers missing embeddings: {len(missing_papers)}")
        if not missing_papers:
            print("[OK] All papers already have embeddings.")
            return

        batch_size = 64
        for i in range(0, len(missing_papers), batch_size):
            batch = missing_papers[i : i + batch_size]
            texts = [f"{p.title} {p.abstract or ''}" for p in batch]
            embeddings = get_embedding_service().encode(texts, batch_size=batch_size)
            for paper, emb in zip(batch, embeddings, strict=True):
                paper.embedding = emb
            await db.commit()
            print(f"Encoded batch {i + len(batch)}/{len(missing_papers)}")

        print("[OK] All embeddings successfully generated and stored in Neon DB.")


if __name__ == "__main__":
    asyncio.run(main())
