# Biến môi trường

`.env.example` là danh sách biến mẫu có thể commit. `.env` chứa cấu hình local và secret, không được commit.

## Khởi tạo

```powershell
Copy-Item .env.example .env
notepad .env
```

Cấu hình an toàn để chạy lần đầu:

```env
ENVIRONMENT=development
DEBUG=true
OPENALEX_MODE=seed
LLM_PROVIDER=mock
BILLING_MODE=mock
EMAIL_BACKEND=console
STORAGE_BACKEND=local
```

## Nhóm biến

| Nhóm | Biến chính | Chứa secret |
|---|---|---:|
| App | `ENVIRONMENT`, `DEBUG`, `CORS_ORIGINS` | Không |
| Database | `DATABASE_URL`, `POSTGRES_PASSWORD` | Có |
| Auth | `JWT_SECRET_KEY` | Có |
| OpenAlex | `OPENALEX_API_KEY` | Có |
| LLM | `LLM_API_KEY` | Có |
| Stripe | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Có |
| Storage | `S3_SECRET_ACCESS_KEY` | Có |
| Frontend | `NEXT_PUBLIC_API_URL` | Chỉ public value |

## Tạo JWT secret

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Dán kết quả vào `JWT_SECRET_KEY`. Không dùng cùng secret cho development và production.

## Docker hostname

Trong container, database host là `postgres`, Redis host là `redis`. Khi backend chạy trực tiếp trên Windows, host thường là `localhost`.

Docker:

```env
DATABASE_URL=postgresql+asyncpg://openresearch_user:password@postgres:5432/openresearch
REDIS_URL=redis://redis:6379/0
```

Chạy local:

```env
DATABASE_URL=postgresql+asyncpg://openresearch_user:password@localhost:5432/openresearch
REDIS_URL=redis://localhost:6379/0
```

## Áp dụng thay đổi

```powershell
docker compose up -d --force-recreate backend worker frontend
python scripts/system_doctor.py
```

`docker compose restart` có thể không đọc lại mọi thay đổi env trong một số tình huống; `--force-recreate` rõ ràng hơn.

## Kiểm tra secret trước commit

```powershell
git status
python scripts/check_secrets.py
git check-ignore .env
```

`git check-ignore .env` phải cho thấy file đang bị ignore. Nếu `.env` từng được commit, cần remove khỏi Git index và rotate key đã lộ.
