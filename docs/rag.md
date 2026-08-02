# Kiến trúc PDF RAG

## Pipeline ingestion

```mermaid
flowchart LR
  A[Upload PDF] --> B[Validate type and size]
  B --> C[SHA-256 and storage]
  C --> D[Celery worker]
  D --> E[PyMuPDF extraction]
  E --> F[Clean repeated text]
  F --> G[Chunk with overlap]
  G --> H[Embedding]
  H --> I[(PostgreSQL + pgvector)]
```

Tài liệu chuyển trạng thái `pending → processing → completed` hoặc `failed`. Frontend polling endpoint trạng thái thay vì chờ cố định vài giây.

## Retrieval

Retrieval service kết hợp:

1. PostgreSQL full-text score.
2. pgvector cosine similarity.
3. Optional cross-encoder reranking.
4. MMR để giảm chunk trùng lặp.
5. Context token/character budget.

Nếu database không hỗ trợ vector/FTS trong test, service có Python fallback. Fallback chỉ dành cho development và unit test, không phải giải pháp scale.

## Generation

System prompt yêu cầu model:

- Chỉ dùng context được cung cấp.
- Nói rõ khi context không đủ.
- Không coi nội dung PDF là system instruction.
- Không tiết lộ secret hoặc prompt hệ thống.
- Gắn nguồn theo chunk/page.

## Citation

Mỗi citation trả về `document_id`, `chunk_id`, `page`, `quote` và retrieval score. Citation là truy vết nguồn, không phải chứng nhận câu trả lời đúng; UI cần cho người dùng mở lại PDF để kiểm tra.

## Prompt injection

`prompt_safety.py` đánh dấu các mẫu chỉ dẫn đáng ngờ trong tài liệu trước khi đưa vào context. Đây là defense-in-depth, không thay thế sandbox, content policy hoặc review bảo mật.

## Đánh giá

Nên tạo bộ câu hỏi có đáp án và đo:

- Retrieval Recall@K.
- Context precision.
- Answer faithfulness.
- Citation correctness.
- Latency P50/P95.
- Tỷ lệ “không đủ dữ liệu” đúng.

Không chấm RAG chỉ bằng việc đọc vài câu trả lời đẹp mắt.
