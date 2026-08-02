# Redis và Celery worker

Redis phục vụ ba mục đích: Celery broker/result backend, cache và rate limiting. PostgreSQL vẫn là nguồn dữ liệu chính.

## Khởi động

```powershell
docker compose up -d redis worker
docker compose ps redis worker
```

## Kiểm tra Redis

```powershell
docker compose exec redis redis-cli ping
```

Kết quả phải là `PONG`.

## Theo dõi worker

```powershell
docker compose logs -f worker
```

Khi upload PDF, log phải cho thấy task nhận document ID, chuyển trạng thái processing/completed hoặc failed.

## PDF đứng ở pending

1. `docker compose ps worker redis`.
2. Kiểm tra worker dùng đúng `REDIS_URL`.
3. Xem backend có enqueue task thành công không.
4. Xem worker import model/service có lỗi không.
5. Retry task sau khi sửa nguyên nhân; không đổi status database bằng tay.

## Retry và idempotency

Task PDF phải có khả năng chạy lại mà không tạo chunks trùng: xóa/rebuild chunks trong transaction hoặc kiểm tra processing version. External API task dùng retry có backoff, nhưng lỗi validation không nên retry vô hạn.

## Scale worker

Tách queue theo workload khi cần:

- `documents`: extraction/embedding.
- `ingestion`: OpenAlex batch.
- `maintenance`: cleanup/recommendation refresh.

Model embedding tốn RAM; tăng số worker process quá cao có thể nhân bản model nhiều lần.
