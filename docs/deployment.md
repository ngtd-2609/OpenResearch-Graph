# Deployment entry point

Tài liệu triển khai chi tiết nằm tại [`15_DEPLOYMENT_VI.md`](15_DEPLOYMENT_VI.md).

## Mục tiêu kiến trúc

- Frontend, backend và worker là các workload độc lập.
- PostgreSQL, Redis và object storage là dịch vụ có state.
- Cùng một backend image được dùng cho API và worker để tránh lệch version model/schema.
- Mọi secret được cấu hình ngoài source code.

## Kiểm tra trước release

```powershell
python scripts/check_secrets.py
docker compose config
docker compose build
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend pytest
docker compose run --rm frontend npm run build
```

Sau deploy, chạy smoke test cho health, auth, search, upload, worker và RAG. Chưa vượt qua smoke test thì không gắn nhãn production-ready.
