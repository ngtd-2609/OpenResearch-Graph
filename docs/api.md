# API reference

FastAPI sinh OpenAPI tự động từ route và Pydantic schema.

## Mở Swagger

```text
http://localhost:8000/docs
```

OpenAPI JSON:

```text
http://localhost:8000/openapi.json
```

## Prefix và version

Mọi endpoint sản phẩm dùng prefix `/api/v1`. Endpoint `/health` dùng cho healthcheck và không yêu cầu đăng nhập.

## Authentication

Gửi access token trong header:

```http
Authorization: Bearer <access-token>
```

Khi access token hết hạn, frontend gọi `/api/v1/auth/refresh` bằng refresh token rồi retry request đúng một lần. Refresh token được rotate; token cũ bị tái sử dụng sẽ thu hồi cả token family.

## Nhóm endpoint

| Nhóm | Prefix | Chức năng |
|---|---|---|
| Auth | `/api/v1/auth` | đăng ký, login, refresh, reset password |
| Search | `/api/v1/search` | hybrid paper retrieval |
| Papers | `/api/v1/papers` | metadata, related paper, citation |
| Documents | `/api/v1/documents` | upload, trạng thái, xóa PDF |
| Chat | `/api/v1/chat` | session và RAG messages |
| Recommendations | `/api/v1/recommendations` | hybrid recommendation và feedback |
| Library | `/api/v1/library` | save, collection, tags, notes |
| Subscriptions | `/api/v1/subscriptions` | mock/Stripe checkout và webhook |
| Admin | `/api/v1/admin` | health, integrations, jobs |

## Error format

Các lỗi validation dùng chuẩn FastAPI. Lỗi ứng dụng trả `detail` dễ đọc và status code phù hợp. Frontend dùng `ApiError` để giữ status và message.

Ví dụ:

```json
{
  "detail": "Document is still processing"
}
```

## Pagination

Search dùng `page` và `per_page`; ingestion OpenAlex dùng cursor vì phù hợp với tập kết quả lớn. Không sử dụng offset pagination để quét toàn bộ OpenAlex.

## Kiểm thử nhanh

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Dùng Swagger để đăng ký/login, bấm **Authorize**, rồi thử search và upload. Không dán credential production vào ảnh chụp README.
