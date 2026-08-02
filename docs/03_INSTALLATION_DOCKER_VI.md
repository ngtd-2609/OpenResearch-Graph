# Docker Desktop và Docker Compose

## Các service

```text
frontend  → Next.js
backend   → FastAPI
worker    → Celery tasks
postgres  → PostgreSQL + pgvector
redis     → queue/cache/rate limit
mailpit   → email development, profile tùy chọn
```

## Khởi động

```powershell
docker compose up --build
```

Lệnh này build image và giữ log trong terminal. Để chạy nền:

```powershell
docker compose up -d --build
```

Nếu chỉ khởi động hạ tầng:

```powershell
docker compose up -d postgres redis
```

## Trạng thái và log

```powershell
docker compose ps
docker compose logs --tail=200 backend
docker compose logs -f worker
docker compose logs postgres
docker compose logs redis
```

`-f` theo dõi log liên tục; nhấn `Ctrl+C` chỉ dừng việc xem log, không dừng container chạy nền.

## Restart và rebuild

```powershell
docker compose restart backend worker
docker compose up -d --build backend worker
```

Restart không cài dependency mới. Khi đổi `requirements.txt`, `package.json` hoặc Dockerfile, phải build lại.

## Dừng an toàn

```powershell
docker compose down
```

Lệnh này xóa container/network nhưng giữ named volumes.

> **Cảnh báo:** `docker compose down -v` xóa PostgreSQL, Redis state và uploads local. Không dùng như bước troubleshooting đầu tiên.

## Vào container

```powershell
docker compose exec backend bash
docker compose exec postgres psql -U openresearch_user -d openresearch
docker compose exec redis redis-cli
```

## Healthcheck

```powershell
docker inspect --format='{{json .State.Health}}' openresearch-backend
```

Tên container có thể khác; lấy tên đúng từ `docker compose ps`.

## Dọn dung lượng

```powershell
docker system df
docker image prune
```

Không chạy `docker system prune --volumes` nếu chưa hiểu volume nào chứa dữ liệu.
