# Security design

Tài liệu thao tác chi tiết: [`18_SECURITY_CHECKLIST_VI.md`](18_SECURITY_CHECKLIST_VI.md).

## Authentication

- Mật khẩu hash bằng Argon2.
- Access JWT sống ngắn, có `exp`, `nbf`, `jti` và subject.
- Refresh token lưu dưới dạng hash.
- Refresh-token rotation và family reuse detection.
- Đổi/reset mật khẩu thu hồi session cũ.
- Endpoint admin kiểm tra role ở backend, không chỉ ẩn UI.

## Authorization

Mọi thao tác document, chat, library và subscription phải scope theo `user_id`. Không nhận user ID từ frontend rồi tin tưởng trực tiếp.

## Secret

- `.env` không được commit.
- Frontend không được nhận backend secret.
- Không ghi token/password/key vào log.
- Chạy `python scripts/check_secrets.py` trước commit.
- Khi secret lộ, revoke và rotate; xóa commit không đủ nếu key đã bị sao chép.

## Upload

Kiểm tra file type, size, checksum và stored filename. Production cần malware scanning, quota và retention policy.

## Prompt injection

PDF là dữ liệu không đáng tin cậy. Nội dung tài liệu không được thay đổi system prompt, gọi tool tùy ý hoặc truy cập secret.

## Production hardening

Development frontend dùng localStorage để minh họa refresh flow. Production nên dùng secure, HttpOnly, SameSite cookie cho refresh token; bổ sung CSRF defense, CSP, HSTS, trusted proxy và audit logging.

## Kiểm thử bắt buộc

- Token expired/invalid/reused.
- User A không đọc/xóa tài nguyên User B.
- Admin route từ user thường trả 403.
- Stripe webhook sai signature bị từ chối.
- Upload giả PDF hoặc vượt quota bị chặn.
- Rate limit hoạt động khi Redis tạm lỗi.
