import time
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.chat import ChatResponse, CitationItem
from app.services.llm_service import Message, get_llm_provider
from app.services.prompt_safety import sanitize_retrieved_text
from app.services.retrieval_service import RetrievalService


class RAGService:
    """Grounded PDF question answering with hybrid retrieval and page citations."""

    async def answer(
        self,
        db: AsyncSession,
        document_id: UUID,
        question: str,
        top_k: int | None = None,
    ) -> ChatResponse:
        started = time.perf_counter()
        retrieved = await RetrievalService().retrieve(
            db,
            document_id=document_id,
            query=question,
            top_k=top_k,
        )
        if not retrieved:
            return ChatResponse(
                answer=(
                    "Không tìm thấy đoạn văn bản đủ liên quan trong tài liệu. "
                    "Hãy thử đặt câu hỏi cụ thể hơn."
                ),
                citations=[],
                model="none",
                latency_ms=int((time.perf_counter() - started) * 1_000),
            )

        context_parts: list[str] = []
        context_size = 0
        used_items = []
        for item in retrieved:
            safe_text = sanitize_retrieved_text(item.chunk.content.strip())
            block = (
                f"[SOURCE chunk={item.chunk.id} page={item.chunk.page_number}]\n"
                f"{safe_text}\n"
            )
            if context_parts and context_size + len(block) > settings.rag_max_context_chars:
                break
            context_parts.append(block)
            context_size += len(block)
            used_items.append(item)

        prompt = (
            "BẠN LÀ MỘT TRỢ LÝ NGHIÊN CỨU KHOA HỌC CHUYÊN SÂU (SCIENTIFIC RESEARCH AGENT).\n\n"
            "CÂU HỎI NGHIÊN CỨU:\n"
            f"{question.strip()}\n\n"
            "TÀI LIỆU TRÍCH XUẤT TỪ FILE PDF (GROUNDED CONTEXT):\n"
            + "\n".join(context_parts)
            + "\n\n"
            "HƯỚNG DẪN BIÊN SOẠN BÁO CÁO NGHIÊN CỨU:\n"
            "- Trả lời bằng tiếng Việt, văn phong học thuật, rõ ràng, gãy gọn.\n"
            "- Cấu trúc câu trả lời có đề mục rõ ràng (nếu câu hỏi bao quát: Tóm tắt cốt lõi, Phương pháp/Kiến trúc, Kết quả/Phát hiện chính, Hạn chế/Hướng phát triển).\n"
            "- BẮT BUỘC: Khi trích dẫn thông tin, hãy ghi rõ nguồn số trang theo định dạng [Trang X] tương ứng với chunk được cung cấp trong CONTEXT.\n"
            "- TUYỆT ĐỐI KHÔNG bịa đặt thông tin hoặc số trang không có trong CONTEXT.\n"
            "- Nếu CONTEXT không đủ dữ liệu để trả lời trọn vẹn, hãy nói rõ phần nào tài liệu chưa đề cập."
        )
        response = await get_llm_provider().generate(
            [
                Message(
                    "system",
                    "Bạn là trợ lý nghiên cứu có tính kiểm chứng và luôn bám sát nguồn được cung cấp.",
                ),
                Message("user", prompt),
            ]
        )
        citations = [
            CitationItem(
                document_id=document_id,
                page=item.chunk.page_number,
                chunk_id=item.chunk.id,
                quote=item.chunk.content[:400],
                score=round(item.final_score, 4),
            )
            for item in used_items
        ]
        return ChatResponse(
            answer=response.text,
            citations=citations,
            model=response.model,
            latency_ms=int((time.perf_counter() - started) * 1_000),
        )
