# OpenAlex data pipeline

Pipeline hỗ trợ hai đường ingest khác nhau:

1. **OpenAlex API cursor ingestion** cho query có phạm vi vừa phải.
2. **Snapshot streaming ingestion** cho dữ liệu quy mô lớn đã tải về.

Cả hai dùng validation, in-batch deduplication, batch upsert, checkpoint atomic, resume và thống kê lỗi. Không nạp toàn bộ dataset vào RAM.

## API ingestion

```powershell
docker compose exec backend python -m data_pipeline.ingestion.openalex `
  --query "deep learning" `
  --max-records 5000 `
  --batch-size 100 `
  --checkpoint-path checkpoints/deep-learning.json
```

Checkpoint lưu query, cursor, page count, processed và errors. Nếu dùng cùng checkpoint cho query khác, command từ chối để tránh trộn dữ liệu.

## Snapshot ingestion

Mount thư mục snapshot vào container rồi chạy:

```powershell
docker compose exec backend python -m data_pipeline.ingestion.snapshot `
  --input-path /data/openalex-snapshot `
  --batch-size 5000 `
  --checkpoint-path checkpoints/snapshot.json `
  --dead-letter-path checkpoints/snapshot-errors.jsonl
```

Định dạng reader hiện hỗ trợ `.jsonl` và `.jsonl.gz`/`.gz` chứa mỗi JSON object trên một dòng. Hãy kiểm tra định dạng snapshot thực tế trước khi chạy toàn bộ.

## Dry run

```powershell
docker compose exec backend python -m data_pipeline.ingestion.snapshot `
  --input-path /data/sample `
  --batch-size 100 `
  --max-records 1000 `
  --dry-run
```

Dry run vẫn parse, normalize, checkpoint và ghi dead-letter nhưng không upsert database.

## Resume

Không xóa checkpoint khi job bị dừng. Chạy lại cùng command để tiếp tục từ cursor hoặc file/line gần nhất. Checkpoint được ghi qua file tạm rồi `os.replace`, giảm nguy cơ file JSON dở dang.

## Dead-letter records

Malformed JSON hoặc record không đạt quy tắc dữ liệu như thiếu OpenAlex ID/title, năm không hợp lệ được ghi vào JSONL với source, line, error và phần raw bị cắt. Không để một record lỗi làm dừng toàn bộ batch.

## Vận hành an toàn

- Bắt đầu bằng `--max-records 1000`.
- Theo dõi disk, WAL, database connections và index growth.
- Backup trước batch lớn.
- Không build HNSW lại liên tục sau từng record; ingest theo batch.
- Tách pipeline process khỏi API process khi chạy lớn.
- Không tuyên bố đã xử lý hàng triệu paper nếu chưa lưu benchmark, log và row count.

## Kiểm tra kết quả

```powershell
docker compose exec postgres psql -U openresearch_user -d openresearch -c "SELECT count(*) FROM papers;"
docker compose exec postgres psql -U openresearch_user -d openresearch -c "SELECT publication_year, count(*) FROM papers GROUP BY 1 ORDER BY 1 DESC LIMIT 10;"
```


## Validation và deduplication

Mỗi paper được chuẩn hóa rồi kiểm tra `openalex_id`, title, publication year và citation count. DOI được chuẩn hóa chữ thường. Trong mỗi batch, bản ghi trùng OpenAlex ID được gộp ổn định trước khi upsert để tránh một lệnh PostgreSQL tác động cùng một row nhiều lần.

Các module liên quan:

```text
data_pipeline/validation/records.py
data_pipeline/processing/deduplication.py
```
