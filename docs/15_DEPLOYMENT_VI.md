# Triển khai OpenResearch Graph

Dự án được thiết kế theo modular monolith: một codebase nhưng frontend, API và worker có thể triển khai thành các tiến trình riêng.

## Thành phần production

| Thành phần | Vai trò | Có state |
|---|---|---:|
| Frontend | Next.js UI | Không |
| Backend | FastAPI REST API | Không |
| Worker | PDF, embedding, ingestion | Không |
| PostgreSQL + pgvector | dữ liệu chính và vector | Có |
| Redis | queue, cache, rate limit | Có |
| Object storage | PDF gốc | Có |

Không dùng SQLite, local filesystem hoặc mock billing làm production backend.

## Checklist trước khi deploy

- [ ] Tạo database production riêng.
- [ ] Bật extension `vector` và `pgcrypto`.
- [ ] Thiết lập backup và thử restore.
- [ ] Tạo Redis có persistence phù hợp với queue.
- [ ] Dùng object storage private.
- [ ] Thay JWT secret và database password.
- [ ] Cấu hình domain thật trong CORS.
- [ ] Dùng HTTPS.
- [ ] Tạo Stripe webhook HTTPS nếu bật billing.
- [ ] Tắt demo accounts và seed password.
- [ ] Chạy CI xanh trước deploy.

## Trình tự release

1. Backup database.
2. Build image bằng commit SHA, không dùng tag mơ hồ `latest` duy nhất.
3. Chạy `alembic upgrade head` bằng release job một lần.
4. Deploy backend và worker dùng cùng image version.
5. Deploy frontend với `NEXT_PUBLIC_API_URL` đúng.
6. Chạy smoke test `/health`, đăng nhập, search, upload PDF.
7. Theo dõi error rate và worker queue.

## Biến môi trường quan trọng

```env
ENVIRONMENT=production
DEBUG=false
FRONTEND_URL=https://your-domain.example
CORS_ORIGINS=https://your-domain.example
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
JWT_SECRET_KEY=<random-long-secret>
STORAGE_BACKEND=s3
```

Frontend chỉ nhận biến `NEXT_PUBLIC_*` thực sự công khai. Không đưa database URL, Stripe secret hoặc LLM key vào bundle frontend.

## Zero-downtime và migration

Migration thêm cột/index thường an toàn hơn migration đổi kiểu hoặc xóa cột. Với bảng paper lớn, tạo index cần kế hoạch riêng để tránh khóa lâu. Chỉ rollback application khi schema vẫn tương thích; downgrade database tùy tiện có thể làm mất dữ liệu.

## Quan sát hệ thống

Theo dõi tối thiểu:

- API latency và tỷ lệ 5xx.
- PostgreSQL connection pool và query chậm.
- Redis availability.
- Celery queue depth, retry và dead-letter jobs.
- PDF processing time.
- OpenAlex 429/timeout.
- LLM latency, token usage và chi phí.
- Storage error và dung lượng.

## Domain và webhook

Stripe webhook phải trỏ tới URL public HTTPS của backend. CORS chỉ liên quan trình duyệt; nó không bảo vệ API khỏi request server-to-server. Phải dựa vào authentication, authorization, webhook signature và rate limiting.
