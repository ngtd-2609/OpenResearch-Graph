# Ma trận dịch vụ bên ngoài

| Dịch vụ | Mục đích | Core bắt buộc | Dev fallback | Secret/biến | Cách kiểm tra | Cách tắt |
|---|---|---:|---|---|---|---|
| PostgreSQL | dữ liệu chính | Có | Docker local | `DATABASE_URL` | `/health`, SQL | Không |
| pgvector | vector retrieval | Có | Docker local | dimension config | extension/index query | Không |
| Redis | queue/cache/rate limit | Có | in-memory limiter hạn chế | `REDIS_URL` | `redis-cli ping` | chỉ test đơn lẻ |
| OpenAlex | metadata thật | Không | seed data | `OPENALEX_*` | test script, sample search | `OPENALEX_MODE=seed` |
| Hugging Face | embedding/rerank | Không tuyệt đối | hash/lexical fallback | model names | vector dimension test | offline fallback |
| Ollama | local generation | Không | mock | `OLLAMA_*` | `/api/tags`, LLM test | `LLM_PROVIDER=mock` |
| OpenAI-compatible | hosted generation | Không | mock/Ollama | `LLM_*` | LLM test script | mock |
| Stripe | subscription | Không | mock billing | `STRIPE_*` | checkout + webhook event | `BILLING_MODE=mock` |
| Email | verification/reset | Không | console/Mailpit | `SMTP_*` | test email/log | console |
| S3-compatible | PDF production | Không local | local volume | `S3_*` | storage test | local |
| GitHub Actions | CI | Nên có | local commands | repo secrets khi deploy | Actions tab | local test |

## Thứ tự bật

1. PostgreSQL, pgvector, Redis.
2. Seed data + mock LLM/billing.
3. OpenAlex API.
4. Hugging Face model hoặc Ollama.
5. Stripe test.
6. Email/S3.
7. Production deployment.

Không bật mọi tích hợp cùng lúc; khi lỗi sẽ khó xác định nguyên nhân.
