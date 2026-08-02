# Strict Quality Scorecard V2

## Cách chấm

Điểm dưới đây áp dụng cho **nhóm file có logic hoặc tài liệu có nội dung thực tế**. Không chấm riêng các file đánh dấu package như `__init__.py`, file sinh tự động, giấy phép hoặc file cấu hình vài dòng vì thang điểm 10 không có ý nghĩa với chúng.

Tiêu chuẩn 8/10 yêu cầu: mục đích rõ, code có cấu trúc, lỗi được xử lý, bảo mật hợp lý, có test/bằng chứng, không tuyên bố quá khả năng đã kiểm tra.

## Điểm sau nâng cấp

| Nhóm file | Điểm ước tính | Bằng chứng |
|---|---:|---|
| Kiến trúc repository | 8.8 | Modular monolith, phân lớp frontend/backend/pipeline, adapter dịch vụ ngoài |
| FastAPI routes và schemas | 8.6 | Typed responses, ownership checks, quota, HTTP errors, 46 routes |
| PostgreSQL và Alembic | 8.6 | Migration tường minh, constraints, JSONB, FTS GIN, pgvector HNSW |
| Authentication và security | 8.7 | Argon2, JWT claims, token-family rotation, reuse detection, role checks |
| Search và OpenAlex | 8.4 | FTS/vector candidate retrieval, rerank, filters, cursor ingestion, fallback |
| PDF và RAG | 8.5 | Safe extraction, repeated-margin cleanup, hybrid retrieval, MMR, citations |
| Recommendation | 8.5 | Content, collaborative co-occurrence, Personalized PageRank, diversity |
| Deep Learning | 8.3 | Query/title/abstract model, train/validation loop, early stopping, inference |
| Data pipeline | 8.5 | Validation, stable deduplication, streaming, batch upsert, checkpoint, dead letter |
| Frontend | 8.0 có điều kiện | Typed API, refresh retry, guards, polling, billing/admin flows; cần full npm CI |
| Testing | 8.7 | 94 backend tests, 81.65% measured coverage, DB/frontend/E2E jobs configured |
| Docker và CI | 8.2 có điều kiện | Non-root images, health checks, PostgreSQL integration and 80% coverage gate |
| Tài liệu vận hành | 8.8 | Setup, external services, security, troubleshooting, deployment, Windows scripts |

**Điểm tổng thể ước tính: 8.5/10**, với điều kiện frontend build, Docker migration và credential-backed integrations phải vượt qua CI trên máy của người dùng.

## Những điều chưa được chứng nhận

- Không thể bảo đảm “mọi file tuyệt đối trên 8” bằng một con số khách quan; điểm là đánh giá kỹ thuật có tiêu chí.
- Chưa chạy production Next.js build do registry trong môi trường bàn giao không tải được dependency.
- Chưa chạy Docker/PostgreSQL integration vì không có Docker daemon.
- Chưa kiểm tra OpenAlex, Stripe, SMTP, Ollama và S3 bằng credential của người dùng.
- Chưa benchmark thực tế hàng triệu paper hoặc concurrent load lớn.

## Điều kiện để bỏ dấu “có điều kiện”

1. Push repository lên GitHub và làm xanh toàn bộ GitHub Actions.
2. Tạo, review và commit `package-lock.json`; chuyển CI/Docker từ `npm install` sang `npm ci`.
3. Chạy Alembic và integration tests trên PostgreSQL + pgvector thật.
4. Chạy Vitest, Playwright và `next build` thành công.
5. Test từng integration bằng test credential, sau đó lưu bằng chứng không chứa secret.
6. Chạy load test và ghi P50/P95 latency, error rate và resource usage.
