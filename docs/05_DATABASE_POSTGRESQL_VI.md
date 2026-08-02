# PostgreSQL + pgvector

PostgreSQL là nguồn dữ liệu chính. pgvector lưu embedding trong cùng transaction với paper/chunk; Redis chỉ làm cache, queue và rate limit.

## Khởi động

```powershell
docker compose up -d postgres
docker compose ps postgres
```

## Migration

```powershell
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend alembic current
```

Migration đầu tiên tạo extension `pgcrypto`, `vector`, tables, constraints, GIN full-text indexes và HNSW vector indexes.

## Kết nối DBeaver/pgAdmin

```text
Host: localhost
Port: 5432
Database: giá trị POSTGRES_DB
Username: giá trị POSTGRES_USER
Password: giá trị POSTGRES_PASSWORD
```

Không lưu password production vào screenshot hoặc README.

## Kiểm tra extension/index

```powershell
docker compose exec postgres psql -U openresearch_user -d openresearch -c "SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector','pgcrypto');"
docker compose exec postgres psql -U openresearch_user -d openresearch -c "SELECT indexname FROM pg_indexes WHERE indexname LIKE '%hnsw%' OR indexname LIKE '%search%';"
```

## Các bảng nên kiểm tra

- `users`, `refresh_tokens`, `subscriptions`.
- `papers`, `authors`, `institutions`, `citations`.
- `uploaded_documents`, `document_chunks`.
- `user_paper_interactions`, `recommendation_logs`.
- `payment_webhook_events` để chống xử lý webhook lặp.

## Truy vấn mẫu

```sql
SELECT publication_year, count(*)
FROM papers
GROUP BY publication_year
ORDER BY publication_year DESC;

SELECT status, count(*)
FROM uploaded_documents
GROUP BY status;
```

## Backup/restore

```powershell
.\scripts\windows\backup_database.ps1
.\scripts\windows\restore_database.ps1 -BackupFile .\backups\openresearch-YYYYMMDD-HHMMSS.sql
```

Thử restore sang database test trước khi coi backup là hợp lệ.

## Không nên làm

- Không sửa embedding bằng tay.
- Không tạo bảng trực tiếp rồi bỏ qua Alembic.
- Không chạy query lấy toàn bộ chunks/papers vào RAM.
- Không xóa volume để sửa lỗi migration khi chưa đọc log.
