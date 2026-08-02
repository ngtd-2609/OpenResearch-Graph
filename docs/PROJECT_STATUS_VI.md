# Trạng thái dự án sau đợt nâng cấp V2

## Đã kiểm tra trong môi trường bàn giao

- Python compile thành công cho backend, migration, pipeline và scripts.
- FastAPI import thành công: 46 routes, 35 OpenAPI paths.
- 94 backend unit/service tests đạt.
- Backend measured coverage: 82%, threshold CI là 80%.
- Authentication flow tests gồm register, login, refresh rotation/reuse, reset/change password và email verification.
- Recommendation end-to-end test đi qua content, collaborative và citation graph.
- Local storage tests gồm hash, quota, materialize, delete và path traversal.
- Payment service tests gồm mock, cấu hình Stripe và non-blocking SDK invocation.
- TypeScript/TSX của 35 file không có parse error.
- JSON, YAML và 4 notebooks parse thành công.
- Secret scan cơ bản không phát hiện high-confidence secret.

## Nâng cấp quan trọng

- LLM provider đã sửa lỗi `slots` serialization; có timeout, retry và response validation.
- Migration không còn dùng `Base.metadata.create_all`; schema và index được khai báo tường minh.
- Search/RAG dùng PostgreSQL FTS + pgvector candidate retrieval, reranker và MMR.
- Recommendation có collaborative co-occurrence và Personalized PageRank thật.
- Deep Learning model nhận query/title/abstract thay vì vài feature giả lập.
- OpenAlex API ingestion dùng cursor checkpoint; snapshot reader có resume/dead-letter.
- Stripe webhook có signature flow, lifecycle mapping và event idempotency.
- Storage local chặn path escape; email SMTP chạy ngoài event loop.
- Frontend có refresh retry, status polling, checkout/account flow, integration dashboard và nhiều test hơn.
- Tài liệu không còn là các file 3 dòng; mỗi tích hợp có setup, test, lỗi và fallback.

## Cần chạy trên máy người dùng/CI

- `npm install`, lint, typecheck, Vitest, Playwright và Next.js build.
- Docker build và `docker compose up`.
- Alembic migration trên PostgreSQL + pgvector thật.
- Real credentials cho OpenAlex, Stripe, SMTP, Ollama/LLM và S3.

## Giới hạn còn lại

- Refresh token ở frontend development vẫn dùng localStorage; production cần HttpOnly cookie + CSRF strategy.
- PDF scan chưa có OCR/malware scanning.
- Chưa benchmark snapshot nhiều triệu records hoặc tải đồng thời lớn.
- Recommendation cần interaction dataset thật và temporal evaluation.
- External integration code cần CI/credential verification trước khi tuyên bố production-ready.
