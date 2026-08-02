import asyncio
from pathlib import Path
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete

from app.db.session import AsyncSessionLocal
from app.models.entities import DocumentChunk, ProcessingStatus, UploadedDocument
from app.services.embedding_service import get_embedding_service
from app.services.pdf_service import PDFService
from app.services.storage_service import get_storage
from app.workers.celery_app import celery_app


async def _process_document(document_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        document = await db.get(UploadedDocument, UUID(document_id))
        if document is None:
            return {"status": "missing"}
        document.processing_status = ProcessingStatus.RUNNING
        await db.commit()
        try:
            local_path = await get_storage().materialize(document.storage_path)
            pages, chunks = PDFService().extract_chunks(local_path)
            if not chunks:
                raise ValueError("No extractable text found. OCR is not enabled in the default setup.")
            embeddings = get_embedding_service().encode([chunk.content for chunk in chunks])
            await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
            db.add_all([
                DocumentChunk(
                    document_id=document.id, page_number=chunk.page_number, chunk_index=chunk.chunk_index,
                    content=chunk.content, token_count=chunk.token_count, embedding=embedding,
                    metadata_json={"source": document.original_filename},
                )
                for chunk, embedding in zip(chunks, embeddings, strict=True)
            ])
            document.page_count = pages
            document.processing_status = ProcessingStatus.COMPLETED
            document.processing_error = None
            await db.commit()
            if local_path != document.storage_path and local_path.startswith("/tmp/"):
                Path(local_path).unlink(missing_ok=True)
            return {"status": "completed", "chunks": len(chunks)}
        except Exception as exc:
            document.processing_status = ProcessingStatus.FAILED
            document.processing_error = str(exc)[:1000]
            await db.commit()
            return {"status": "failed", "error": str(exc)}


@celery_app.task(name="app.tasks.document_tasks.process_document")
def process_document(document_id: str) -> dict:
    return asyncio.run(_process_document(document_id))


async def process_document_inline(document_id: str) -> dict:
    return await _process_document(document_id)
