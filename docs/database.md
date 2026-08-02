# Database design

Database mặc định là PostgreSQL + pgvector. Redis chỉ dùng cache, queue và rate limit; Redis không thay thế nguồn dữ liệu chính.

## Nhóm dữ liệu

- Identity: users, refresh tokens, subscriptions.
- Research graph: papers, authors, institutions, topics, citations.
- User behavior: interactions, library items, search history, recommendation logs.
- RAG: uploaded documents, chunks, chat sessions và messages.

Chi tiết model nằm tại `backend/app/models/entities.py`; migration tường minh nằm tại `backend/alembic/versions/0001_initial.py`.

## Kiểu dữ liệu quan trọng

- `JSONB`: metadata linh hoạt nhưng vẫn query/index được.
- `Vector(384)`: embeddings của paper, topic và chunk.
- Enum: role, document status, subscription status.
- UUID: khóa chính khó đoán cho tài nguyên người dùng.
- Timestamp có timezone: tránh phụ thuộc timezone máy chủ.

## Index

Migration tạo:

- Unique index cho email, username, OpenAlex ID và DOI phù hợp.
- GIN expression index cho full-text title/abstract/chunk.
- HNSW cosine index cho vector search.
- Composite index cho user interactions, library và trạng thái tài liệu.

## Migration

```powershell
docker compose exec backend alembic current
docker compose exec backend alembic upgrade head
docker compose exec backend alembic history
```

Không chỉnh schema trực tiếp bằng pgAdmin rồi bỏ qua Alembic. Mọi thay đổi schema phải có migration reviewable và test trên database trống lẫn database có dữ liệu.

## Kiểm tra pgvector

```powershell
docker compose exec postgres psql -U openresearch_user -d openresearch -c "SELECT extversion FROM pg_extension WHERE extname='vector';"
```

## Backup và restore

```powershell
.\scripts\windows\backup_database.ps1
.\scripts\windows\restore_database.ps1 -BackupFile .\backups\<file>.sql
```

Luôn thử restore vào database khác trước khi tin rằng backup sử dụng được.

## Quy tắc mở rộng

- Không nạp hàng triệu row vào Python để tính similarity.
- Dùng vector/FTS index để thu hẹp candidate.
- Tính analytics theo aggregate query hoặc materialized view.
- Batch upsert khi ingest.
- Theo dõi query plan bằng `EXPLAIN (ANALYZE, BUFFERS)` trước khi thêm index tùy tiện.
