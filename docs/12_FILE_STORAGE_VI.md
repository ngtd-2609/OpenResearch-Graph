# Lưu trữ PDF và tệp người dùng

Hệ thống tách **file nhị phân**, **metadata** và **embedding** để dễ mở rộng:

- PDF gốc: local volume hoặc S3-compatible storage.
- Metadata tài liệu, trạng thái xử lý và checksum: PostgreSQL.
- Text chunk và vector embedding: PostgreSQL + pgvector.

## Chế độ local

```env
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=/app/uploads
```

Docker volume `uploads_data` giữ file khi container được tạo lại. `docker compose down` giữ volume; `docker compose down -v` xóa cả PDF và database development.

Kiểm tra quyền ghi:

```powershell
docker compose exec backend python scripts/test_storage_connection.py
```

## Chế độ S3-compatible

```env
STORAGE_BACKEND=s3
S3_ENDPOINT_URL=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
S3_BUCKET=
S3_REGION=auto
```

Backend và worker phải dùng cùng bucket, endpoint và credential. Bucket không nên public. Khi cần tải file, backend nên tạo URL có thời hạn hoặc stream qua endpoint đã xác thực.

## Quy tắc bảo mật

- Không tin tên file do người dùng cung cấp.
- Kiểm tra MIME type, phần mở rộng, kích thước và magic bytes.
- Dùng UUID làm stored filename.
- Tính SHA-256 để phát hiện upload trùng.
- Không thực thi macro, JavaScript hoặc code nhúng trong PDF.
- Production cần malware scanning và chính sách retention.
- Không commit `uploads/` lên GitHub.

## Xóa tài liệu

Luồng xóa phải thực hiện theo thứ tự:

1. Xác nhận tài liệu thuộc user hiện tại.
2. Xóa file khỏi storage.
3. Xóa metadata và chunks trong transaction.
4. Ghi log sự kiện nhưng không ghi nội dung PDF.

Nếu xóa file thành công nhưng database lỗi, job cleanup phải có khả năng phát hiện orphan record. Nếu database xóa trước nhưng storage lỗi, cần retry xóa object.

## Sao lưu

Sao lưu database không tự động sao lưu PDF. Với local development, sao lưu cả volume `uploads_data`; với S3, bật versioning hoặc lifecycle phù hợp. Kiểm tra restore định kỳ thay vì chỉ tạo backup mà chưa từng thử phục hồi.
