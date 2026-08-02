# Kết nối OpenAlex

OpenAlex cung cấp metadata paper, author, institution, topic và citation reference. Dự án mặc định dùng seed mode để không phụ thuộc mạng.

## Tạo key

1. Mở tài khoản OpenAlex.
2. Tạo hoặc sao chép API key từ khu vực API/account.
3. Không gửi key trong chat công khai hoặc commit Git.

```env
OPENALEX_MODE=api
OPENALEX_API_KEY=your_key
OPENALEX_BASE_URL=https://api.openalex.org
```

Áp dụng:

```powershell
docker compose up -d --force-recreate backend worker
python scripts/test_openalex_connection.py
```

Script chỉ in dạng key đã che, không in secret đầy đủ.

## Search trực tiếp

Frontend search sẽ dùng database trước và có thể fallback API theo cấu hình. Không để mỗi lần gõ phím gọi OpenAlex; cần submit/debounce và Redis cache.

## Ingestion query

```powershell
docker compose exec backend python -m data_pipeline.ingestion.openalex `
  --query "retrieval augmented generation" `
  --max-records 1000 `
  --batch-size 100
```

Sau khi kiểm tra 1.000 records, mới tăng quy mô. Cursor checkpoint cho phép resume mà không bắt đầu lại.

## Lỗi thường gặp

| Mã/lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| 401/403 | key sai hoặc quyền | tạo/chép lại key |
| 429 | vượt rate limit | tôn trọng Retry-After, giảm tốc, cache |
| timeout | mạng/API chậm | retry backoff, chạy lại checkpoint |
| 0 kết quả | query/filter quá hẹp | thử query ngắn hơn |
| trùng DOI/ID | record đã có | pipeline upsert, không insert mù |

## Quy mô lớn

Không dùng page-offset để quét toàn bộ kho. Query lớn dùng cursor; toàn bộ dataset nên dùng snapshot streaming. Đọc [`data_pipeline/README.md`](../data_pipeline/README.md) trước khi ingest lớn.

## Tắt tích hợp

```env
OPENALEX_MODE=seed
OPENALEX_API_KEY=
```

Restart backend/worker; search quay về dữ liệu seed/local.
