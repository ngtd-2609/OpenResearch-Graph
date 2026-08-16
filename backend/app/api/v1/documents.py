from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import Plan, Subscription, UploadedDocument, User
from app.schemas.documents import DocumentPublic, DocumentUploadResponse
from app.services.storage_service import get_storage
from app.tasks.document_tasks import process_document, process_document_inline

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    if file.content_type != "application/pdf" or not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are accepted")

    # Validate PDF magic bytes to prevent spoofed uploads (Audit §11.2 / §14.5)
    header = await file.read(5)
    if header != b"%PDF-":
        raise HTTPException(status_code=400, detail="File is not a valid PDF (invalid header)")
    await file.seek(0)

    subscription = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    document_count = int(
        await db.scalar(
            select(func.count()).select_from(UploadedDocument).where(UploadedDocument.user_id == user.id)
        )
        or 0
    )
    plan = subscription.plan if subscription else Plan.FREE
    maximum = settings.max_premium_documents if plan == Plan.PREMIUM else settings.max_free_documents
    if document_count >= maximum:
        raise HTTPException(status_code=403, detail=f"Document limit reached for {plan.value} plan")

    try:
        stored_name, path, size, checksum = await get_storage().save_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc

    duplicate = await db.scalar(
        select(UploadedDocument).where(
            UploadedDocument.user_id == user.id,
            UploadedDocument.checksum == checksum,
        )
    )
    if duplicate:
        await get_storage().delete(path)
        return DocumentUploadResponse(
            id=duplicate.id,
            status=duplicate.processing_status,
            filename=duplicate.original_filename,
        )

    document = UploadedDocument(
        user_id=user.id,
        original_filename=file.filename or "document.pdf",
        stored_filename=stored_name,
        mime_type=file.content_type,
        file_size=size,
        storage_path=path,
        checksum=checksum,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    try:
        process_document.delay(str(document.id))
    except Exception as exc:
        # Fallback to async background processing so HTTP response isn't blocked (Audit §11.3)
        asyncio.create_task(process_document_inline(str(document.id)))
    return DocumentUploadResponse(
        id=document.id,
        status=document.processing_status,
        filename=document.original_filename,
    )


def _serialize(document: UploadedDocument) -> DocumentPublic:
    return DocumentPublic(
        id=document.id,
        filename=document.original_filename,
        status=document.processing_status,
        pages=document.page_count,
        file_size=document.file_size,
        error=document.processing_error,
        created_at=document.created_at,
    )


@router.get("", response_model=list[DocumentPublic])
async def list_documents(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentPublic]:
    documents = list(
        (
            await db.scalars(
                select(UploadedDocument)
                .where(UploadedDocument.user_id == user.id)
                .order_by(UploadedDocument.created_at.desc())
            )
        ).all()
    )
    return [_serialize(document) for document in documents]


@router.get("/{document_id}", response_model=DocumentPublic)
async def get_document(
    document_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentPublic:
    document = await db.get(UploadedDocument, document_id)
    if document is None or document.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return _serialize(document)


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    document = await db.get(UploadedDocument, document_id)
    if document is None or document.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    await get_storage().delete(document.storage_path)
    await db.delete(document)
    await db.commit()
    return {"message": "Document deleted"}
