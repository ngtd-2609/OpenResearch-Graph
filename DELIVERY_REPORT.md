# Delivery Report V2

## Mục tiêu đợt nâng cấp

Nâng repository từ một MVP rộng nhưng còn nông thành portfolio-grade modular monolith có thể giải thích và bảo vệ trong phỏng vấn kỹ thuật. Mục tiêu không phải thêm tên tính năng, mà tăng độ sâu triển khai, test và tài liệu.

## Nâng cấp chính

- Sửa hoàn toàn serialization của Ollama/OpenAI-compatible providers; thêm timeout, retry và schema validation.
- Search và RAG dùng PostgreSQL FTS + pgvector candidate retrieval, reranking, MMR và grounded page citations.
- Recommendation kết hợp content, collaborative implicit feedback, Personalized PageRank, popularity, recency, feedback và diversity.
- Deep Learning nhận trực tiếp query/title/abstract, có training, validation, early stopping, checkpoint và inference.
- Alembic migration tường minh, có PostgreSQL extensions, constraints, JSONB, GIN và HNSW indexes.
- Authentication có access/refresh token, token-family rotation, reuse detection, reset/verify flows và role authorization.
- Stripe webhook có signature path, lifecycle mapping và event idempotency.
- PDF extraction đóng file an toàn, kiểm tra chunk parameters, loại header/footer lặp và giữ page metadata.
- Storage chặn path traversal; SMTP/Stripe sync SDK chạy ngoài async event loop.
- OpenAlex API/snapshot ingestion có validation, stable deduplication, batch upsert, checkpoint, resume và dead-letter records.
- Frontend có typed client, refresh retry, auth guard, status polling, search filters, recommendation feedback, pricing/account và admin integration health.
- Tài liệu tiếng Việt được mở rộng thành cẩm nang thao tác từng dịch vụ và xử lý lỗi.

## Bằng chứng kiểm tra trong môi trường bàn giao

- Python compile: đạt.
- Backend tests: **94 passed**.
- Backend measured coverage: **81.65%**, CI gate **80%**.
- FastAPI: **46 routes / 35 OpenAPI paths**.
- TypeScript/TSX syntax: **34 source/config files, 0 parse errors**; `next-env.d.ts` là file generated declaration nên không transpile.
- JSON/YAML/notebooks: parse thành công.
- High-confidence secret scan: đạt.
- Placeholder scan: không có TODO/FIXME/NotImplemented hay `except Exception: pass` trong logic bàn giao.

## Chưa được kiểm tra trong môi trường bàn giao

- Full npm install, ESLint, TypeScript module resolution, Vitest, Playwright và Next.js production build.
- Docker images, Docker Compose, Alembic PostgreSQL migration và DB integration test.
- OpenAlex, Stripe, SMTP, Ollama/OpenAI-compatible LLM và S3 bằng credential thật.
- Benchmark ingestion nhiều triệu records hoặc tải đồng thời production.

Không được tuyên bố production-ready cho đến khi các gate trên chạy xanh trên máy/CI của người dùng.
