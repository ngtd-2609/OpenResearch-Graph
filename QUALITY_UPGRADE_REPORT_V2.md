# Quality Upgrade Report V2

## Mục tiêu

Nâng các file quan trọng từ scaffold/demo lên mức có thể giải thích, kiểm thử và bảo vệ trong phỏng vấn kỹ thuật. Điểm số là đánh giá kỹ thuật có điều kiện, không phải chứng nhận tuyệt đối cho từng file nhỏ như `__init__.py`.

## So sánh trước và sau

| Hạng mục | Trước | V2 ước tính | Bằng chứng chính |
|---|---:|---:|---|
| Kiến trúc/module | 7.5 | 8.8 | modular monolith, layer boundaries, diagrams |
| Backend API | 6.0 | 8.3 | typed services, errors, quotas, lifecycle flows |
| Database/migration | 4.5 | 8.6 | explicit Alembic, JSONB, constraints, FTS/HNSW indexes |
| Auth/security | 5.0 | 8.4 | Argon2, JWT claims, refresh family rotation/reuse tests |
| Search/OpenAlex | 5.0 | 8.3 | FTS/vector candidates, reranking, cursor ingestion |
| PDF/RAG | 4.5 | 8.2 | hybrid retrieval, MMR, context budget, citations, polling |
| Recommendation | 3.5 | 8.5 | content + collaborative + Personalized PageRank + diversity |
| Deep Learning | 2.0 | 8.2 | query/document text model, training, early stopping, inference |
| Frontend/UX | 3.5 | 8.0* | typed client, refresh retry, real polling/checkout/admin status |
| Testing | 2.5 | 8.2 | 94 tests, 82% backend coverage, frontend/E2E tests configured |
| Docker/CI | 5.5 | 8.1* | non-root runtime, DB integration job, 80% gate, E2E/build jobs |
| Documentation | 4.5 | 8.8 | setup/operation/security/troubleshooting manuals |

`*` Frontend production build and Docker execution remain conditional because those tools/dependencies were unavailable in the delivery environment.

## Defects removed

1. Ollama/OpenAI-compatible providers no longer access `__dict__` on a slots dataclass.
2. RAG no longer retrieves every chunk into Python as the primary path.
3. Recommendation graph score is no longer an alias of popularity.
4. Deep Learning is no longer a four-row MLP demo over handcrafted numeric features.
5. Initial migration no longer calls `create_all/drop_all`.
6. PDF UI no longer assumes processing completes after three seconds.
7. Stripe events are idempotent and subscription records can be created by webhook.
8. Local storage cannot delete/materialize a path outside its configured root.
9. Synchronous Stripe/SMTP operations no longer block the async event loop.
10. Empty/stub documentation has been replaced by operational guidance.

## Verification evidence

```text
94 backend tests passed
82% backend coverage
46 FastAPI routes / 35 OpenAPI paths
34 TypeScript/TSX source/config files parsed successfully; generated `next-env.d.ts` excluded
JSON/YAML/notebooks validated
secret scan passed
```

## Remaining gates before claiming 8+/10 without conditions

- Run GitHub Actions successfully after pushing.
- Generate and commit a reviewed `package-lock.json` after `npm install`.
- Pass full frontend lint/typecheck/test/build/E2E.
- Pass Alembic migration and integration tests on real PostgreSQL + pgvector.
- Test each external provider with user-owned test credentials.
- Run load tests and record P50/P95 latency.
- Replace development token storage with production cookie/CSRF design before public deployment.

## Recommended GitHub wording

Use:

> Portfolio-grade research intelligence platform with production-oriented architecture, development fallbacks and explicit limitations.

Do not use:

> Production-ready platform already processing millions of papers.
